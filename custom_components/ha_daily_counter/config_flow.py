from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    TextSelector,
    TextSelectorConfig
)
from homeassistant.data_entry_flow import FlowResult
from typing import Any

from .const import ATTR_TRIGGER_ENTITY, ATTR_TRIGGER_STATE
from .options_flow import HADailyCounterOptionsFlow


class HADailyCounterConfigFlow(config_entries.ConfigFlow, domain="ha_daily_counter"):  # type: ignore[call-arg]
    """Config flow for HA Daily Counter."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            name = user_input[CONF_NAME]
            trigger_entity = user_input[ATTR_TRIGGER_ENTITY]
            trigger_state = user_input[ATTR_TRIGGER_STATE]

            counter_id = trigger_entity.replace(".", "_")

            counter = {
                "id": counter_id,
                "name": name,
                "trigger_entity": trigger_entity,
                "trigger_state": trigger_state,
            }

            return self.async_create_entry(
                title="HA Daily Counter",
                data={},
                options={"counters": [counter]},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=config_entries.vol.Schema({
                config_entries.vol.Required(CONF_NAME): str,
                config_entries.vol.Required(ATTR_TRIGGER_ENTITY): EntitySelector(
                    EntitySelectorConfig()
                ),
                config_entries.vol.Required(ATTR_TRIGGER_STATE): TextSelector(
                    TextSelectorConfig(type="text")
                ),
            }),
        )

    @staticmethod
    def async_get_options_flow(entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Return the options flow."""
        return HADailyCounterOptionsFlow(entry)
