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
from src.base_datos.tableros_manager import tableros_manager
from src.base_datos.tarjetas_manager import tarjetas_manager


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
        
        # Fondo neutral oscuro
        self.setStyleSheet("""
            QFrame {
                background-color: #2d2d44;
                border: 1px solid #3d3d54;
                border-radius: 8px;
                padding: 0px;
                margin: 5px;
            }
            QFrame:hover {
                border: 2px solid #9333EA;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Línea de color superior
        color = self.tarjeta_data.get('color', '#9333EA')
        color_stripe = QtWidgets.QFrame()
        color_stripe.setFixedHeight(4)
        color_stripe.setStyleSheet(f"background-color: {color}; border: none; border-top-left-radius: 8px; border-top-right-radius: 8px;")
        layout.addWidget(color_stripe)
        
        # Contenedor de contenido con padding
        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet("background: transparent; border: none;")
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 8, 10, 8)
        content_layout.setSpacing(5)
        
        # Header Layout (Título y Botón Menú)
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(5)
        
        # Título
        titulo = QtWidgets.QLabel(self.tarjeta_data['titulo'])
        titulo.setStyleSheet("font-weight: bold; font-size: 13px; color: #FFFFFF; background: transparent;")
        titulo.setWordWrap(True)
        header_layout.addWidget(titulo, 1)
        
        # Botón Menú (...)
        btn_menu = QtWidgets.QPushButton("...")
        btn_menu.setFixedSize(24, 24)
        btn_menu.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn_menu.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-weight: bold;
                color: #B4B4C8;
                font-size: 14px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #3d3d54;
                color: #FFFFFF;
            }
        """)
        btn_menu.clicked.connect(self.abrir_edicion)
        header_layout.addWidget(btn_menu)
        
        content_layout.addLayout(header_layout)
        
        # Descripción (si existe)
        if self.tarjeta_data.get('descripcion'):
            desc = QtWidgets.QLabel(self.tarjeta_data['descripcion'][:50] + "...")
            desc.setStyleSheet("font-size: 11px; color: #B4B4C8; background: transparent;")
            desc.setWordWrap(True)
            content_layout.addWidget(desc)
        
        # Footer Layout (Fecha y Prioridad)
        footer_layout = QtWidgets.QHBoxLayout()
        footer_layout.setSpacing(10)
        
        # Fecha (si existe)
        if self.tarjeta_data.get('fecha_vencimiento'):
            fecha = QtWidgets.QLabel(f"📅 {self.tarjeta_data['fecha_vencimiento']}")
            fecha.setStyleSheet("font-size: 10px; color: #B4B4C8; background: transparent;")
            footer_layout.addWidget(fecha)
        
        footer_layout.addStretch()
        
        # Prioridad
        orden = self.tarjeta_data.get('orden', 2)
        texto_prioridad = "Normal"
        color_prioridad = "#B4B4C8"
        
        if orden == 0:
            texto_prioridad = "Muy Importante"
            color_prioridad = "#EF4444"  # Rojo
        elif orden == 1:
            texto_prioridad = "Importante"
            color_prioridad = "#F59E0B"  # Naranja
            
        prioridad_label = QtWidgets.QLabel(texto_prioridad)
        prioridad_label.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {color_prioridad}; background: transparent;")
        footer_layout.addWidget(prioridad_label)
        
        content_layout.addLayout(footer_layout)
        
        # Usuarios asignados
        if self.tarjeta_data.get('tarjetas_usuarios'):
            num_usuarios = len(self.tarjeta_data['tarjetas_usuarios'])
            usuarios_label = QtWidgets.QLabel(f"👥 {num_usuarios} asignado(s)")
            usuarios_label.setStyleSheet("font-size: 10px; color: #B4B4C8; background: transparent;")
            content_layout.addWidget(usuarios_label)
        
        layout.addWidget(content_widget)
    
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
            
    def abrir_edicion(self):
        """Abre diálogo de edición"""
        dialog = EditarTarjetaDialogDark(self.tarjeta_data, self)
        if dialog.exec_():
            # Recargar tablero (emitir señal o buscar padre)
            # Buscamos el KanbanView padre
            parent = self.parent()
            while parent:
                if hasattr(parent, 'cargar_tarjetas'):
                    parent.cargar_tarjetas()
                    break
                parent = parent.parent()


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
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header de columna
        header_layout = QtWidgets.QHBoxLayout()
        
        nombre = QtWidgets.QLabel(self.columna_data['nombre'])
        nombre.setStyleSheet("font-weight: bold; font-size: 14px; color: #FFFFFF; background: transparent;")
        header_layout.addWidget(nombre)
        
        header_layout.addStretch()
        
        # Botón agregar tarjeta
        btn_add = QtWidgets.QPushButton("➕")
        btn_add.setFixedSize(30, 30)
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #9333EA;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
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
        dialog = CrearTarjetaDialogDark(self.columna_id, self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            # Buscar la ventana KanbanView en los ancestros
            parent = self.parent()
            while parent and not isinstance(parent, KanbanViewDark):
                parent = parent.parent()
            if parent:
                parent.cargar_tarjetas()
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QFrame {
                    background-color: #3d3d54;
                    border: 2px dashed #9333EA;
                    border-radius: 12px;
                    padding: 10px;
                }
            """)
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border-radius: 12px;
                padding: 10px;
            }
        """)
    
    def dropEvent(self, event):
        tarjeta_id = event.mimeData().text()
        self.tarjeta_movida.emit(tarjeta_id, self.columna_id)
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        event.acceptProposedAction()


