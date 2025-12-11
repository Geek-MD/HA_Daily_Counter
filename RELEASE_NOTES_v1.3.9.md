# Release Notes for v1.3.9 / Notas de Lanzamiento v1.3.9

---

## 🇬🇧 English Version

### ✨ New Feature: Counter Reconfiguration via Options Flow

This release adds the ability to edit and reconfigure existing counters directly through the Home Assistant UI, without having to delete and recreate them.

#### What's new?
- ✨ **Edit Counter Option**: New "Edit counter" action in the options flow menu
- 🔄 **Reconfigure Trigger Entity**: Change the entity that triggers the counter
- 🔄 **Reconfigure Trigger State**: Change the state that increments the counter
- 🔄 **Automatic Reload**: Integration automatically reloads when configuration changes are saved
- 📋 **Current Values Display**: See current configuration before making changes

#### Who should use this?
**All users who want to modify their existing counters** without losing their current count values or having to delete and recreate the counter.

#### How to use the new feature?
1. Go to Settings → Devices & Services
2. Find your HA Daily Counter integration
3. Click "Configure" on any existing counter entry
4. Select "Edit counter" from the action menu
5. Choose which counter you want to edit
6. Update the trigger entity or trigger state
7. The integration will automatically reload with the new configuration

#### Technical Changes
- Added `async_reload_entry` function in `__init__.py` to handle config entry reloads
- Registered update listener in `async_setup_entry` to detect option changes
- Added `async_step_select_edit`, `async_step_edit_trigger_entity`, and `async_step_edit_trigger_state` methods to `HADailyCounterOptionsFlow`
- Updated translation files (en.json, es.json, strings.json) with new edit-related strings
- Updated version to 1.3.9 in manifest.json

#### Installation
1. Update via HACS or manually install v1.3.9
2. Restart Home Assistant
3. Navigate to your integration settings to try the new edit feature

#### Need help?
If you experience any issues:
1. Check your Home Assistant logs for errors
2. Try reloading the integration from Settings → Devices & Services
3. Report issues at: https://github.com/Geek-MD/HA_Daily_Counter/issues

---

## 🇪🇸 Versión en Español

### ✨ Nueva Funcionalidad: Reconfiguración de Contadores vía Options Flow

Este lanzamiento añade la capacidad de editar y reconfigurar contadores existentes directamente a través de la interfaz de Home Assistant, sin necesidad de eliminar y recrear.

#### ¿Qué hay de nuevo?
- ✨ **Opción de Editar Contador**: Nueva acción "Editar contador" en el menú de flujo de opciones
- 🔄 **Reconfigurar Entidad Disparadora**: Cambia la entidad que dispara el contador
- 🔄 **Reconfigurar Estado Disparador**: Cambia el estado que incrementa el contador
- 🔄 **Recarga Automática**: La integración se recarga automáticamente cuando se guardan los cambios de configuración
- 📋 **Visualización de Valores Actuales**: Ve la configuración actual antes de hacer cambios

#### ¿Quién debería usar esto?
**Todos los usuarios que quieran modificar sus contadores existentes** sin perder los valores actuales del contador o tener que eliminar y recrear el contador.

#### ¿Cómo usar la nueva funcionalidad?
1. Ve a Configuración → Dispositivos y Servicios
2. Encuentra tu integración HA Daily Counter
3. Haz clic en "Configurar" en cualquier entrada de contador existente
4. Selecciona "Editar contador" del menú de acciones
5. Elige qué contador quieres editar
6. Actualiza la entidad disparadora o el estado disparador
7. La integración se recargará automáticamente con la nueva configuración

#### Cambios Técnicos
- Agregada función `async_reload_entry` en `__init__.py` para manejar recargas de entradas de configuración
- Registrado listener de actualización en `async_setup_entry` para detectar cambios de opciones
- Agregados métodos `async_step_select_edit`, `async_step_edit_trigger_entity` y `async_step_edit_trigger_state` a `HADailyCounterOptionsFlow`
- Actualizados archivos de traducción (en.json, es.json, strings.json) con nuevas cadenas relacionadas con edición
- Actualizada versión a 1.3.9 en manifest.json

#### Instalación
1. Actualiza a través de HACS o instala manualmente la v1.3.9
2. Reinicia Home Assistant
3. Navega a la configuración de tu integración para probar la nueva función de edición

#### ¿Necesitas ayuda?
Si experimentas algún problema:
1. Verifica los registros de Home Assistant para errores
2. Intenta recargar la integración desde Configuración → Dispositivos y Servicios
3. Reporta problemas en: https://github.com/Geek-MD/HA_Daily_Counter/issues

---

## 📋 Copy-Paste for GitHub Release / Para copiar en GitHub Release

### Short Version / Versión Corta

**✨ New Feature: Counter Reconfiguration via Options Flow**

This release adds the ability to edit existing counters through the Home Assistant UI without deleting and recreating them.

**What's New:**
- ✨ Edit counter option in options flow menu
- 🔄 Reconfigure trigger entity and state
- 🔄 Automatic reload when changes are saved
- 📋 Display current values before editing

**How to Use:**
1. Go to Settings → Devices & Services
2. Click "Configure" on any counter
3. Select "Edit counter"
4. Update trigger entity or state
5. Changes apply automatically after save

**Installation:** Update via HACS and restart Home Assistant.

---

**✨ Nueva Funcionalidad: Reconfiguración de Contadores vía Options Flow**

Este lanzamiento añade la capacidad de editar contadores existentes a través de la interfaz de Home Assistant sin eliminarlos y recrearlos.

**Qué Hay de Nuevo:**
- ✨ Opción de editar contador en el menú de flujo de opciones
- 🔄 Reconfigurar entidad y estado disparador
- 🔄 Recarga automática cuando se guardan los cambios
- 📋 Mostrar valores actuales antes de editar

**Cómo Usar:**
1. Ve a Configuración → Dispositivos y Servicios
2. Haz clic en "Configurar" en cualquier contador
3. Selecciona "Editar contador"
4. Actualiza entidad o estado disparador
5. Los cambios se aplican automáticamente después de guardar

**Instalación:** Actualiza vía HACS y reinicia Home Assistant.
