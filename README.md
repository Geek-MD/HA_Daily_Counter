[![Geek-MD - HA Daily Counter](https://img.shields.io/static/v1?label=Geek-MD&message=HA%20Daily%20Counter&color=blue&logo=github)](https://github.com/Geek-MD/HA_Daily_Counter)
[![Stars](https://img.shields.io/github/stars/Geek-MD/HA_Daily_Counter?style=social)](https://github.com/Geek-MD/HA_Daily_Counter)
[![Forks](https://img.shields.io/github/forks/Geek-MD/HA_Daily_Counter?style=social)](https://github.com/Geek-MD/HA_Daily_Counter)

[![GitHub Release](https://img.shields.io/github/release/Geek-MD/HA_Daily_Counter?include_prereleases&sort=semver&color=blue)](https://github.com/Geek-MD/HA_Daily_Counter/releases)
[![License](https://img.shields.io/badge/License-MIT-blue)](https://github.com/Geek-MD/HA_Daily_Counter/blob/main/LICENSE)
[![HACS Custom Repository](https://img.shields.io/badge/HACS-Custom%20Repository-blue)](https://hacs.xyz/)

[![Ruff + Mypy + Hassfest](https://github.com/Geek-MD/HA_Daily_Counter/actions/workflows/validate.yaml/badge.svg)](https://github.com/Geek-MD/HA_Daily_Counter/actions/workflows/validate.yaml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

![](https://github.com/Geek-MD/HA_Daily_Counter/blob/main/custom_components/ha_daily_counter/brand/logo.png)

# HA Daily Counter

**HA Daily Counter** is a custom integration for Home Assistant that provides **daily-resettable counters**, perfect for tracking repetitive actions like door openings, light switches, sensor triggers, and more. Now with **multiple trigger support** and **custom logic operators**.

---

## ✨ Features

- Create one or more counters with custom names.  
- Configure **one or more trigger entities** from multiple domains:
  - **Binary Sensors** (doors, windows, motion detectors)
  - **Sensors** (temperature, humidity, etc.)
  - **Automations** (track automation executions)
  - **Scripts** (monitor script runs)
  - **Input Helpers** (input_boolean, input_number, input_select)
- Choose the **trigger state** from a **smart dropdown** populated with the entity's known states (`on`/`off`, `open`/`closed`, input_select options, etc.). Custom values are always allowed.
- Define how multiple triggers are combined with **logic operators**:  
  - **AND** → All triggers must be active.  
  - **OR** → Any trigger increments the counter.  
- Filter entities by domain type for easy selection.
- **Auto-associate** the counter sensor with the trigger entity's device — the counter appears on the device's page in HA. When monitoring **multiple entities** the counter is created as an independent virtual device so it is never duplicated across several device pages.
- Auto-reset counters daily at midnight (00:00 local time).  
- Persistent values across Home Assistant restarts.  
- Fully manageable via the UI (no YAML required).  
- Exposed as `sensor` entities with `state_class: total_increasing` and `mdi:counter` icon.  
- Includes **reset** and **set** services for manual control.
- **Multi-language Support**: English, Spanish, French, Portuguese, and German

---

## 🛠 Installation

### Option 1: Installation via HACS
1. Go to **HACS → Integrations → Custom Repositories**.  
2. Add the repository URL:  
   ```
   https://github.com/Geek-MD/HA_Daily_Counter
   ```
3. Select category **Integration**.  
4. Search for **HA Daily Counter** in HACS and install it.  
5. Restart Home Assistant.  

### Option 2: Manual installation
1. Download the latest release from [GitHub](https://github.com/Geek-MD/HA_Daily_Counter/releases).  
2. Copy the `ha_daily_counter` folder into:  
   ```
   /config/custom_components/ha_daily_counter/
   ```
3. Restart Home Assistant.  

---

## ⚙️ Configuration

1. Go to **Settings → Devices & Services → Add Integration → HA Daily Counter**.  
2. Fill in the multi-step form:  
   - **Step 1 – Counter Setup**:
     - **Name**: Friendly name of the counter.
     - **Entity Type**: Select the domain to filter entities (Binary Sensor, Sensor, Automation, Script, or Input Helpers).
   - **Step 2 – Trigger Entity**:
     - **Trigger Entity**: Entity that will increment the counter (filtered to the selected type).
   - **Step 3 – Trigger State**:
     - **State to Monitor**: Select from a dropdown of the entity's known states (e.g., `on`, `off`, `open`). You can type a custom value if needed.
     - **Add Another Trigger?**: Toggle to add additional triggers. Subsequent entity selectors are automatically filtered to the **same domain** as the first entity.

3. If multiple triggers are added:  
   - For each additional trigger, first select the entity, then select its state from the dropdown.
   - Configure the **logic operator** (AND/OR) when adding the second trigger.
   - The same logic applies to all subsequent triggers.  

---

## 💡 Example Use Cases

- Count how many times the front door opened today.  
- Track how often lights were turned **on**.  
- Monitor motion detectors across multiple rooms, combined with **OR** logic.  
- Track automation executions (e.g., how many times "Turn on lights" automation ran).
- Monitor script runs (e.g., count "Night mode" script executions).
- Require two conditions (e.g., window open **AND** heater on) to increment.  
- Use multiple binary sensors to track activity across different zones.  

---

## 🖥 Services

Available services under the `ha_daily_counter` domain:

### 1. `ha_daily_counter.reset_counter`
Reset a counter to zero.

```yaml
service: ha_daily_counter.reset_counter
target:
  entity_id: sensor.my_counter
```

---

### 2. `ha_daily_counter.set_counter`
Set a counter to a specific integer value.

```yaml
service: ha_daily_counter.set_counter
data:
  entity_id: sensor.my_counter
  value: 42
```

---

## 📊 How It Works

- The counter increases by `+1` when its triggers match the configured states.  
- If multiple triggers are configured, the logic operator defines how they combine.  
- Counters reset to **0 every midnight** (local time).  
- Values persist across Home Assistant restarts.  

---

## 📜 License
MIT License. See [LICENSE](LICENSE) for details.  

---

## 🙏 Credits & Community

| Contribution | Contributor |
|---|---|
| Feature request: attach counter to existing device ([#34](https://github.com/Geek-MD/HA_Daily_Counter/issues/34)) | [@alsmaison](https://github.com/alsmaison) |
| Only binary sensor entities are shown when selecting a different entity type ([#31](https://github.com/Geek-MD/HA_Daily_Counter/issues/31)) | [@ikswokinok](https://github.com/ikswokinok) |

---

<div align="center">
  
💻 **Proudly developed with GitHub Copilot** 🚀

</div>
