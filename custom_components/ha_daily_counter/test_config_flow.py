import pytest
from homeassistant.core import HomeAssistant
from homeassistant import config_entries
from custom_components.ha_daily_counter.const import DOMAIN


@pytest.mark.asyncio
async def test_options_flow(hass: HomeAssistant) -> None:
    """Test the options flow."""
    entry = config_entries.ConfigEntry(
        version=1,
        domain=DOMAIN,
        title="HA Daily Counter",
        data={},
        options={"counters": []},
        entry_id="1234",
        source="user",
    )

    flow = hass.config_entries.options.async_create_flow(entry)
    result = await flow.async_step_init()
    assert result["type"] == "form"
    assert result["step_id"] == "init"
