"""
Gestor de Proyectos para Community
Maneja operaciones CRUD de proyectos y membresías
"""
from typing import Optional, List, Dict, Tuple
import sys
import os
# Asegurar que el path esté configurado correctamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.base_datos.datos import db_manager


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
            # Obtener usuario actual desde la sesión almacenada
            if not db_manager.current_session:
                return False, None, "Usuario no autenticado"
            user_id = db_manager.current_session.user.id
            
            # Crear proyecto
            response = self.supabase.table('proyectos').insert({
                'nombre': nombre,
                'descripcion': descripcion,
                'color': color,
                'creador_id': user_id
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
            # Obtener usuario actual usando la sesión almacenada
            
            # Verificar si hay una sesión almacenada
            if not db_manager.current_session:
                return False, None, "Usuario no autenticado"
            
            # Obtener el user_id de la sesión almacenada
            user_id = db_manager.current_session.user.id
            
            # Obtener proyectos donde el usuario es propietario
            proyectos_propios = self.supabase.table('proyectos').select('*').eq('creador_id', user_id).execute()
            
            # Obtener proyectos donde el usuario es miembro (invitado)
            try:
                proyectos_miembro = self.supabase.table('proyectos').select(
                    '*, miembros_proyecto!inner(rol)'
                ).eq('miembros_proyecto.usuario_id', user_id).execute()
            except Exception as e:
                proyectos_miembro = type('obj', (object,), {'data': []})()
            
            # Combinar resultados evitando duplicados y añadiendo el rol del usuario
            proyectos_dict = {}
            
            if proyectos_propios.data:
                for p in proyectos_propios.data:
                    p['rol_usuario'] = 'CREADOR'  # Marcar como creador
                    proyectos_dict[p['id']] = p
            
            if proyectos_miembro.data:
                for p in proyectos_miembro.data:
                    if p['id'] not in proyectos_dict:
                        p['rol_usuario'] = 'MIEMBRO'  # Marcar como miembro
                        proyectos_dict[p['id']] = p
            
            proyectos = list(proyectos_dict.values())
            return True, proyectos, None
                
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
    
    def buscar_usuario_por_email(self, email: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Busca un usuario por email en Supabase Auth
        
        Args:
            email: Email del usuario a buscar
        
        Returns:
            Tupla (éxito, datos_usuario, error)
        """
        try:
            # Verificar autenticación usando la sesión almacenada
            if not db_manager.current_session:
                return False, None, "No autenticado"
            
            # Verificar si el usuario existe buscando en miembros_proyecto
            # (usuarios que ya están en algún proyecto)
            check_existing = self.supabase.table('miembros_proyecto').select('usuario_id').eq('usuario_id', email).limit(1).execute()
            
            if check_existing.data and len(check_existing.data) > 0:
                # Usuario encontrado en miembros_proyecto
                return True, {'id': email, 'email': email}, None
            
            # Si no está en miembros_proyecto, intentar verificar si existe en auth
            # Nota: Esto requiere que el email sea de un usuario registrado
            # Como fallback, asumimos que el email es válido si tiene formato correcto
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(email_pattern, email):
                return True, {'id': email, 'email': email}, None
            else:
                return False, None, "Formato de email inválido"
                
        except Exception as e:
            return False, None, f"Error al buscar usuario: {str(e)}"
    
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
            # Verificar autenticación usando la sesión almacenada
            if not db_manager.current_session:
                return False, "Usuario no autenticado"
            
            # Verificar que el email tenga formato válido
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return False, "El formato del email no es válido"
            
            # Buscar el UUID del usuario usando la función SQL
            usuario_id = None
            try:
                # Llamar a la función RPC que creaste en Supabase
                result = self.supabase.rpc('get_user_id_by_email', {'user_email': email}).execute()
                
                if result.data:
                    usuario_id = result.data
                else:
                    return False, f"No se encontró ningún usuario con el email '{email}'. Asegúrate de que el usuario esté registrado."
                    
            except Exception as e:
                return False, f"Error al buscar usuario: {str(e)}"
            
            # Verificar si el usuario ya es miembro
            if usuario_id:
                check = self.supabase.table('miembros_proyecto').select('*').eq('proyecto_id', proyecto_id).eq('usuario_id', usuario_id).execute()
                if check.data and len(check.data) > 0:
                    return False, "El usuario ya es miembro de este proyecto"
                
                # Agregar usuario al proyecto
                response = self.supabase.table('miembros_proyecto').insert({
                    'proyecto_id': proyecto_id,
                    'usuario_id': usuario_id,
                    'rol': rol
                }).execute()
                
                if response.data:
                    return True, None
                else:
                    return False, "Error al añadir usuario al proyecto"
            else:
                return False, f"No se pudo encontrar el usuario con email '{email}'"
                
        except Exception as e:
            error_msg = str(e)
            if 'uuid' in error_msg.lower() or '22p02' in error_msg:
                return False, f"No se pudo encontrar el usuario '{email}' en el sistema."
            return False, f"Error: {error_msg}"
    
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
