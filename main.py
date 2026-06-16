import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from app.login_window import LoginWindow
from app.main_window import MainWindow


def main():
    # Must be set before QApplication on some platforms
    try:
        from PySide6.QtWebEngineCore import QWebEngineUrlScheme
    except ImportError:
        pass

    # On Wayland, use XCB (X11/XWayland) so frameless windows render correctly
    import os
    if 'WAYLAND_DISPLAY' in os.environ and 'QT_QPA_PLATFORM' not in os.environ:
        os.environ['QT_QPA_PLATFORM'] = 'xcb'

    app = QApplication(sys.argv)
    app.setApplicationName('eWM')
    app.setOrganizationName('eWater')

    font = QFont('Ubuntu', 13)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)

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
