import sys
import os
from PyQt5 import QtWidgets, QtCore, QtGui

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from resource_helper import resource_path
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from resource_helper import resource_path

from src.base_datos.proyectos_manager import proyectos_manager
from src.base_datos.datos import db_manager


class ProyectoCardHome(QtWidgets.QFrame):
    clicked = QtCore.pyqtSignal(str)  
    favorito_toggled = QtCore.pyqtSignal(str, bool)  
    proyecto_eliminado = QtCore.pyqtSignal() 
    
    def __init__(self, proyecto_data, favorito=False, parent=None):
        super().__init__(parent)
        self.proyecto_id = proyecto_data['id']
        self.proyecto_data = proyecto_data
        self.es_favorito = favorito

        self.es_propietario = False
        if db_manager.current_session and db_manager.current_session.user:
            self.es_propietario = (proyecto_data.get('creador_id') == db_manager.current_session.user.id)
        
        self._configurar_interfaz()
    
    def _configurar_interfaz(self):
        self.setMinimumSize(220, 160)
        self.setMaximumSize(240, 180)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        color = self.proyecto_data.get('color', '#9333EA')
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #E0E0E0;
                border-radius: 8px;
            }}
            QFrame:hover {{
                background-color: #D0D0D0;
            }}
        """)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        top_part = QtWidgets.QLabel()
        top_part.setMinimumHeight(50)
        top_part.setStyleSheet(f"background-color: {color}; border-top-left-radius: 8px; border-top-right-radius: 8px;")
        layout.addWidget(top_part)
        
        bottom_part = QtWidgets.QFrame()
        bottom_part.setStyleSheet("background-color: #E5E5E5; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;")
        bottom_layout = QtWidgets.QVBoxLayout(bottom_part)
        bottom_layout.setContentsMargins(8, 5, 8, 5)
        
        nombre_label = QtWidgets.QLabel(self.proyecto_data['nombre'])
        nombre_label.setStyleSheet("font-weight: bold; font-size: 15px; color: #333; background: transparent;")
        nombre_label.setWordWrap(True)
        nombre_label.setMaximumHeight(50)
        bottom_layout.addWidget(nombre_label)
        
        rol = self.proyecto_data.get('miembros_proyecto', [{}])[0].get('rol', 'miembro')
        rol_label = QtWidgets.QLabel(f"{rol.upper()}")
        rol_label.setStyleSheet("font-size: 11px; color: #444; background: transparent; font-weight: 500;")
        bottom_layout.addWidget(rol_label)
        
        self.btn_favorito = QtWidgets.QPushButton(self)
        self.btn_favorito.setFixedSize(30, 30)
        self.btn_favorito.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.7);
                border-radius: 15px;
                font-size: 18px;
                border: none;
                color: #999;
            }
            QPushButton:hover {
                background: white;
            }
        """)
        self.btn_favorito.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_favorito.clicked.connect(self._alternar_favorito)
        self._actualizar_favorito()
        
        self.btn_eliminar = QtWidgets.QPushButton("🗑️", self)
        self.btn_eliminar.setFixedSize(30, 30)
        self.btn_eliminar.setStyleSheet("""
            QPushButton {
                background: rgba(0, 0, 0, 0.1);
                border-radius: 15px;
                font-size: 14px;
                border: none;
                color: #666;
            }
            QPushButton:hover {
                background: #EF4444;
                color: white;
            }
        """)
        self.btn_eliminar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_eliminar.clicked.connect(self.confirmar_borrado)
        
        self.btn_agregar_usuario = QtWidgets.QPushButton("➕", self)
        self.btn_agregar_usuario.setFixedSize(30, 30)
        self.btn_agregar_usuario.setVisible(self.es_propietario)  
        self.btn_agregar_usuario.setStyleSheet("""
            QPushButton {
                background: rgba(0, 0, 0, 0.1);
                border-radius: 15px;
                font-size: 14px;
                border: none;
                color: #666;
            }
            QPushButton:hover {
                background: #3B82F6;
                color: white;
            }
        """)
        self.btn_agregar_usuario.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_agregar_usuario.clicked.connect(self.abrir_invitacion)
        
        layout.addWidget(bottom_part)
    
    def _alternar_favorito(self):
        self.es_favorito = not self.es_favorito
        self._actualizar_favorito()
        self.favorito_toggled.emit(self.proyecto_id, self.es_favorito)
    
    def _actualizar_favorito(self):
        if self.es_favorito:
            self.btn_favorito.setText("★")
            self.btn_favorito.setStyleSheet(self.btn_favorito.styleSheet().replace("color: #999;", "color: #FFD700;"))
        else:
            self.btn_favorito.setText("☆")
            self.btn_favorito.setStyleSheet(self.btn_favorito.styleSheet().replace("color: #FFD700;", "color: #999;"))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'btn_favorito'):
            self.btn_favorito.move(self.width() - 35, 5)
            self.btn_favorito.raise_()
        if hasattr(self, 'btn_agregar_usuario'):
            self.btn_agregar_usuario.move(self.width() - 35, self.height() - 75)
            self.btn_agregar_usuario.raise_()
        if hasattr(self, 'btn_eliminar'):
            self.btn_eliminar.move(self.width() - 35, self.height() - 35)
            self.btn_eliminar.raise_()
    
    def confirmar_borrado(self):
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
    
    def abrir_invitacion(self):
        dialogo = InvitarUsuarioDialog(self.proyecto_id, self.proyecto_data['nombre'], self)
        if dialogo.exec_() == QtWidgets.QDialog.Accepted:
            pass
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            child = self.childAt(event.pos())
            if isinstance(child, QtWidgets.QPushButton):
                return
            self.clicked.emit(self.proyecto_id)


