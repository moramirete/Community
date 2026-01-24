"""
Vista de Tableros DARK para Community
Muestra lista de tableros de un proyecto en modo oscuro
"""
import os
import sys
from PyQt5 import QtWidgets, QtCore, QtGui

# Importar managers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from base_datos.tableros_manager import tableros_manager
from base_datos.proyectos_manager import proyectos_manager


class TableroCardDark(QtWidgets.QFrame):
    """Tarjeta de tablero dark"""
    clicked = QtCore.pyqtSignal(str)
    
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
                background-color: #1e1e2e;
                border: 2px solid #2d2d44;
                border-radius: 12px;
                padding: 15px;
            }
            QFrame:hover {
                border: 2px solid #9333EA;
                background-color: #252535;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        nombre_label = QtWidgets.QLabel(self.tablero_data['nombre'])
        nombre_label.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: bold; background: transparent;")
        nombre_label.setWordWrap(True)
        layout.addWidget(nombre_label)
        
        if self.tablero_data.get('descripcion'):
            desc_label = QtWidgets.QLabel(self.tablero_data['descripcion'])
            desc_label.setStyleSheet("color: #B4B4C8; font-size: 12px; background: transparent;")
            desc_label.setWordWrap(True)
            desc_label.setMaximumHeight(40)
            layout.addWidget(desc_label)
        
        layout.addStretch()
        
        icon_label = QtWidgets.QLabel("📋")
        icon_label.setStyleSheet("font-size: 24px; background: transparent;")
        layout.addWidget(icon_label)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self.tablero_id)


class TablerosViewDark(QtWidgets.QMainWindow):
    """Vista de tableros dark"""
    tablero_seleccionado = QtCore.pyqtSignal(str)
    volver_clicked = QtCore.pyqtSignal()
    
    def __init__(self, proyecto_id, parent=None):
        super().__init__(parent)
        self.proyecto_id = proyecto_id
        self.setWindowTitle("Community - Tableros")
        self.setMinimumSize(1024, 768)
        self._setup_ui()
        self.cargar_proyecto()
        self.cargar_tableros()
    
    def _setup_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        header = self._crear_header()
        main_layout.addWidget(header)
        
        content_area = QtWidgets.QScrollArea()
        content_area.setWidgetResizable(True)
        content_area.setStyleSheet("QScrollArea { border: none; background-color: #0f0f1e; }")
        
        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet("background-color: #0f0f1e;")  # Fondo oscuro
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        self.titulo_proyecto = QtWidgets.QLabel("Cargando...")
        self.titulo_proyecto.setStyleSheet("font-size: 28px; font-weight: bold; color: #FFFFFF;")
        content_layout.addWidget(self.titulo_proyecto)
        
        subtitulo = QtWidgets.QLabel("Tableros")
        subtitulo.setStyleSheet("font-size: 18px; color: #B4B4C8;")
        content_layout.addWidget(subtitulo)
        
        self.tableros_layout = QtWidgets.QGridLayout()
        self.tableros_layout.setSpacing(20)
        content_layout.addLayout(self.tableros_layout)
        
        content_layout.addStretch()
        
        content_area.setWidget(content_widget)
        main_layout.addWidget(content_area)
    
    def _crear_header(self):
        header = QtWidgets.QFrame()
        header.setMinimumHeight(60)
        header.setStyleSheet("background-color: #7C3AED; border: none;")
        
        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(30, 10, 30, 10)
        
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
        
        self.btn_crear = QtWidgets.QPushButton("➕ Crear Tablero")
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
        self.btn_crear.clicked.connect(self.crear_tablero)
        layout.addWidget(self.btn_crear)
        
        return header
    
    def cargar_proyecto(self):
        exito, proyecto, error = proyectos_manager.obtener_proyecto(self.proyecto_id)
        if exito and proyecto:
            self.titulo_proyecto.setText(proyecto['nombre'])
    
    def cargar_tableros(self):
        while self.tableros_layout.count():
            item = self.tableros_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        exito, tableros, error = tableros_manager.obtener_tableros(self.proyecto_id)
        
        if not exito:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error al cargar tableros: {error}")
            return
        
        if not tableros:
            mensaje = QtWidgets.QLabel("No hay tableros aún.\\nHaz clic en 'Crear Tablero' para empezar.")
            mensaje.setStyleSheet("color: #B4B4C8; font-size: 16px;")
            mensaje.setAlignment(QtCore.Qt.AlignCenter)
            self.tableros_layout.addWidget(mensaje, 0, 0)
            return
        
        row = 0
        col = 0
        max_cols = 3
        
        for tablero in tableros:
            card = TableroCardDark(tablero)
            card.clicked.connect(self.abrir_tablero)
            self.tableros_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def crear_tablero(self):
        from tableros_view import CrearTableroDialog
        dialog = CrearTableroDialog(self.proyecto_id, self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.cargar_tableros()
    
    def abrir_tablero(self, tablero_id):
        self.tablero_seleccionado.emit(tablero_id)


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = TablerosViewDark("test-proyecto-id")
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
