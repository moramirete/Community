import os
import sys
from PyQt5 import QtWidgets, QtCore, QtGui, uic


class HomeCommunityDarkWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), '..', '.ui', 'home_community_dark.ui')
        ui_path = os.path.abspath(ui_path)
        uic.loadUi(ui_path, self)
        self._wire_star_labels()

    def _wire_star_labels(self):
        for i in range(1, 10):
            name = f'lbl_star_{i}'
            lbl = getattr(self, name, None)
            if lbl is None:
                continue
            lbl.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            if not hasattr(lbl, '_fav'):
                lbl._fav = False
            if not lbl.text().strip():
                lbl.setText('☆')
            def make_handler(l):
                def handler(event):
                    self._toggle_star(l)
                return handler
            lbl.mousePressEvent = make_handler(lbl)

    def _toggle_star(self, lbl):
        lbl._fav = not getattr(lbl, '_fav', False)
        if lbl._fav:
            lbl.setText('★')
            lbl.setStyleSheet('color: #FFD700;')
        else:
            lbl.setText('☆')
            lbl.setStyleSheet('color: #E5E5E5;')


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = HomeCommunityDarkWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