class InvitarUsuarioDialog(QtWidgets.QDialog):
    
    def __init__(self, proyecto_id, proyecto_nombre, parent=None):
        super().__init__(parent)
        self.proyecto_id = proyecto_id
        self.proyecto_nombre = proyecto_nombre
        self.setWindowTitle(f"Invitar Usuario - {proyecto_nombre}")
        self.setMinimumWidth(400)
        self._configurar_interfaz()
    
    def _configurar_interfaz(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        
        titulo = QtWidgets.QLabel(f"Añadir usuario al proyecto:")
        titulo.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        layout.addWidget(titulo)
        
        proyecto_label = QtWidgets.QLabel(f"\"{self.proyecto_nombre}\"")
        proyecto_label.setStyleSheet("font-size: 12px; color: #666; font-style: italic;")
        layout.addWidget(proyecto_label)
        
        email_label = QtWidgets.QLabel("Email del usuario:")
        email_label.setStyleSheet("font-size: 12px; color: #333;")
        layout.addWidget(email_label)
        
        self.input_email = QtWidgets.QLineEdit()
        self.input_email.setPlaceholderText("usuario@ejemplo.com")
        self.input_email.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #DDD;
                border-radius: 5px;
                font-size: 13px;
                font-weight: 500;
            }
            QLineEdit:focus {
                border: 1px solid #9333EA;
            }
        """)
        layout.addWidget(self.input_email)
        
        layout.addStretch()
        
        botones_layout = QtWidgets.QHBoxLayout()
        botones_layout.addStretch()
        
        btn_cancelar = QtWidgets.QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                border: 1px solid #DDD;
                border-radius: 5px;
                background: white;
            }
            QPushButton:hover {
                background: #F5F5F5;
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
                background: #9333EA;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7C3AED;
            }
        """)
        botones_layout.addWidget(btn_invitar)
        
        layout.addLayout(botones_layout)
    
    def invitar_usuario(self):
        email = self.input_email.text().strip()
        
        if not email:
            QtWidgets.QMessageBox.warning(self, "Error", "Por favor ingresa un email")
            return
        
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


