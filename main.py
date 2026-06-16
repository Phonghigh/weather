import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtCore import Qt

from app.login_window import LoginWindow
from app.main_window import MainWindow


def main():
    # Enable WebEngine before QApplication on some platforms
    try:
        from PySide6.QtWebEngineCore import QWebEngineUrlScheme
    except ImportError:
        pass

    app = QApplication(sys.argv)
    app.setApplicationName('eWM')
    app.setOrganizationName('eWater')

    # Use Ubuntu font if available (pre-installed on Ubuntu systems)
    font = QFont('Ubuntu', 13)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)

    # High-DPI
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    login = LoginWindow()
    main_win = None

    def on_login():
        nonlocal main_win
        main_win = MainWindow()
        main_win.show()

    login.login_accepted.connect(on_login)
    login.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
