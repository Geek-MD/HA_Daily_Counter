[![Geek-MD - HA Daily Counter](https://img.shields.io/static/v1?label=Geek-MD&message=HA%20Daily%20Counter&color=blue&logo=github)](https://github.com/Geek-MD/HA_Daily_Counter)
[![Stars](https://img.shields.io/github/stars/Geek-MD/HA_Daily_Counter?style=social)](https://github.com/Geek-MD/HA_Daily_Counter)
[![Forks](https://img.shields.io/github/forks/Geek-MD/HA_Daily_Counter?style=social)](https://github.com/Geek-MD/HA_Daily_Counter)

[![GitHub Release](https://img.shields.io/github/release/Geek-MD/HA_Daily_Counter?include_prereleases&sort=semver&color=blue)](https://github.com/Geek-MD/HA_Daily_Counter/releases)
[![License](https://img.shields.io/badge/License-MIT-blue)](https://github.com/Geek-MD/HA_Daily_Counter/blob/main/LICENSE)

[![Ruff + Mypy + Hassfest](https://github.com/Geek-MD/HA_Daily_Counter/actions/workflows/validate.yaml/badge.svg)](https://github.com/Geek-MD/HA_Daily_Counter/actions/workflows/validate.yaml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

<!-- ha-marketplace:exclude-start -->
[![Open your Home Assistant instance and open HA Daily Counter in the Marketplace.](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/marketplace_repository/?owner=Geek-MD&repository=HA_Daily_Counter&category=integration)
<!-- ha-marketplace:exclude-end -->

![](https://github.com/Geek-MD/HA_Daily_Counter/blob/main/custom_components/ha_daily_counter/brand/logo.png)

# HA Daily Counter

**HA Daily Counter** is a custom integration for Home Assistant that provides **automatically resettable counters** and optional **usage-time sensors**, perfect for tracking repetitive actions and how long equipment remains active. Now with **configurable reset cycles**, **multiple trigger support**, and **custom logic operators**.

---

## ✨ Features

- Create one or more counters with custom names.  
- Configure **one or more trigger entities** from multiple domains:
  - **Binary Sensors** (doors, windows, motion detectors)
  - **Sensors** (temperature, humidity, etc.)
  - **Switches, Lights, and Fans**
  - **Covers, Locks, and Alarm Control Panels**
  - **Automations** (track automation executions)
  - **Scripts** (monitor script runs)
  - **Input Helpers** (input_boolean, input_number, input_select)
- Choose the **trigger state** with Home Assistant's native **dynamic state selector**, linked to the entity selected in the preceding step. Custom and previously stored values remain supported.
- Define how multiple triggers are combined with **logic operators**:  
  - **AND** → All triggers must be active.  
  - **OR** → Any trigger increments the counter.  
- Filter entities by domain type for easy selection.
- **Auto-associate** the counter sensor with the trigger entity's device — the counter appears on the device's page in HA and automatically follows it if the source device is recreated after an integration reload failure. When monitoring **multiple entities** the counter is created as an independent virtual device so it is never duplicated across several device pages.
- Choose a reset cycle for each counter: every 15 minutes, hourly, daily, weekly, monthly, every two months, quarterly, yearly, or no automatic reset.
- Count either **all matching changes** or only a configurable maximum per reset cycle (default limit: `1`).
- Optionally classify the counter sensor, its Reset button, and its usage-time sensor as **Diagnostic** entities. Normal sensor classification remains the default.
- Optionally create a **usage-time sensor** that accumulates hours while the primary monitored entity remains in a selected state. Available states are discovered dynamically during configuration.
- Persistent values across Home Assistant restarts.  
- Fully manageable and reconfigurable via the UI (no YAML required). Existing counters can opt into the new per-cycle limit without being recreated.
- Renaming a counter entity in Home Assistant takes effect in place; integration services immediately follow its new entity ID.
- Exposed as `sensor` entities with `state_class: total_increasing`, the `events` unit and `mdi:counter` icon, so Home Assistant Recorder can generate long-term statistics.
- Includes **reset** and **set** services for manual control.
- Creates a **Reset** button entity for each counter, so manual cycles such as refilling a water softener can be restarted directly from the UI.
- **Multi-language Support**: English, Spanish, French, Portuguese, and German
- Native [**Probatio**](https://probatio.frenck.dev/) validation for configuration and options flows.

### Requirements

- Home Assistant **2026.9.0 or newer**. This integration uses the Probatio validation engine included with Home Assistant starting in 2026.9; see the [Home Assistant developer announcement](https://developers.home-assistant.io/blog/2026/09/30/probatio-validation-engine/).

---

## 🛠 Installation

<!-- ha-marketplace:exclude-start -->

### Option 1: Marketplace (Home Assistant 2026.11 or newer)

Marketplace is included with Home Assistant; no separate store installation or GitHub connection is required for this catalog integration.

1. Go to **Settings → Marketplace**.
2. Search for **HA Daily Counter** and open its repository page.
3. Select **Install**, review the version, and select **Install** again.
4. When installation finishes, complete the integration setup page that Home Assistant opens. If you close it, go to **Settings → Devices & services → Add integration → HA Daily Counter**.

Home Assistant will tell you through **Settings → System → Repairs** if a restart is required. A restart is no longer an unconditional installation step.

### Option 2: HACS (Home Assistant 2026.9–2026.10 only)

Marketplace replaced HACS in Home Assistant 2026.11. Use these legacy instructions only on an older supported Home Assistant release where HACS is already installed.

1. Open **HACS → Integrations**.
2. Search for **HA Daily Counter** and download it.
3. Restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration → HA Daily Counter**.

### Option 3: Manual installation

1. Download the latest release from [GitHub](https://github.com/Geek-MD/HA_Daily_Counter/releases).  
2. Copy the `ha_daily_counter` folder into:  
   ```
   /config/custom_components/ha_daily_counter/
   ```
3. Restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration → HA Daily Counter**.

<!-- ha-marketplace:exclude-end -->

---

## ⚙️ Configuration

1. Go to **Settings → Devices & Services → Add Integration → HA Daily Counter**.  
2. Fill in the multi-step form:  
   - **Step 1 – Counter Setup**:
     - **Name**: Friendly name of the counter.
     - **Entity Type**: Select the domain to filter entities (Binary Sensor, Sensor, Switch, Light, Fan, Cover, Lock, Alarm Control Panel, Automation, Script, or Input Helpers).
   - **Step 2 – Trigger Entity**:
     - **Trigger Entity**: Entity that will increment the counter (filtered to the selected type).
   - **Step 3 – Trigger State**:
     - **State to Monitor**: Home Assistant dynamically shows the states available for the entity selected in the preceding step. You can still enter a custom value when needed.
     - **Add Another Trigger?**: Toggle to add additional triggers. Subsequent entity selectors are automatically filtered to the **same domain** as the first entity.
   - **Step 4 – Reset Frequency**:
     - Choose when the counter returns to zero. Daily remains the default for backward compatibility.
     - Weekly cycles start on Monday. Monthly, bimonthly, quarterly, and yearly cycles start on the first day of their calendar period. All boundaries use Home Assistant's local timezone.
   - **Step 5 – Changes per Cycle**:
     - Choose **Count all changes** or **Count a limited number of changes**.
     - When limited counting is selected, set the maximum number of changes for each reset cycle. The default and minimum value is `1`.
   - **Step 6 – Additional Sensors and Classification**:
     - Enable **Classify entities as diagnostic** to move the counter and related entities to Home Assistant's Diagnostic section.
     - Enable **Create usage-time sensor** to add a duration sensor. This option is disabled by default.
   - **Step 7 – Usage State** *(shown only when usage-time tracking is enabled)*:
     - Select the state whose active duration should be accumulated. Home Assistant loads the choices dynamically from the first entity configured for the counter.

3. If multiple triggers are added:  
   - For each additional trigger, first select the entity, then select its state from the dropdown.
   - Configure the **logic operator** (AND/OR) when adding the second trigger.
   - The same logic applies to all subsequent triggers.  

To migrate an existing counter, open **Settings → Devices & Services → HA Daily Counter → Configure**. Complete the reconfiguration flow and select the desired mode under **Changes per Cycle**. Existing counters default to **Count all changes**, so upgrading does not change their behaviour until the user opts into a limit.

The same reconfiguration flow can enable or disable Diagnostic classification and usage-time tracking. Changing the usage entity or state starts a fresh duration measurement; disabling usage-time tracking removes the optional entity.

---

## 💡 Example Use Cases

- Count how many times the front door opened today.  
- Track how often lights were turned **on**.  
- Monitor motion detectors across multiple rooms, combined with **OR** logic.  
- Track automation executions (e.g., how many times "Turn on lights" automation ran).
- Monitor script runs (e.g., count "Night mode" script executions).
- Require two conditions (e.g., window open **AND** heater on) to increment.  
- Use multiple binary sensors to track activity across different zones.  
- Count washing-machine cycles between water-softener refills, using the counter's **Reset** button after each refill.

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
- In limited mode, matching changes are ignored after the configured maximum is reached. Scheduled, button, and service resets start a new counting cycle.
- The optional usage-time sensor reports hours with duration and `total_increasing` metadata. It updates once per minute while active and shares the counter's scheduled and manual resets.
- Time accumulated before a Home Assistant restart is restored when it belongs to the current reset period. Time while Home Assistant is offline is not inferred.
- If multiple triggers are configured, the logic operator defines how they combine.  
- Counters reset to **0 at the configured period boundary** in Home Assistant's local timezone.
- Values persist across Home Assistant restarts.  

---

## 📜 License
MIT License. See [LICENSE](LICENSE) for details.  

---

## 🙏 Credits & Community

| Contribution | Contributor |
|---|---|
| Bug report: restore the device attachment after the source device is recreated ([#53](https://github.com/Geek-MD/HA_Daily_Counter/issues/53)) | [@alsmaison](https://github.com/alsmaison) |
| Feature request: attach counter to existing device ([#34](https://github.com/Geek-MD/HA_Daily_Counter/issues/34)) | [@alsmaison](https://github.com/alsmaison) |
| Only binary sensor entities are shown when selecting a different entity type ([#31](https://github.com/Geek-MD/HA_Daily_Counter/issues/31)) | [@ikswokinok](https://github.com/ikswokinok) |

---

<div align="center">
  
💻 **Proudly developed with GitHub Copilot and ChatGPT Codex** 🚀

</div>
