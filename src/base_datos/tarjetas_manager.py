from typing import Optional, List, Dict, Tuple
from datetime import date
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.base_datos.datos import db_manager


class TarjetasManager:
    
    def __init__(self):
        self.supabase = db_manager.supabase
    
    def crear_tarjeta(self, columna_id: str, titulo: str, descripcion: str = "", 
                     fecha_vencimiento: Optional[date] = None, color: str = "#FFFFFF", orden: int = 2) -> Tuple[bool, Optional[Dict], Optional[str]]:
        try:
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
        try:
            response = self.supabase.table('tarjetas').delete().eq('id', tarjeta_id).execute()
            return True, None
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def asignar_usuario(self, tarjeta_id: str, usuario_id: str) -> Tuple[bool, Optional[str]]:
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
        try:
            response = self.supabase.table('tarjetas_usuarios').delete().eq(
                'tarjeta_id', tarjeta_id
            ).eq('usuario_id', usuario_id).execute()
            
            return True, None
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def obtener_usuarios_asignados(self, tarjeta_id: str) -> Tuple[bool, Optional[List[str]], Optional[str]]:
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


tarjetas_manager = TarjetasManager()
