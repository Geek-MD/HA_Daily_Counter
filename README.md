[![Geek-MD - HADailyCounter](https://img.shields.io/static/v1?label=Geek-MD&message=HADailyCounter&color=blue&logo=github)](https://github.com/Geek-MD/HADailyCounter "Go to GitHub repo")
[![stars - HADailyCounter](https://img.shields.io/github/stars/Geek-MD/HADailyCounter?style=social)](https://github.com/Geek-MD/HADailyCounter)
[![forks - HADailyCounter](https://img.shields.io/github/forks/Geek-MD/HADailyCounter?style=social)](https://github.com/Geek-MD/HADailyCounter)

![Static Badge](https://img.shields.io/badge/custom_repository-HACS-blue)
[![GitHub release](https://img.shields.io/github/release/Geek-MD/HADailyCounter?include_prereleases=&sort=semver&color=blue)](https://github.com/Geek-MD/HADailyCounter/releases/)
[![License](https://img.shields.io/badge/License-MIT-blue)](#license)

![](https://github.com/Geek-MD/HADailyCounter/blob/develop/icon.png)

# HADailyCounter

**HADailyCounter** is a custom Home Assistant integration that provides resettable counters that increment on specific triggers and automatically reset daily.

## Features
- Increment counter when a trigger entity reaches a defined state.
- Reset counter to 0 every day at midnight.
- Persist counter value across Home Assistant restarts.
- Configure entirely via the UI (no YAML required).

## Installation

1. Add this repository to HACS as a **custom repository**.
2. Install the **HADailyCounter** integration from HACS.
3. Restart Home Assistant.

## Configuration

1. Navigate to **Settings → Devices & Services**.
2. Click **Add Integration** and search for **HADailyCounter**.
3. Set the following:
   - **Name**: Friendly name for your counter.
   - **Trigger Entity**: The entity to monitor (e.g., binary_sensor.door).
   - **Trigger State**: The state that will increment the counter (e.g., `on`, `open`).

## Usage Example

- Count how many times a door has been opened during the day.
- Track how often a light is turned on.
- Monitor sensor activations (motion, switches, etc.) with a daily reset.

## Development Notes

This integration is based on `HADailySensor`, adapted to provide counters with reset logic and dynamic configuration.

## License

This project is licensed under the MIT License.
