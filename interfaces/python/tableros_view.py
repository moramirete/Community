"""
Vista de Tableros para Community
Muestra lista de tableros de un proyecto
"""
import os
import sys
from PyQt5 import QtWidgets, QtCore, QtGui

# Importar managers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from base_datos.tableros_manager import tableros_manager
from base_datos.proyectos_manager import proyectos_manager


class TableroCard(QtWidgets.QFrame):
    """Tarjeta de tablero"""
    clicked = QtCore.pyqtSignal(str)  # Emite el ID del tablero
    
    def __init__(self, tablero_data, parent=None):
        super().__init__(parent)
        self.tablero_id = tablero_data['id']
        self.tablero_data = tablero_data
        self._setup_ui()
    
    def _setup_ui(self):
        self.setMinimumSize(250, 120)
        self.setMaximumSize(300, 150)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #E5E7EB;
                border-radius: 12px;
                padding: 15px;
            }
            QFrame:hover {
                border: 2px solid #9333EA;
                background-color: #F9FAFB;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Nombre del tablero
        nombre_label = QtWidgets.QLabel(self.tablero_data['nombre'])
        nombre_label.setStyleSheet("color: #333; font-size: 16px; font-weight: bold; background: transparent;")
        nombre_label.setWordWrap(True)
        layout.addWidget(nombre_label)
        
        # Descripción
        if self.tablero_data.get('descripcion'):
            desc_label = QtWidgets.QLabel(self.tablero_data['descripcion'])
            desc_label.setStyleSheet("color: #666; font-size: 12px; background: transparent;")
            desc_label.setWordWrap(True)
            desc_label.setMaximumHeight(40)
            layout.addWidget(desc_label)
        
        layout.addStretch()
        
        # Icono
        icon_label = QtWidgets.QLabel("📋")
        icon_label.setStyleSheet("font-size: 24px; background: transparent;")
        layout.addWidget(icon_label)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self.tablero_id)


