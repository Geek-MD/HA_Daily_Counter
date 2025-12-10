# Changelog

All notable changes to HA Daily Counter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
