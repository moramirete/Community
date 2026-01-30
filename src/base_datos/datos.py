import os
from typing import Optional, Tuple
from supabase import create_client, Client


class DatabaseManager:
    
    SUPABASE_URL = "https://hdhykbdkavtbvbbcymvo.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkaHlrYmRrYXZ0YnZiYmN5bXZvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkyNzQxNzEsImV4cCI6MjA4NDg1MDE3MX0.HgCz3Mw1PmMyt5wrC09Xs7EDM2bbkwW0uGYo_22Qg4c"
    
    def __init__(self):
        
        self.supabase: Client = None
        self.current_session = None
        self._inicializar_cliente()
    
    def _inicializar_cliente(self):
        
        try:
            self.supabase = create_client(self.SUPABASE_URL, self.SUPABASE_KEY)
            print("Conexión a Supabase Auth establecida correctamente")
        except Exception as e:
            print(f"Error al conectar con Supabase: {e}")
            print("Verifica tus credenciales en src/base_datos/datos.py")
            raise
    
    def autenticar_usuario(self, email: str, password: str) -> Tuple[bool, Optional[dict]]:
        
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            
            if response.user and response.session:
                self.current_session = response.session
                
                self.supabase.auth.set_session(
                    access_token=response.session.access_token,
                    refresh_token=response.session.refresh_token
                )
                
                user_data = {
                    'id': response.user.id,
                    'email': response.user.email
                }
                
                
                check_user = self.supabase.auth.get_user()
                
                return True, user_data
            else:
                return False, None
                
        except Exception as e:
            print(f"Error durante autenticación: {e}")
            return False, None
    
    def crear_usuario(self, email: str, password: str) -> Tuple[bool, Optional[str]]:
       
        try:
            
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
    
    def cerrar_sesion(self):
        
        try:
            self.supabase.auth.sign_out()
            self.current_session = None  
        except Exception as e:
            print(f"Error al cerrar sesión: {e}")
    
    def obtener_usuario_por_email(self, email: str) -> Tuple[bool, Optional[str]]:
        
        try:
            current_user = self.supabase.auth.get_user()
            if current_user and current_user.user and current_user.user.email == email:
                return True, current_user.user.id
            
            return False, None
            
        except Exception as e:
            print(f"Error al buscar usuario: {e}")
            return False, None

db_manager = DatabaseManager()
