"""
Gestor de Proyectos para Community
Maneja operaciones CRUD de proyectos y membresías
"""
from typing import Optional, List, Dict, Tuple
from .datos import db_manager


class ProyectosManager:
    """Gestor de proyectos usando Supabase"""
    
    def __init__(self):
        self.supabase = db_manager.supabase
    
    def crear_proyecto(self, nombre: str, descripcion: str = "", color: str = "#9333EA") -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Crea un nuevo proyecto
        
        Args:
            nombre: Nombre del proyecto
            descripcion: Descripción del proyecto
            color: Color del proyecto en formato hex
        
        Returns:
            Tupla (éxito, datos_proyecto, error)
        """
        try:
            # Obtener usuario actual
            user = self.supabase.auth.get_user()
            if not user or not user.user:
                return False, None, "Usuario no autenticado"
            
            # Crear proyecto
            response = self.supabase.table('proyectos').insert({
                'nombre': nombre,
                'descripcion': descripcion,
                'color': color,
                'creador_id': user.user.id
            }).execute()
            
            if response.data and len(response.data) > 0:
                return True, response.data[0], None
            else:
                return False, None, "Error al crear proyecto"
                
        except Exception as e:
            return False, None, f"Error: {str(e)}"
    
    def obtener_proyectos_usuario(self) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """
        Obtiene todos los proyectos del usuario actual
        
        Returns:
            Tupla (éxito, lista_proyectos, error)
        """
        try:
            # Obtener proyectos donde el usuario es miembro
            response = self.supabase.table('proyectos').select(
                '*, miembros_proyecto!inner(rol)'
            ).execute()
            
            if response.data:
                return True, response.data, None
            else:
                return True, [], None
                
        except Exception as e:
            return False, None, f"Error: {str(e)}"
    
    def obtener_proyecto(self, proyecto_id: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Obtiene un proyecto específico
        
        Args:
            proyecto_id: ID del proyecto
        
        Returns:
            Tupla (éxito, datos_proyecto, error)
        """
        try:
            response = self.supabase.table('proyectos').select('*').eq('id', proyecto_id).execute()
            
            if response.data and len(response.data) > 0:
                return True, response.data[0], None
            else:
                return False, None, "Proyecto no encontrado"
                
        except Exception as e:
            return False, None, f"Error: {str(e)}"
    
    def actualizar_proyecto(self, proyecto_id: str, nombre: Optional[str] = None, 
                          descripcion: Optional[str] = None, color: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Actualiza un proyecto
        
        Args:
            proyecto_id: ID del proyecto
            nombre: Nuevo nombre (opcional)
            descripcion: Nueva descripción (opcional)
            color: Nuevo color (opcional)
        
        Returns:
            Tupla (éxito, error)
        """
        try:
            datos = {}
            if nombre is not None:
                datos['nombre'] = nombre
            if descripcion is not None:
                datos['descripcion'] = descripcion
            if color is not None:
                datos['color'] = color
            
            if not datos:
                return True, None
            
            response = self.supabase.table('proyectos').update(datos).eq('id', proyecto_id).execute()
            
            if response.data:
                return True, None
            else:
                return False, "Error al actualizar proyecto"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def eliminar_proyecto(self, proyecto_id: str) -> Tuple[bool, Optional[str]]:
        """
        Elimina un proyecto
        
        Args:
            proyecto_id: ID del proyecto
        
        Returns:
            Tupla (éxito, error)
        """
        try:
            response = self.supabase.table('proyectos').delete().eq('id', proyecto_id).execute()
            return True, None
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def invitar_usuario(self, proyecto_id: str, email: str, rol: str = "miembro") -> Tuple[bool, Optional[str]]:
        """
        Invita un usuario al proyecto por email
        
        Args:
            proyecto_id: ID del proyecto
            email: Email del usuario a invitar
            rol: Rol del usuario (miembro, admin)
        
        Returns:
            Tupla (éxito, error)
        """
        try:
            # Buscar usuario por email en auth.users
            # Nota: Esto requiere que el usuario ya exista en Supabase Auth
            response = self.supabase.table('miembros_proyecto').insert({
                'proyecto_id': proyecto_id,
                'usuario_id': email,  # Aquí deberías buscar el user_id por email
                'rol': rol
            }).execute()
            
            if response.data:
                return True, None
            else:
                return False, "Error al invitar usuario"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def obtener_miembros(self, proyecto_id: str) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """
        Obtiene los miembros de un proyecto
        
        Args:
            proyecto_id: ID del proyecto
        
        Returns:
            Tupla (éxito, lista_miembros, error)
        """
        try:
            response = self.supabase.table('miembros_proyecto').select('*').eq('proyecto_id', proyecto_id).execute()
            
            if response.data:
                return True, response.data, None
            else:
                return True, [], None
                
        except Exception as e:
            return False, None, f"Error: {str(e)}"


# Instancia global
proyectos_manager = ProyectosManager()
