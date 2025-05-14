[![Geek-MD - HA Daily Counter](https://img.shields.io/static/v1?label=Geek-MD&message=HA%20Daily%20Counter&color=blue&logo=github)](https://github.com/Geek-MD/HA_Daily_Counter)
[![stars - HA Daily Counter](https://img.shields.io/github/stars/Geek-MD/HA_Daily_Counter?style=social)](https://github.com/Geek-MD/HA_Daily_Counter)
[![forks - HA Daily Counter](https://img.shields.io/github/forks/Geek-MD/HA_Daily_Counter?style=social)](https://github.com/Geek-MD/HA_Daily_Counter)

![HACS Custom Repository](https://img.shields.io/badge/HACS-Custom%20Repository-blue)
[![GitHub Release](https://img.shields.io/github/release/Geek-MD/HA_Daily_Counter?include_prereleases&sort=semver&color=blue)](https://github.com/Geek-MD/HA_Daily_Counter/releases)
[![License](https://img.shields.io/badge/License-MIT-blue)](#license)

![HA Daily Counter Icon](https://github.com/Geek-MD/HA_Daily_Counter/blob/develop/icon.png)

# HA Daily Counter

**HA Daily Counter** is a custom integration for Home Assistant that provides **daily resettable counters**, perfect for tracking repetitive actions like door openings, light switches, or sensor triggers.

## 🛠️ Features
- Create one or more counters with custom names.
- Increment counters when a trigger entity reaches a specific state.
- Auto-reset counters daily at midnight.
- Persistent counter values across HA restarts.
- Fully manageable via the UI (no YAML required).
- Entities linked to devices for easy management in Home Assistant.
- Compatible with dashboards, automations, and statistics.

## 📦 Installation

1. Add this repository as a **custom repository in HACS**.
2. Install **HA Daily Counter** from HACS.
3. Restart Home Assistant.

## ⚙️ Configuration

1. Navigate to **Settings → Devices & Services**.
2. Click **Add Integration** and search for **HA Daily Counter**.
3. Configure:
   - **Name**: Friendly name for your counter.
   - **Trigger Entity**: Entity to monitor (e.g., `binary_sensor.door`).
   - **Trigger State**: State that will increment the counter (e.g., `on`, `open`).

### 📝 Example Use Cases
- Count how many times a door was opened today.
- Track how often a light has been switched on.
- Monitor motion detections or button presses daily.
- Combine with automations to notify when thresholds are reached.

## 🔎 How it Works
- The counter increases by 1 when the trigger entity changes to the defined state.
- Automatically resets to 0 every day at midnight.
- Remembers its value even after Home Assistant restarts.
- Visible as a **sensor entity** linked to a virtual device in the UI.

## 🧑‍💻 Development & Support
This integration is maintained by [Geek-MD](https://github.com/Geek-MD).

Pull requests, feature requests and contributions are welcome!

## 📄 License
MIT License
