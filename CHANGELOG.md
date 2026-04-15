# Changelog

All notable changes to HA Daily Counter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2026-04-15

### ✨ New Feature: Attach Counter to an Existing Device (closes #34)

Counter sensors are now automatically associated with the device that owns their trigger entity. When you configure a counter whose trigger entity belongs to a physical or virtual device (e.g. a Tuya light, a Z-Wave switch, etc.), the counter sensor will appear directly on that device's page in Home Assistant instead of creating a separate virtual device entry.

### Added
- ✨ **Automatic device association**: `device_info` now queries the entity registry and device registry at runtime. If the trigger entity is linked to an existing device, the counter sensor adopts that device's identifiers and appears alongside it in the HA UI.
- ✅ **Graceful fallback**: If the trigger entity has no associated device (e.g. virtual helpers, template sensors), the counter falls back to the existing behaviour of creating its own virtual device entry.

### Changed
- Updated version to 1.5.0 in `manifest.json`.
- Added `device_registry` and `entity_registry` imports to `sensor.py`.

### Technical Details
- `HADailyCounterEntity.device_info` uses `er.async_get(hass).async_get(entity_id)` to retrieve the trigger entity's `device_id`, then `dr.async_get(hass).async_get(device_id)` to fetch the full `DeviceEntry` and its `identifiers`.
- Both registry lookups are synchronous in-memory operations (no I/O), so they are safe to perform inside a property.
- Inspired by the approach used in [ha_real-last-changed](https://github.com/HamletDuFromage/ha_real-last-changed).

### Credits
- 🙏 Feature requested by [@alsmaison](https://github.com/alsmaison) in [#34](https://github.com/Geek-MD/HA_Daily_Counter/issues/34).

---

## [1.4.2] - 2026-03-31

### ✨ New Feature: Monitor Any Entity Type + Fix Domain Filter (closes #31)

This release allows any entity domain to be used as a trigger entity, not just binary sensors, and fixes the bug where the entity selector always showed binary sensor entities regardless of the domain filter selected.

### Fixed
- ✅ **Domain Filter Bug** (#31): The entity selector was always showing binary sensor entities even when a different entity type was selected. The root cause was that HA config flow forms are static — a domain filter dropdown and an EntitySelector cannot coexist on the same form step and keep in sync. Fixed by splitting the step into two: one for name + domain selection, and a second for entity + state selection.

### Added
- ✨ **Any Entity Domain as Trigger**: Counters can now monitor entities from any domain:
  - **Binary Sensors** (doors, windows, motion detectors)
  - **Sensors** (temperature, humidity, etc.)
  - **Automations** (track automation executions)
  - **Scripts** (monitor script runs)
  - **Input Helpers** (`input_boolean`, `input_number`, `input_select`)
- ✨ **Domain Filter in Options Flow**: When adding or editing a counter via the options flow, a domain selection step is now shown before the entity selector, ensuring the correct entity type is displayed.
- ✨ **Cross-Domain Additional Triggers**: The "Add Another Trigger" step now uses a native EntitySelector with no domain restriction, allowing each additional trigger to reference a different entity domain.

### Changed
- 🏗️ **Config Flow Restructure**: `async_step_user` now only collects the counter name and domain filter. A new `async_step_first_trigger` handles entity and state selection, using an `EntitySelector` filtered to the chosen domain.
- 🏗️ **Options Flow Restructure**: Added `async_step_trigger_domain` (for adding) and `async_step_edit_trigger_domain` (for editing) steps before entity selection.
- 🧹 **Simplified `another_trigger` Step**: Replaced the complex server-side entity list builder (custom `SelectSelector`) and text filter with a native `EntitySelector` that supports all entity types and has built-in search.
- Updated all translation files (en.json, es.json, strings.json) with new step titles and descriptions.
- Updated version to 1.4.2 in manifest.json.

### Technical Details
- HA config flow forms are rendered statically: changing a dropdown value does not dynamically update other selectors on the same form. The fix separates domain selection and entity selection into consecutive steps.
- `EntitySelector` with `domain=[selected_domain]` is now created on a fresh step after the domain is already known, guaranteeing the correct entity list is shown.
- The `TextSelector` text filter in `another_trigger` has been removed; `EntitySelector` provides built-in search/filter natively in the HA frontend.

### Who Should Upgrade?
**All users should upgrade to v1.4.2** if experiencing:
- Entity selector always showing binary sensor entities regardless of domain selection
- Inability to configure non-binary-sensor entities as triggers

### Installation
1. Update via HACS or manually install v1.4.2
2. Restart Home Assistant
3. New counters can now be configured with any supported entity type

## [1.4.1] - 2026-02-17

### 🔧 Critical Bug Fix: OptionsFlow AttributeError

This release fixes a critical error that prevented users from accessing the options/configuration menu for existing integrations.

### Fixed
- ✅ **AttributeError Fix**: Fixed "property 'config_entry' of 'OptionsFlowHandler' object has no setter" error
- ✅ **OptionsFlow Initialization**: Corrected `OptionsFlowHandler.__init__()` to follow Home Assistant's OptionsFlow pattern
- ✅ **Configuration Access**: Users can now access the options menu without errors

### Technical Details
- Removed manual `config_entry` parameter from `OptionsFlowHandler.__init__()`
- The `config_entry` property is automatically provided by Home Assistant's `OptionsFlow` base class
- Updated `async_step_init()` to initialize counters from `self.config_entry.options` on first call
- The `config_entry` property is read-only and should not be assigned in `__init__`

### Who Should Upgrade?
**All users should upgrade to v1.4.1 immediately** if experiencing errors when trying to configure existing integrations, especially:
- "AttributeError: property 'config_entry' of 'OptionsFlowHandler' object has no setter" errors
- HTTP 500 errors when clicking "Configure" on an integration
- Unable to add, edit, or delete counters through the options flow

### Installation
1. Update via HACS or manually install v1.4.1
2. Restart Home Assistant
3. Configuration menu should now work without errors

## [1.4.0] - 2026-02-17

### 🔧 Critical Bug Fix: Error 500 During Reconfiguration + Code Structure Improvements

This release fixes HTTP 500 errors that could occur during integration configuration and reconfiguration, applying lessons learned from the Battery Devices Monitor integration. Additionally, the code structure has been refactored to follow Home Assistant best practices.

### Fixed
- ✅ **Error 500 Prevention**: Added comprehensive error handling throughout the config flow to prevent HTTP 500 errors
- ✅ **Empty Entity List Handling**: Fixed crash when no entities are available in the domain filter
- ✅ **Safe Schema Creation**: All form schema creation now wrapped in try-except blocks with safe fallback schemas
- ✅ **Robust Entity Filtering**: Added error handling for individual entity filtering operations
- ✅ **Better Error Logging**: Added debug and error logging throughout the config flow for easier troubleshooting

### Changed
- 🏗️ **Code Structure (Best Practice)**: Renamed classes following professional integration standards:
  - `HADailyCounterConfigFlow` → `FlowHandler`
  - `HADailyCounterOptionsFlow` → `OptionsFlowHandler`
  - Consolidated both classes into single `config_flow.py` file (removed separate `options_flow.py`)
  - Matches structure used by Battery Devices Monitor and other professional integrations
- Enhanced `async_step_user()` with comprehensive error handling and fallback schema
- Enhanced `async_step_another_trigger()` with multiple layers of error protection:
  - Input processing wrapped in try-except
  - Entity filtering with individual error handling
  - Empty entity list detection with safe fallback
  - Schema creation with comprehensive fallback
- Enhanced `async_step_finish()` with error handling and informational logging
- Updated version to 1.4.0 in manifest.json
- Modernized type hints to use native Python syntax (`dict[str, Any]` instead of `Dict[str, Any]`)

### Technical Details
- Applied Battery Devices Monitor pattern: defensive programming with try-except blocks
- All user input processing now safely handles exceptions
- Empty dropdown prevention: provides safe fallback when no entities available
- Form schema creation failures now return minimal functional schemas instead of crashing
- Added `_LOGGER` for consistent debug and error logging throughout config flow
- File structure now follows Home Assistant integration best practices with both flow handlers in single file

### Who Should Upgrade?
**All users should upgrade to v1.4.0** to ensure stable configuration and reconfiguration experience, especially when:
- Adding multiple triggers to a counter
- Using domain or text filters
- Working with limited entity availability
- Reconfiguring existing integrations

### Installation
1. Update via HACS or manually install v1.4.0
2. Restart Home Assistant
3. Configuration and reconfiguration should now work smoothly without 500 errors

## [1.3.9] - 2025-12-11

### ✨ New Feature: Counter Reconfiguration via Options Flow

This release adds the ability to edit and reconfigure existing counters directly through the Home Assistant UI, without having to delete and recreate them.

### Added
- ✨ **Edit Counter Option**: New "Edit counter" action in the options flow menu
- 🔄 **Reconfigure Trigger Entity**: Ability to change the entity that triggers the counter
- 🔄 **Reconfigure Trigger State**: Ability to change the state that increments the counter
- 🔄 **Automatic Reload**: Integration automatically reloads when configuration changes are saved
- 📋 **Current Values Display**: Shows current configuration before making changes in the edit flow

### Changed
- Updated `__init__.py` to register an update listener that reloads the integration when options are modified
- Enhanced `options_flow.py` with new edit steps: `async_step_select_edit`, `async_step_edit_trigger_entity`, and `async_step_edit_trigger_state`
- Updated all translation files (en.json, es.json, strings.json) with new edit-related strings
- Updated version to 1.3.9 in manifest.json

### Technical Details
- Added `async_reload_entry` function in `__init__.py` to handle config entry reloads
- Registered update listener in `async_setup_entry` to detect option changes and trigger reload
- Modified `HADailyCounterOptionsFlow` class to track editing state with `_selected_edit_index` and `_editing_counter`
- Edit flow preserves counter ID to maintain entity continuity

### How to Use
1. Go to Settings → Devices & Services
2. Find your HA Daily Counter integration
3. Click "Configure" on any existing counter entry
4. Select "Edit counter" from the action menu
5. Choose which counter you want to edit
6. Update the trigger entity or trigger state
7. The integration will automatically reload with the new configuration

## [1.3.8] - 2025-12-10

### 🔧 Critical Bug Fix Release

This release fixes the persistent migration error that continued to affect users even after v1.3.7.

### Fixed
- ✅ **Root Cause Fixed**: Resolved persistent "Flow handler not found for entry" error by properly registering ConfigFlow with Home Assistant
- ✅ Updated `HADailyCounterConfigFlow` to use modern ConfigFlow registration syntax: `class HADailyCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN)`
- ✅ Added `async_migrate_entry` function in `__init__.py` for better config entry migration handling
- ✅ All existing counters now load properly after restart
- ✅ Options menu now accessible for all config entries

### Who should upgrade?
**All users experiencing "Flow handler not found" errors should upgrade to v1.3.8 immediately** to restore full functionality.

### Technical Details
- The root cause was that the ConfigFlow class used old-style domain registration (`domain = DOMAIN` as class attribute) instead of the modern approach (`domain=DOMAIN` as class parameter)
- In Home Assistant 2021.11+, ConfigFlow classes must register by passing domain as a parameter to the parent class
- v1.3.7 added `async_get_options_flow` but didn't fix the underlying registration issue
- This fix ensures proper ConfigFlow registration with Home Assistant's flow handler registry

### Installation
1. Update via HACS or manually install v1.3.8
2. Restart Home Assistant
3. Verify all counters load properly and options menu is accessible

## [1.3.7] - 2025-12-10

### 🔧 Critical Bug Fix Release

This release fixes a critical migration error introduced in v1.3.6 that prevented existing counters from working properly.

### Fixed
- ✅ **Critical Migration Error**: Resolved "Flow handler not found for entry" error that caused all existing counters to be disabled after upgrading to v1.3.6
- ✅ Added missing `async_get_options_flow` static method to `HADailyCounterConfigFlow` class to properly link the options flow handler
- ✅ Existing config entries now work correctly and counters are no longer disabled after upgrade

### Who should upgrade?
**All users who upgraded to v1.3.6 should upgrade to v1.3.7 immediately** to restore functionality to their existing counters.

### Technical Details
- The issue occurred because Home Assistant could not find the options flow handler for existing config entries
- The `config_flow.py` had a `HADailyCounterConfigFlow` class but was missing the `async_get_options_flow` static method
- This method is required to connect the config flow to the `HADailyCounterOptionsFlow` class defined in `options_flow.py`
- This fix ensures backward compatibility with existing installations

### Installation
1. Update via HACS or manually install v1.3.7
2. Restart Home Assistant
3. Your existing counters should now be enabled and working

## [1.3.6] - Previous Release

### Added
- Multiple trigger support with custom logic operators (AND/OR)
- Domain filtering for entity selection
- Text filtering when adding additional triggers
- Enhanced multi-step configuration flow

### Changed
- Improved entity selection UI with domain-specific filtering
- Enhanced configuration workflow for adding multiple triggers

---

## Release Notes for v1.3.7

**🔧 Critical Bug Fix Release**

This release fixes a critical migration error introduced in v1.3.6 that prevented existing counters from working properly.

### What was fixed?
- ✅ Resolved "Flow handler not found for entry" error
- ✅ Existing counters are no longer disabled after upgrade
- ✅ All previously created counters now work correctly

### Who should upgrade?
**All users who upgraded to v1.3.6 should upgrade to v1.3.7 immediately** to restore functionality to their existing counters.

### What caused the issue?
The integration was missing a required method that links the configuration flow to the options flow handler. This prevented Home Assistant from properly loading existing config entries, causing all counters to appear as disabled.

### Installation
1. Update via HACS or manually install v1.3.7
2. Restart Home Assistant
3. Your existing counters should now be enabled and working

### Need help?
If you continue to experience issues after upgrading:
1. Check your Home Assistant logs for any errors
2. Try reloading the integration from Settings → Devices & Services
3. Report issues at: https://github.com/Geek-MD/HA_Daily_Counter/issues
