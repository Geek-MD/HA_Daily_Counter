[![Geek-MD - HA Daily Counter](https://img.shields.io/static/v1?label=Geek-MD&message=HA%20Daily%20Counter&color=blue&logo=github)](https://github.com/Geek-MD/HA_Daily_Counter)
[![Stars](https://img.shields.io/github/stars/Geek-MD/HA_Daily_Counter?style=social)](https://github.com/Geek-MD/HA_Daily_Counter)
[![Forks](https://img.shields.io/github/forks/Geek-MD/HA_Daily_Counter?style=social)](https://github.com/Geek-MD/HA_Daily_Counter)

[![GitHub Release](https://img.shields.io/github/release/Geek-MD/HA_Daily_Counter?include_prereleases&sort=semver&color=blue)](https://github.com/Geek-MD/HA_Daily_Counter/releases)
[![License](https://img.shields.io/badge/License-MIT-blue)](#license)
![HACS Custom Repository](https://img.shields.io/badge/HACS-Custom%20Repository-blue)
[![Ruff](https://github.com/Geek-MD/HA_Daily_Counter/actions/workflows/ci.yaml/badge.svg?branch=main&label=Ruff)](https://github.com/Geek-MD/HA_Daily_Counter/actions/workflows/ci.yaml)

<img width="200" height="200" alt="image" src="https://github.com/user-attachments/assets/028786f5-7c8e-4a18-9baa-23002cd368c0" />

# HA Daily Counter

**HA Daily Counter** is a custom integration for Home Assistant that provides **daily-resettable counters**, perfect for tracking repetitive actions like door openings, light switches, sensor triggers, and more.

---

## Features

- Create one or more counters with custom names.  
- Increment counters when a trigger entity reach a specified state.  
- Auto-reset counters daily at midnight (00:00 local time).  
- Persistent counter values across Home Assistant restarts.  
- Fully manageable via the UI (no YAML required).  
- Exposed as devices and `sensor` entities with `state_class: total_increasing` and `mdi:counter` icon for proper history graphs.  
- Two custom services to reset or set counter values manually.  

---

## Installation

1. Add this repository as a **custom repository in HACS**.  
2. Install **HA Daily Counter** from HACS.  
3. Restart Home Assistant.  

---

## Previous Steps

- If you need to configure multiple triggers, you must first create a “group” type helper and then use that helper as the trigger when setting up the sensor.

---

## Configuration

1. Go to **Settings → Devices & Services**.
2. Click **Add Integration** and search for **HA Daily Counter**.
3. Follow the multi-step form to:
   - **Name**: Friendly label for your counter.
   - **Trigger Entity**: Pick an entity that will increment the counter.
   - **Trigger State**: Specify the state value that will trigger an increment.
4. Finish to create the counter.

---

### Example Use Cases

- Count how many times a front door opened today.  
- Track how often a light was switched on or off.  
- Monitor motion detector activations or button presses.  
- Combine with automations to notify when thresholds are reached.  

---

## How It Works

- The counter increases by 1 whenever the configured trigger entity enters its matching state.  
- Automatically resets to 0 every day at **00:00 local time**.  
- Remembers its value after Home Assistant restarts.  
- Visible as a **sensor entity** linked to a device for easy management.  

---

## Services

After setup, the following services are available under the `ha_daily_counter` domain:

### ha_daily_counter.reset_counter

Reset a counter back to zero.

**Fields:**
- `entity_id` _(required)_: The `entity_id` of the counter to reset.

**Example:**
    service: ha_daily_counter.reset_counter
    target:
      entity_id: sensor.my_counter

### ha_daily_counter.set_counter

Set a counter to a specific integer value.

**Fields:**
- `entity_id` _(required)_: The `entity_id` of the counter to adjust.  
- `value` _(required)_: Integer to assign to the counter.

**Example:**
    service: ha_daily_counter.set_counter
    data:
      entity_id: sensor.my_counter
      value: 42

---

## Development & Support

Maintained by [Geek-MD](https://github.com/Geek-MD). Pull requests and feature suggestions are welcome!

---

## Icon Curiosity

Why does the icon shows the number 28? Simply because it's a very interesting number, it's a perfect number. What is a perfect number? A perfect number is a positive integer that equals the sum of its positive proper divisors. In the case of number 28, its divisors are 1, 2, 4, 7 and 14. Mathematics, beauty, and poetry.

---

## License

MIT License 
