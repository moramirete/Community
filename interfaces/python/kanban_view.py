"""
Vista Kanban para Community
Tablero con 3 columnas y drag & drop de tarjetas
"""
import os
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from datetime import datetime

# Importar managers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from base_datos.tableros_manager import tableros_manager
from base_datos.tarjetas_manager import tarjetas_manager


class TarjetaWidget(QtWidgets.QFrame):
    """Widget de tarjeta con drag & drop"""
    clicked = QtCore.pyqtSignal(str)  # Emite ID de tarjeta
    
    def __init__(self, tarjeta_data, parent=None):
        super().__init__(parent)
        self.tarjeta_id = tarjeta_data['id']
        self.tarjeta_data = tarjeta_data
        self.setAcceptDrops(False)  # Las tarjetas no aceptan drops
        self._setup_ui()
    
    def _setup_ui(self):
        self.setMinimumHeight(80)
        self.setMaximumHeight(150)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        color = self.tarjeta_data.get('color', '#FFFFFF')
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }}
            QFrame:hover {{
                border: 2px solid #9333EA;
            }}
        """)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(5)
        
        # Título
        titulo = QtWidgets.QLabel(self.tarjeta_data['titulo'])
        titulo.setStyleSheet("font-weight: bold; font-size: 13px; color: #333; background: transparent;")
        titulo.setWordWrap(True)
        layout.addWidget(titulo)
        
        # Descripción (si existe)
        if self.tarjeta_data.get('descripcion'):
            desc = QtWidgets.QLabel(self.tarjeta_data['descripcion'][:50] + "...")
            desc.setStyleSheet("font-size: 11px; color: #666; background: transparent;")
            desc.setWordWrap(True)
            layout.addWidget(desc)
        
        # Fecha (si existe)
        if self.tarjeta_data.get('fecha_vencimiento'):
            fecha = QtWidgets.QLabel(f"📅 {self.tarjeta_data['fecha_vencimiento']}")
            fecha.setStyleSheet("font-size: 10px; color: #888; background: transparent;")
            layout.addWidget(fecha)
        
        # Usuarios asignados
        if self.tarjeta_data.get('tarjetas_usuarios'):
            num_usuarios = len(self.tarjeta_data['tarjetas_usuarios'])
            usuarios_label = QtWidgets.QLabel(f"👥 {num_usuarios} asignado(s)")
            usuarios_label.setStyleSheet("font-size: 10px; color: #888; background: transparent;")
            layout.addWidget(usuarios_label)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            # Iniciar drag
            drag = QtGui.QDrag(self)
            mime_data = QtCore.QMimeData()
            mime_data.setText(self.tarjeta_id)
            drag.setMimeData(mime_data)
            
            # Crear pixmap para el drag
            pixmap = self.grab()
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())
            
            drag.exec_(QtCore.Qt.MoveAction)


class ColumnaWidget(QtWidgets.QFrame):
    """Widget de columna que acepta drops"""
    tarjeta_movida = QtCore.pyqtSignal(str, str)  # (tarjeta_id, columna_id)
    
    def __init__(self, columna_data, parent=None):
        super().__init__(parent)
        self.columna_id = columna_data['id']
        self.columna_data = columna_data
        self.setAcceptDrops(True)
        self._setup_ui()
    
    def _setup_ui(self):
        self.setMinimumWidth(300)
        self.setStyleSheet("""
            QFrame {
                background-color: #F3F4F6;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header de columna
        header_layout = QtWidgets.QHBoxLayout()
        
        nombre = QtWidgets.QLabel(self.columna_data['nombre'])
        nombre.setStyleSheet("font-weight: bold; font-size: 14px; color: #333; background: transparent;")
        header_layout.addWidget(nombre)
        
        header_layout.addStretch()
        
        # Botón agregar tarjeta
        btn_add = QtWidgets.QPushButton("➕")
        btn_add.setFixedSize(30, 30)
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #9333EA;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #7C3AED;
            }
        """)
        btn_add.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn_add.clicked.connect(self.agregar_tarjeta)
        header_layout.addWidget(btn_add)
        
        layout.addLayout(header_layout)
        
        # Área de scroll para tarjetas
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.tarjetas_widget = QtWidgets.QWidget()
        self.tarjetas_layout = QtWidgets.QVBoxLayout(self.tarjetas_widget)
        self.tarjetas_layout.setSpacing(5)
        self.tarjetas_layout.addStretch()
        
        scroll.setWidget(self.tarjetas_widget)
        layout.addWidget(scroll)
    
    def agregar_tarjeta_widget(self, tarjeta_data):
        """Agrega una tarjeta a la columna"""
        tarjeta = TarjetaWidget(tarjeta_data)
        # Insertar antes del stretch
        self.tarjetas_layout.insertWidget(self.tarjetas_layout.count() - 1, tarjeta)
    
    def limpiar_tarjetas(self):
        """Limpia todas las tarjetas"""
        while self.tarjetas_layout.count() > 1:  # Dejar el stretch
            item = self.tarjetas_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def agregar_tarjeta(self):
        """Muestra diálogo para agregar tarjeta"""
        dialog = CrearTarjetaDialog(self.columna_id, self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            # Buscar la ventana KanbanView en los ancestros
            parent = self.parent()
            while parent and not isinstance(parent, KanbanView):
                parent = parent.parent()
            if parent:
                parent.cargar_tarjetas()
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QFrame {
                    background-color: #E0E7FF;
                    border: 2px dashed #9333EA;
                    border-radius: 12px;
                    padding: 10px;
                }
            """)
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QFrame {
                background-color: #F3F4F6;
                border-radius: 12px;
                padding: 10px;
            }
        """)
    
    def dropEvent(self, event):
        tarjeta_id = event.mimeData().text()
        self.tarjeta_movida.emit(tarjeta_id, self.columna_id)
        self.setStyleSheet("""
            QFrame {
                background-color: #F3F4F6;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        event.acceptProposedAction()


class KanbanView(QtWidgets.QMainWindow):
    """Vista Kanban con 3 columnas"""
    volver_clicked = QtCore.pyqtSignal()  # Señal para volver
    
    def __init__(self, tablero_id, parent=None):
        super().__init__(parent)
        self.tablero_id = tablero_id
        self.columnas_widgets = {}
        self.setWindowTitle("Community - Tablero Kanban")
        self.setMinimumSize(1200, 768)
        self._setup_ui()
        self.cargar_tablero()
    
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
        
        # Área de columnas
        columnas_area = QtWidgets.QWidget()
        columnas_area.setStyleSheet("background-color: #f5f5f5;")
        self.columnas_layout = QtWidgets.QHBoxLayout(columnas_area)
        self.columnas_layout.setContentsMargins(20, 20, 20, 20)
        self.columnas_layout.setSpacing(15)
        
        main_layout.addWidget(columnas_area)
    
    def _crear_header(self):
        """Crea el header"""
        header = QtWidgets.QFrame()
        header.setMinimumHeight(60)
        header.setStyleSheet("background-color: #9333EA; border: none;")
        
        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(30, 10, 30, 10)
        
        # Botón volver
        btn_volver = QtWidgets.QPushButton("← Volver")
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
        
        # Título del tablero
        self.titulo_label = QtWidgets.QLabel("Cargando...")
        self.titulo_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; background: transparent;")
        layout.addWidget(self.titulo_label)
        
        layout.addStretch()
        
        return header
    
    def cargar_tablero(self):
        """Carga el tablero y sus columnas"""
        # Obtener info del tablero
        exito, tablero, error = tableros_manager.obtener_tablero(self.tablero_id)
        if exito and tablero:
            self.titulo_label.setText(tablero['nombre'])
        
        # Obtener columnas
        exito, columnas, error = tableros_manager.obtener_columnas(self.tablero_id)
        
        if not exito:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error al cargar columnas: {error}")
            return
        
        # Crear widgets de columnas
        for columna in columnas:
            columna_widget = ColumnaWidget(columna)
            columna_widget.tarjeta_movida.connect(self.mover_tarjeta)
            self.columnas_widgets[columna['id']] = columna_widget
            self.columnas_layout.addWidget(columna_widget)
        
        # Cargar tarjetas
        self.cargar_tarjetas()
    
    def cargar_tarjetas(self):
        """Carga las tarjetas en cada columna"""
        for columna_id, columna_widget in self.columnas_widgets.items():
            columna_widget.limpiar_tarjetas()
            
            exito, tarjetas, error = tableros_manager.obtener_tarjetas(columna_id)
            
            if exito and tarjetas:
                for tarjeta in tarjetas:
                    columna_widget.agregar_tarjeta_widget(tarjeta)
    
    def mover_tarjeta(self, tarjeta_id, nueva_columna_id):
        """Mueve una tarjeta a otra columna"""
        exito, error = tarjetas_manager.mover_tarjeta(tarjeta_id, nueva_columna_id)
        
        if exito:
            self.cargar_tarjetas()
        else:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error al mover tarjeta: {error}")


class CrearTarjetaDialog(QtWidgets.QDialog):
    """Diálogo para crear tarjeta"""
    
    def __init__(self, columna_id, parent=None):
        super().__init__(parent)
        self.columna_id = columna_id
        self.setWindowTitle("Nueva Tarjeta")
        self.setMinimumSize(400, 350)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Título
        layout.addWidget(QtWidgets.QLabel("Título:"))
        self.input_titulo = QtWidgets.QLineEdit()
        self.input_titulo.setPlaceholderText("Título de la tarea...")
        self.input_titulo.setStyleSheet("padding: 8px; border: 2px solid #E5E7EB; border-radius: 8px;")
        layout.addWidget(self.input_titulo)
        
        # Descripción
        layout.addWidget(QtWidgets.QLabel("Descripción:"))
        self.input_descripcion = QtWidgets.QTextEdit()
        self.input_descripcion.setPlaceholderText("Descripción de la tarea...")
        self.input_descripcion.setMaximumHeight(100)
        self.input_descripcion.setStyleSheet("padding: 8px; border: 2px solid #E5E7EB; border-radius: 8px;")
        layout.addWidget(self.input_descripcion)
        
        # Fecha
        layout.addWidget(QtWidgets.QLabel("Fecha de vencimiento (opcional):"))
        self.input_fecha = QtWidgets.QDateEdit()
        self.input_fecha.setCalendarPopup(True)
        self.input_fecha.setDate(QtCore.QDate.currentDate())
        self.input_fecha.setStyleSheet("padding: 8px; border: 2px solid #E5E7EB; border-radius: 8px;")
        layout.addWidget(self.input_fecha)
        
        layout.addStretch()
        
        # Botones
        botones_layout = QtWidgets.QHBoxLayout()
        botones_layout.addStretch()
        
        btn_cancelar = QtWidgets.QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        botones_layout.addWidget(btn_cancelar)
        
        btn_crear = QtWidgets.QPushButton("Crear Tarjeta")
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
        """Crea la tarjeta"""
        titulo = self.input_titulo.text().strip()
        if not titulo:
            QtWidgets.QMessageBox.warning(self, "Error", "El título es obligatorio")
            return
        
        descripcion = self.input_descripcion.toPlainText().strip()
        fecha = self.input_fecha.date().toPyDate()
        
        exito, tarjeta, error = tarjetas_manager.crear_tarjeta(
            self.columna_id, titulo, descripcion, fecha
        )
        
        if exito:
            self.accept()
        else:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error al crear tarjeta: {error}")


def main():
    app = QtWidgets.QApplication(sys.argv)
    # Necesitas un tablero_id válido para probar
    w = KanbanView("test-tablero-id")
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
