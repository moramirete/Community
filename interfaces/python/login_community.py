import os
import sys
from PyQt5 import QtWidgets, uic


class LoginCommunityWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), '..', '.ui', 'login_community.ui')
        ui_path = os.path.abspath(ui_path)
        uic.loadUi(ui_path, self)


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = LoginCommunityWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