class KanbanViewDark(QtWidgets.QMainWindow):
    """Vista Kanban con 3 columnas - Dark Mode"""
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
        columnas_area.setStyleSheet("background-color: #0f0f1e;")
        self.columnas_layout = QtWidgets.QHBoxLayout(columnas_area)
        self.columnas_layout.setContentsMargins(20, 20, 20, 20)
        self.columnas_layout.setSpacing(15)
        
        main_layout.addWidget(columnas_area)
    
    def _crear_header(self):
        """Crea el header"""
        header = QtWidgets.QFrame()
        header.setMinimumHeight(60)
        header.setStyleSheet("background-color: #7C3AED; border: none;")
        
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


class CrearTarjetaDialogDark(QtWidgets.QDialog):
    """Diálogo para crear tarjeta - Dark Mode"""
    
    def __init__(self, columna_id, parent=None):
        super().__init__(parent)
        self.columna_id = columna_id
        self.setWindowTitle("Nueva Tarjeta")
        self.setMinimumSize(400, 350)
        self._setup_ui()
    
    def _setup_ui(self):
        # Estilo general del diálogo
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
            }
            QLineEdit, QTextEdit, QDateEdit {
                background-color: #2d2d44;
                color: #FFFFFF;
                border: 2px solid #3d3d54;
                border-radius: 8px;
                padding: 8px;
            }
            QLineEdit:focus, QTextEdit:focus, QDateEdit:focus {
                border: 2px solid #9333EA;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Título
        titulo_label = QtWidgets.QLabel("Título:")
        layout.addWidget(titulo_label)
        self.input_titulo = QtWidgets.QLineEdit()
        self.input_titulo.setPlaceholderText("Título de la tarea...")
        layout.addWidget(self.input_titulo)
        
        # Descripción
        desc_label = QtWidgets.QLabel("Descripción:")
        layout.addWidget(desc_label)
        self.input_descripcion = QtWidgets.QTextEdit()
        self.input_descripcion.setPlaceholderText("Descripción de la tarea...")
        self.input_descripcion.setMaximumHeight(100)
        layout.addWidget(self.input_descripcion)
        
        # Color
        color_label = QtWidgets.QLabel("Color de la tarjeta:")
        layout.addWidget(color_label)
        
        # Selector de colores predefinidos
        colors_layout = QtWidgets.QHBoxLayout()
        self.color_buttons = []
        self.selected_color = '#9333EA'  # Color por defecto
        
        colores = [
            ('#9333EA', 'Morado'),
            ('#EF4444', 'Rojo'),
            ('#F59E0B', 'Naranja'),
            ('#10B981', 'Verde'),
            ('#3B82F6', 'Azul'),
            ('#EC4899', 'Rosa'),
            ('#8B5CF6', 'Violeta'),
            ('#6B7280', 'Gris')
        ]
        
        for color, nombre in colores:
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(40, 40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: 3px solid #3d3d54;
                    border-radius: 20px;
                }}
                QPushButton:hover {{
                    border: 3px solid #FFFFFF;
                }}
            """)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            btn.clicked.connect(lambda checked, c=color: self.select_color(c))
            btn.setToolTip(nombre)
            self.color_buttons.append((btn, color))
            colors_layout.addWidget(btn)
        
        colors_layout.addStretch()
        layout.addLayout(colors_layout)
        
        # Marcar el color por defecto
        self.select_color('#9333EA')
        
        # Prioridad
        layout.addWidget(QtWidgets.QLabel("Prioridad:"))
        priority_layout = QtWidgets.QHBoxLayout()
        
        self.radio_muy_importante = QtWidgets.QRadioButton("Muy Importante")
        self.radio_importante = QtWidgets.QRadioButton("Importante")
        self.radio_normal = QtWidgets.QRadioButton("Normal")
        
        # Estilo para los radio buttons en dark mode
        estilo_rb = """
            QRadioButton {
                color: #FFFFFF;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #3d3d54;
                border-radius: 10px;
                background: transparent;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #9333EA;
                border-radius: 10px;
                background: #9333EA;
            }
        """
        self.radio_muy_importante.setStyleSheet(estilo_rb)
        self.radio_importante.setStyleSheet(estilo_rb)
        self.radio_normal.setStyleSheet(estilo_rb)
        
        self.radio_normal.setChecked(True)  # Por defecto
        
        priority_layout.addWidget(self.radio_muy_importante)
        priority_layout.addWidget(self.radio_importante)
        priority_layout.addWidget(self.radio_normal)
        priority_layout.addStretch()
        
        layout.addLayout(priority_layout)
        
        # Fecha
        fecha_label = QtWidgets.QLabel("Fecha de vencimiento (opcional):")
        layout.addWidget(fecha_label)
        self.input_fecha = QtWidgets.QDateEdit()
        self.input_fecha.setCalendarPopup(True)
        self.input_fecha.setDate(QtCore.QDate.currentDate())
        layout.addWidget(self.input_fecha)
        
        layout.addStretch()
        
        # Botones
        botones_layout = QtWidgets.QHBoxLayout()
        botones_layout.addStretch()
        
        btn_cancelar = QtWidgets.QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #3d3d54;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4d4d64;
            }
        """)
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
    
    def select_color(self, color):
        """Selecciona un color"""
        self.selected_color = color
        # Actualizar bordes de botones
        for btn, btn_color in self.color_buttons:
            if btn_color == color:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {btn_color};
                        border: 3px solid #FFFFFF;
                        border-radius: 20px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {btn_color};
                        border: 3px solid #3d3d54;
                        border-radius: 20px;
                    }}
                    QPushButton:hover {{
                        border: 3px solid #FFFFFF;
                    }}
                """)
    
    def crear(self):
        """Crea la tarjeta"""
        titulo = self.input_titulo.text().strip()
        if not titulo:
            QtWidgets.QMessageBox.warning(self, "Error", "El título es obligatorio")
            return
        
        descripcion = self.input_descripcion.toPlainText().strip()
        fecha = self.input_fecha.date().toPyDate()
        
        # Determinar prioridad (orden)
        orden = 2  # Normal por defecto
        if self.radio_muy_importante.isChecked():
            orden = 0
        elif self.radio_importante.isChecked():
            orden = 1
            
        exito, tarjeta, error = tarjetas_manager.crear_tarjeta(
            self.columna_id, titulo, descripcion, fecha, self.selected_color, orden
        )
        
        if exito:
            self.accept()
        else:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error al crear tarjeta: {error}")


class EditarTarjetaDialogDark(CrearTarjetaDialogDark):
    """Diálogo para editar tarjeta en Modo Oscuro"""
    
    def __init__(self, tarjeta_data, parent=None):
        super().__init__(tarjeta_data['columna_id'], parent)
        self.tarjeta_data = tarjeta_data
        self.setWindowTitle("Editar Tarjeta")
        
        # Pre-llenar datos
        self.input_titulo.setText(tarjeta_data['titulo'])
        self.input_descripcion.setText(tarjeta_data.get('descripcion', ''))
        
        # Color
        color = tarjeta_data.get('color', '#9333EA')
        self.select_color(color)
        
        # Prioridad
        orden = tarjeta_data.get('orden', 2)
        if orden == 0:
            self.radio_muy_importante.setChecked(True)
        elif orden == 1:
            self.radio_importante.setChecked(True)
        else:
            self.radio_normal.setChecked(True)
            
        # Fecha
        if tarjeta_data.get('fecha_vencimiento'):
            fecha = datetime.strptime(tarjeta_data['fecha_vencimiento'], '%Y-%m-%d').date()
            self.input_fecha.setDate(fecha)
            
        # Modificar botones
        layout = self.layout()
        
        # Buscar el botón "Crear Tarjeta" y cambiar texto
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.layout():
                btn_layout = item.layout()
                for j in range(btn_layout.count()):
                    widget = btn_layout.itemAt(j).widget()
                    if isinstance(widget, QtWidgets.QPushButton) and widget.text() == "Crear Tarjeta":
                        widget.setText("Guardar Cambios")
                        widget.clicked.disconnect()
                        widget.clicked.connect(self.guardar_cambios)
        
        # Añadir botón de eliminar con estilo oscuro
        btn_eliminar = QtWidgets.QPushButton("Eliminar Tarjeta")
        btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        btn_eliminar.clicked.connect(self.eliminar_tarjeta)
        
        # Insertar al principio del layout de botones
        botones_layout = layout.itemAt(layout.count() - 1).layout()
        botones_layout.insertWidget(0, btn_eliminar)

    def guardar_cambios(self):
        """Guarda los cambios de la tarjeta"""
        titulo = self.input_titulo.text().strip()
        if not titulo:
            QtWidgets.QMessageBox.warning(self, "Error", "El título es obligatorio")
            return
        
        descripcion = self.input_descripcion.toPlainText().strip()
        fecha = self.input_fecha.date().toPyDate()
        
        # Prioridad
        orden = 2
        if self.radio_muy_importante.isChecked():
            orden = 0
        elif self.radio_importante.isChecked():
            orden = 1
            
        exito, error = tarjetas_manager.actualizar_tarjeta(
            self.tarjeta_data['id'],
            titulo=titulo,
            descripcion=descripcion,
            fecha_vencimiento=fecha,
            color=self.selected_color,
            orden=orden
        )
        
        if exito:
            self.accept()
        else:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error al actualizar: {error}")

    def eliminar_tarjeta(self):
        """Elimina la tarjeta con confirmación específica"""
        orden_actual = 2
        if self.radio_muy_importante.isChecked():
            orden_actual = 0
        elif self.radio_importante.isChecked():
            orden_actual = 1
            
        confirmacion = False
        
        if orden_actual == 0:
            # Mensaje específico para tareas muy importantes
            respuesta = QtWidgets.QMessageBox.warning(
                self,
                "⚠️ Atención",
                f"Esta es una tarea muy importante, ¿estás seguro de borrar la tarjeta: {self.tarjeta_data['titulo']}?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            confirmacion = (respuesta == QtWidgets.QMessageBox.Yes)
        else:
            # Mensaje estándar
            respuesta = QtWidgets.QMessageBox.question(
                self,
                "Confirmar eliminación",
                "¿Estás seguro de que quieres eliminar esta tarjeta?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            confirmacion = (respuesta == QtWidgets.QMessageBox.Yes)
            
        if confirmacion:
            exito, error = tarjetas_manager.eliminar_tarjeta(self.tarjeta_data['id'])
            if exito:
                self.accept()
            else:
                QtWidgets.QMessageBox.critical(self, "Error", f"Error al eliminar: {error}")


def main():
    app = QtWidgets.QApplication(sys.argv)
    # Necesitas un tablero_id válido para probar
    w = KanbanViewDark("test-tablero-id")
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
