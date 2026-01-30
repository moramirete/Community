import sys
import os
import json
from PyQt5 import QtWidgets, QtCore, QtGui

# Importar helper de recursos
try:
    from resource_helper import resource_path
except ImportError:
    # Fallback si se ejecuta desde otra ubicación
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from resource_helper import resource_path

# Asegurar que src es importable
if not getattr(sys, 'frozen', False):
    sys.path.insert(0, resource_path(''))

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
    logout_requested = QtCore.pyqtSignal()  # Emite cuando se solicita logout
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Community - Gestión de Proyectos")
        self.setMinimumSize(1200, 800)
        
        # Establecer icono de la aplicación
        icon_path = resource_path("interfaces/imagenes/logoCommunity.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
        
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
        self.user_data = None
        self.favoritos_compartidos = set()
        
        # Ruta archivo favoritos (persistente, fuera del ejecutable)
        if getattr(sys, 'frozen', False):
            # En ejecutable, guardar junto al exe
            self.fav_file = os.path.join(os.path.dirname(sys.executable), 'favorites.json')
        else:
            # En desarrollo
            self.fav_file = resource_path('favorites.json')
        
    def set_user_data(self, user_data):
        """Asigna los datos del usuario y carga sus favoritos"""
        self.user_data = user_data
        self.load_favorites()
        # Mostrar home con los favoritos cargados
        self.show_home(dark=False)

    def load_favorites(self):
        """Carga los favoritos desde el archivo JSON"""
        if not self.user_data or not os.path.exists(self.fav_file):
            return
        
        try:
            with open(self.fav_file, 'r') as f:
                data = json.load(f)
                user_id = self.user_data.get('id')
                if user_id in data:
                    self.favoritos_compartidos.update(data[user_id])
        except Exception as e:
            print(f"Error cargando favoritos: {e}")

    def save_favorites(self):
        """Guarda los favoritos en el archivo JSON"""
        if not self.user_data:
            return
            
        try:
            user_id = self.user_data.get('id')
            data = {}
            if os.path.exists(self.fav_file):
                with open(self.fav_file, 'r') as f:
                    try:
                        data = json.load(f)
                    except:
                        pass
            
            data[user_id] = list(self.favoritos_compartidos)
            
            with open(self.fav_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error guardando favoritos: {e}")

    def closeEvent(self, event):
        """Al cerrar la ventana, guardar favoritos"""
        self.save_favorites()
        super().closeEvent(event)

    def show_home(self, dark=False):
        """Muestra la vista home"""
        self.is_dark = dark
        
        # Crear vistas home si no existen
        if not self.home_light:
            self.home_light = HomeCommunityWindow(favoritos_sharing=self.favoritos_compartidos)
            self.home_light.proyecto_seleccionado.connect(self.show_tableros)
            self.home_light.logout_requested.connect(self.logout_requested.emit)
            try:
                self.home_light.btn_theme.clicked.connect(self.toggle_theme)
            except:
                pass
            self.stack.addWidget(self.home_light)
        
        if not self.home_dark:
            self.home_dark = HomeCommunityDarkWindow(favoritos_sharing=self.favoritos_compartidos)
            self.home_dark.proyecto_seleccionado.connect(self.show_tableros)
            self.home_dark.logout_requested.connect(self.logout_requested.emit)
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
        """Cambia entre tema claro y oscuro desde cualquier vista"""
        # Cambiar el estado del tema
        self.is_dark = not self.is_dark
        
        # Detectar qué vista está activa
        current_widget = self.stack.currentWidget()
        
        # Si es home
        if current_widget in [self.home_light, self.home_dark]:
            self.show_home(dark=self.is_dark)
        # Si es tableros, guardar el proyecto_id y recrear
        elif current_widget == self.tableros_view and self.tableros_view:
            proyecto_id = self.tableros_view.proyecto_id if hasattr(self.tableros_view, 'proyecto_id') else None
            if proyecto_id:
                self.show_tableros(proyecto_id)
        # Si es kanban, guardar el tablero_id y recrear
        elif current_widget == self.kanban_view and self.kanban_view:
            tablero_id = self.kanban_view.tablero_id if hasattr(self.kanban_view, 'tablero_id') else None
            if tablero_id:
                self.show_kanban(tablero_id)
        # Por defecto, volver al home
        else:
            self.show_home(dark=self.is_dark)
    
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
        
        self.proyecto_id = proyecto_id  # Guardar para toggle_theme
        self.vista = TablerosView(proyecto_id)
        self.vista.tablero_seleccionado.connect(self.tablero_seleccionado.emit)
        self.vista.volver_clicked.connect(self.volver_clicked.emit)
        
        # Conectar botón de tema si existe
        if hasattr(self.vista, 'btn_theme') and parent:
            try:
                self.vista.btn_theme.clicked.connect(parent.toggle_theme)
            except:
                pass
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.vista)


class KanbanViewEmbedded(QtWidgets.QWidget):
    """Vista Kanban embebida"""
    volver_clicked = QtCore.pyqtSignal()
    
    def __init__(self, tablero_id, parent=None):
        super().__init__(parent)
        from kanban_view import KanbanView
        
        self.tablero_id = tablero_id  # Guardar para toggle_theme
        self.vista = KanbanView(tablero_id)
        self.vista.volver_clicked.connect(self.volver_clicked.emit)
        
        # Conectar botón de tema si existe
        if hasattr(self.vista, 'btn_theme') and parent:
            try:
                self.vista.btn_theme.clicked.connect(parent.toggle_theme)
            except:
                pass
        
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
        
        self.proyecto_id = proyecto_id  # Guardar para toggle_theme
        self.vista = TablerosViewDark(proyecto_id)
        self.vista.tablero_seleccionado.connect(self.tablero_seleccionado.emit)
        self.vista.volver_clicked.connect(self.volver_clicked.emit)
        
        # Conectar botón de tema si existe
        if hasattr(self.vista, 'btn_theme') and parent:
            try:
                self.vista.btn_theme.clicked.connect(parent.toggle_theme)
            except:
                pass
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.vista)


class KanbanViewEmbeddedDark(QtWidgets.QWidget):
    """Vista Kanban embebida dark"""
    volver_clicked = QtCore.pyqtSignal()
    
    def __init__(self, tablero_id, parent=None):
        super().__init__(parent)
        from kanban_view_dark import KanbanViewDark
        
        self.tablero_id = tablero_id  # Guardar para toggle_theme
        self.vista = KanbanViewDark(tablero_id)
        self.vista.volver_clicked.connect(self.volver_clicked.emit)
        
        # Conectar botón de tema si existe
        if hasattr(self.vista, 'btn_theme') and parent:
            try:
                self.vista.btn_theme.clicked.connect(parent.toggle_theme)
            except:
                pass
        
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
                user_data = self.login_win.authenticated_user
                self.login_win.hide()
                self.show_main_window(user_data)
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

    def show_main_window(self, user_data=None):
        """Muestra la ventana principal"""
        if not self.main_win:
            self.main_win = MainWindow()
            self.main_win.logout_requested.connect(self.handle_logout)
        
        if user_data:
            self.main_win.set_user_data(user_data)
        
        self.main_win.show()
    
    def handle_logout(self):
        """Maneja el cierre de sesión"""
        if self.main_win:
            self.main_win.hide()
        self.show_login()

    def run(self):
        self.show_login()
        sys.exit(self.app.exec_())


def main():
    controller = AppController()
    controller.run()


if __name__ == '__main__':
    main()
