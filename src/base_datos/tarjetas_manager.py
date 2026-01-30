"""
Gestor de Tarjetas para Community
Maneja operaciones CRUD de tarjetas y asignaciones
"""
from typing import Optional, List, Dict, Tuple
from datetime import date
import sys
import os
# Asegurar que el path esté configurado correctamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.base_datos.datos import db_manager


class TarjetasManager:
    """Gestor de tarjetas usando Supabase"""
    
    def __init__(self):
        self.supabase = db_manager.supabase
    
    def crear_tarjeta(self, columna_id: str, titulo: str, descripcion: str = "", 
                     fecha_vencimiento: Optional[date] = None, color: str = "#FFFFFF", orden: int = 2) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Crea una nueva tarjeta
        
        Args:
            columna_id: ID de la columna
            titulo: Título de la tarjeta
            descripcion: Descripción de la tarjeta
            fecha_vencimiento: Fecha de vencimiento (opcional)
            color: Color de la tarjeta
            orden: Prioridad/Orden (0: Muy Importante, 1: Importante, 2: Normal)
        
        Returns:
            Tupla (éxito, datos_tarjeta, error)
        """
        try:
            # Obtener usuario actual desde la sesión almacenada
            if not db_manager.current_session:
                return False, None, "Usuario no autenticado"
            user_id = db_manager.current_session.user.id
            
            datos = {
                'columna_id': columna_id,
                'titulo': titulo,
                'descripcion': descripcion,
                'color': color,
                'orden': orden,
                'creador_id': user_id
            }
            
            if fecha_vencimiento:
                datos['fecha_vencimiento'] = fecha_vencimiento.isoformat()
            
            response = self.supabase.table('tarjetas').insert(datos).execute()
            
            if response.data and len(response.data) > 0:
                return True, response.data[0], None
            else:
                return False, None, "Error al crear tarjeta"
                
        except Exception as e:
            return False, None, f"Error: {str(e)}"
    
    def actualizar_tarjeta(self, tarjeta_id: str, titulo: Optional[str] = None,
                          descripcion: Optional[str] = None, fecha_vencimiento: Optional[date] = None,
                          color: Optional[str] = None, orden: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """
        Actualiza una tarjeta
        
        Args:
            tarjeta_id: ID de la tarjeta
            titulo: Nuevo título (opcional)
            descripcion: Nueva descripción (opcional)
            fecha_vencimiento: Nueva fecha (opcional)
            color: Nuevo color (opcional)
            orden: Nuevo orden/prioridad (opcional)
        
        Returns:
            Tupla (éxito, error)
        """
        try:
            datos = {}
            if titulo is not None:
                datos['titulo'] = titulo
            if descripcion is not None:
                datos['descripcion'] = descripcion
            if fecha_vencimiento is not None:
                datos['fecha_vencimiento'] = fecha_vencimiento.isoformat()
            if color is not None:
                datos['color'] = color
            if orden is not None:
                datos['orden'] = orden
            
            if not datos:
                return True, None
            
            response = self.supabase.table('tarjetas').update(datos).eq('id', tarjeta_id).execute()
            
            if response.data:
                return True, None
            else:
                return False, "Error al actualizar tarjeta"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def mover_tarjeta(self, tarjeta_id: str, nueva_columna_id: str, nuevo_orden: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """
        Mueve una tarjeta a otra columna
        
        Args:
            tarjeta_id: ID de la tarjeta
            nueva_columna_id: ID de la nueva columna
            nuevo_orden: Nuevo orden en la columna (None para mantener)
        
        Returns:
            Tupla (éxito, error)
        """
        try:
            datos_update = {
                'columna_id': nueva_columna_id
            }
            
            if nuevo_orden is not None:
                datos_update['orden'] = nuevo_orden
            
            response = self.supabase.table('tarjetas').update(datos_update).eq('id', tarjeta_id).execute()
            
            if response.data:
                return True, None
            else:
                return False, "Error al mover tarjeta"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def eliminar_tarjeta(self, tarjeta_id: str) -> Tuple[bool, Optional[str]]:
        """
        Elimina una tarjeta
        
        Args:
            tarjeta_id: ID de la tarjeta
        
        Returns:
            Tupla (éxito, error)
        """
        try:
            response = self.supabase.table('tarjetas').delete().eq('id', tarjeta_id).execute()
            return True, None
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def asignar_usuario(self, tarjeta_id: str, usuario_id: str) -> Tuple[bool, Optional[str]]:
        """
        Asigna un usuario a una tarjeta
        
        Args:
            tarjeta_id: ID de la tarjeta
            usuario_id: ID del usuario
        
        Returns:
            Tupla (éxito, error)
        """
        try:
            response = self.supabase.table('tarjetas_usuarios').insert({
                'tarjeta_id': tarjeta_id,
                'usuario_id': usuario_id
            }).execute()
            
            if response.data:
                return True, None
            else:
                return False, "Error al asignar usuario"
                
        except Exception as e:
            error_msg = str(e)
            if 'duplicate' in error_msg.lower():
                return False, "Usuario ya asignado"
            return False, f"Error: {str(e)}"
    
    def desasignar_usuario(self, tarjeta_id: str, usuario_id: str) -> Tuple[bool, Optional[str]]:
        """
        Desasigna un usuario de una tarjeta
        
        Args:
            tarjeta_id: ID de la tarjeta
            usuario_id: ID del usuario
        
        Returns:
            Tupla (éxito, error)
        """
        try:
            response = self.supabase.table('tarjetas_usuarios').delete().eq(
                'tarjeta_id', tarjeta_id
            ).eq('usuario_id', usuario_id).execute()
            
            return True, None
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def obtener_usuarios_asignados(self, tarjeta_id: str) -> Tuple[bool, Optional[List[str]], Optional[str]]:
        """
        Obtiene los IDs de usuarios asignados a una tarjeta
        
        Args:
            tarjeta_id: ID de la tarjeta
        
        Returns:
            Tupla (éxito, lista_usuario_ids, error)
        """
        try:
            response = self.supabase.table('tarjetas_usuarios').select('usuario_id').eq(
                'tarjeta_id', tarjeta_id
            ).execute()
            
            if response.data:
                usuarios = [item['usuario_id'] for item in response.data]
                return True, usuarios, None
            else:
                return True, [], None
                
        except Exception as e:
            return False, None, f"Error: {str(e)}"


# Instancia global
tarjetas_manager = TarjetasManager()
