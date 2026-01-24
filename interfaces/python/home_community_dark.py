"""
Vista Home Dark modificada para mostrar proyectos del usuario
"""
import os
import sys
from PyQt5 import QtWidgets, QtCore, QtGui

# Importar managers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from base_datos.proyectos_manager import proyectos_manager


class ProyectoCardHomeDark(QtWidgets.QFrame):
    """Tarjeta de proyecto para el home dark"""
    clicked = QtCore.pyqtSignal(str)  # Emite el ID del proyecto
    
    def __init__(self, proyecto_data, parent=None):
        super().__init__(parent)
        self.proyecto_id = proyecto_data['id']
        self.proyecto_data = proyecto_data
        self._setup_ui()
    
    def _setup_ui(self):
        self.setMinimumSize(180, 120)
        self.setMaximumSize(200, 130)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        # Color del proyecto
        color = self.proyecto_data.get('color', '#9333EA')
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
        nombre_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #E5E5E5; background: transparent;")
        nombre_label.setWordWrap(True)
        nombre_label.setMaximumHeight(30)
        bottom_layout.addWidget(nombre_label)
        
        # Rol
        rol = self.proyecto_data.get('miembros_proyecto', [{}])[0].get('rol', 'miembro')
        rol_label = QtWidgets.QLabel(f"{rol.upper()}")
        rol_label.setStyleSheet("font-size: 9px; color: #999; background: transparent;")
        bottom_layout.addWidget(rol_label)
        
        layout.addWidget(bottom_part)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self.proyecto_id)


class HomeCommunityDarkWindow(QtWidgets.QMainWindow):
    """Vista Home Dark que muestra proyectos del usuario"""
    proyecto_seleccionado = QtCore.pyqtSignal(str)  # Emite ID del proyecto
    
    def __init__(self, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), '..', '.ui', 'home_community_dark.ui')
        ui_path = os.path.abspath(ui_path)
        
        from PyQt5 import uic
        uic.loadUi(ui_path, self)
        
        self._modificar_ui()
        self.cargar_proyectos()
    
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
        
        # Header con título y botón
        header_layout = QtWidgets.QHBoxLayout()
        
        # Título
        titulo = QtWidgets.QLabel("⭐  MIS PROYECTOS")
        titulo.setStyleSheet("font-size: 14px; font-weight: bold; color: #E5E5E5;")
        header_layout.addWidget(titulo)
        
        header_layout.addStretch()
        
        # Botón crear proyecto
        btn_crear = QtWidgets.QPushButton("➕ Nuevo Proyecto")
        btn_crear.setStyleSheet("""
            QPushButton {
                background-color: #9333EA;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #7C3AED;
            }
        """)
        btn_crear.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn_crear.clicked.connect(self.crear_proyecto)
        header_layout.addWidget(btn_crear)
        
        self.main_content_layout.addLayout(header_layout)
        
        # Layout para proyectos
        self.proyectos_layout = QtWidgets.QHBoxLayout()
        self.proyectos_layout.setSpacing(20)
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
            # Mensaje de no hay proyectos
            mensaje = QtWidgets.QLabel("Aún no tienes proyectos")
            mensaje.setStyleSheet("color: #999; font-size: 13px;")
            mensaje.setAlignment(QtCore.Qt.AlignCenter)
            self.proyectos_layout.addWidget(mensaje)
            self.proyectos_layout.addStretch()
            return
        
        # Agregar tarjetas de proyectos (máximo 3)
        for i, proyecto in enumerate(proyectos[:3]):
            card = ProyectoCardHomeDark(proyecto)
            card.clicked.connect(self.abrir_proyecto)
            self.proyectos_layout.addWidget(card)
        
        self.proyectos_layout.addStretch()
    
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
