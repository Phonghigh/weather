ACCENT = '#1565a7'
ACCENT2 = '#0f4f82'
COLOR_OK = '#3f9d52'
COLOR_WARN = '#e8a33d'
COLOR_ERR = '#d64545'
COLOR_OUTFALL = '#5b6772'

WIN_BG = '#eceff2'
TITLEBAR_BG = '#2b2f36'
MENUBAR_BG = '#f7f8fa'
BORDER = '#dfe3e9'
BORDER_INPUT = '#c3cad3'
TEXT = '#1f2933'
TEXT2 = '#39424d'
TEXT3 = '#5b6772'
TEXT_MUTED = '#8893a0'
TEXT_FAINT = '#aab4c0'

SURFACE = '#fff'
SURFACE_DIM = '#fbfcfd'
SURFACE_CODE = '#1c2430'
SURFACE_LOG = '#10161f'

FONT = 'Ubuntu, system-ui, sans-serif'
FONT_MONO = '"Ubuntu Mono", "Courier New", monospace'

RH = 31  # row height px
FS = 13  # base font size px


def card_style(padding='16px 18px'):
    return (
        f'background:{SURFACE};border:1px solid {BORDER};border-radius:9px;padding:{padding};'
    )


def ghost_btn_qss():
    return f"""
QPushButton {{
    background:{SURFACE};
    border:1.5px solid {BORDER_INPUT};
    border-radius:6px;
    padding:0 14px;
    font-size:12px;
    font-weight:600;
    font-family:{FONT};
    color:{TEXT2};
    height:{RH}px;
}}
QPushButton:hover {{ background:#eef2f7; }}
QPushButton:pressed {{ background:#e5eaf2; }}
"""


def accent_btn_qss(height=42):
    return f"""
QPushButton {{
    background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {ACCENT},stop:1 {ACCENT2});
    color:white;
    border:none;
    border-radius:7px;
    font-size:14px;
    font-weight:600;
    font-family:{FONT};
    height:{height}px;
}}
QPushButton:hover {{ background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #1e72bc,stop:1 #1a5e94); }}
QPushButton:pressed {{ background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {ACCENT2},stop:1 #0a3d65); }}
"""


def green_btn_qss(height=46):
    return f"""
QPushButton {{
    background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #2e7d46,stop:1 #1f6336);
    color:white;
    border:none;
    border-radius:8px;
    font-size:14px;
    font-weight:700;
    font-family:{FONT};
    height:{height}px;
}}
QPushButton:hover {{ background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #368f50,stop:1 #26713f); }}
QPushButton:disabled {{ background:#9aa6b2; }}
"""


def input_qss():
    return f"""
QLineEdit {{
    border:1.5px solid {BORDER_INPUT};
    border-radius:6px;
    padding:0 11px;
    font-size:13px;
    font-family:{FONT};
    color:{TEXT};
    background:{SURFACE};
    height:{RH}px;
}}
QLineEdit:focus {{
    border-color:{ACCENT};
}}
"""


def scrollbar_qss():
    return """
QScrollBar:vertical {
    width:11px;
    background:transparent;
}
QScrollBar::handle:vertical {
    background:#c2cad4;
    border-radius:5px;
    border:2px solid white;
    min-height:20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
QScrollBar:horizontal {
    height:11px;
    background:transparent;
}
QScrollBar::handle:horizontal {
    background:#c2cad4;
    border-radius:5px;
    border:2px solid white;
    min-width:20px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width:0; }
"""
