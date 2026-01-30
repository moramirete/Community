"""
Vista Home Dark modificada para mostrar proyectos del usuario
"""
import sys
import os
from PyQt5 import QtWidgets, QtCore, QtGui

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.base_datos.proyectos_manager import proyectos_manager
from src.base_datos.datos import db_manager

class ProyectoCardHomeDark(QtWidgets.QFrame):
    """Tarjeta de proyecto para el home dark"""
    clicked = QtCore.pyqtSignal(str)  # Emite el ID del proyecto
    favorito_toggled = QtCore.pyqtSignal(str, bool)  # Emite (ID, es_favorito)
    proyecto_eliminado = QtCore.pyqtSignal() # Señal eliminación
    
    def __init__(self, proyecto_data, favorito=False, parent=None):
        super().__init__(parent)
        self.proyecto_id = proyecto_data['id']
        self.proyecto_data = proyecto_data
        self.es_favorito = favorito
        
        # Verificar si el usuario actual es el propietario
        self.es_propietario = False
        if db_manager.current_session and db_manager.current_session.user:
            self.es_propietario = (proyecto_data.get('creador_id') == db_manager.current_session.user.id)

        self._setup_ui()
    
    def _setup_ui(self):
        self.setFixedSize(280, 180) # Changed from min/max to fixed size
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        # Color del proyecto
        color = self.proyecto_data.get('color', '#9333EA')
        # Updated styling to use qlineargradient and adjust_color (assuming adjust_color is defined elsewhere or will be added)
        # For now, I'll use a simplified version if adjust_color is not present, or keep the original if it's not meant to be changed.
        # Given the instruction is about owner check, I'll keep the original styling for now,
        # but if adjust_color is a new method, it needs to be added.
        # As adjust_color is not defined in the original code, I will revert this specific styling change
        # to avoid introducing an error, and only apply the owner check and fixed size.
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #4a4a64;
                border-radius: 10px;
            }}
            QFrame:hover {{
                background-color: #5a5a74;
            }}
        """)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Parte superior con color
        top_part = QtWidgets.QLabel()
        top_part.setMinimumHeight(60)
        top_part.setStyleSheet(f"background-color: {color}; border-top-left-radius: 10px; border-top-right-radius: 10px;")
        layout.addWidget(top_part)
        
        # Parte inferior con info
        bottom_part = QtWidgets.QFrame()
        bottom_part.setStyleSheet("background-color: #4a4a64; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        bottom_layout = QtWidgets.QVBoxLayout(bottom_part)
        bottom_layout.setContentsMargins(10, 8, 10, 8)
        
        # Nombre del proyecto
        nombre_label = QtWidgets.QLabel(self.proyecto_data['nombre'])
        nombre_label.setStyleSheet("font-weight: bold; font-size: 15px; color: #E5E5E5; background: transparent;")
        nombre_label.setWordWrap(True)
        nombre_label.setMaximumHeight(50)
        bottom_layout.addWidget(nombre_label)
        
        # Rol
        rol = self.proyecto_data.get('rol_usuario', 'MIEMBRO')
        rol_label = QtWidgets.QLabel(f"{rol}")
        rol_label.setStyleSheet("font-size: 11px; color: #CCC; background: transparent; font-weight: 500;")
        bottom_layout.addWidget(rol_label)
        
        # Botón de favorito (estrella) - Arriba Derecha
        self.btn_favorito = QtWidgets.QPushButton(self)
        self.btn_favorito.setFixedSize(30, 30)
        self.btn_favorito.setStyleSheet("""
            QPushButton {
                background: rgba(60, 60, 80, 0.7);
                border-radius: 15px;
                font-size: 18px;
                border: none;
                color: #777;
            }
            QPushButton:hover {
                background: #5a5a74;
            }
        """)
        self.btn_favorito.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_favorito.clicked.connect(self._toggle_favorito)
        self._actualizar_estrella()
        
        # Botón Eliminar (Papelera) - Abajo Derecha
        self.btn_eliminar = QtWidgets.QPushButton("🗑️", self)
        self.btn_eliminar.setFixedSize(30, 30)
        self.btn_eliminar.setStyleSheet("""
            QPushButton {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 15px;
                font-size: 14px;
                border: none;
                color: #B4B4C8;
            }
            QPushButton:hover {
                background: #EF4444;
                color: white;
            }
        """)
        self.btn_eliminar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_eliminar.clicked.connect(self.confirmar_eliminacion)
        
        # Botón Agregar Usuario (encima de papelera) - Solo visible para propietarios
        self.btn_agregar_usuario = QtWidgets.QPushButton("➕", self)
        self.btn_agregar_usuario.setFixedSize(30, 30)
        self.btn_agregar_usuario.setVisible(self.es_propietario)  # Solo visible si es propietario
        # Se posiciona en resizeEvent
        self.btn_agregar_usuario.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                font-size: 14px;
                border: none;
                color: #B4B4C8;
            }
            QPushButton:hover {
                background: #3B82F6;
                color: white;
            }
        """)
        self.btn_agregar_usuario.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_agregar_usuario.clicked.connect(self.abrir_dialogo_invitar)
        
        layout.addWidget(bottom_part)
    
    def _toggle_favorito(self):
        self.es_favorito = not self.es_favorito
        self._actualizar_estrella()
        self.favorito_toggled.emit(self.proyecto_id, self.es_favorito)
    
    def _actualizar_estrella(self):
        if self.es_favorito:
            self.btn_favorito.setText("★")
            self.btn_favorito.setStyleSheet(self.btn_favorito.styleSheet().replace("color: #777;", "color: #FFD700;"))
        else:
            self.btn_favorito.setText("☆")
            self.btn_favorito.setStyleSheet(self.btn_favorito.styleSheet().replace("color: #FFD700;", "color: #777;"))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Estrella arriba derecha
        if hasattr(self, 'btn_favorito'):
            self.btn_favorito.move(self.width() - 35, 5)
            self.btn_favorito.raise_()
        # Agregar usuario (encima de papelera)
        if hasattr(self, 'btn_agregar_usuario'):
            self.btn_agregar_usuario.move(self.width() - 35, self.height() - 75)
            self.btn_agregar_usuario.raise_()
        # Papelera abajo derecha
        if hasattr(self, 'btn_eliminar'):
            self.btn_eliminar.move(self.width() - 35, self.height() - 35)
            self.btn_eliminar.raise_()
    
    def confirmar_eliminacion(self):
        """Solicita confirmación y elimina el proyecto"""
        reply = QtWidgets.QMessageBox.question(
            self, 
            'Eliminar Proyecto', 
            f"¿Estás seguro de borrar el proyecto '{self.proyecto_data['nombre']}'?\nEsta acción no se puede deshacer.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, 
            QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            exito, error = proyectos_manager.eliminar_proyecto(self.proyecto_id)
            if exito:
                self.proyecto_eliminado.emit()
            else:
                QtWidgets.QMessageBox.critical(self, "Error", f"Error al eliminar proyecto: {error}")
    
    def abrir_dialogo_invitar(self):
        """Abre el diálogo para invitar usuarios al proyecto"""
        dialogo = InvitarUsuarioDialogDark(self.proyecto_id, self.proyecto_data['nombre'], self)
        if dialogo.exec_() == QtWidgets.QDialog.Accepted:
            # Refrescar si es necesario
            pass
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            child = self.childAt(event.pos())
            if isinstance(child, QtWidgets.QPushButton):
                return
            self.clicked.emit(self.proyecto_id)


class InvitarUsuarioDialogDark(QtWidgets.QDialog):
    """Diálogo para invitar usuarios a un proyecto (Dark Mode)"""
    
    def __init__(self, proyecto_id, proyecto_nombre, parent=None):
        super().__init__(parent)
        self.proyecto_id = proyecto_id
        self.proyecto_nombre = proyecto_nombre
        self.setWindowTitle(f"Invitar Usuario - {proyecto_nombre}")
        self.setMinimumWidth(400)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Título
        titulo = QtWidgets.QLabel(f"Añadir usuario al proyecto:")
        titulo.setStyleSheet("font-size: 14px; font-weight: bold; color: #E5E5E5;")
        layout.addWidget(titulo)
        
        proyecto_label = QtWidgets.QLabel(f'"{self.proyecto_nombre}"')
        proyecto_label.setStyleSheet("font-size: 12px; color: #B4B4C8; font-style: italic;")
        layout.addWidget(proyecto_label)
        
        # Campo de email
        email_label = QtWidgets.QLabel("Email del usuario:")
        email_label.setStyleSheet("font-size: 12px; color: #E5E5E5;")
        layout.addWidget(email_label)
        
        self.input_email = QtWidgets.QLineEdit()
        self.input_email.setPlaceholderText("usuario@ejemplo.com")
        self.input_email.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #444;
                border-radius: 5px;
                font-size: 13px;
                background: #2d2d44;
                color: #E5E5E5;
            }
            QLineEdit:focus {
                border: 1px solid #7C3AED;
            }
        """)
        layout.addWidget(self.input_email)
        
        layout.addStretch()
        
        # Botones
        botones_layout = QtWidgets.QHBoxLayout()
        botones_layout.addStretch()
        
        btn_cancelar = QtWidgets.QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                border: 1px solid #444;
                border-radius: 5px;
                background: #2d2d44;
                color: #E5E5E5;
            }
            QPushButton:hover {
                background: #3d3d54;
            }
        """)
        botones_layout.addWidget(btn_cancelar)
        
        btn_invitar = QtWidgets.QPushButton("Añadir")
        btn_invitar.clicked.connect(self.invitar_usuario)
        btn_invitar.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                border: none;
                border-radius: 5px;
                background: #7C3AED;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #9333EA;
            }
        """)
        botones_layout.addWidget(btn_invitar)
        
        layout.addLayout(botones_layout)
    
    def invitar_usuario(self):
        """Invita al usuario al proyecto"""
        email = self.input_email.text().strip()
        
        if not email:
            QtWidgets.QMessageBox.warning(self, "Error", "Por favor ingresa un email")
            return
        
        # Intentar añadir directamente
        exito, error = proyectos_manager.invitar_usuario(self.proyecto_id, email)
        
        if exito:
            QtWidgets.QMessageBox.information(
                self, 
                "✅ Usuario añadido", 
                f"El usuario {email} ha sido añadido al proyecto \"{self.proyecto_nombre}\" correctamente"
            )
            self.accept()
        else:
            QtWidgets.QMessageBox.critical(
                self, 
                "❌ Error", 
                f"{error}"
            )


class HomeCommunityDarkWindow(QtWidgets.QMainWindow):
    """Vista Home Dark que muestra proyectos del usuario"""
    proyecto_seleccionado = QtCore.pyqtSignal(str)  # Emite ID del proyecto
    logout_requested = QtCore.pyqtSignal()  # Emite cuando se solicita cerrar sesión
    
    def __init__(self, parent=None, favoritos_sharing=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), '..', '.ui', 'home_community_dark.ui')
        ui_path = os.path.abspath(ui_path)
        
        from PyQt5 import uic
        uic.loadUi(ui_path, self)
        
        self._modificar_ui()
        self._cargar_logos()
        self.todos_los_proyectos = []
        self.favoritos_ids = favoritos_sharing if favoritos_sharing is not None else set()
        self.cargar_proyectos()
        # Conectar buscador
        if hasattr(self, 'searchBar_sidebar'):
            self.searchBar_sidebar.textChanged.connect(self.filtrar_proyectos)
        
        # Configurar menú de perfil
        self._setup_profile_menu()
    
    def _setup_profile_menu(self):
        """Configura el menú desplegable del botón de perfil"""
        if hasattr(self, 'btn_profile'):
            # Crear menú
            profile_menu = QtWidgets.QMenu(self)
            profile_menu.setStyleSheet("""
                QMenu {
                    background-color: #2d2d44;
                    border: 1px solid #7C3AED;
                    border-radius: 5px;
                    padding: 5px;
                }
                QMenu::item {
                    padding: 8px 20px;
                    color: #E5E5E5;
                }
                QMenu::item:selected {
                    background-color: #3d3d54;
                    color: #A78BFA;
                }
            """)
            
            # Acción: Ayuda
            action_ayuda = QtWidgets.QAction("❓ Ayuda", self)
            action_ayuda.triggered.connect(self.mostrar_ayuda)
            profile_menu.addAction(action_ayuda)
            
            # Separador
            profile_menu.addSeparator()
            
            # Acción: Cerrar sesión
            action_logout = QtWidgets.QAction("🚪 Cerrar sesión", self)
            action_logout.triggered.connect(self.cerrar_sesion)
            profile_menu.addAction(action_logout)
            
            # Conectar menú al botón
            self.btn_profile.setMenu(profile_menu)
    
    def cerrar_sesion(self):
        """Cierra la sesión del usuario"""
        reply = QtWidgets.QMessageBox.question(
            self,
            'Cerrar sesión',
            '¿Estás seguro de que quieres cerrar sesión?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.logout_requested.emit()
    
    def mostrar_ayuda(self):
        """Muestra el diálogo de ayuda"""
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle('Ayuda - Community')
        msg_box.setTextFormat(QtCore.Qt.RichText)
        msg_box.setText('<h3>Community - Gestor de Proyectos</h3>'
            '<p><b>Versión:</b> 1.0</p>'
            '<p><b>Descripción:</b> Aplicación para gestionar proyectos y tareas con tableros Kanban.</p>'
            '<br>'
            '<p><b>Funcionalidades principales:</b></p>'
            '<ul>'
            '<li>📋 Gestión de proyectos</li>'
            '<li>⭐ Proyectos favoritos</li>'
            '<li>📊 Tableros Kanban</li>'
            '<li>🎨 Tarjetas con colores y prioridades</li>'
            '<li>🗑️ Eliminación de proyectos y tarjetas</li>'
            '</ul>'
            '<br>'
            '<p>Para más información, contacta con el equipo de desarrollo.</p>')
        
        # Botones
        btn_manual = msg_box.addButton("📄 Ver Manual PDF", QtWidgets.QMessageBox.ActionRole)
        msg_box.addButton("Cerrar", QtWidgets.QMessageBox.RejectRole)
        
        msg_box.exec_()
        
        if msg_box.clickedButton() == btn_manual:
            self.abrir_manual_pdf()
            
    def abrir_manual_pdf(self):
        """Abre el archivo PDF del manual de usuario"""
        try:
            # Construir ruta relativa al archivo
            pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'documento', 'Manual_de_Formacion_Community_Profesional.pdf'))
            
            if os.path.exists(pdf_path):
                url = QtCore.QUrl.fromLocalFile(pdf_path)
                QtGui.QDesktopServices.openUrl(url)
            else:
                QtWidgets.QMessageBox.warning(self, "Error", f"No se encontró el manual en:\n{pdf_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo abrir el manual: {e}")
    
    def _cargar_logos(self):
        """Carga el logo de la imagen en las etiquetas correspondientes"""
        try:
            img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'imagenes', 'logoCommunity.png'))
            if os.path.exists(img_path):
                pix = QtGui.QPixmap(img_path)
                if not pix.isNull():
                    # Logo sidebar
                    if hasattr(self, 'label_logo_sidebar'):
                        pix_sidebar = pix.scaled(self.label_logo_sidebar.width(), 
                                               self.label_logo_sidebar.height(), 
                                               QtCore.Qt.KeepAspectRatio, 
                                               QtCore.Qt.SmoothTransformation)
                        self.label_logo_sidebar.setPixmap(pix_sidebar)
                        self.label_logo_sidebar.setText("") # Limpiar el corazón
        except Exception as e:
            print(f"Error cargando logos: {e}")

    def _modificar_ui(self):
        """Modifica la UI para mostrar proyectos"""
        # Buscar el scroll area
        scroll_area = self.findChild(QtWidgets.QScrollArea, 'scrollArea')
        if not scroll_area:
            return
        
        # Crear nuevo widget de contenido
        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet("background-color: #3d3d54;")
        
        self.main_content_layout = QtWidgets.QVBoxLayout(content_widget)
        self.main_content_layout.setContentsMargins(25, 25, 25, 25)
        self.main_content_layout.setSpacing(20)
        
        # Título Favoritos (inicialmente oculto)
        self.header_favoritos = QtWidgets.QLabel("⭐ FAVORITOS")
        self.header_favoritos.setStyleSheet("font-size: 14px; font-weight: bold; color: #E5E5E5; margin-top: 0px;")
        self.header_favoritos.setVisible(False)
        self.main_content_layout.addWidget(self.header_favoritos)

        # Layout para favoritos
        self.favoritos_layout = QtWidgets.QGridLayout()
        self.favoritos_layout.setSpacing(25)
        self.favoritos_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.main_content_layout.addLayout(self.favoritos_layout)

        # Header con título Mis Proyectos
        header_layout = QtWidgets.QHBoxLayout()
        
        # Título
        titulo = QtWidgets.QLabel("MIS PROYECTOS")
        titulo.setStyleSheet("font-size: 14px; font-weight: bold; color: #E5E5E5; margin-top: 20px;")
        header_layout.addWidget(titulo)
        
        header_layout.addStretch()
        
        # Conectar botón crear proyecto de la sidebar
        if hasattr(self, 'btn_crear'):
            try:
                self.btn_crear.clicked.disconnect()
            except:
                pass
            
            # Cargar icono rosa
            icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'imagenes', 'plus_pink.svg'))
            if os.path.exists(icon_path):
                self.btn_crear.setIcon(QtGui.QIcon(icon_path))
                self.btn_crear.setIconSize(QtCore.QSize(14, 14))
            
            self.btn_crear.setText("  NUEVO PROYECTO")
            self.btn_crear.clicked.connect(self.crear_proyecto)
        
        self.main_content_layout.addLayout(header_layout)
        
        # Layout para proyectos (Grid para aprovechar pantalla)
        self.proyectos_layout = QtWidgets.QGridLayout()
        self.proyectos_layout.setSpacing(25)
        self.proyectos_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.main_content_layout.addLayout(self.proyectos_layout)

        self.main_content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
    
    def cargar_proyectos(self):
        """Carga los proyectos del usuario"""
        # Limpiar layout
        while self.proyectos_layout.count():
            item = self.proyectos_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Obtener proyectos
        exito, proyectos, error = proyectos_manager.obtener_proyectos_usuario()
        
        if not exito or not proyectos:
            self.todos_los_proyectos = []
            # Mensaje de no hay proyectos
            mensaje = QtWidgets.QLabel("Aún no tienes proyectos")
            mensaje.setStyleSheet("color: #999; font-size: 13px;")
            mensaje.setAlignment(QtCore.Qt.AlignCenter)
            self.proyectos_layout.addWidget(mensaje)
            return
        
        self.todos_los_proyectos = proyectos
        self.mostrar_proyectos(proyectos)
    
    def mostrar_proyectos(self, proyectos):
        """Muestra una lista de proyectos en el layout"""
        # Limpiar layouts
        for layout in [self.proyectos_layout, self.favoritos_layout]:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        
        if not proyectos:
            # Mensaje de no hay proyectos
            # Si no hay proyectos favoritos tampoco
            if not self.favoritos_ids and not hasattr(self, 'msg_no_proyectos'):
                mensaje = QtWidgets.QLabel("No tienes proyectos aún.\nHaz clic en 'Crear Proyecto' para empezar.")
                mensaje.setStyleSheet("color: #B4B4C8; font-size: 16px;")
                mensaje.setAlignment(QtCore.Qt.AlignCenter)
                self.proyectos_layout.addWidget(mensaje, 0, 0)
            self.header_favoritos.setVisible(False)
            return

        # Agregar tarjetas de proyectos
        cols = 4 # Default columns
        
        favoritos = [p for p in proyectos if p['id'] in self.favoritos_ids]
        normales = [p for p in proyectos if p['id'] not in self.favoritos_ids]
        
        # Mostrar Favoritos
        self.header_favoritos.setVisible(len(favoritos) > 0)
        for i, proyecto in enumerate(favoritos):
            card = ProyectoCardHomeDark(proyecto, favorito=True)
            card.clicked.connect(self.abrir_proyecto)
            card.favorito_toggled.connect(self.on_favorito_toggled)
            card.proyecto_eliminado.connect(self.cargar_proyectos) # Conectar borrado
            self.favoritos_layout.addWidget(card, i // cols, i % cols)
        
        # Mostrar Normales
        for i, proyecto in enumerate(normales):
            card = ProyectoCardHomeDark(proyecto, favorito=False)
            card.clicked.connect(self.abrir_proyecto)
            card.favorito_toggled.connect(self.on_favorito_toggled)
            card.proyecto_eliminado.connect(self.cargar_proyectos) # Conectar borrado
            self.proyectos_layout.addWidget(card, i // cols, i % cols)

    def on_favorito_toggled(self, proyecto_id, es_favorito):
        if es_favorito:
            self.favoritos_ids.add(proyecto_id)
        else:
            self.favoritos_ids.discard(proyecto_id)
        self.mostrar_proyectos(self.todos_los_proyectos)

    def filtrar_proyectos(self, texto):
        """Filtra proyectos por nombre"""
        if not texto:
            self.mostrar_proyectos(self.todos_los_proyectos[:3])
            return
            
        proyectos_filtrados = [
            p for p in self.todos_los_proyectos 
            if texto.lower() in p['nombre'].lower()
        ]
        self.mostrar_proyectos(proyectos_filtrados)
    
    def crear_proyecto(self):
        """Muestra diálogo para crear proyecto"""
        from proyectos_view import CrearProyectoDialog
        dialog = CrearProyectoDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.cargar_proyectos()
    
    def abrir_proyecto(self, proyecto_id):
        """Emite señal para abrir proyecto"""
        self.proyecto_seleccionado.emit(proyecto_id)


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = HomeCommunityDarkWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
