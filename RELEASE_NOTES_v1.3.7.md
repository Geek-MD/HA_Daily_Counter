# Release Notes for v1.3.7 / Notas de Lanzamiento v1.3.7

---

## 🇬🇧 English Version

### 🔧 Critical Bug Fix Release

This release fixes a critical migration error introduced in v1.3.6 that prevented existing counters from working properly.

#### What was fixed?
- ✅ Resolved "Flow handler not found for entry" error
- ✅ Existing counters are no longer disabled after upgrade
- ✅ All previously created counters now work correctly

#### Who should upgrade?
**All users who upgraded to v1.3.6 should upgrade to v1.3.7 immediately** to restore functionality to their existing counters.

#### What caused the issue?
The integration was missing a required method (`async_get_options_flow`) that links the configuration flow to the options flow handler. This prevented Home Assistant from properly loading existing config entries, causing all counters to appear as disabled with the error message:

```
Flow handler not found for entry [counter_name] for ha_daily_counter
```

#### Technical Changes
- Added `async_get_options_flow` static method to `HADailyCounterConfigFlow` class
- Updated version to 1.3.7 in manifest.json
- Ensured backward compatibility with existing installations

#### Installation
1. Update via HACS or manually install v1.3.7
2. Restart Home Assistant
3. Your existing counters should now be enabled and working

#### Need help?
If you continue to experience issues after upgrading:
1. Check your Home Assistant logs for any errors
2. Try reloading the integration from Settings → Devices & Services
3. Report issues at: https://github.com/Geek-MD/HA_Daily_Counter/issues

---

## 🇪🇸 Versión en Español

### 🔧 Lanzamiento de Corrección Crítica

Este lanzamiento corrige un error crítico de migración introducido en v1.3.6 que impedía que los contadores existentes funcionaran correctamente.

#### ¿Qué se corrigió?
- ✅ Resuelto el error "Flow handler not found for entry"
- ✅ Los contadores existentes ya no se deshabilitan después de la actualización
- ✅ Todos los contadores creados previamente ahora funcionan correctamente

#### ¿Quién debería actualizar?
**Todos los usuarios que actualizaron a v1.3.6 deben actualizar a v1.3.7 inmediatamente** para restaurar la funcionalidad de sus contadores existentes.

#### ¿Qué causó el problema?
La integración carecía de un método requerido (`async_get_options_flow`) que vincula el flujo de configuración con el manejador de flujo de opciones. Esto impidió que Home Assistant cargara correctamente las entradas de configuración existentes, causando que todos los contadores aparecieran como deshabilitados con el mensaje de error:

```
Flow handler not found for entry [nombre_contador] for ha_daily_counter
```

#### Cambios Técnicos
- Agregado método estático `async_get_options_flow` a la clase `HADailyCounterConfigFlow`
- Actualizada la versión a 1.3.7 en manifest.json
- Asegurada la compatibilidad con instalaciones existentes

#### Instalación
1. Actualiza a través de HACS o instala manualmente la v1.3.7
2. Reinicia Home Assistant
3. Tus contadores existentes deberían estar ahora habilitados y funcionando

#### ¿Necesitas ayuda?
Si continúas experimentando problemas después de actualizar:
1. Verifica los registros de Home Assistant para cualquier error
2. Intenta recargar la integración desde Configuración → Dispositivos y Servicios
3. Reporta problemas en: https://github.com/Geek-MD/HA_Daily_Counter/issues

---

## 📋 Copy-Paste for GitHub Release / Para copiar en GitHub Release

### Short Version / Versión Corta

**🔧 Critical Fix: Resolves migration error from v1.3.6**

This release fixes the "Flow handler not found for entry" error that disabled all existing counters after upgrading to v1.3.6. All users on v1.3.6 should upgrade immediately.

**What's Fixed:**
- ✅ Existing counters no longer disabled after upgrade
- ✅ All previously created counters work correctly
- ✅ Added missing `async_get_options_flow` method

**Installation:** Update via HACS and restart Home Assistant.

---

**🔧 Corrección Crítica: Resuelve error de migración de v1.3.6**

Este lanzamiento corrige el error "Flow handler not found for entry" que deshabilitaba todos los contadores existentes después de actualizar a v1.3.6. Todos los usuarios en v1.3.6 deben actualizar inmediatamente.

**Qué se Corrigió:**
- ✅ Los contadores existentes ya no se deshabilitan después de actualizar
- ✅ Todos los contadores creados previamente funcionan correctamente
- ✅ Agregado método `async_get_options_flow` faltante

**Instalación:** Actualiza vía HACS y reinicia Home Assistant.
