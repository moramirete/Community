"""
Vista de Proyectos DARK para Community
Muestra lista de proyectos del usuario en modo oscuro
"""
import os
import sys
from PyQt5 import QtWidgets, QtCore, QtGui

# Importar managers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from base_datos.proyectos_manager import proyectos_manager


class ProyectoCardDark(QtWidgets.QFrame):
    """Tarjeta de proyecto dark"""
    clicked = QtCore.pyqtSignal(str)
    
    def __init__(self, proyecto_data, parent=None):
        super().__init__(parent)
        self.proyecto_id = proyecto_data['id']
        self.proyecto_data = proyecto_data
        self._setup_ui()
    
    def _setup_ui(self):
        self.setMinimumSize(250, 150)
        self.setMaximumSize(300, 180)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        color = self.proyecto_data.get('color', '#9333EA')
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 12px;
                padding: 15px;
            }}
            QFrame:hover {{
                background-color: {self._lighten_color(color)};
            }}
        """)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        nombre_label = QtWidgets.QLabel(self.proyecto_data['nombre'])
        nombre_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; background: transparent;")
        nombre_label.setWordWrap(True)
        layout.addWidget(nombre_label)
        
        if self.proyecto_data.get('descripcion'):
            desc_label = QtWidgets.QLabel(self.proyecto_data['descripcion'])
            desc_label.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 12px; background: transparent;")
            desc_label.setWordWrap(True)
            desc_label.setMaximumHeight(60)
            layout.addWidget(desc_label)
        
        layout.addStretch()
        
        rol = self.proyecto_data.get('miembros_proyecto', [{}])[0].get('rol', 'miembro')
        rol_label = QtWidgets.QLabel(f"📌 {rol.upper()}")
        rol_label.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 10px; background: transparent;")
        layout.addWidget(rol_label)
    
    def _lighten_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, r + 20)
        g = min(255, g + 20)
        b = min(255, b + 20)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self.proyecto_id)


class ProyectosViewDark(QtWidgets.QMainWindow):
    """Vista de proyectos dark"""
    proyecto_seleccionado = QtCore.pyqtSignal(str)
    volver_clicked = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Community - Proyectos")
        self.setMinimumSize(1024, 768)
        self._setup_ui()
        self.cargar_proyectos()
    
    def _setup_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self._crear_header()
        main_layout.addWidget(header)
        
        # Área de contenido
        content_area = QtWidgets.QScrollArea()
        content_area.setWidgetResizable(True)
        content_area.setStyleSheet("QScrollArea { border: none; background-color: #0f0f1e; }")
        
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # Título y Buscador
        header_content_layout = QtWidgets.QHBoxLayout()
        titulo = QtWidgets.QLabel("Mis Proyectos")
        titulo.setStyleSheet("font-size: 28px; font-weight: bold; color: #FFFFFF;")
        header_content_layout.addWidget(titulo)
        
        header_content_layout.addStretch()
        
        # Buscador
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Buscar por nombre de proyecto...")
        self.search_bar.setFixedWidth(350)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                border-radius: 15px;
                border: 2px solid #3d3d54;
                padding: 8px 15px;
                font-size: 14px;
                background-color: #1a1a2e;
                color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #7C3AED;
            }
        """)
        self.search_bar.textChanged.connect(self.filtrar_proyectos)
        header_content_layout.addWidget(self.search_bar)
        
        content_layout.addLayout(header_content_layout)
        
        self.proyectos_layout = QtWidgets.QGridLayout()
        self.proyectos_layout.setSpacing(20)
        content_layout.addLayout(self.proyectos_layout)
        
        self.todos_los_proyectos = []
        
        content_layout.addStretch()
        
        content_area.setWidget(content_widget)
        main_layout.addWidget(content_area)
    
    def _crear_header(self):
        header = QtWidgets.QFrame()
        header.setMinimumHeight(60)
        header.setStyleSheet("background-color: #7C3AED; border: none;")
        
        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(30, 10, 30, 10)
        
        logo_label = QtWidgets.QLabel("❤️ COMMUNITY")
        logo_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; background: transparent;")
        layout.addWidget(logo_label)
        
        layout.addStretch()
        
        self.btn_crear = QtWidgets.QPushButton("➕ Crear Proyecto")
        self.btn_crear.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #7C3AED;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        self.btn_crear.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_crear.clicked.connect(self.crear_proyecto)
        layout.addWidget(self.btn_crear)
        
        return header
    
    def cargar_proyectos(self):
        """Carga los proyectos del usuario"""
        exito, proyectos, error = proyectos_manager.obtener_proyectos_usuario()
        
        if not exito:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error al cargar proyectos: {error}")
            return
            
        self.todos_los_proyectos = proyectos
        self.mostrar_proyectos(proyectos)
    
    def mostrar_proyectos(self, proyectos):
        """Muestra una lista de proyectos en el grid"""
        # Limpiar layout
        while self.proyectos_layout.count():
            item = self.proyectos_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not proyectos:
            mensaje = QtWidgets.QLabel("No se encontraron proyectos")
            mensaje.setStyleSheet("color: #B4B4C8; font-size: 16px;")
            mensaje.setAlignment(QtCore.Qt.AlignCenter)
            self.proyectos_layout.addWidget(mensaje, 0, 0)
            return
 
        # Agregar tarjetas de proyectos
        row = 0
        col = 0
        max_cols = 3
        
        for proyecto in proyectos:
            card = ProyectoCardDark(proyecto)
            card.clicked.connect(self.abrir_proyecto)
            self.proyectos_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def filtrar_proyectos(self, texto):
        """Filtra proyectos por nombre"""
        proyectos_filtrados = [
            p for p in self.todos_los_proyectos 
            if texto.lower() in p['nombre'].lower()
        ]
        self.mostrar_proyectos(proyectos_filtrados)
    
    def crear_proyecto(self):
        from proyectos_view import CrearProyectoDialog
        dialog = CrearProyectoDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.cargar_proyectos()
    
    def abrir_proyecto(self, proyecto_id):
        self.proyecto_seleccionado.emit(proyecto_id)


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = ProyectosViewDark()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
