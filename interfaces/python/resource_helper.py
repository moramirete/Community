import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # En desarrollo, asumimos que este archivo está en interfaces/python
        # La raíz del proyecto está dos niveles arriba
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

    return os.path.join(base_path, relative_path)
