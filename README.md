[![Geek-MD - HA Daily Counter](https://img.shields.io/static/v1?label=Geek-MD&message=HA%20Daily%20Counter&color=blue&logo=github)](https://github.com/Geek-MD/HA_Daily_Counter)
[![Stars](https://img.shields.io/github/stars/Geek-MD/HA_Daily_Counter?style=social)](https://github.com/Geek-MD/HA_Daily_Counter)
[![Forks](https://img.shields.io/github/forks/Geek-MD/HA_Daily_Counter?style=social)](https://github.com/Geek-MD/HA_Daily_Counter)

[![GitHub Release](https://img.shields.io/github/release/Geek-MD/HA_Daily_Counter?include_prereleases&sort=semver&color=blue)](https://github.com/Geek-MD/HA_Daily_Counter/releases)
[![License](https://img.shields.io/badge/License-MIT-blue)](#license)
![HACS Custom Repository](https://img.shields.io/badge/HACS-Custom%20Repository-blue)

[![Ruff](https://github.com/Geek-MD/HA_Daily_Counter/actions/workflows/ci.yaml/badge.svg?branch=main&label=Ruff)](https://github.com/Geek-MD/HA_Daily_Counter/actions/workflows/ci.yaml)
[![Mypy](https://github.com/Geek-MD/HA_Daily_Counter/actions/workflows/ci.yaml/badge.svg?branch=main&label=Mypy)](https://github.com/Geek-MD/HA_Daily_Counter/actions/workflows/ci.yaml)
[![Hassfest](https://github.com/Geek-MD/HA_Daily_Counter/actions/workflows/ci.yaml/badge.svg?branch=main&label=Hassfest)](https://github.com/Geek-MD/HA_Daily_Counter/actions/workflows/ci.yaml)

![HA Daily Counter Icon](https://github.com/Geek-MD/HA_Daily_Counter/blob/main/icon.png?raw=true)
# HA Daily Counter

**HA Daily Counter** is a custom integration for Home Assistant that provides **daily-resettable counters**, perfect for tracking repetitive actions like door openings, light switches, or sensor triggers.

---

## 🛠️ Features

- Create one or more counters with custom names.
- Increment counters when a trigger entity reaches a specific state.
- Auto-reset counters daily at midnight (00:00).
- Persistent values across Home Assistant restarts.
- Manage everything via the UI — no YAML required.
- Exposed as devices and entities for dashboards, automations, and statistics.

---

## 📦 Installation

1. Add this repository as a **custom repository in HACS**.
2. Install **HA Daily Counter** from HACS.
3. Restart Home Assistant.

---

## ⚙️ Configuration

1. Go to **Settings → Devices & Services**.
2. Click **Add Integration** and search for **HA Daily Counter**.
3. Create counters with:
   - **Name**: Friendly label (e.g. "Door Open Counter")
   - **Trigger Entity**: Entity to monitor (e.g. `binary_sensor.door`)
   - **Trigger State**: Value to match (e.g. `on`, `open`, `pressed`)

---

### 📝 Example Use Cases

- Count how many times the front door opened today.
- Track light switches or button presses.
- Monitor motion detector activations.
- Trigger automations when counters reach thresholds.

---

## 🔎 How It Works

- The counter increases when the trigger entity enters the specified state.
- Resets automatically to 0 at 00:00 daily.
- State is restored after Home Assistant restarts.
- Each counter is exposed as a **sensor entity** attached to a device.

---

## 🧑‍💻 Development & Support

Maintained by [Geek-MD](https://github.com/Geek-MD).  
Pull requests and feature suggestions are welcome!

---

## 📄 License

MIT License
