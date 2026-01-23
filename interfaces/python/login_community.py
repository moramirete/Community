import os
import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class LoginCommunityWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), '..', '.ui', 'login_community.ui')
        ui_path = os.path.abspath(ui_path)
        uic.loadUi(ui_path, self)
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


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = LoginCommunityWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
