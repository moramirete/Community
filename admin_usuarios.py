"""
Aplicación de Administración de Usuarios para Community (Versión con tabla pública)
Permite crear cuentas de usuario y gestionar usuarios existentes
"""
import sys
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from supabase import create_client, Client
from datetime import datetime

# Configuración de Supabase
SUPABASE_URL = "https://hdhykbdkavtbvbbcymvo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkaHlrYmRrYXZ0YnZiYmN5bXZvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkyNzQxNzEsImV4cCI6MjA4NDg1MDE3MX0.HgCz3Mw1PmMyt5wrC09Xs7EDM2bbkwW0uGYo_22Qg4c"


class AdminUsuariosApp(QtWidgets.QMainWindow):
    """Aplicación principal de administración de usuarios"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Community - Administración de Usuarios")
        self.setMinimumSize(900, 700)
        
        # Conectar a Supabase
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.current_user = None
        
        # Mostrar login primero
        self.show_login()
    
    def show_login(self):
        """Muestra la pantalla de login"""
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QtWidgets.QVBoxLayout(central_widget)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        
        # Contenedor de login
        login_container = QtWidgets.QWidget()
        login_container.setMaximumWidth(400)
        login_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        login_layout = QtWidgets.QVBoxLayout(login_container)
        
        # Título
        titulo = QtWidgets.QLabel("🔐 Admin Login")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #9333EA; background: transparent;")
        titulo.setAlignment(QtCore.Qt.AlignCenter)
        login_layout.addWidget(titulo)
        
        login_layout.addSpacing(20)
        
        # Campos de login
        self.login_email = QtWidgets.QLineEdit()
        self.login_email.setPlaceholderText("Email de administrador")
        self.login_email.setStyleSheet("padding: 10px; border: 2px solid #E5E7EB; border-radius: 6px; background: white;")
        
        self.login_password = QtWidgets.QLineEdit()
        self.login_password.setPlaceholderText("Contraseña")
        self.login_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login_password.setStyleSheet("padding: 10px; border: 2px solid #E5E7EB; border-radius: 6px; background: white;")
        
        login_layout.addWidget(self.login_email)
        login_layout.addWidget(self.login_password)
        
        login_layout.addSpacing(10)
        
        # Botón de login
        btn_login = QtWidgets.QPushButton("Iniciar Sesión")
        btn_login.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #9333EA, stop:1 #A855F7);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7C3AED, stop:1 #9333EA);
            }
        """)
        btn_login.clicked.connect(self.login)
        login_layout.addWidget(btn_login)
        
        layout.addWidget(login_container)
    
    def login(self):
        """Realiza el login del administrador con credenciales hardcodeadas"""
        email = self.login_email.text().strip()
        password = self.login_password.text()
        
        # Credenciales de administrador hardcodeadas
        ADMIN_EMAIL = "admin@community.com"
        ADMIN_PASSWORD = "admin123"
        
        # Cuenta de servicio para acceder a Supabase (debe existir en tu base de datos)
        SERVICE_EMAIL = "admin@community.com"
        SERVICE_PASSWORD = "Community2025"
        
        if not email or not password:
            QtWidgets.QMessageBox.warning(self, "Error", "Por favor completa todos los campos")
            return
        
        # Verificar credenciales hardcodeadas
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            try:
                # Autenticar con Supabase usando cuenta de servicio para acceder a los datos
                response = self.supabase.auth.sign_in_with_password({
                    "email": SERVICE_EMAIL,
                    "password": SERVICE_PASSWORD
                })
                
                if response.user:
                    # Crear un objeto de usuario simulado para la UI
                    class AdminUser:
                        def __init__(self):
                            self.email = ADMIN_EMAIL
                            self.id = "admin-hardcoded"
                    
                    self.current_user = AdminUser()
                    self._setup_ui()
                    self.cargar_usuarios()
                else:
                    QtWidgets.QMessageBox.critical(
                        self, 
                        "Error de Configuración", 
                        f"No se pudo autenticar con la cuenta de servicio.\n\nPor favor, crea una cuenta en Supabase con:\nEmail: {SERVICE_EMAIL}\nContraseña: {SERVICE_PASSWORD}"
                    )
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, 
                    "Error de Configuración", 
                    f"Error al conectar con Supabase.\n\nAsegúrate de:\n1. Ejecutar el script SQL en Supabase\n2. Crear una cuenta con email: {SERVICE_EMAIL}\n\nError: {str(e)}"
                )
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "Credenciales incorrectas")
    
    def _setup_ui(self):
        """Configura la interfaz de usuario principal"""
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QtWidgets.QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header con título y botón de logout
        header_layout = QtWidgets.QHBoxLayout()
        
        titulo = QtWidgets.QLabel("Administración de Usuarios")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #9333EA;")
        header_layout.addWidget(titulo)
        
        header_layout.addStretch()
        
        # Info del usuario logueado
        user_label = QtWidgets.QLabel(f"👤 {self.current_user.email}")
        user_label.setStyleSheet("font-size: 12px; color: #666;")
        header_layout.addWidget(user_label)
        
        btn_logout = QtWidgets.QPushButton("Cerrar Sesión")
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        btn_logout.clicked.connect(self.logout)
        header_layout.addWidget(btn_logout)
        
        layout.addLayout(header_layout)
        
        # Sección de registro
        registro_group = QtWidgets.QGroupBox("Crear Nueva Cuenta")
        registro_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #9333EA;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        registro_layout = QtWidgets.QFormLayout()
        
        # Campos de registro
        self.input_email = QtWidgets.QLineEdit()
        self.input_email.setPlaceholderText("correo@ejemplo.com")
        self.input_email.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
        
        self.input_password = QtWidgets.QLineEdit()
        self.input_password.setPlaceholderText("Contraseña (mínimo 6 caracteres)")
        self.input_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.input_password.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
        
        registro_layout.addRow("Email:", self.input_email)
        registro_layout.addRow("Contraseña:", self.input_password)
        
        # Botón de crear cuenta
        btn_crear = QtWidgets.QPushButton("✓ Crear Cuenta")
        btn_crear.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #9333EA, stop:1 #A855F7);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7C3AED, stop:1 #9333EA);
            }
        """)
        btn_crear.clicked.connect(self.crear_usuario)
        registro_layout.addRow("", btn_crear)
        
        registro_group.setLayout(registro_layout)
        layout.addWidget(registro_group)
        
        # Sección de usuarios existentes
        usuarios_group = QtWidgets.QGroupBox("Usuarios Registrados")
        usuarios_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #9333EA;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        usuarios_layout = QtWidgets.QVBoxLayout()
        
        # Botón de refrescar
        btn_refresh = QtWidgets.QPushButton("🔄 Actualizar Lista")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #E5E7EB;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #D1D5DB;
            }
        """)
        btn_refresh.clicked.connect(self.cargar_usuarios)
        usuarios_layout.addWidget(btn_refresh)
        
        # Tabla de usuarios
        self.tabla_usuarios = QtWidgets.QTableWidget()
        self.tabla_usuarios.setColumnCount(3)
        self.tabla_usuarios.setHorizontalHeaderLabels(["Email", "Fecha Creación", "Acciones"])
        self.tabla_usuarios.horizontalHeader().setStretchLastSection(False)
        self.tabla_usuarios.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tabla_usuarios.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.tabla_usuarios.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.tabla_usuarios.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #F3F4F6;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        usuarios_layout.addWidget(self.tabla_usuarios)
        
        usuarios_group.setLayout(usuarios_layout)
        layout.addWidget(usuarios_group)
    
    def logout(self):
        """Cierra la sesión"""
        self.supabase.auth.sign_out()
        self.current_user = None
        self.show_login()
    
    def crear_usuario(self):
        """Crea un nuevo usuario en Supabase Auth"""
        email = self.input_email.text().strip()
        password = self.input_password.text()
        
        # Validaciones
        if not email or "@" not in email:
            QtWidgets.QMessageBox.warning(self, "Error", "Por favor ingresa un email válido")
            return
        
        if len(password) < 6:
            QtWidgets.QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 6 caracteres")
            return
        
        try:
            # Crear usuario en Supabase Auth con email auto-confirmado
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "email_confirm": True  # Auto-confirmar email
                }
            })
            
            if response.user:
                QtWidgets.QMessageBox.information(
                    self,
                    "✓ Usuario Creado",
                    f"Usuario {email} creado exitosamente"
                )
                
                # Limpiar campos
                self.input_email.clear()
                self.input_password.clear()
                
                # Recargar lista
                self.cargar_usuarios()
            else:
                QtWidgets.QMessageBox.critical(self, "Error", "No se pudo crear el usuario")
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error al crear usuario: {str(e)}")
    
    def cargar_usuarios(self):
        """Carga la lista de usuarios desde la tabla usuarios_info"""
        try:
            print("🔍 Intentando cargar usuarios desde usuarios_info...")
            
            # Obtener usuarios desde la tabla pública usuarios_info
            response = self.supabase.table('usuarios_info').select('*').order('created_at', desc=True).execute()
            
            print(f"✓ Respuesta recibida. Usuarios encontrados: {len(response.data) if response.data else 0}")
            
            self.tabla_usuarios.setRowCount(0)
            
            if response.data:
                for usuario in response.data:
                    row = self.tabla_usuarios.rowCount()
                    self.tabla_usuarios.insertRow(row)
                    
                    # Email
                    self.tabla_usuarios.setItem(row, 0, QtWidgets.QTableWidgetItem(usuario.get('email', 'N/A')))
                    
                    # Fecha
                    fecha = usuario.get('created_at', '')
                    if fecha:
                        try:
                            fecha_dt = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
                            fecha_str = fecha_dt.strftime('%d/%m/%Y %H:%M')
                        except:
                            fecha_str = fecha
                    else:
                        fecha_str = 'N/A'
                    self.tabla_usuarios.setItem(row, 1, QtWidgets.QTableWidgetItem(fecha_str))
                    
                    # Botón eliminar
                    btn_eliminar = QtWidgets.QPushButton("🗑️ Eliminar")
                    btn_eliminar.setStyleSheet("""
                        QPushButton {
                            background-color: #FEE2E2;
                            color: #DC2626;
                            border: none;
                            border-radius: 4px;
                            padding: 6px 12px;
                            font-size: 11px;
                        }
                        QPushButton:hover {
                            background-color: #FCA5A5;
                        }
                    """)
                    user_id = usuario.get('id')
                    btn_eliminar.clicked.connect(lambda checked, uid=user_id: self.eliminar_usuario(uid))
                    self.tabla_usuarios.setCellWidget(row, 2, btn_eliminar)
                
                print(f"✓ {len(response.data)} usuarios cargados en la tabla")
            else:
                print("⚠️ No hay usuarios en la tabla usuarios_info")
                QtWidgets.QMessageBox.information(
                    self, 
                    "Sin usuarios", 
                    "No hay usuarios registrados todavía.\n\n¿Ejecutaste el script SQL en Supabase?"
                )
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error al cargar usuarios: {error_msg}")
            
            if "relation" in error_msg.lower() and "does not exist" in error_msg.lower():
                QtWidgets.QMessageBox.critical(
                    self, 
                    "Tabla no encontrada", 
                    "La tabla 'usuarios_info' no existe en Supabase.\n\n"
                    "Por favor:\n"
                    "1. Ve a Supabase Dashboard → SQL Editor\n"
                    "2. Ejecuta el script 'supabase_setup_usuarios.sql'\n"
                    "3. Vuelve a intentar cargar usuarios"
                )
            else:
                QtWidgets.QMessageBox.critical(self, "Error", f"Error al cargar usuarios: {error_msg}")

    
    def eliminar_usuario(self, user_id):
        """Elimina un usuario"""
        reply = QtWidgets.QMessageBox.question(
            self,
            'Confirmar Eliminación',
            '¿Estás seguro de que quieres eliminar este usuario?\nEsta acción no se puede deshacer.',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                # Llamar a la función RPC para eliminar usuario
                self.supabase.rpc('delete_user', {'user_id': user_id}).execute()
                
                QtWidgets.QMessageBox.information(self, "✓ Eliminado", "Usuario eliminado correctamente")
                self.cargar_usuarios()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Error al eliminar usuario: {str(e)}")


def main():
    app = QtWidgets.QApplication(sys.argv)
    
    # Estilo global
    app.setStyle("Fusion")
    app.setStyleSheet("""
        QMainWindow {
            background-color: #F9FAFB;
        }
    """)
    
    window = AdminUsuariosApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