class TablerosView(QtWidgets.QMainWindow):
    """Vista de tableros de un proyecto"""
    tablero_seleccionado = QtCore.pyqtSignal(str)  # Emite ID del tablero
    volver_clicked = QtCore.pyqtSignal()  # Señal para volver
    
    def __init__(self, proyecto_id, parent=None):
        super().__init__(parent)
        self.proyecto_id = proyecto_id
        self.setWindowTitle("Community - Tableros")
        self.setMinimumSize(1024, 768)
        self._setup_ui()
        self.cargar_proyecto()
        self.cargar_tableros()
    
    def _setup_ui(self):
        # Widget central
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self._crear_header()
        main_layout.addWidget(header)
        
        # Área de contenido
        content_area = QtWidgets.QScrollArea()
        content_area.setWidgetResizable(True)
        content_area.setStyleSheet("QScrollArea { border: none; background-color: #FFFFFF; }")
        
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # Título
        self.titulo_proyecto = QtWidgets.QLabel("Cargando...")
        self.titulo_proyecto.setStyleSheet("font-size: 28px; font-weight: bold; color: #333;")
        content_layout.addWidget(self.titulo_proyecto)
        
        # Subtítulo
        subtitulo = QtWidgets.QLabel("Tableros")
        subtitulo.setStyleSheet("font-size: 18px; color: #666;")
        content_layout.addWidget(subtitulo)
        
        # Grid de tableros
        self.tableros_layout = QtWidgets.QGridLayout()
        self.tableros_layout.setSpacing(20)
        content_layout.addLayout(self.tableros_layout)
        
        content_layout.addStretch()
        
        content_area.setWidget(content_widget)
        main_layout.addWidget(content_area)
    
    def _crear_header(self):
        """Crea el header"""
        header = QtWidgets.QFrame()
        header.setMinimumHeight(60)
        header.setStyleSheet("background-color: #9333EA; border: none;")
        
        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(30, 10, 30, 10)
        
        # Botón volver
        btn_volver = QtWidgets.QPushButton("← Volver a Proyectos")
        btn_volver.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: 2px solid white;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.1);
            }
        """)
        btn_volver.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn_volver.clicked.connect(lambda: self.volver_clicked.emit())
        layout.addWidget(btn_volver)
        
        layout.addStretch()
        
        # Botón crear tablero
        self.btn_crear = QtWidgets.QPushButton("➕ Crear Tablero")
        self.btn_crear.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #9333EA;
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
        self.btn_crear.clicked.connect(self.crear_tablero)
        layout.addWidget(self.btn_crear)
        
        return header
    
    def cargar_proyecto(self):
        """Carga información del proyecto"""
        exito, proyecto, error = proyectos_manager.obtener_proyecto(self.proyecto_id)
        if exito and proyecto:
            self.titulo_proyecto.setText(proyecto['nombre'])
    
    def cargar_tableros(self):
        """Carga los tableros del proyecto"""
        # Limpiar layout
        while self.tableros_layout.count():
            item = self.tableros_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Obtener tableros
        exito, tableros, error = tableros_manager.obtener_tableros(self.proyecto_id)
        
        if not exito:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error al cargar tableros: {error}")
            return
        
        if not tableros:
            # Mensaje de no hay tableros
            mensaje = QtWidgets.QLabel("No hay tableros aún.\nHaz clic en 'Crear Tablero' para empezar.")
            mensaje.setStyleSheet("color: #666; font-size: 16px;")
            mensaje.setAlignment(QtCore.Qt.AlignCenter)
            self.tableros_layout.addWidget(mensaje, 0, 0)
            return
        
        # Agregar tarjetas de tableros
        row = 0
        col = 0
        max_cols = 3
        
        for tablero in tableros:
            card = TableroCard(tablero)
            card.clicked.connect(self.abrir_tablero)
            self.tableros_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def crear_tablero(self):
        """Muestra diálogo para crear tablero"""
        dialog = CrearTableroDialog(self.proyecto_id, self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.cargar_tableros()
    
    def abrir_tablero(self, tablero_id):
        """Emite señal para abrir tablero"""
        self.tablero_seleccionado.emit(tablero_id)


class CrearTableroDialog(QtWidgets.QDialog):
    """Diálogo para crear tablero"""
    
    def __init__(self, proyecto_id, parent=None):
        super().__init__(parent)
        self.proyecto_id = proyecto_id
        self.setWindowTitle("Crear Tablero")
        self.setMinimumSize(400, 250)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Nombre
        layout.addWidget(QtWidgets.QLabel("Nombre del Tablero:"))
        self.input_nombre = QtWidgets.QLineEdit()
        self.input_nombre.setPlaceholderText("Ej: Sprint 1")
        self.input_nombre.setStyleSheet("padding: 8px; border: 2px solid #E5E7EB; border-radius: 8px;")
        layout.addWidget(self.input_nombre)
        
        # Descripción
        layout.addWidget(QtWidgets.QLabel("Descripción:"))
        self.input_descripcion = QtWidgets.QTextEdit()
        self.input_descripcion.setPlaceholderText("Descripción del tablero...")
        self.input_descripcion.setMaximumHeight(80)
        self.input_descripcion.setStyleSheet("padding: 8px; border: 2px solid #E5E7EB; border-radius: 8px;")
        layout.addWidget(self.input_descripcion)
        
        layout.addStretch()
        
        # Botones
        botones_layout = QtWidgets.QHBoxLayout()
        botones_layout.addStretch()
        
        btn_cancelar = QtWidgets.QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        botones_layout.addWidget(btn_cancelar)
        
        btn_crear = QtWidgets.QPushButton("Crear Tablero")
        btn_crear.setStyleSheet("""
            QPushButton {
                background-color: #9333EA;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7C3AED;
            }
        """)
        btn_crear.clicked.connect(self.crear)
        botones_layout.addWidget(btn_crear)
        
        layout.addLayout(botones_layout)
    
    def crear(self):
        """Crea el tablero"""
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QtWidgets.QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        
        descripcion = self.input_descripcion.toPlainText().strip()
        
        exito, tablero, error = tableros_manager.crear_tablero(self.proyecto_id, nombre, descripcion)
        
        if exito:
            QtWidgets.QMessageBox.information(self, "Éxito", "Tablero creado correctamente")
            self.accept()
        else:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error al crear tablero: {error}")


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = TablerosView("test-proyecto-id")
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
