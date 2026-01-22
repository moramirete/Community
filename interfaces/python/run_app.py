import sys
from PyQt5 import QtWidgets

from login_community import LoginCommunityWindow
from home_community import HomeCommunityWindow
from home_community_dark import HomeCommunityDarkWindow


class AppController:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.login_win = None
        self.home_win = None
        self.is_dark = False

    def show_login(self):
        self.login_win = LoginCommunityWindow()
        self.login_win.btn_login.clicked.connect(self._on_login)
        self.login_win.show()

    def _on_login(self):
        # Simple flow: hide login, show light home
        try:
            if self.login_win:
                self.login_win.hide()
            self.show_home(dark=False)
        except Exception as e:
            import traceback
            traceback.print_exc()

    def show_home(self, dark=False):
        self.is_dark = dark
        if self.home_win:
            try:
                self.home_win.close()
            except Exception:
                pass
        if dark:
            self.home_win = HomeCommunityDarkWindow()
        else:
            self.home_win = HomeCommunityWindow()

        # Connect theme toggle
        try:
            self.home_win.btn_theme.clicked.connect(self.toggle_theme)
        except Exception:
            pass

        self.home_win.show()

    def toggle_theme(self):
        # Toggle between light and dark home
        self.show_home(dark=not self.is_dark)

    def run(self):
        self.show_login()
        sys.exit(self.app.exec_())


def main():
    controller = AppController()
    controller.run()


if __name__ == '__main__':
    main()
