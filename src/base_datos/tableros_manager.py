"""
Gestor de Tableros para Community
Maneja operaciones CRUD de tableros, columnas y tarjetas
"""
from typing import Optional, List, Dict, Tuple
from .datos import db_manager


class TablerosManager:
    """Gestor de tableros usando Supabase"""
    
    def __init__(self):
        self.supabase = db_manager.supabase
    
    def crear_tablero(self, proyecto_id: str, nombre: str, descripcion: str = "") -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Crea un nuevo tablero (las columnas se crean automáticamente por trigger)
        
        Args:
            proyecto_id: ID del proyecto
            nombre: Nombre del tablero
            descripcion: Descripción del tablero
        
        Returns:
            Tupla (éxito, datos_tablero, error)
        """
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
        """
        Obtiene todos los tableros de un proyecto
        
        Args:
            proyecto_id: ID del proyecto
        
        Returns:
            Tupla (éxito, lista_tableros, error)
        """
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
        """
        Obtiene un tablero específico
        
        Args:
            tablero_id: ID del tablero
        
        Returns:
            Tupla (éxito, datos_tablero, error)
        """
        try:
            response = self.supabase.table('tableros').select('*').eq('id', tablero_id).execute()
            
            if response.data and len(response.data) > 0:
                return True, response.data[0], None
            else:
                return False, None, "Tablero no encontrado"
                
        except Exception as e:
            return False, None, f"Error: {str(e)}"
    
    def obtener_columnas(self, tablero_id: str) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """
        Obtiene las columnas de un tablero
        
        Args:
            tablero_id: ID del tablero
        
        Returns:
            Tupla (éxito, lista_columnas, error)
        """
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
        """
        Obtiene las tarjetas de una columna
        
        Args:
            columna_id: ID de la columna
        
        Returns:
            Tupla (éxito, lista_tarjetas, error)
        """
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
        """
        Elimina un tablero
        
        Args:
            tablero_id: ID del tablero
        
        Returns:
            Tupla (éxito, error)
        """
        try:
            response = self.supabase.table('tableros').delete().eq('id', tablero_id).execute()
            return True, None
                
        except Exception as e:
            return False, f"Error: {str(e)}"


# Instancia global
tableros_manager = TablerosManager()
