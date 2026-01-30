import os
import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

# Importar el gestor de base de datos usando el mismo path que los managers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.base_datos.datos import db_manager


class LoginCommunityWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), '..', '.ui', 'login_community.ui')
        ui_path = os.path.abspath(ui_path)
        uic.loadUi(ui_path, self)
        
        # Variable para almacenar datos del usuario autenticado
        self.authenticated_user = None
        
        # Load logo image from interfaces/imagenes/logoCommunity.png if available
        try:
            img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'imagenes', 'logoCommunity.png'))
            if os.path.exists(img_path):
                pix = QPixmap(img_path)
                if not pix.isNull():
                    # Scale to label size while keeping aspect ratio
                    pix = pix.scaled(self.label_logo.width(), self.label_logo.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.label_logo.setPixmap(pix)
                    self.label_logo.setAlignment(Qt.AlignCenter)
        except Exception:
            pass
    
    def validate_login(self):
        """
        Valida las credenciales del usuario contra la base de datos
        
        Returns:
            bool: True si la autenticación es exitosa, False en caso contrario
        """
        username = self.input_username.text().strip()
        password = self.input_password.text()
        
        if not username or not password:
            QtWidgets.QMessageBox.warning(
                self,
                "Error de validación",
                "Por favor ingresa usuario y contraseña"
            )
            return False
        
        # Autenticar con la base de datos
        authenticated, user_data = db_manager.authenticate_user(username, password)
        
        if authenticated:
            self.authenticated_user = user_data
            return True
        else:
            QtWidgets.QMessageBox.critical(
                self,
                "Error de autenticación",
                "Usuario o contraseña incorrectos"
            )
            return False


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = LoginCommunityWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
