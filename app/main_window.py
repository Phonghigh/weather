from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QSizePolicy, QFrame,
)
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QFont, QColor

from app import theme
from app.tabs.input_tab import InputTab
from app.tabs.simulation_tab import SimulationTab
from app.tabs.output_tab import OutputTab
from app.results_window import ResultsWindow


TABS = [
    ('input',      '⬚', 'Input',        'valid'),
    ('simulation', '◷', 'Simulation',   ''),
    ('output',     '▶', 'Output & Run', ''),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.resize(1280, 860)
        self.setMinimumSize(960, 600)

        self._current_tab = 'input'
        self._drag_pos = None
        self._run_state = 'idle'
        self._elapsed = 0
        self._elapsed_str = '00:00'
        self._results_window = None

        self._build()

        # Elapsed tick for status bar
        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self._tick_status)

    # ── Drag to move ──────────────────────────────────────────────────────────
    def _is_titlebar(self, pos):
        return self._titlebar.geometry().contains(pos)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton and self._is_titlebar(ev.pos()):
            self._drag_pos = ev.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, ev):
        if self._drag_pos and ev.buttons() == Qt.LeftButton:
            self.move(ev.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, ev):
        self._drag_pos = None

    # ── Build ─────────────────────────────────────────────────────────────────
    def _build(self):
        central = QWidget()
        central.setStyleSheet(f'background:{theme.WIN_BG};')
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._titlebar = self._build_titlebar()
        root.addWidget(self._titlebar)
        root.addWidget(self._build_menubar())
        root.addWidget(self._build_tabstrip())

        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f'background:{theme.WIN_BG};')
        root.addWidget(self._stack, stretch=1)

        root.addWidget(self._build_statusbar())

        # Build tabs
        self._input_tab = InputTab()
        self._input_tab.goto_simulation.connect(lambda: self._switch_tab('simulation'))
        self._stack.addWidget(self._input_tab)  # index 0

        self._sim_tab = SimulationTab()
        self._stack.addWidget(self._sim_tab)  # index 1

        self._output_tab = OutputTab()
        self._output_tab.run_state_changed.connect(self._on_run_state)
        self._output_tab.results_ready.connect(self._open_results)
        self._stack.addWidget(self._output_tab)  # index 2

        self._switch_tab('input')

    # ── Title bar ─────────────────────────────────────────────────────────────
    def _build_titlebar(self):
        bar = QFrame()
        bar.setFixedHeight(34)
        bar.setStyleSheet(f'background:{theme.TITLEBAR_BG};')

        row = QHBoxLayout(bar)
        row.setContentsMargins(12, 0, 12, 0)
        row.setSpacing(0)

        drop = QLabel('💧')
        drop.setStyleSheet('font-size:13px;color:#7fb2e0;')
        row.addWidget(drop)
        row.addSpacing(8)

        title = QLabel('eWM — eWater Warning Model')
        title.setStyleSheet('font-size:12.5px;font-weight:500;color:#cdd3da;')
        row.addWidget(title)
        row.addSpacing(8)

        filename = QLabel('— urban_flood_2026.ewm')
        filename.setStyleSheet(f'font-size:11.5px;color:#7a828c;')
        row.addWidget(filename)
        row.addStretch()

        for label, slot in [('—', self.showMinimized), ('⬜', self._toggle_max), ('✕', self.close)]:
            btn = QPushButton(label)
            btn.setFlat(True)
            btn.setFixedSize(24, 20)
            btn.setCursor(Qt.PointingHandCursor)
            if label == '✕':
                btn.setStyleSheet("""
                    QPushButton { color:#aeb6c0;font-size:15px;background:transparent;border:none; }
                    QPushButton:hover { color:#ff6b6b; }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton { color:#aeb6c0;background:transparent;border:none; }
                    QPushButton:hover { color:white; }
                """)
            btn.clicked.connect(slot)
            row.addWidget(btn)
            row.addSpacing(6)

        return bar

    def _toggle_max(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    # ── Menu bar ──────────────────────────────────────────────────────────────
    def _build_menubar(self):
        bar = QFrame()
        bar.setFixedHeight(30)
        bar.setStyleSheet(
            f'background:{theme.MENUBAR_BG};border-bottom:1px solid {theme.BORDER};'
        )

        row = QHBoxLayout(bar)
        row.setContentsMargins(6, 0, 8, 0)
        row.setSpacing(2)

        for name in ['Project', 'View', 'Settings', 'License', 'Help']:
            btn = QPushButton(name)
            btn.setFlat(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(22)
            btn.setStyleSheet(f"""
                QPushButton {{
                    font-size:12.5px;
                    padding:4px 10px;
                    border-radius:5px;
                    color:{theme.TEXT2};
                    background:transparent;
                    border:none;
                }}
                QPushButton:hover {{ background:#e7ebf1; }}
            """)
            row.addWidget(btn)

        row.addStretch()

        lic_lbl = QLabel('License')
        lic_lbl.setStyleSheet(f'font-size:11px;color:{theme.TEXT_MUTED};')
        row.addWidget(lic_lbl)
        row.addSpacing(10)

        lic_badge = QLabel('365 days')
        lic_badge.setStyleSheet(f"""
            font-size:11px;font-weight:600;color:#2e7d46;
            background:#e7f4ea;border:1px solid #c4e3cd;
            padding:2px 8px;border-radius:10px;
        """)
        row.addWidget(lic_badge)

        return bar

    # ── Tab strip ─────────────────────────────────────────────────────────────
    def _build_tabstrip(self):
        bar = QFrame()
        bar.setFixedHeight(46)
        bar.setStyleSheet(
            f'background:white;border-bottom:1px solid {theme.BORDER};'
        )

        row = QHBoxLayout(bar)
        row.setContentsMargins(14, 0, 14, 0)
        row.setSpacing(2)
        row.setAlignment(Qt.AlignBottom)

        self._tab_btns = {}
        for key, glyph, label, badge in TABS:
            btn = QPushButton()
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty('tabKey', key)

            inner = QHBoxLayout()
            inner.setSpacing(8)
            glyph_lbl = QLabel(glyph)
            glyph_lbl.setAlignment(Qt.AlignCenter)
            glyph_lbl.setFixedSize(18, 18)
            label_lbl = QLabel(label)
            inner.addWidget(glyph_lbl)
            inner.addWidget(label_lbl)
            if badge:
                badge_lbl = QLabel(badge)
                badge_lbl.setStyleSheet(f"""
                    font-size:10px;background:#e7f4ea;color:#2e7d46;
                    border:1px solid #c4e3cd;border-radius:10px;padding:0 6px;font-weight:600;
                """)
                inner.addWidget(badge_lbl)

            btn.setLayout(inner)
            btn.setFixedHeight(38)
            btn.clicked.connect(lambda checked=False, k=key: self._switch_tab(k))
            self._tab_btns[key] = btn
            row.addWidget(btn)

        row.addStretch()
        return bar

    def _update_tab_styles(self):
        for key, btn in self._tab_btns.items():
            active = key == self._current_tab
            if active:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        display:flex;align-items:center;gap:8px;
                        height:38px;padding:0 18px;
                        font-size:13.5px;font-weight:600;
                        background:{theme.WIN_BG};
                        color:{theme.ACCENT};
                        border:1px solid {theme.BORDER};
                        border-bottom:none;
                        border-radius:8px 8px 0 0;
                        position:relative;top:1px;
                        font-family:{theme.FONT};
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        height:38px;padding:0 18px;
                        font-size:13.5px;font-weight:600;
                        background:transparent;
                        color:{theme.TEXT_MUTED};
                        border:1px solid transparent;
                        border-bottom:none;
                        border-radius:8px 8px 0 0;
                        font-family:{theme.FONT};
                    }}
                    QPushButton:hover {{ color:{theme.TEXT2}; }}
                """)

    # ── Status bar ────────────────────────────────────────────────────────────
    def _build_statusbar(self):
        bar = QFrame()
        bar.setFixedHeight(26)
        bar.setStyleSheet(f'background:{theme.ACCENT2};')

        row = QHBoxLayout(bar)
        row.setContentsMargins(13, 0, 13, 0)
        row.setSpacing(0)

        self._status_dot = QLabel('●')
        self._status_dot.setStyleSheet(f'color:#6fd18a;font-size:9px;')
        self._status_text = QLabel('Ready')
        self._status_text.setStyleSheet('font-size:11.5px;color:#dce9f6;')

        row.addWidget(self._status_dot)
        row.addSpacing(6)
        row.addWidget(self._status_text)
        row.addSpacing(14)

        sep1 = QLabel('|')
        sep1.setStyleSheet('color:#dce9f6;opacity:0.4;font-size:11.5px;')
        row.addWidget(sep1)
        row.addSpacing(14)

        mapset = QLabel('Mapset: urban_flood_2026/PERMANENT')
        mapset.setStyleSheet(f'font-size:11.5px;color:#dce9f6;font-family:{theme.FONT_MONO};')
        row.addWidget(mapset)
        row.addStretch()

        self._status_right = QLabel('ITZI v25.8 · GRASS 8.4 · 00:00')
        self._status_right.setStyleSheet(
            f'font-size:11.5px;color:#dce9f6;font-family:{theme.FONT_MONO};'
        )
        row.addWidget(self._status_right)

        return bar

    # ── Switching ─────────────────────────────────────────────────────────────
    def _switch_tab(self, key):
        self._current_tab = key
        idx = {'input': 0, 'simulation': 1, 'output': 2}[key]
        self._stack.setCurrentIndex(idx)
        self._update_tab_styles()

    # ── Run state updates ──────────────────────────────────────────────────────
    def _on_run_state(self, state):
        self._run_state = state
        if state == 'running':
            self._status_dot.setStyleSheet('color:#ffcf66;font-size:9px;')
            self._status_text.setText('Running simulation…')
            self._elapsed = 0
            self._status_timer.start(1000)
        elif state == 'done':
            self._status_dot.setStyleSheet('color:#6fd18a;font-size:9px;')
            self._status_text.setText('Completed — 4 nodes flooded')
            self._status_timer.stop()
        else:
            self._status_dot.setStyleSheet('color:#6fd18a;font-size:9px;')
            self._status_text.setText('Ready')
            self._status_timer.stop()

    def _tick_status(self):
        self._elapsed += 1
        m = self._elapsed // 60
        s = self._elapsed % 60
        self._elapsed_str = f'{m:02d}:{s:02d}'
        self._status_right.setText(f'ITZI v25.8 · GRASS 8.4 · {self._elapsed_str}')

    # ── Results window ─────────────────────────────────────────────────────────
    def _open_results(self):
        if self._results_window is None:
            self._results_window = ResultsWindow(self)
        self._results_window.open_over(self.geometry())

    def logout(self):
        self.close()
