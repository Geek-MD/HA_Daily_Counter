from __future__ import annotations

import uuid
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
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

LOGIC_OPTIONS = ["AND", "OR"]  # Solo AND y OR, OR por defecto

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


class HADailyCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for HA Daily Counter with multiple triggers and an overall logic operator."""

    VERSION = 1

    def __init__(self) -> None:
        self._name: str | None = None
        self._triggers: list[dict[str, str]] = []
        self._available_domain: str | None = None
        self._add_more: bool = False
        self._logic: str = "OR"  # lógica elegida SOLO en el primer paso
        self._domain_filter: str | None = None  # Domain filter selected by user
        self._text_filter: str = ""  # Text filter for additional triggers

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """
        Primer paso: nombre, selección de dominio, entidad disparadora inicial,
        estado y checkbox add_another. NO incluye selector de lógica.
        """
        errors: dict[str, str] = {}

        if user_input is not None:
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

        # Default domain filter
        domain_filter = self._domain_filter or "binary_sensor"

        # Formulario inicial con dominio y selector de entidad (sin lógica)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
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
            ),
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
        errors: dict[str, str] = {}

        if user_input is not None:
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

        # Excluir entidades ya seleccionadas para no duplicar
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
            available_entities = [
                e for e in available_entities
                if text_filter in e.lower() or 
                (self.hass.states.get(e) and text_filter in self.hass.states.get(e).name.lower())
            ]

        # Friendly names de triggers previos (si existen en hass.states)
        prev_friendly = [
            f"{self.hass.states.get(t['entity']).name} ({t['state']})"
            for t in self._triggers
            if self.hass.states.get(t["entity"])
        ]

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

        return self.async_show_form(
            step_id="another_trigger",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={"previous_triggers": ", ".join(prev_friendly)} if prev_friendly else {},
            errors=errors,
        )

    async def async_step_finish(self) -> FlowResult:
        """Finaliza el flujo y crea la entry con los triggers y la lógica seleccionada en el primer paso."""
        title = self._name or "HA Daily Counter"
        data = {
            "triggers": self._triggers,
            "logic": self._logic,  # AND u OR
        }

        return self.async_create_entry(title=title, data=data)
