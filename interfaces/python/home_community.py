"""
Vista Home modificada para mostrar proyectos del usuario
"""
import os
import sys
from PyQt5 import QtWidgets, QtCore, QtGui

# Importar managers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from base_datos.proyectos_manager import proyectos_manager


class ProyectoCardHome(QtWidgets.QFrame):
    """Tarjeta de proyecto para el home"""
    clicked = QtCore.pyqtSignal(str)  # Emite el ID del proyecto
    favorito_toggled = QtCore.pyqtSignal(str, bool)  # Emite (ID, es_favorito)
    
    def __init__(self, proyecto_data, favorito=False, parent=None):
        super().__init__(parent)
        self.proyecto_id = proyecto_data['id']
        self.proyecto_data = proyecto_data
        self.es_favorito = favorito
        self._setup_ui()
    
    def _setup_ui(self):
        self.setMinimumSize(220, 160)
        self.setMaximumSize(240, 180)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        # Color del proyecto
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
        
        # Parte superior con color
        top_part = QtWidgets.QLabel()
        top_part.setMinimumHeight(50)
        top_part.setStyleSheet(f"background-color: {color}; border-top-left-radius: 8px; border-top-right-radius: 8px;")
        layout.addWidget(top_part)
        
        # Parte inferior con info
        bottom_part = QtWidgets.QFrame()
        bottom_part.setStyleSheet("background-color: #E5E5E5; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;")
        bottom_layout = QtWidgets.QVBoxLayout(bottom_part)
        bottom_layout.setContentsMargins(8, 5, 8, 5)
        
        # Nombre del proyecto
        nombre_label = QtWidgets.QLabel(self.proyecto_data['nombre'])
        nombre_label.setStyleSheet("font-weight: bold; font-size: 15px; color: #333; background: transparent;")
        nombre_label.setWordWrap(True)
        nombre_label.setMaximumHeight(50)
        bottom_layout.addWidget(nombre_label)
        
        # Rol
        rol = self.proyecto_data.get('miembros_proyecto', [{}])[0].get('rol', 'miembro')
        rol_label = QtWidgets.QLabel(f"{rol.upper()}")
        rol_label.setStyleSheet("font-size: 11px; color: #444; background: transparent; font-weight: 500;")
        bottom_layout.addWidget(rol_label)
        
        # Botón de favorito (estrella)
        self.btn_favorito = QtWidgets.QPushButton(self)
        self.btn_favorito.setFixedSize(30, 30)
        self.btn_favorito.move(self.width() - 35, 5)
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
        self.btn_favorito.clicked.connect(self._toggle_favorito)
        self._actualizar_estrella()
        
        layout.addWidget(bottom_part)
    
    def _toggle_favorito(self):
        self.es_favorito = not self.es_favorito
        self._actualizar_estrella()
        self.favorito_toggled.emit(self.proyecto_id, self.es_favorito)
    
    def _actualizar_estrella(self):
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
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self.proyecto_id)


class HomeCommunityWindow(QtWidgets.QMainWindow):
    """Vista Home que muestra proyectos del usuario"""
    proyecto_seleccionado = QtCore.pyqtSignal(str)  # Emite ID del proyecto
    
    def __init__(self, parent=None, favoritos_sharing=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), '..', '.ui', 'home_community.ui')
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
        content_widget.setStyleSheet("background-color: #f5f5f5;")
        
        self.main_content_layout = QtWidgets.QVBoxLayout(content_widget)
        self.main_content_layout.setContentsMargins(20, 20, 20, 20)
        self.main_content_layout.setSpacing(20)
        
        # Header con título
        header_layout = QtWidgets.QHBoxLayout()
        
        # Título
        titulo = QtWidgets.QLabel("⭐  MIS PROYECTOS")
        titulo.setStyleSheet("font-size: 13px; font-weight: bold; color: #333;")
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
        
        # Título Favoritos (inicialmente oculto)
        self.header_favoritos = QtWidgets.QLabel("❤️ FAVORITOS")
        self.header_favoritos.setStyleSheet("font-size: 13px; font-weight: bold; color: #333; margin-top: 20px;")
        self.header_favoritos.setVisible(False)
        self.main_content_layout.addWidget(self.header_favoritos)

        # Layout para favoritos
        self.favoritos_layout = QtWidgets.QGridLayout()
        self.favoritos_layout.setSpacing(25)
        self.favoritos_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.main_content_layout.addLayout(self.favoritos_layout)

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
            mensaje.setStyleSheet("color: #999; font-size: 12px;")
            mensaje.setAlignment(QtCore.Qt.AlignCenter)
            self.proyectos_layout.addWidget(mensaje)
            self.proyectos_layout.addStretch()
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
            mensaje = QtWidgets.QLabel("No se encontraron proyectos")
            mensaje.setStyleSheet("color: #999; font-size: 12px;")
            mensaje.setAlignment(QtCore.Qt.AlignCenter)
            self.proyectos_layout.addWidget(mensaje, 0, 0)
            self.header_favoritos.setVisible(False)
        else:
            favoritos = [p for p in proyectos if p['id'] in self.favoritos_ids]
            normales = [p for p in proyectos if p['id'] not in self.favoritos_ids]
            
            # Mostrar Favoritos
            self.header_favoritos.setVisible(len(favoritos) > 0)
            cols = 4
            for i, proyecto in enumerate(favoritos):
                card = ProyectoCardHome(proyecto, favorito=True)
                card.clicked.connect(self.abrir_proyecto)
                card.favorito_toggled.connect(self.on_favorito_toggled)
                self.favoritos_layout.addWidget(card, i // cols, i % cols)
            
            # Mostrar Normales
            for i, proyecto in enumerate(normales):
                card = ProyectoCardHome(proyecto, favorito=False)
                card.clicked.connect(self.abrir_proyecto)
                card.favorito_toggled.connect(self.on_favorito_toggled)
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
            self.mostrar_proyectos(self.todos_los_proyectos)
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
    w = HomeCommunityWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
