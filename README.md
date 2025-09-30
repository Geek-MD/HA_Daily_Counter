[![Geek-MD - HA Daily Counter](https://img.shields.io/static/v1?label=Geek-MD&message=HA%20Daily%20Counter&color=blue&logo=github)](https://github.com/Geek-MD/HA_Daily_Counter)
[![Stars](https://img.shields.io/github/stars/Geek-MD/HA_Daily_Counter?style=social)](https://github.com/Geek-MD/HA_Daily_Counter)
[![Forks](https://img.shields.io/github/forks/Geek-MD/HA_Daily_Counter?style=social)](https://github.com/Geek-MD/HA_Daily_Counter)

[![GitHub Release](https://img.shields.io/github/release/Geek-MD/HA_Daily_Counter?include_prereleases&sort=semver&color=blue)](https://github.com/Geek-MD/HA_Daily_Counter/releases)
[![License](https://img.shields.io/badge/License-MIT-blue)](#license)
![HACS Custom Repository](https://img.shields.io/badge/HACS-Custom%20Repository-blue)
[![Ruff](https://github.com/Geek-MD/HA_Daily_Counter/actions/workflows/ci.yaml/badge.svg?branch=main&label=Ruff)](https://github.com/Geek-MD/HA_Daily_Counter/actions/workflows/ci.yaml)

<img width="200" height="200" alt="image" src="https://github.com/user-attachments/assets/028786f5-7c8e-4a18-9baa-23002cd368c0" />

# HA Daily Counter

**HA Daily Counter** is a custom Home Assistant integration that provides **daily-resettable counters**, perfect for tracking repetitive actions like door openings, light switches, sensor triggers, and more.

---

## ✨ Features
- Create one or more counters with custom names.  
- Increment counters when a trigger entity reaches a specified state.  
- Auto-reset counters daily at midnight (**00:00 local time**).  
- Persistent counter values across Home Assistant restarts.  
- Fully manageable via the UI (no YAML required).  
- Exposed as devices and `sensor` entities with `state_class: total_increasing` and `mdi:counter` icon for proper history graphs.  
- Two custom services to reset or set counter values manually.  
- **UI improvements in v1.2.5**:  
  - Trigger entities filtered to only show valid sensors/helpers.  
  - Trigger state options dynamically populated based on the selected entity.  
  - Proper usage of friendly strings in the setup dialog.

---

## ⚙️ Requirements
- Home Assistant **2024.6.0** or newer.  
- No additional dependencies required.  

---

## 📥 Installation

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

## 🔧 Configuration
When adding the integration:  
- **Name**: Friendly label for your counter.  
- **Trigger Entity**: Pick a valid sensor or helper that will increment the counter.  
- **Trigger State**: Select dynamically from the available states of the chosen entity.  

📌 If you need multiple triggers, first create a **Group Helper** in Home Assistant, and then use that group as the trigger.

---

## 🛠️ Services

### 1. `ha_daily_counter.reset_counter`
Reset a counter back to zero.

**Fields:**
- `entity_id` _(required)_: The `entity_id` of the counter to reset.

**Example:**
```yaml
service: ha_daily_counter.reset_counter
target:
  entity_id: sensor.my_counter
```

---

### 2. `ha_daily_counter.set_counter`
Set a counter to a specific integer value.

**Fields:**
- `entity_id` _(required)_: The `entity_id` of the counter.  
- `value` _(required)_: Integer to assign to the counter.  

**Example:**
```yaml
service: ha_daily_counter.set_counter
data:
  entity_id: sensor.my_counter
  value: 42
```

---

## 💡 Example Use Cases
- Count how many times the front door opened today.  
- Track how often a light was switched on or off.  
- Monitor motion detector activations or button presses.  
- Combine with automations to notify when thresholds are reached.  

---

## ⚙️ How It Works
- The counter increases by 1 whenever the configured trigger entity enters its matching state.  
- Automatically resets to 0 every day at **00:00 local time**.  
- Restores its value after Home Assistant restarts.  
- Exposed as a **sensor entity** linked to a device for easy dashboards and automations.  

---

## 🎨 Icon Curiosity
Why does the icon show the number **28**?  
Because 28 is a **perfect number**. A perfect number is a positive integer equal to the sum of its proper divisors. For 28, its divisors are **1 + 2 + 4 + 7 + 14**. Mathematics, beauty, and poetry.  

---

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.  
