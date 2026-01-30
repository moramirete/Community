import sys
import os
import json
from PyQt5 import QtWidgets, QtCore, QtGui

try:
    from resource_helper import resource_path
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from resource_helper import resource_path

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
    logout_requested = QtCore.pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Community - Gestión de Proyectos")
        self.setMinimumSize(1200, 800)
        
        icon_path = resource_path("interfaces/imagenes/logoCommunity.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
        
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self.home_light = None
        self.home_dark = None
        self.proyectos_view = None
        self.tableros_view = None
        self.kanban_view = None
        self.is_dark = False
        self.user_data = None
        self.favoritos_compartidos = set()
        
        if getattr(sys, 'frozen', False):
            self.fav_file = os.path.join(os.path.dirname(sys.executable), 'favorites.json')
        else:
            self.fav_file = resource_path('favorites.json')
        
    def establecer_datos_usuario(self, user_data):
        self.user_data = user_data
        self.cargar_favoritos()
        self.ver_inicio(dark=False)

    def cargar_favoritos(self):
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

    def guardar_favoritos(self):
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
        self.guardar_favoritos()
        super().closeEvent(event)

    def ver_inicio(self, dark=False):
        self.is_dark = dark
        
        if not self.home_light:
            self.home_light = HomeCommunityWindow(favoritos_sharing=self.favoritos_compartidos)
            self.home_light.proyecto_seleccionado.connect(self.ver_tableros)
            self.home_light.logout_requested.connect(self.logout_requested.emit)
            try:
                self.home_light.btn_theme.clicked.connect(self.alternar_tema)
            except:
                pass
            self.stack.addWidget(self.home_light)
        
        if not self.home_dark:
            self.home_dark = HomeCommunityDarkWindow(favoritos_sharing=self.favoritos_compartidos)
            self.home_dark.proyecto_seleccionado.connect(self.ver_tableros)
            self.home_dark.logout_requested.connect(self.logout_requested.emit)
            try:
                self.home_dark.btn_theme.clicked.connect(self.alternar_tema)
            except:
                pass
            self.stack.addWidget(self.home_dark)
        
        if dark:
            if hasattr(self.home_dark, 'obtener_proyectos'):
                self.home_dark.obtener_proyectos()
            self.stack.setCurrentWidget(self.home_dark)
        else:
            if hasattr(self.home_light, 'obtener_proyectos'):
                self.home_light.obtener_proyectos()
            self.stack.setCurrentWidget(self.home_light)
    
    def alternar_tema(self):
        self.is_dark = not self.is_dark
        
        current_widget = self.stack.currentWidget()
        
        if current_widget in [self.home_light, self.home_dark]:
            self.ver_inicio(dark=self.is_dark)
        elif current_widget == self.tableros_view and self.tableros_view:
            proyecto_id = self.tableros_view.proyecto_id if hasattr(self.tableros_view, 'proyecto_id') else None
            if proyecto_id:
                self.ver_tableros(proyecto_id)
        elif current_widget == self.kanban_view and self.kanban_view:
            tablero_id = self.kanban_view.tablero_id if hasattr(self.kanban_view, 'tablero_id') else None
            if tablero_id:
                self.ver_kanban(tablero_id)
        else:
            self.ver_inicio(dark=self.is_dark)
    
    def ver_proyectos(self):
        if not self.proyectos_view:
            if self.is_dark:
                self.proyectos_view = ProyectosViewEmbeddedDark(self)
            else:
                self.proyectos_view = ProyectosViewEmbedded(self)
            self.proyectos_view.proyecto_seleccionado.connect(self.ver_tableros)
            self.proyectos_view.volver_clicked.connect(lambda: self.ver_inicio(self.is_dark))
            self.stack.addWidget(self.proyectos_view)
        
        self.proyectos_view.obtener_proyectos()
        self.stack.setCurrentWidget(self.proyectos_view)
    
    def ver_tableros(self, proyecto_id):
        if self.tableros_view:
            self.stack.removeWidget(self.tableros_view)
            self.tableros_view.deleteLater()
            self.tableros_view = None
        
        if self.is_dark:
            self.tableros_view = TablerosViewEmbeddedDark(proyecto_id, self)
        else:
            self.tableros_view = TablerosViewEmbedded(proyecto_id, self)
        
        self.tableros_view.tablero_seleccionado.connect(self.ver_kanban)
        self.tableros_view.volver_clicked.connect(lambda: self.ver_inicio(self.is_dark))
        self.stack.addWidget(self.tableros_view)
        self.stack.setCurrentWidget(self.tableros_view)
    
    def ver_kanban(self, tablero_id):
        if self.kanban_view:
            self.stack.removeWidget(self.kanban_view)
            self.kanban_view.deleteLater()
            self.kanban_view = None
        
        if self.is_dark:
            self.kanban_view = KanbanViewEmbeddedDark(tablero_id, self)
        else:
            self.kanban_view = KanbanViewEmbedded(tablero_id, self)
        
        self.kanban_view.volver_clicked.connect(self.regresar_a_tableros)
        self.stack.addWidget(self.kanban_view)
        self.stack.setCurrentWidget(self.kanban_view)
    
    def regresar_a_tableros(self):
        if self.tableros_view:
            self.stack.setCurrentWidget(self.tableros_view)


class ProyectosViewEmbedded(QtWidgets.QWidget):
    proyecto_seleccionado = QtCore.pyqtSignal(str)
    volver_clicked = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        from proyectos_view import ProyectosView
        
        self.vista = ProyectosView()
        self.vista.proyecto_seleccionado.connect(self.proyecto_seleccionado.emit)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.vista)
    
    def obtener_proyectos(self):
        if hasattr(self.vista, 'obtener_proyectos'):
            self.vista.obtener_proyectos()


