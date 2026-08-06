"""Pytest configuration for the integration test suite."""

import sys
from types import ModuleType
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

# Load pure helper modules without executing the integration package's
# Home Assistant-dependent __init__.py.
package = ModuleType("custom_components.ha_daily_counter")
package.__path__ = [str(ROOT / "custom_components" / "ha_daily_counter")]
sys.modules[package.__name__] = package
