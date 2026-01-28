"""
Controlador principal de la aplicación Community
Gestiona todas las vistas en una sola ventana
"""
import sys
from PyQt5 import QtWidgets, QtCore

from login_community import LoginCommunityWindow
from home_community import HomeCommunityWindow
from home_community_dark import HomeCommunityDarkWindow
from proyectos_view import ProyectosView
from proyectos_view_dark import ProyectosViewDark
from tableros_view import TablerosView
from tableros_view_dark import TablerosViewDark
from kanban_view import KanbanView
from kanban_view_dark import KanbanViewDark


class MainWindow(QtWidgets.QMainWindow):
    """Ventana principal que contiene todas las vistas"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Community - Gestión de Proyectos")
        self.setMinimumSize(1200, 800)
        
        # Stack de widgets
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Referencias a vistas
        self.home_light = None
        self.home_dark = None
        self.proyectos_view = None
        self.tableros_view = None
        self.kanban_view = None
        self.is_dark = False
        self.favoritos_compartidos = set()
        
        # Mostrar home por defecto
        self.show_home(dark=False)
    
    def show_home(self, dark=False):
        """Muestra la vista home"""
        self.is_dark = dark
        
        # Crear vistas home si no existen
        if not self.home_light:
            self.home_light = HomeCommunityWindow(favoritos_sharing=self.favoritos_compartidos)
            self.home_light.proyecto_seleccionado.connect(self.show_tableros)
            try:
                self.home_light.btn_theme.clicked.connect(self.toggle_theme)
            except:
                pass
            self.stack.addWidget(self.home_light)
        
        if not self.home_dark:
            self.home_dark = HomeCommunityDarkWindow(favoritos_sharing=self.favoritos_compartidos)
            self.home_dark.proyecto_seleccionado.connect(self.show_tableros)
            try:
                self.home_dark.btn_theme.clicked.connect(self.toggle_theme)
            except:
                pass
            self.stack.addWidget(self.home_dark)
        
        # Seleccionar vista según tema
        if dark:
            if hasattr(self.home_dark, 'cargar_proyectos'):
                self.home_dark.cargar_proyectos()
            self.stack.setCurrentWidget(self.home_dark)
        else:
            if hasattr(self.home_light, 'cargar_proyectos'):
                self.home_light.cargar_proyectos()
            self.stack.setCurrentWidget(self.home_light)
    
    def toggle_theme(self):
        """Cambia entre tema claro y oscuro"""
        self.show_home(dark=not self.is_dark)
    
    def show_proyectos(self):
        """Muestra la vista de proyectos"""
        if not self.proyectos_view:
            if self.is_dark:
                self.proyectos_view = ProyectosViewEmbeddedDark(self)
            else:
                self.proyectos_view = ProyectosViewEmbedded(self)
            self.proyectos_view.proyecto_seleccionado.connect(self.show_tableros)
            self.proyectos_view.volver_clicked.connect(lambda: self.show_home(self.is_dark))
            self.stack.addWidget(self.proyectos_view)
        
        self.proyectos_view.cargar_proyectos()
        self.stack.setCurrentWidget(self.proyectos_view)
    
    def show_tableros(self, proyecto_id):
        """Muestra la vista de tableros"""
        # Remover vista anterior si existe
        if self.tableros_view:
            self.stack.removeWidget(self.tableros_view)
            self.tableros_view.deleteLater()
            self.tableros_view = None
        
        # Crear nueva vista de tableros según tema
        if self.is_dark:
            self.tableros_view = TablerosViewEmbeddedDark(proyecto_id, self)
        else:
            self.tableros_view = TablerosViewEmbedded(proyecto_id, self)
        
        self.tableros_view.tablero_seleccionado.connect(self.show_kanban)
        self.tableros_view.volver_clicked.connect(lambda: self.show_home(self.is_dark))
        self.stack.addWidget(self.tableros_view)
        self.stack.setCurrentWidget(self.tableros_view)
    
    def show_kanban(self, tablero_id):
        """Muestra la vista Kanban"""
        # Remover vista anterior si existe
        if self.kanban_view:
            self.stack.removeWidget(self.kanban_view)
            self.kanban_view.deleteLater()
            self.kanban_view = None
        
        # Crear nueva vista kanban según tema
        if self.is_dark:
            self.kanban_view = KanbanViewEmbeddedDark(tablero_id, self)
        else:
            self.kanban_view = KanbanViewEmbedded(tablero_id, self)
        
        self.kanban_view.volver_clicked.connect(self.volver_a_tableros)
        self.stack.addWidget(self.kanban_view)
        self.stack.setCurrentWidget(self.kanban_view)
    
    def volver_a_tableros(self):
        """Vuelve a la vista de tableros"""
        if self.tableros_view:
            self.stack.setCurrentWidget(self.tableros_view)


class ProyectosViewEmbedded(QtWidgets.QWidget):
    """Vista de proyectos embebida"""
    proyecto_seleccionado = QtCore.pyqtSignal(str)
    volver_clicked = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Importar aquí para evitar importación circular
        from proyectos_view import ProyectosView
        
        # Crear la vista original
        self.vista = ProyectosView()
        self.vista.proyecto_seleccionado.connect(self.proyecto_seleccionado.emit)
        
        # Conectar botón volver (si existe)
        # La vista original ya tiene su propio layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.vista)
    
    def cargar_proyectos(self):
        """Recarga los proyectos"""
        if hasattr(self.vista, 'cargar_proyectos'):
            self.vista.cargar_proyectos()


class TablerosViewEmbedded(QtWidgets.QWidget):
    """Vista de tableros embebida"""
    tablero_seleccionado = QtCore.pyqtSignal(str)
    volver_clicked = QtCore.pyqtSignal()
    
    def __init__(self, proyecto_id, parent=None):
        super().__init__(parent)
        from tableros_view import TablerosView
        
        self.vista = TablerosView(proyecto_id)
        self.vista.tablero_seleccionado.connect(self.tablero_seleccionado.emit)
        self.vista.volver_clicked.connect(self.volver_clicked.emit)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.vista)


class KanbanViewEmbedded(QtWidgets.QWidget):
    """Vista Kanban embebida"""
    volver_clicked = QtCore.pyqtSignal()
    
    def __init__(self, tablero_id, parent=None):
        super().__init__(parent)
        from kanban_view import KanbanView
        
        self.vista = KanbanView(tablero_id)
        self.vista.volver_clicked.connect(self.volver_clicked.emit)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.vista)


# ============ DARK MODE WRAPPERS ============

class ProyectosViewEmbeddedDark(QtWidgets.QWidget):
    """Vista de proyectos embebida dark"""
    proyecto_seleccionado = QtCore.pyqtSignal(str)
    volver_clicked = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        from proyectos_view_dark import ProyectosViewDark
        
        self.vista = ProyectosViewDark()
        self.vista.proyecto_seleccionado.connect(self.proyecto_seleccionado.emit)
        self.vista.volver_clicked.connect(self.volver_clicked.emit)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.vista)
    
    def cargar_proyectos(self):
        if hasattr(self.vista, 'cargar_proyectos'):
            self.vista.cargar_proyectos()


class TablerosViewEmbeddedDark(QtWidgets.QWidget):
    """Vista de tableros embebida dark"""
    tablero_seleccionado = QtCore.pyqtSignal(str)
    volver_clicked = QtCore.pyqtSignal()
    
    def __init__(self, proyecto_id, parent=None):
        super().__init__(parent)
        from tableros_view_dark import TablerosViewDark
        
        self.vista = TablerosViewDark(proyecto_id)
        self.vista.tablero_seleccionado.connect(self.tablero_seleccionado.emit)
        self.vista.volver_clicked.connect(self.volver_clicked.emit)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.vista)


class KanbanViewEmbeddedDark(QtWidgets.QWidget):
    """Vista Kanban embebida dark"""
    volver_clicked = QtCore.pyqtSignal()
    
    def __init__(self, tablero_id, parent=None):
        super().__init__(parent)
        from kanban_view_dark import KanbanViewDark
        
        self.vista = KanbanViewDark(tablero_id)
        self.vista.volver_clicked.connect(self.volver_clicked.emit)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.vista)


class AppController:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.login_win = None
        self.main_win = None

    def show_login(self):
        self.login_win = LoginCommunityWindow()
        self.login_win.btn_login.clicked.connect(self._on_login)
        self.login_win.show()

    def _on_login(self):
        # Validate login credentials
        try:
            if self.login_win and self.login_win.validate_login():
                # Login successful, hide login window and show main window
                self.login_win.hide()
                self.show_main_window()
            # If validation fails, the login window will show an error message
            # and remain visible
        except Exception as e:
            import traceback
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(
                self.login_win,
                "Error",
                f"Error durante el login: {str(e)}"
            )

    def show_main_window(self):
        """Muestra la ventana principal"""
        if not self.main_win:
            self.main_win = MainWindow()
        self.main_win.show()

    def run(self):
        self.show_login()
        sys.exit(self.app.exec_())


def main():
    controller = AppController()
    controller.run()


if __name__ == '__main__':
    main()
