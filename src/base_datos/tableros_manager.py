from typing import Optional, List, Dict, Tuple
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.base_datos.datos import db_manager


class TablerosManager:
    
    def __init__(self):
        self.supabase = db_manager.supabase
    
    def crear_tablero(self, proyecto_id: str, nombre: str, descripcion: str = "") -> Tuple[bool, Optional[Dict], Optional[str]]:
        try:
            response = self.supabase.table('tableros').insert({
                'proyecto_id': proyecto_id,
                'nombre': nombre,
                'descripcion': descripcion
            }).execute()
            
            if response.data and len(response.data) > 0:
                return True, response.data[0], None
            else:
                return False, None, "Error al crear tablero"
                
        except Exception as e:
            return False, None, f"Error: {str(e)}"
    
    def obtener_tableros(self, proyecto_id: str) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        try:
            response = self.supabase.table('tableros').select('*').eq(
                'proyecto_id', proyecto_id
            ).order('orden').execute()
            
            if response.data:
                return True, response.data, None
            else:
                return True, [], None
                
        except Exception as e:
            return False, None, f"Error: {str(e)}"
    
    def obtener_tablero(self, tablero_id: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        try:
            response = self.supabase.table('tableros').select('*').eq('id', tablero_id).execute()
            
            if response.data and len(response.data) > 0:
                return True, response.data[0], None
            else:
                return False, None, "Tablero no encontrado"
                
        except Exception as e:
            return False, None, f"Error: {str(e)}"
    
    def obtener_columnas(self, tablero_id: str) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        try:
            response = self.supabase.table('columnas').select('*').eq(
                'tablero_id', tablero_id
            ).order('orden').execute()
            
            if response.data:
                return True, response.data, None
            else:
                return True, [], None
                
        except Exception as e:
            return False, None, f"Error: {str(e)}"
    
    def obtener_tarjetas(self, columna_id: str) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        try:
            response = self.supabase.table('tarjetas').select(
                '*, tarjetas_usuarios(usuario_id)'
            ).eq('columna_id', columna_id).order('orden').execute()
            
            if response.data:
                return True, response.data, None
            else:
                return True, [], None
                
        except Exception as e:
            return False, None, f"Error: {str(e)}"
    
    def eliminar_tablero(self, tablero_id: str) -> Tuple[bool, Optional[str]]:
        try:
            response = self.supabase.table('tableros').delete().eq('id', tablero_id).execute()
            return True, None
                
        except Exception as e:
            return False, f"Error: {str(e)}"


tableros_manager = TablerosManager()