class HomeCommunityWindow(QtWidgets.QMainWindow):
    proyecto_seleccionado = QtCore.pyqtSignal(str)  
    logout_requested = QtCore.pyqtSignal()  
    
    def __init__(self, parent=None, favoritos_sharing=None):
        super().__init__(parent)
        ui_path = resource_path('interfaces/.ui/home_community.ui')
        
        from PyQt5 import uic
        uic.loadUi(ui_path, self)
        
        self._ajustar_interfaz()
        self._cargar_imagenes()
        self.todos_los_proyectos = []
        self.favoritos_ids = favoritos_sharing if favoritos_sharing is not None else set()
        self.obtener_proyectos()
        if hasattr(self, 'searchBar_sidebar'):
            self.searchBar_sidebar.textChanged.connect(self.buscar_proyectos)
        
        self._configurar_menu_perfil()
    
    def _configurar_menu_perfil(self):
        if hasattr(self, 'btn_profile'):
            profile_menu = QtWidgets.QMenu(self)
            profile_menu.setStyleSheet("""
                QMenu {
                    background-color: white;
                    border: 1px solid #9333EA;
                    border-radius: 5px;
                    padding: 5px;
                }
                QMenu::item {
                    padding: 8px 20px;
                    color: #333;
                }
                QMenu::item:selected {
                    background-color: #F3E8FF;
                    color: #9333EA;
                }
            """)
            
            action_ayuda = QtWidgets.QAction("❓ Ayuda", self)
            action_ayuda.triggered.connect(self.mostrar_ayuda)
            profile_menu.addAction(action_ayuda)
            
            profile_menu.addSeparator()
            
            action_logout = QtWidgets.QAction("🚪 Cerrar sesión", self)
            action_logout.triggered.connect(self.cerrar_sesion)
            profile_menu.addAction(action_logout)
            
            self.btn_profile.setMenu(profile_menu)
    
    def cerrar_sesion(self):
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
        
        btn_manual = msg_box.addButton("📄 Ver Manual PDF", QtWidgets.QMessageBox.ActionRole)
        msg_box.addButton("Cerrar", QtWidgets.QMessageBox.RejectRole)
        
        msg_box.exec_()
        
        if msg_box.clickedButton() == btn_manual:
            self.abrir_manual_pdf()
            
    def abrir_manual_pdf(self):
        try:
            pdf_path = resource_path('interfaces/documento/Manual_de_Formacion_Community_Profesional.pdf')
            
            if os.path.exists(pdf_path):
                url = QtCore.QUrl.fromLocalFile(pdf_path)
                QtGui.QDesktopServices.openUrl(url)
            else:
                QtWidgets.QMessageBox.warning(self, "Error", f"No se encontró el manual en:\n{pdf_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo abrir el manual: {e}")
    
    def _cargar_imagenes(self):
        try:
            img_path = resource_path('interfaces/imagenes/logoCommunity.png')
            if os.path.exists(img_path):
                pix = QtGui.QPixmap(img_path)
                if not pix.isNull():
                    if hasattr(self, 'label_logo_sidebar'):
                        pix_sidebar = pix.scaled(self.label_logo_sidebar.width(), 
                                               self.label_logo_sidebar.height(), 
                                               QtCore.Qt.KeepAspectRatio, 
                                               QtCore.Qt.SmoothTransformation)
                        self.label_logo_sidebar.setPixmap(pix_sidebar)
                        self.label_logo_sidebar.setText("") 
        except Exception as e:
            print(f"Error cargando logos: {e}")

    def _ajustar_interfaz(self):
        scroll_area = self.findChild(QtWidgets.QScrollArea, 'scrollArea')
        if not scroll_area:
            return
        
        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet("background-color: #f5f5f5;")
        
        self.main_content_layout = QtWidgets.QVBoxLayout(content_widget)
        self.main_content_layout.setContentsMargins(20, 20, 20, 20)
        self.main_content_layout.setSpacing(20)
        
        self.header_favoritos = QtWidgets.QLabel("⭐ FAVORITOS")
        self.header_favoritos.setStyleSheet("font-size: 13px; font-weight: bold; color: #333; margin-top: 0px;")
        self.header_favoritos.setVisible(False)
        self.main_content_layout.addWidget(self.header_favoritos)

        self.favoritos_layout = QtWidgets.QGridLayout()
        self.favoritos_layout.setSpacing(25)
        self.favoritos_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.main_content_layout.addLayout(self.favoritos_layout)

        header_layout = QtWidgets.QHBoxLayout()
        
        titulo = QtWidgets.QLabel("MIS PROYECTOS")
        titulo.setStyleSheet("font-size: 13px; font-weight: bold; color: #333; margin-top: 20px;")
        header_layout.addWidget(titulo)
        
        header_layout.addStretch()
        
        if hasattr(self, 'btn_crear'):
            try:
                self.btn_crear.clicked.disconnect()
            except:
                pass
            
            icon_path = resource_path('interfaces/imagenes/plus_pink.svg')
            if os.path.exists(icon_path):
                self.btn_crear.setIcon(QtGui.QIcon(icon_path))
                self.btn_crear.setIconSize(QtCore.QSize(14, 14))
            
            self.btn_crear.setText("  NUEVO PROYECTO")
            self.btn_crear.clicked.connect(self.crear_proyecto)
        
        self.main_content_layout.addLayout(header_layout)
        
        self.proyectos_layout = QtWidgets.QGridLayout()
        self.proyectos_layout.setSpacing(25)
        self.proyectos_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.main_content_layout.addLayout(self.proyectos_layout)

        self.main_content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)

    
    def obtener_proyectos(self):
        while self.proyectos_layout.count():
            item = self.proyectos_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        exito, proyectos, error = proyectos_manager.obtener_proyectos_usuario()
        
        if not exito or not proyectos:
            self.todos_los_proyectos = []
            mensaje = QtWidgets.QLabel("Aún no tienes proyectos")
            mensaje.setStyleSheet("color: #999; font-size: 12px;")
            mensaje.setAlignment(QtCore.Qt.AlignCenter)
            self.proyectos_layout.addWidget(mensaje)
            return
        
        self.todos_los_proyectos = proyectos
        self.ver_proyectos(proyectos)
    
    def ver_proyectos(self, proyectos):
        for layout in [self.proyectos_layout, self.favoritos_layout]:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        
        if not proyectos:
            if not self.favoritos_ids and not hasattr(self, 'msg_no_proyectos'):
                mensaje = QtWidgets.QLabel("No tienes proyectos aún.\nHaz clic en 'Crear Proyecto' para empezar.")
                mensaje.setStyleSheet("color: #666; font-size: 16px;")
                mensaje.setAlignment(QtCore.Qt.AlignCenter)
                self.proyectos_layout.addWidget(mensaje, 0, 0)
            self.header_favoritos.setVisible(False) 
            return

        cols = 4 
        
        favoritos = [p for p in proyectos if p['id'] in self.favoritos_ids]
        normales = [p for p in proyectos if p['id'] not in self.favoritos_ids]
        
        self.header_favoritos.setVisible(len(favoritos) > 0)
        for i, proyecto in enumerate(favoritos):
            card = ProyectoCardHome(proyecto, favorito=True)
            card.clicked.connect(self.abrir_proyecto)
            card.favorito_toggled.connect(self.al_cambiar_favorito)
            card.proyecto_eliminado.connect(self.obtener_proyectos) 
            self.favoritos_layout.addWidget(card, i // cols, i % cols)
        
        for i, proyecto in enumerate(normales):
            card = ProyectoCardHome(proyecto, favorito=False)
            card.clicked.connect(self.abrir_proyecto)
            card.favorito_toggled.connect(self.al_cambiar_favorito)
            card.proyecto_eliminado.connect(self.obtener_proyectos) 
            self.proyectos_layout.addWidget(card, i // cols, i % cols)

    def al_cambiar_favorito(self, proyecto_id, es_favorito):
        if es_favorito:
            self.favoritos_ids.add(proyecto_id)
        else:
            self.favoritos_ids.discard(proyecto_id)
        self.ver_proyectos(self.todos_los_proyectos)

    def buscar_proyectos(self, texto):
        if not texto:
            self.ver_proyectos(self.todos_los_proyectos)
            return
            
        proyectos_filtrados = [
            p for p in self.todos_los_proyectos 
            if texto.lower() in p['nombre'].lower()
        ]
        self.ver_proyectos(proyectos_filtrados)
    
    def crear_proyecto(self):
        from proyectos_view import CrearProyectoDialog
        dialog = CrearProyectoDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.obtener_proyectos()
    
    def abrir_proyecto(self, proyecto_id):
        self.proyecto_seleccionado.emit(proyecto_id)


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = HomeCommunityWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
