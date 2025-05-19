import pytest
from homeassistant.core import HomeAssistant
from homeassistant import config_entries
from custom_components.ha_daily_counter.const import DOMAIN, CONF_RESET_HOUR


@pytest.mark.asyncio
async def test_options_flow(hass: HomeAssistant) -> None:
    """Test the options flow."""
    entry = config_entries.ConfigEntry(
        version=1,
        domain=DOMAIN,
        title="HA Daily Counter",
        data={},
        options={CONF_RESET_HOUR: 5},
        entry_id="1234",
        source="user",
    )

    flow = hass.config_entries.options.async_create_flow(entry)
    result = await flow.async_step_init()
    assert result["type"] == "form"
    assert result["step_id"] == "init"

    result2 = await flow.async_step_init(user_input={CONF_RESET_HOUR: 12})
    assert result2["type"] == "create_entry"
    assert result2["data"][CONF_RESET_HOUR] == 12
