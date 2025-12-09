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

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """
        Primer paso: nombre, selección de dominio, entidad disparadora inicial,
        estado, checkbox add_another, y selector de lógica (AND/OR).
        La lógica se guarda y se usa para todos los triggers.
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

            # Guardamos la lógica seleccionada (OR por defecto)
            self._logic = user_input.get("logic", "OR")

            self._add_more = user_input.get("add_another", False)
            # Si no se pide agregar otro sensor, terminamos y creamos la entrada
            if not self._add_more:
                return await self.async_step_finish()

            # Si se pidió agregar otro, vamos al paso de añadir más triggers
            return await self.async_step_another_trigger()

        # Default domain filter
        domain_filter = self._domain_filter or "binary_sensor"

        # Formulario inicial con dominio y selector de entidad
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
                    vol.Optional("logic", default="OR"): vol.In(LOGIC_OPTIONS),
                }
            ),
            errors=errors,
        )

    async def async_step_another_trigger(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """
        Paso repetible para añadir triggers adicionales.
        Muestra: selector de entidad filtrado por el mismo dominio que la primera entidad,
        selector de estado y la casilla add_another para repetir. NO muestra el selector de lógica:
        la lógica ya fue elegida en el primer paso y se aplica a todos los triggers.
        """
        errors: dict[str, str] = {}

        if user_input is not None:
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

        # Friendly names de triggers previos (si existen en hass.states)
        prev_friendly = [
            f"{self.hass.states.get(t['entity']).name} ({t['state']})"
            for t in self._triggers
            if self.hass.states.get(t["entity"])
        ]

        # Usamos SelectSelector con opciones construidas desde available_entities
        select_options = [SelectOptionDict(value=e, label=e) for e in available_entities]

        return self.async_show_form(
            step_id="another_trigger",
            data_schema=vol.Schema(
                {
                    vol.Required(ATTR_TRIGGER_ENTITY): SelectSelector(
                        SelectSelectorConfig(
                            options=select_options,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Required(ATTR_TRIGGER_STATE): str,
                    vol.Optional("add_another", default=False): bool,
                }
            ),
            description_placeholders={"previous": ", ".join(prev_friendly)} if prev_friendly else {},
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
