-- Función SQL para obtener todos los usuarios
-- Esta función debe ejecutarse en el SQL Editor de Supabase

-- Primero, crear una tabla para almacenar información de usuarios si no existe
CREATE TABLE IF NOT EXISTS public.usuarios_info (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Habilitar RLS (Row Level Security)
ALTER TABLE public.usuarios_info ENABLE ROW LEVEL SECURITY;

-- Eliminar políticas existentes si existen
DROP POLICY IF EXISTS "Usuarios autenticados pueden ver usuarios" ON public.usuarios_info;
DROP POLICY IF EXISTS "Sistema puede insertar usuarios" ON public.usuarios_info;

-- Política para que los usuarios autenticados puedan ver todos los usuarios
CREATE POLICY "Usuarios autenticados pueden ver usuarios"
ON public.usuarios_info
FOR SELECT
TO authenticated
USING (true);

-- Política para que solo el sistema pueda insertar
CREATE POLICY "Sistema puede insertar usuarios"
ON public.usuarios_info
FOR INSERT
TO authenticated
WITH CHECK (true);

-- Función para sincronizar usuarios de auth.users a usuarios_info
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.usuarios_info (id, email, created_at)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.created_at
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger para sincronizar automáticamente
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Función para eliminar usuario (requiere permisos especiales)
CREATE OR REPLACE FUNCTION public.delete_user(user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    -- Eliminar de usuarios_info (cascade eliminará de auth.users si está configurado)
    DELETE FROM public.usuarios_info WHERE id = user_id;
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- MIGRACIÓN DE USUARIOS EXISTENTES
-- ========================================
-- Este script copia todos los usuarios existentes de auth.users a usuarios_info
-- Solo se ejecuta una vez para migrar usuarios que ya existían antes de crear el trigger

INSERT INTO public.usuarios_info (id, email, created_at)
SELECT 
    id,
    email,
    created_at
FROM auth.users
WHERE id NOT IN (SELECT id FROM public.usuarios_info)
ON CONFLICT (id) DO NOTHING;
