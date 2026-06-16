from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QGraphicsDropShadowEffect, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import (
    QPainter, QRadialGradient, QColor, QFont, QFontMetrics,
    QPainterPath, QLinearGradient, QPen,
)
from app import theme


class LoginWindow(QDialog):
    login_accepted = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(1100, 700)
        self.resize(1280, 860)

        self._drag_pos = None
        self._build_ui()

    # ── drag to move ──────────────────────────────────────────────────────────
    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            self._drag_pos = ev.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, ev):
        if self._drag_pos and ev.buttons() == Qt.LeftButton:
            self.move(ev.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, ev):
        self._drag_pos = None

    # ── background painting ───────────────────────────────────────────────────
    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        # Radial gradient matching prototype: #1f5f97 → #15466f → #0c2a45
        grad = QRadialGradient(rect.width() * 0.70, rect.height() * 0.10,
                               max(rect.width(), rect.height()) * 1.2)
        grad.setColorAt(0.0, QColor('#1f5f97'))
        grad.setColorAt(0.38, QColor('#15466f'))
        grad.setColorAt(1.0, QColor('#0c2a45'))
        p.fillRect(rect, grad)

        # Decorative topo lines
        pen = QPen(QColor(191, 224, 255, 41), 1.2)
        p.setPen(pen)
        w, h = rect.width(), rect.height()

        def wave(y_frac, offset, amp):
            y = h * y_frac
            path = QPainterPath()
            path.moveTo(-50, y)
            path.cubicTo(w * 0.25 + offset, y - amp,
                         w * 0.5, y + amp * 1.1,
                         w + 50, y + offset * 0.3)
            p.drawPath(path)

        for yf, off, amp in [
            (0.30, -12, 18), (0.37, 10, 20), (0.45, -8, 15),
            (0.59, 14, 22), (0.68, -10, 18), (0.76, 12, 16),
        ]:
            wave(yf, off, amp)

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addStretch()

        row = QHBoxLayout()
        row.addStretch()

        card = QFrame()
        card.setFixedWidth(392)
        card.setObjectName('loginCard')
        card.setStyleSheet("""
            QFrame#loginCard {
                background: white;
                border-radius: 12px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(80)
        shadow.setOffset(0, 30)
        shadow.setColor(QColor(5, 20, 40, 128))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 38, 40, 26)
        card_layout.setSpacing(0)

        # Logo + title
        logo_row = QVBoxLayout()
        logo_row.setSpacing(4)
        logo_row.setAlignment(Qt.AlignCenter)

        logo_label = QLabel()
        logo_label.setFixedSize(62, 62)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet(f"""
            background:qlineargradient(x1:0.2,y1:0,x2:0.8,y2:1,
                stop:0 {theme.ACCENT},stop:1 {theme.ACCENT2});
            border-radius:15px;
        """)
        logo_label.setText('💧')
        logo_label.setFont(QFont('Ubuntu', 28))

        title_lbl = QLabel('eWM')
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setFont(QFont('Ubuntu', 24, QFont.Bold))
        title_lbl.setStyleSheet('color:#1f2933;margin-top:10px;letter-spacing:-0.5px;')

        sub1 = QLabel('eWater Warning Model')
        sub1.setAlignment(Qt.AlignCenter)
        sub1.setStyleSheet('color:#5b6772;font-size:12px;')

        sub2 = QLabel('Urban Flood Simulation Platform')
        sub2.setAlignment(Qt.AlignCenter)
        sub2.setStyleSheet('color:#8893a0;font-size:11px;letter-spacing:0.3px;')

        logo_row.addWidget(logo_label, alignment=Qt.AlignCenter)
        logo_row.addWidget(title_lbl)
        logo_row.addWidget(sub1)
        logo_row.addWidget(sub2)

        logo_container = QFrame()
        logo_container.setLayout(logo_row)
        logo_container.setContentsMargins(0, 0, 0, 26)
        card_layout.addWidget(logo_container)

        # Password label
        pw_label = QLabel('Password')
        pw_label.setStyleSheet('font-size:11px;font-weight:600;color:#5b6772;')
        card_layout.addWidget(pw_label)
        card_layout.addSpacing(6)

        # Password input
        self._pw_edit = QLineEdit()
        self._pw_edit.setEchoMode(QLineEdit.Password)
        self._pw_edit.setPlaceholderText('Enter password')
        self._pw_edit.setFixedHeight(40)
        self._pw_edit.setStyleSheet(f"""
            QLineEdit {{
                border:1.5px solid #c3cad3;
                border-radius:7px;
                padding:0 12px;
                font-size:14px;
                font-family:{theme.FONT};
                color:#1f2933;
                background:white;
            }}
            QLineEdit:focus {{
                border-color:{theme.ACCENT};
                background:white;
            }}
        """)
        self._pw_edit.returnPressed.connect(self._on_login)
        card_layout.addWidget(self._pw_edit)
        card_layout.addSpacing(4)

        # Error label
        self._err_label = QLabel('')
        self._err_label.setStyleSheet(f'color:{theme.COLOR_ERR};font-size:11px;')
        self._err_label.setVisible(False)
        card_layout.addWidget(self._err_label)
        card_layout.addSpacing(12)

        # Login button
        login_btn = QPushButton('Login')
        login_btn.setFixedHeight(42)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setStyleSheet(f"""
            QPushButton {{
                background:qlineargradient(x1:0.15,y1:0,x2:0.85,y2:1,
                    stop:0 {theme.ACCENT},stop:1 {theme.ACCENT2});
                color:white;
                border:none;
                border-radius:7px;
                font-size:14px;
                font-weight:600;
                font-family:{theme.FONT};
            }}
            QPushButton:hover {{
                background:qlineargradient(x1:0.15,y1:0,x2:0.85,y2:1,
                    stop:0 #1e72bc,stop:1 #1a5e94);
            }}
            QPushButton:pressed {{ padding-top:1px; }}
        """)
        login_btn.clicked.connect(self._on_login)
        card_layout.addWidget(login_btn)

        # Divider
        card_layout.addSpacing(22)
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet('background:#e6eaef;')
        card_layout.addWidget(divider)
        card_layout.addSpacing(12)

        # License row
        lic_row = QHBoxLayout()
        dot = QLabel('●')
        dot.setStyleSheet(f'color:{theme.COLOR_OK};font-size:9px;')
        lic_text = QLabel('License valid until 2027-06-16')
        lic_text.setStyleSheet('color:#8893a0;font-size:11px;')
        ver = QLabel('v1.0.0')
        ver.setStyleSheet('color:#8893a0;font-size:11px;')
        lic_row.addWidget(dot)
        lic_row.addWidget(lic_text)
        lic_row.addStretch()
        lic_row.addWidget(ver)
        card_layout.addLayout(lic_row)
        card_layout.addSpacing(8)

        # Demo hint
        hint = QLabel('Demo — any password unlocks the prototype')
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet('color:#aab4c0;font-size:10px;')
        card_layout.addWidget(hint)

        row.addWidget(card)
        row.addStretch()
        outer.addLayout(row)
        outer.addStretch()

    def _on_login(self):
        pw = self._pw_edit.text().strip()
        if not pw:
            self._err_label.setText('Please enter a password.')
            self._err_label.setVisible(True)
            return
        self._err_label.setVisible(False)
        self.login_accepted.emit()
        self.accept()
