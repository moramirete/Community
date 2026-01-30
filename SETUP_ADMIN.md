# 🔧 Configuración de la Aplicación de Administración

## Pasos para configurar `admin_usuarios.py`

### 1️⃣ Ejecutar el Script SQL en Supabase

1. Ve a tu proyecto en Supabase: https://supabase.com/dashboard
2. Navega a **SQL Editor**
3. Copia y pega el contenido completo de `supabase_setup_usuarios.sql`
4. Haz clic en **Run** para ejecutar el script

Esto creará:
- ✅ Tabla `usuarios_info`
- ✅ Políticas RLS (Row Level Security)
- ✅ Trigger para sincronizar usuarios
- ✅ Función `delete_user` para eliminar usuarios
- ✅ Migración de usuarios existentes

### 2️⃣ Crear la Cuenta de Servicio en Supabase

Para que la aplicación pueda acceder a los datos, necesitas crear una cuenta de servicio:

**Opción A: Desde Supabase Dashboard**
1. Ve a **Authentication** → **Users**
2. Haz clic en **Add user** → **Create new user**
3. Ingresa:
   - **Email**: `admin@community.com`
   - **Password**: `Community2025`
4. Haz clic en **Create user**

**Opción B: Desde la aplicación Community**
1. Ejecuta `python interfaces/python/run_app.py`
2. Regístrate con:
   - **Email**: `admin@community.com`
   - **Password**: `Community2025`

### 3️⃣ Ejecutar la Aplicación de Administración

```bash
python admin_usuarios.py
```

### 4️⃣ Iniciar Sesión

Usa las credenciales de administrador:
- **Email**: `admin@community.com`
- **Contraseña**: `admin123`

---

## 🔑 Credenciales

### Credenciales de la UI (hardcodeadas en el código)
- **Email**: `admin@community.com`
- **Contraseña**: `admin123`

### Cuenta de Servicio (debe existir en Supabase)
- **Email**: `admin@community.com`
- **Password**: `Community2025`

---

## 🔒 Cambiar Credenciales

Si quieres cambiar las credenciales, edita el archivo `admin_usuarios.py` líneas 104-109:

```python
# Credenciales de administrador hardcodeadas
ADMIN_EMAIL = "admin@community.com"
ADMIN_PASSWORD = "admin123"

# Cuenta de servicio para acceder a Supabase
SERVICE_EMAIL = "admin@community.com"
SERVICE_PASSWORD = "Community2025"
```

**Importante**: Si cambias `SERVICE_EMAIL` o `SERVICE_PASSWORD`, asegúrate de crear esa cuenta en Supabase.

---

## ❌ Solución de Problemas

### Error: "JSON could not be generated"
- **Causa**: No has ejecutado el script SQL o la cuenta de servicio no existe
- **Solución**: Sigue los pasos 1 y 2 de esta guía

### Error: "Invalid API Key"
- **Causa**: Las credenciales de Supabase en el código son incorrectas
- **Solución**: Verifica `SUPABASE_URL` y `SUPABASE_KEY` en línea 12-13 de `admin_usuarios.py`

### No se muestran usuarios
- **Causa**: La tabla `usuarios_info` está vacía
- **Solución**: El script SQL incluye una migración automática. Si no funcionó, crea usuarios manualmente desde la aplicación Community.
