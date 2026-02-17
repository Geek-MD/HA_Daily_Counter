from __future__ import annotations

import logging
import uuid
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE, DOMAIN

_LOGGER = logging.getLogger(__name__)

LOGIC_OPTIONS = ["AND", "OR"]  # Only AND and OR, OR by default

# Domain options for entity filtering
DOMAIN_OPTIONS = [
    SelectOptionDict(value="binary_sensor", label="Binary Sensor"),
    SelectOptionDict(value="sensor", label="Sensor"),
    SelectOptionDict(value="automation", label="Automation"),
    SelectOptionDict(value="script", label="Script"),
    SelectOptionDict(value="input_boolean", label="Input Boolean"),
    SelectOptionDict(value="input_number", label="Input Number"),
    SelectOptionDict(value="input_select", label="Input Select"),
]


class FlowHandler(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Config flow for HA Daily Counter with multiple triggers and an overall logic operator."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    def __init__(self) -> None:
        self._name: str | None = None
        self._triggers: list[dict[str, str]] = []
        self._available_domain: str | None = None
        self._add_more: bool = False
        self._logic: str = "OR"  # Logic selected only in first step
        self._domain_filter: str | None = None  # Domain filter selected by user
        self._text_filter: str = ""  # Text filter for additional triggers

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """
        Primer paso: nombre, selección de dominio, entidad disparadora inicial,
        estado y checkbox add_another. NO incluye selector de lógica.
        """
        _LOGGER.debug("Config flow step 'user' started")
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                self._name = user_input[CONF_NAME]
                
                # Store domain filter for next steps
                self._domain_filter = user_input.get("domain_filter")
                
                trigger_entity = user_input[ATTR_TRIGGER_ENTITY]
                trigger_state = user_input[ATTR_TRIGGER_STATE]

                # Guardamos el dominio para los siguientes disparadores
                if self._available_domain is None:
                    self._available_domain = trigger_entity.split(".")[0]

                self._triggers.append(
                    {
                        "id": str(uuid.uuid4()),
                        "entity": trigger_entity,
                        "state": trigger_state,
                    }
                )

                self._add_more = user_input.get("add_another", False)
                # Si no se pide agregar otro sensor, terminamos y creamos la entrada
                if not self._add_more:
                    return await self.async_step_finish()

                # Si se pidió agregar otro, vamos al paso de añadir más triggers
                return await self.async_step_another_trigger()
                
            except Exception as err:
                _LOGGER.error(
                    "Error in user step: %s",
                    err,
                    exc_info=True,
                )
                errors["base"] = "unknown"

        # Default domain filter
        domain_filter = self._domain_filter or "binary_sensor"

        # Formulario inicial con dominio y selector de entidad (sin lógica)
        try:
            data_schema = vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
                    vol.Required("domain_filter", default=domain_filter): SelectSelector(
                        SelectSelectorConfig(
                            options=DOMAIN_OPTIONS,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Required(ATTR_TRIGGER_ENTITY): EntitySelector(
                        EntitySelectorConfig(
                            domain=[domain_filter]
                        )
                    ),
                    vol.Required(ATTR_TRIGGER_STATE): str,
                    vol.Optional("add_another", default=False): bool,
                }
            )
        except Exception as err:
            _LOGGER.error(
                "Error creating user form schema: %s",
                err,
                exc_info=True,
            )
            errors["base"] = "unknown"
            # Fallback to minimal schema
            data_schema = vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
                    vol.Required(ATTR_TRIGGER_ENTITY): EntitySelector(
                        EntitySelectorConfig()
                    ),
                    vol.Required(ATTR_TRIGGER_STATE): str,
                }
            )
        
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_another_trigger(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """
        Paso repetible para añadir triggers adicionales.
        Muestra: campo de texto para filtrar, selector de entidad filtrado por el mismo dominio,
        selector de estado, selector de lógica (solo en el primer trigger adicional),
        y la casilla add_another para repetir.
        """
        _LOGGER.debug("Config flow step 'another_trigger' started")
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Store text filter if provided
                self._text_filter = user_input.get("text_filter", "")
                
                # Guardamos la lógica seleccionada solo en el primer trigger adicional
                if len(self._triggers) == 1 and "logic" in user_input:
                    self._logic = user_input.get("logic", "OR")
                
                # If entity is selected, add to triggers
                if ATTR_TRIGGER_ENTITY in user_input:
                    trigger_entity = user_input[ATTR_TRIGGER_ENTITY]
                    trigger_state = user_input[ATTR_TRIGGER_STATE]

                    self._triggers.append(
                        {
                            "id": str(uuid.uuid4()),
                            "entity": trigger_entity,
                            "state": trigger_state,
                        }
                    )

                    self._add_more = user_input.get("add_another", False)
                    # Si no se pide agregar otro, terminamos y creamos la entrada
                    if not self._add_more:
                        return await self.async_step_finish()

                    # Si se pidió agregar otro, repetimos este mismo paso
                    return await self.async_step_another_trigger()
                    
            except Exception as err:
                _LOGGER.error(
                    "Error processing another_trigger input: %s",
                    err,
                    exc_info=True,
                )
                errors["base"] = "unknown"

        # Excluir entidades ya seleccionadas para no duplicar
        try:
            excluded_entities = [t["entity"] for t in self._triggers]

            all_entities = [
                e.entity_id
                for e in self.hass.states.async_all()
                if self._available_domain and e.entity_id.startswith(self._available_domain)
            ]
            available_entities = [e for e in all_entities if e not in excluded_entities]
            
            # Apply text filter if provided
            text_filter = self._text_filter.lower()
            if text_filter:
                filtered = []
                for e in available_entities:
                    try:
                        if text_filter in e.lower():
                            filtered.append(e)
                            continue
                        state = self.hass.states.get(e)
                        if state and state.name and text_filter in state.name.lower():
                            filtered.append(e)
                    except Exception as err:
                        _LOGGER.warning(
                            "Error filtering entity %s: %s",
                            e,
                            err,
                        )
                        continue
                available_entities = filtered

            # Friendly names de triggers previos (si existen en hass.states)
            prev_friendly = []
            for t in self._triggers:
                try:
                    state = self.hass.states.get(t["entity"])
                    if state and state.name:
                        prev_friendly.append(f"{state.name} ({t['state']})")
                except Exception as err:
                    _LOGGER.warning(
                        "Error getting friendly name for %s: %s",
                        t.get("entity"),
                        err,
                    )

            # Handle case when no entities are available
            if not available_entities:
                _LOGGER.warning("No available entities found for domain %s", self._available_domain)
                # Instead of showing an error, go back to user step to start over
                return await self.async_step_finish()

            # Usamos SelectSelector con opciones construidas desde available_entities
            select_options = [SelectOptionDict(value=e, label=e) for e in available_entities]

            # Determinar si mostrar el selector de lógica (solo en el primer trigger adicional)
            is_first_additional = len(self._triggers) == 1
            
            # Construir el esquema del formulario dinámicamente
            schema_dict = {
                vol.Optional("text_filter", default=self._text_filter): TextSelector(
                    TextSelectorConfig(
                        type=TextSelectorType.TEXT,
                    )
                ),
                vol.Required(ATTR_TRIGGER_ENTITY): SelectSelector(
                    SelectSelectorConfig(
                        options=select_options,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(ATTR_TRIGGER_STATE): str,
            }
            
            # Agregar selector de lógica solo si es el primer trigger adicional
            if is_first_additional:
                schema_dict[vol.Optional("logic", default="OR")] = vol.In(LOGIC_OPTIONS)
            
            # Agregar checkbox add_another al final
            schema_dict[vol.Optional("add_another", default=False)] = bool

            data_schema = vol.Schema(schema_dict)
            
        except Exception as err:
            _LOGGER.error(
                "Error building another_trigger form schema: %s",
                err,
                exc_info=True,
            )
            errors["base"] = "unknown"
            # Fallback to minimal schema with conditional domain parameter
            entity_config = EntitySelectorConfig()
            if self._available_domain:
                entity_config = EntitySelectorConfig(domain=[self._available_domain])
            
            data_schema = vol.Schema(
                {
                    vol.Required(ATTR_TRIGGER_ENTITY): EntitySelector(entity_config),
                    vol.Required(ATTR_TRIGGER_STATE): str,
                }
            )

        return self.async_show_form(
            step_id="another_trigger",
            data_schema=data_schema,
            description_placeholders={"previous_triggers": ", ".join(prev_friendly)} if prev_friendly else {},
            errors=errors,
        )

    async def async_step_finish(self) -> FlowResult:
        """Finaliza el flujo y crea la entry con los triggers y la lógica seleccionada en el primer paso."""
        _LOGGER.debug("Config flow step 'finish' started")
        
        try:
            title = self._name or "HA Daily Counter"
            data = {
                "triggers": self._triggers,
                "logic": self._logic,  # AND u OR
            }

            _LOGGER.info(
                "Creating config entry: title=%s, triggers_count=%d, logic=%s",
                title,
                len(self._triggers),
                self._logic,
            )

            return self.async_create_entry(title=title, data=data)
            
        except Exception as err:
            _LOGGER.error(
                "Error creating config entry: %s",
                err,
                exc_info=True,
            )
            # Return to user step if creation fails
            return await self.async_step_user()


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle the options flow for HA Daily Counter."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry
        self._counters = list(config_entry.options.get("counters", []))
        self._new_counter: dict[str, Any] = {}
        self._selected_delete_name: str | None = None
        self._selected_edit_index: int | None = None
        self._editing_counter: dict[str, Any] = {}

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Initial step: add, edit, or delete a counter."""
        if user_input is not None:
            if user_input["action"] == "add":
                return await self.async_step_user()
            elif user_input["action"] == "edit":
                return await self.async_step_select_edit()
            elif user_input["action"] == "delete":
                return await self.async_step_select_delete()

            return self.async_create_entry(title="", data={"counters": self._counters})

        return self.async_show_form(
            step_id="init",
            data_schema={
                "action": SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value="add", label="Add counter"),
                            SelectOptionDict(value="edit", label="Edit counter"),
                            SelectOptionDict(value="delete", label="Delete counter"),
                            SelectOptionDict(value="finish", label="Finish setup")
                        ],
                        mode=SelectSelectorMode.DROPDOWN
                    )
                )
            },
        )

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step to collect the name of the new counter."""
        if user_input is not None:
            self._new_counter["name"] = user_input["name"]
            return await self.async_step_trigger_entity()

        return self.async_show_form(
            step_id="user",
            data_schema={"name": str},
        )

    async def async_step_trigger_entity(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step to collect the entity that triggers the counter."""
        if user_input is not None:
            self._new_counter["trigger_entity"] = user_input["trigger_entity"]
            return await self.async_step_trigger_state()

        return self.async_show_form(
            step_id="trigger_entity",
            data_schema={
                "trigger_entity": EntitySelector(EntitySelectorConfig())
            },
        )

    async def async_step_trigger_state(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step to collect the trigger state."""
        if user_input is not None:
            self._new_counter["trigger_state"] = user_input["trigger_state"]
            self._new_counter["id"] = str(uuid.uuid4())
            self._counters.append(self._new_counter)

            return await self.async_step_init()

        return self.async_show_form(
            step_id="trigger_state",
            data_schema={
                "trigger_state": str
            },
        )

    async def async_step_select_edit(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step to select a counter to edit."""
        if not self._counters:
            return await self.async_step_init()

        if user_input is not None:
            selected_name = user_input["edit_target"]
            # Find the counter index by name
            for idx, counter in enumerate(self._counters):
                if counter["name"] == selected_name:
                    self._selected_edit_index = idx
                    self._editing_counter = dict(counter)
                    return await self.async_step_edit_trigger_entity()
            # If not found, go back to init
            return await self.async_step_init()

        return self.async_show_form(
            step_id="select_edit",
            data_schema={
                "edit_target": SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value=c["name"], label=c["name"])
                            for c in self._counters
                        ],
                        mode=SelectSelectorMode.DROPDOWN
                    )
                )
            },
        )

    async def async_step_edit_trigger_entity(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step to edit the trigger entity."""
        if user_input is not None:
            self._editing_counter["trigger_entity"] = user_input["trigger_entity"]
            return await self.async_step_edit_trigger_state()

        # Get current trigger entity value
        current_entity = self._editing_counter.get("trigger_entity", "")

        return self.async_show_form(
            step_id="edit_trigger_entity",
            data_schema={
                "trigger_entity": EntitySelector(
                    EntitySelectorConfig()
                )
            },
            description_placeholders={
                "current_value": current_entity,
                "counter_name": self._editing_counter.get("name", "")
            }
        )

    async def async_step_edit_trigger_state(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step to edit the trigger state."""
        if user_input is not None:
            self._editing_counter["trigger_state"] = user_input["trigger_state"]
            # Update the counter in the list
            if self._selected_edit_index is not None and 0 <= self._selected_edit_index < len(self._counters):
                self._counters[self._selected_edit_index] = self._editing_counter
            
            # Reset editing state
            self._selected_edit_index = None
            self._editing_counter = {}
            
            return await self.async_step_init()

        # Get current trigger state value
        current_state = self._editing_counter.get("trigger_state", "")

        return self.async_show_form(
            step_id="edit_trigger_state",
            data_schema={
                "trigger_state": str
            },
            description_placeholders={
                "current_value": current_state,
                "counter_name": self._editing_counter.get("name", "")
            }
        )

    async def async_step_select_delete(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step to select a counter to delete."""
        if not self._counters:
            return await self.async_step_init()

        if user_input is not None:
            self._selected_delete_name = user_input["delete_target"]
            return await self.async_step_confirm_delete()

        return self.async_show_form(
            step_id="select_delete",
            data_schema={
                "delete_target": SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value=c["name"], label=c["name"])
                            for c in self._counters
                        ],
                        mode=SelectSelectorMode.DROPDOWN
                    )
                )
            },
        )

    async def async_step_confirm_delete(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Confirm and delete the selected counter."""
        if user_input is not None and user_input.get("confirm_delete"):
            self._counters = [c for c in self._counters if c["name"] != self._selected_delete_name]

        return await self.async_step_init()

    @callback
    def async_get_options(self) -> dict[str, Any]:
        return {"counters": self._counters}
