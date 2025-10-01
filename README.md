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

## ✨ Features

- Create one or more counters with custom names.  
- Configure **one or multiple trigger entities**, all within the same counter.  
- Support for logical operators:  
  - **AND** → All triggers must be active to increment.  
  - **OR** → Any trigger increments the counter.  
  - **NAND** → Increments only if *not all* triggers are active.  
  - **NOR** → Increments only if *none* of the triggers are active.  
- Increment counters when trigger entities reach a specific state.  
- Auto-reset counters daily at midnight (**local time**).  
- Persistent values across Home Assistant restarts.  
- Manage everything via the **UI — no YAML required**.  
- Exposed as devices and `sensor` entities with `state_class: total_increasing` and `mdi:counter` icon for proper line graph history.  
- Includes **two services** to reset or set counter values manually.  

---

## 📦 Installation

### Option 1: Manual installation
1. Download the latest release from [GitHub](https://github.com/Geek-MD/HA_Daily_Counter/releases).  
2. Copy the `ha_daily_counter` folder into:  
   ```
   /config/custom_components/ha_daily_counter/
   ```
3. Restart Home Assistant.  
4. Add the integration from **Settings → Devices & Services → Add Integration → HA Daily Counter**.  

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

## ⚙️ Configuration

When adding the integration you’ll be guided through a multi-step form:

1. **Name** → Friendly label for your counter.  
2. **Trigger Entity** → Pick an entity to monitor (e.g. `binary_sensor.door`).  
3. **Trigger State** → Select the state that should increment the counter.  
4. **Add Another Trigger?** → Choose whether to add more entities.  
5. **Trigger Logic** → Define how multiple triggers interact (`AND`, `OR`, `NAND`, `NOR`).  

The counter will be created once configuration is complete.

---

## 📝 Example Use Cases

- Count how many times the **front door** opened today.  
- Track how often a **light** was switched on or off.  
- Monitor **motion detector activations** or button presses.  
- Combine with automations to notify when counters reach thresholds.  
- Create **compound counters** (e.g., count when two windows are open at the same time with `AND`).  

---

## 🔎 How It Works

- The counter increases by 1 whenever the configured trigger(s) match the logic and state.  
- Automatically resets to 0 every day at **00:00 local time**.  
- State is restored after Home Assistant restarts.  
- Each counter is exposed as a **sensor entity** attached to a device.  

---

## 🛠️ Services

After setup, the following services are available under the `ha_daily_counter` domain:

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
- `entity_id` _(required)_: The `entity_id` of the counter to adjust.  
- `value` _(required)_: Integer to assign to the counter.  

**Example:**
```yaml
service: ha_daily_counter.set_counter
data:
  entity_id: sensor.my_counter
  value: 42
```

---

## 👨‍💻 Development & Support

Maintained by [Geek-MD](https://github.com/Geek-MD).  
Pull requests and feature suggestions are welcome!

---

## 🎨 Icon Curiosity

Why does the icon show the number **28**?  
Because 28 is a **perfect number**: a positive integer equal to the sum of its proper divisors.  
For 28: `1 + 2 + 4 + 7 + 14 = 28`.  
Mathematics, beauty, and poetry.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
