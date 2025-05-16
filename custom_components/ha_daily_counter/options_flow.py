from homeassistant import config_entries

class HADailyCounterOptionsFlow(config_entries.OptionsFlow):
    """Handle the options flow for HA Daily Counter."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the HA Daily Counter options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=config_entries.vol.Schema({}),
        )
