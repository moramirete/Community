"""
Módulo de base de datos para Community
Gestiona la autenticación usando Supabase Auth
"""
import os
from typing import Optional, Tuple
from supabase import create_client, Client


class DatabaseManager:
    """Gestor de autenticación usando Supabase Auth"""
    
    # ========== CONFIGURACIÓN DE SUPABASE ==========
    # Solo necesitas configurar estos 2 valores:
    SUPABASE_URL = "https://hdhykbdkavtbvbbcymvo.supabase.co"  # Tu Project URL
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkaHlrYmRrYXZ0YnZiYmN5bXZvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkyNzQxNzEsImV4cCI6MjA4NDg1MDE3MX0.HgCz3Mw1PmMyt5wrC09Xs7EDM2bbkwW0uGYo_22Qg4c"  # Tu anon/public key
    # ===============================================
    
    def __init__(self):
        """Inicializa el gestor de base de datos"""
        self.supabase: Client = None
        self._init_client()
    
    def _init_client(self):
        """Inicializa el cliente de Supabase"""
        try:
            self.supabase = create_client(self.SUPABASE_URL, self.SUPABASE_KEY)
            print("✓ Conexión a Supabase Auth establecida correctamente")
        except Exception as e:
            print(f"✗ Error al conectar con Supabase: {e}")
            print("Verifica tus credenciales en src/base_datos/datos.py")
            raise
    
    def authenticate_user(self, email: str, password: str) -> Tuple[bool, Optional[dict]]:
        """
        Autentica un usuario usando Supabase Auth
        
        Args:
            email: Email del usuario
            password: Contraseña en texto plano
        
        Returns:
            Tupla (autenticado: bool, datos_usuario: dict o None)
        """
        try:
            # Autenticar con Supabase Auth
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                user_data = {
                    'id': response.user.id,
                    'email': response.user.email
                }
                return True, user_data
            else:
                return False, None
                
        except Exception as e:
            print(f"Error durante autenticación: {e}")
            return False, None
    
    def create_user(self, email: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        Crea un nuevo usuario usando Supabase Auth
        
        Args:
            email: Email del usuario
            password: Contraseña en texto plano
        
        Returns:
            Tupla (éxito: bool, mensaje_error: str o None)
        """
        try:
            # Crear usuario con Supabase Auth
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if response.user:
                return True, None
            else:
                return False, "Error al crear usuario"
            
        except Exception as e:
            error_msg = str(e)
            if 'already registered' in error_msg.lower():
                return False, "El usuario ya existe"
            return False, f"Error al crear usuario: {e}"
    
    def sign_out(self):
        """Cierra la sesión del usuario actual"""
        try:
            self.supabase.auth.sign_out()
        except Exception as e:
            print(f"Error al cerrar sesión: {e}")


# Instancia global del gestor de base de datos
db_manager = DatabaseManager()
