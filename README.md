[![Geek-MD - HA Daily Counter](https://img.shields.io/static/v1?label=Geek-MD&message=HA%20Daily%20Counter&color=blue&logo=github)](https://github.com/Geek-MD/HA_Daily_Counter)
[![Stars](https://img.shields.io/github/stars/Geek-MD/HA_Daily_Counter?style=social)](https://github.com/Geek-MD/HA_Daily_Counter)
[![Forks](https://img.shields.io/github/forks/Geek-MD/HA_Daily_Counter?style=social)](https://github.com/Geek-MD/HA_Daily_Counter)

[![GitHub Release](https://img.shields.io/github/release/Geek-MD/HA_Daily_Counter?include_prereleases&sort=semver&color=blue)](https://github.com/Geek-MD/HA_Daily_Counter/releases)
[![License](https://img.shields.io/badge/License-MIT-blue)](#license)
![HACS Custom Repository](https://img.shields.io/badge/HACS-Custom%20Repository-blue)
[![Ruff](https://github.com/Geek-MD/HA_Daily_Counter/actions/workflows/ci.yaml/badge.svg?branch=main&label=Ruff)](https://github.com/Geek-MD/HA_Daily_Counter/actions/workflows/ci.yaml)

<img width="200" height="200" alt="icon" src="https://github.com/user-attachments/assets/028786f5-7c8e-4a18-9baa-23002cd368c0" />

# HA Daily Counter

**HA Daily Counter** is a custom Home Assistant integration to create **daily-resettable counters**, useful for tracking repetitive events such as door openings, light switches, or sensor activations.

---

## Features
- Create multiple counters with custom names.
- Increment counters when a trigger entity reaches a defined state.
- Automatic reset every day at **00:00 local time**.
- Persistent values across Home Assistant restarts.
- Fully managed through the UI (no YAML needed).
- Exposed as devices with `sensor` entities using the `mdi:counter` icon.
- Two custom services: reset a counter or set a specific value manually.

---

## Requirements
- Home Assistant 2024.6.0 or newer.

---

## Installation

### Option 1: Manual installation
1. Download the latest release from [GitHub](https://github.com/Geek-MD/HA_Daily_Counter/releases).
2. Copy the `ha_daily_counter` folder into:
   ```
   /config/custom_components/ha_daily_counter/
   ```
3. Restart Home Assistant.
4. Add the integration from **Settings → Devices & Services → Add Integration → HA Daily Counter**.

---

### Option 2: Installation via HACS
1. Go to **HACS → Integrations → Custom Repositories**.
2. Add the repository URL:  
   ```
   https://github.com/Geek-MD/HA_Daily_Counter
   ```
3. Select category **Integration**.
4. Search for **HA Daily Counter** in HACS and install it.
5. Restart Home Assistant.
6. Add the integration from **Settings → Devices & Services → Add Integration → HA Daily Counter**.

---

## Configuration
When adding a new counter:
- **Name**: Friendly name for the counter.
- **Trigger Entity**: Select a sensor or helper entity to watch.
- **Trigger State**: Choose from the available states of that entity.

👉 If you need to configure multiple triggers, first create a **group helper** and use that helper as the trigger.

---

## Services

### 1. `ha_daily_counter.reset_counter`
Resets a counter back to zero.

#### Service Data
| Field       | Required | Description                              |
|-------------|----------|------------------------------------------|
| `entity_id` | yes      | Entity ID of the counter to reset.       |

#### Example
```yaml
- service: ha_daily_counter.reset_counter
  target:
    entity_id: sensor.door_counter
```

---

### 2. `ha_daily_counter.set_counter`
Sets a counter to a specific integer value.

#### Service Data
| Field       | Required | Description                              |
|-------------|----------|------------------------------------------|
| `entity_id` | yes      | Entity ID of the counter to set.         |
| `value`     | yes      | Integer value to assign to the counter.  |

#### Example
```yaml
- service: ha_daily_counter.set_counter
  data:
    entity_id: sensor.door_counter
    value: 42
```

---

## Example Use Cases
- Count how many times the **front door** opened today.
- Track how many times a **light** was turned on.
- Monitor **motion sensor activations**.
- Combine with automations to trigger actions when thresholds are reached.

---

## Icon Curiosity
Why does the icon show the number **28**?  
Because 28 is a **perfect number**.  

👉 A perfect number is a positive integer equal to the sum of its proper divisors.  
For 28, the divisors are:  
`1 + 2 + 4 + 7 + 14 = 28`  

Mathematics, beauty, and poetry.

---

## License
MIT License. See [LICENSE](LICENSE) for details.
