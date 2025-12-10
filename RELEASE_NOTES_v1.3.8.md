# Release Notes for v1.3.8 / Notas de Lanzamiento v1.3.8

---

## 🇬🇧 English Version

### 🔧 Critical Bug Fix Release

This release fixes the persistent migration error that continued to affect users even after v1.3.7.

#### What was fixed?
- ✅ Resolved persistent "Flow handler not found for entry" error
- ✅ Fixed ConfigFlow registration with Home Assistant
- ✅ All existing counters now load properly after restart
- ✅ Options menu now accessible for all config entries

#### Who should upgrade?
**All users experiencing "Flow handler not found" errors should upgrade to v1.3.8 immediately** to restore full functionality to their existing counters.

#### What caused the issue?
The ConfigFlow class was not properly registered with Home Assistant's config flow registry. While v1.3.7 added the `async_get_options_flow` method, the root cause was that the ConfigFlow class used the old-style domain registration (`domain = DOMAIN` as a class attribute) instead of the modern approach (`domain=DOMAIN` as a class parameter).

In Home Assistant 2021.11 and later, ConfigFlow classes must be registered by passing the domain as a parameter to the parent class. The error manifested as:

```
Flow handler not found for entry [counter_name] for ha_daily_counter
```

#### Technical Changes
- Updated `HADailyCounterConfigFlow` to use modern ConfigFlow registration: `class HADailyCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN)`
- Added `async_migrate_entry` function in `__init__.py` for better entry migration handling
- Updated version to 1.3.8 in manifest.json
- Ensured full backward compatibility with existing installations

#### Installation
1. Update via HACS or manually install v1.3.8
2. Restart Home Assistant
3. All existing counters should now load properly
4. Options menu should be accessible for all entries

#### Verification
After upgrading, verify the fix by:
1. Go to Settings → Devices & Services
2. Find the HA Daily Counter integration
3. Click on any existing entry
4. You should see "Configure" option available
5. Check Home Assistant logs - no "Flow handler not found" errors should appear

#### Need help?
If you continue to experience issues after upgrading:
1. Check your Home Assistant logs for any errors
2. Try removing and re-adding the integration (note: this will reset your counters)
3. Report issues at: https://github.com/Geek-MD/HA_Daily_Counter/issues

---

## 🇪🇸 Versión en Español

### 🔧 Lanzamiento de Corrección Crítica

Este lanzamiento corrige el error de migración persistente que continuó afectando a los usuarios incluso después de v1.3.7.

#### ¿Qué se corrigió?
- ✅ Resuelto el error persistente "Flow handler not found for entry"
- ✅ Corregido el registro de ConfigFlow con Home Assistant
- ✅ Todos los contadores existentes ahora se cargan correctamente después de reiniciar
- ✅ Menú de opciones ahora accesible para todas las entradas de configuración

#### ¿Quién debería actualizar?
**Todos los usuarios que experimentan errores "Flow handler not found" deben actualizar a v1.3.8 inmediatamente** para restaurar la funcionalidad completa de sus contadores existentes.

#### ¿Qué causó el problema?
La clase ConfigFlow no estaba correctamente registrada con el registro de flujo de configuración de Home Assistant. Mientras que v1.3.7 agregó el método `async_get_options_flow`, la causa raíz fue que la clase ConfigFlow usaba el registro de dominio de estilo antiguo (`domain = DOMAIN` como atributo de clase) en lugar del enfoque moderno (`domain=DOMAIN` como parámetro de clase).

En Home Assistant 2021.11 y posteriores, las clases ConfigFlow deben registrarse pasando el dominio como parámetro a la clase padre. El error se manifestó como:

```
Flow handler not found for entry [nombre_contador] for ha_daily_counter
```

#### Cambios Técnicos
- Actualizado `HADailyCounterConfigFlow` para usar el registro moderno de ConfigFlow: `class HADailyCounterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN)`
- Agregada función `async_migrate_entry` en `__init__.py` para mejor manejo de migración de entradas
- Actualizada la versión a 1.3.8 en manifest.json
- Asegurada compatibilidad total con instalaciones existentes

#### Instalación
1. Actualiza a través de HACS o instala manualmente la v1.3.8
2. Reinicia Home Assistant
3. Todos los contadores existentes deberían cargarse correctamente
4. El menú de opciones debería estar accesible para todas las entradas

#### Verificación
Después de actualizar, verifica la corrección mediante:
1. Ve a Configuración → Dispositivos y Servicios
2. Encuentra la integración HA Daily Counter
3. Haz clic en cualquier entrada existente
4. Deberías ver la opción "Configurar" disponible
5. Revisa los registros de Home Assistant - no deberían aparecer errores "Flow handler not found"

#### ¿Necesitas ayuda?
Si continúas experimentando problemas después de actualizar:
1. Verifica los registros de Home Assistant para cualquier error
2. Intenta eliminar y volver a agregar la integración (nota: esto reiniciará tus contadores)
3. Reporta problemas en: https://github.com/Geek-MD/HA_Daily_Counter/issues

---

## 📋 Copy-Paste for GitHub Release / Para copiar en GitHub Release

### Short Version / Versión Corta

**🔧 Critical Fix: Resolves persistent migration error from v1.3.6-v1.3.7**

This release fixes the root cause of the "Flow handler not found for entry" error by properly registering the ConfigFlow class with Home Assistant's modern registration system.

**What's Fixed:**
- ✅ Fixed ConfigFlow registration using modern Home Assistant approach
- ✅ Existing counters now load properly after restart
- ✅ Options menu accessible for all config entries
- ✅ Added migration handler for better entry management

**Installation:** Update via HACS and restart Home Assistant.

---

**🔧 Corrección Crítica: Resuelve error de migración persistente de v1.3.6-v1.3.7**

Este lanzamiento corrige la causa raíz del error "Flow handler not found for entry" al registrar correctamente la clase ConfigFlow con el sistema de registro moderno de Home Assistant.

**Qué se Corrigió:**
- ✅ Corregido el registro de ConfigFlow usando el enfoque moderno de Home Assistant
- ✅ Los contadores existentes ahora se cargan correctamente después de reiniciar
- ✅ Menú de opciones accesible para todas las entradas de configuración
- ✅ Agregado manejador de migración para mejor gestión de entradas

**Instalación:** Actualiza vía HACS y reinicia Home Assistant.
