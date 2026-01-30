# Instrucciones para Configurar la Administración de Usuarios

## Paso 1: Ejecutar el Script SQL en Supabase

1. Ve a tu proyecto en Supabase Dashboard
2. Haz clic en "SQL Editor" en el menú lateral
3. Crea una nueva query
4. Copia y pega todo el contenido del archivo `supabase_setup_usuarios.sql`
5. Haz clic en "Run" para ejecutar el script

Este script creará:
- Una tabla `usuarios_info` para almacenar información de usuarios
- Un trigger que sincroniza automáticamente los usuarios de `auth.users` a `usuarios_info`
- Una función `delete_user()` para eliminar usuarios
- Políticas de seguridad (RLS) para proteger los datos

## Paso 2: Ejecutar la Aplicación

```bash
python admin_usuarios.py
```

## Características de la Aplicación

### Login de Administrador
- Debes iniciar sesión con una cuenta existente de Community
- Solo usuarios autenticados pueden acceder al panel de administración

### Crear Usuarios
- Nombre completo
- Email
- Contraseña (mínimo 6 caracteres)
- Los usuarios se crean automáticamente en `auth.users` y se sincronizan a `usuarios_info`

### Ver Usuarios
- Lista completa de todos los usuarios registrados
- Muestra: Nombre, Email, Fecha de creación
- Actualización en tiempo real

### Eliminar Usuarios
- Botón de eliminar para cada usuario
- Confirmación antes de eliminar
- Eliminación permanente de la base de datos

## Seguridad

✅ **Ventajas de este enfoque:**
- No necesitas la Service Role Key en tu código
- Toda la lógica de seguridad está en el servidor (Supabase)
- Las políticas RLS protegen los datos
- Solo usuarios autenticados pueden acceder

⚠️ **Importante:**
- Solo usuarios con sesión activa pueden ver/gestionar usuarios
- La función `delete_user()` está protegida con `SECURITY DEFINER`
- Los datos están protegidos por Row Level Security (RLS)

## Solución de Problemas

### Error: "relation usuarios_info does not exist"
- Asegúrate de haber ejecutado el script SQL en Supabase

### Error: "function delete_user does not exist"
- Verifica que el script SQL se ejecutó completamente sin errores

### No aparecen usuarios en la tabla
- Crea un nuevo usuario desde la aplicación
- El trigger debería sincronizarlo automáticamente
- Si ya tenías usuarios, ejecuta manualmente:
  ```sql
  INSERT INTO public.usuarios_info (id, email, nombre, created_at)
  SELECT id, email, raw_user_meta_data->>'nombre', created_at
  FROM auth.users;
  ```