class TablerosViewEmbedded(QtWidgets.QWidget):
    tablero_seleccionado = QtCore.pyqtSignal(str)
    volver_clicked = QtCore.pyqtSignal()
    
    def __init__(self, proyecto_id, parent=None):
        super().__init__(parent)
        from tableros_view import TablerosView
        
        self.proyecto_id = proyecto_id
        self.vista = TablerosView(proyecto_id)
        self.vista.tablero_seleccionado.connect(self.tablero_seleccionado.emit)
        self.vista.volver_clicked.connect(self.volver_clicked.emit)
        
        if hasattr(self.vista, 'btn_theme') and parent:
            try:
                self.vista.btn_theme.clicked.connect(parent.alternar_tema)
            except:
                pass
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.vista)


class KanbanViewEmbedded(QtWidgets.QWidget):
    volver_clicked = QtCore.pyqtSignal()
    
    def __init__(self, tablero_id, parent=None):
        super().__init__(parent)
        from kanban_view import KanbanView
        
        self.tablero_id = tablero_id
        self.vista = KanbanView(tablero_id)
        self.vista.volver_clicked.connect(self.volver_clicked.emit)
        
        if hasattr(self.vista, 'btn_theme') and parent:
            try:
                self.vista.btn_theme.clicked.connect(parent.alternar_tema)
            except:
                pass
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.vista)


class ProyectosViewEmbeddedDark(QtWidgets.QWidget):
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
    
    def obtener_proyectos(self):
        if hasattr(self.vista, 'obtener_proyectos'):
            self.vista.obtener_proyectos()


class TablerosViewEmbeddedDark(QtWidgets.QWidget):
    tablero_seleccionado = QtCore.pyqtSignal(str)
    volver_clicked = QtCore.pyqtSignal()
    
    def __init__(self, proyecto_id, parent=None):
        super().__init__(parent)
        from tableros_view_dark import TablerosViewDark
        
        self.proyecto_id = proyecto_id
        self.vista = TablerosViewDark(proyecto_id)
        self.vista.tablero_seleccionado.connect(self.tablero_seleccionado.emit)
        self.vista.volver_clicked.connect(self.volver_clicked.emit)
        
        if hasattr(self.vista, 'btn_theme') and parent:
            try:
                self.vista.btn_theme.clicked.connect(parent.alternar_tema)
            except:
                pass
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.vista)


class KanbanViewEmbeddedDark(QtWidgets.QWidget):
    volver_clicked = QtCore.pyqtSignal()
    
    def __init__(self, tablero_id, parent=None):
        super().__init__(parent)
        from kanban_view_dark import KanbanViewDark
        
        self.tablero_id = tablero_id
        self.vista = KanbanViewDark(tablero_id)
        self.vista.volver_clicked.connect(self.volver_clicked.emit)
        
        if hasattr(self.vista, 'btn_theme') and parent:
            try:
                self.vista.btn_theme.clicked.connect(parent.alternar_tema)
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

    def ver_login(self):
        self.login_win = LoginCommunityWindow()
        self.login_win.btn_login.clicked.connect(self._al_iniciar_sesion)
        self.login_win.show()

    def _al_iniciar_sesion(self):
        try:
            if self.login_win and self.login_win.validar_login():
                user_data = self.login_win.authenticated_user
                self.login_win.hide()
                self.ver_ventana_principal(user_data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(
                self.login_win,
                "Error",
                f"Error durante el login: {str(e)}"
            )

    def ver_ventana_principal(self, user_data=None):
        if not self.main_win:
            self.main_win = MainWindow()
            self.main_win.logout_requested.connect(self.cerrar_sesion)
        
        if user_data:
            self.main_win.establecer_datos_usuario(user_data)
        
        self.main_win.show()
    
    def cerrar_sesion(self):
        if self.main_win:
            self.main_win.hide()
        self.ver_login()

    def ejecutar(self):
        self.ver_login()
        sys.exit(self.app.exec_())


def main():
    controller = AppController()
    controller.ejecutar()


if __name__ == '__main__':
    main()
