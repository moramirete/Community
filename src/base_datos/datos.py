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
        self.current_session = None  # Almacenar la sesión actual
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
            
            
            if response.user and response.session:
                # Guardar la sesión
                self.current_session = response.session
                
                # Establecer la sesión explícitamente en el cliente
                self.supabase.auth.set_session(
                    access_token=response.session.access_token,
                    refresh_token=response.session.refresh_token
                )
                
                user_data = {
                    'id': response.user.id,
                    'email': response.user.email
                }
                
                
                # Verificar que la sesión se guardó correctamente
                check_user = self.supabase.auth.get_user()
                
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
            self.current_session = None  # Limpiar la sesión almacenada
        except Exception as e:
            print(f"Error al cerrar sesión: {e}")
    
    def get_user_by_email(self, email: str) -> Tuple[bool, Optional[str]]:
        """
        Obtiene el UUID de un usuario por su email
        
        Args:
            email: Email del usuario
        
        Returns:
            Tupla (éxito, user_id o None)
        """
        try:
            # Intentar obtener el usuario actual primero
            current_user = self.supabase.auth.get_user()
            if current_user and current_user.user and current_user.user.email == email:
                return True, current_user.user.id
            
            # Si el email coincide con el usuario actual, retornar su ID
            # Para otros usuarios, necesitaríamos acceso admin o una función RPC
            # Como workaround, retornamos None para indicar que no se encontró
            return False, None
            
        except Exception as e:
            print(f"Error al buscar usuario: {e}")
            return False, None


# Instancia global del gestor de base de datos
db_manager = DatabaseManager()
