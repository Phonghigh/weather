from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QComboBox,
    QPlainTextEdit, QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from app import theme


def _card(parent=None):
    f = QFrame(parent)
    f.setStyleSheet(f"""
        QFrame {{
            background:{theme.SURFACE};
            border:1px solid {theme.BORDER};
            border-radius:9px;
        }}
    """)
    return f


def _section_label(text):
    lbl = QLabel(text.upper())
    lbl.setStyleSheet(
        f'font-size:11px;font-weight:700;letter-spacing:0.8px;color:{theme.TEXT_MUTED};'
    )
    return lbl


def _field_label(text):
    lbl = QLabel(text)
    lbl.setStyleSheet(f'font-size:12px;font-weight:500;color:{theme.TEXT3};')
    return lbl


def _ro_field(text):
    lbl = QLabel(text)
    lbl.setFixedHeight(theme.RH)
    lbl.setStyleSheet(f"""
        border:1.5px solid #e1e6ec;
        border-radius:6px;
        padding:0 11px;
        font-size:12.5px;
        color:{theme.TEXT2};
        background:#f6f8fa;
    """)
    return lbl


class SimulationTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ini_edit_mode = False
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(14)

        left = QVBoxLayout()
        left.setSpacing(13)
        left.addWidget(self._build_period_card())
        left.addWidget(self._build_params_card())
        left.addStretch()

        left_w = QWidget()
        left_w.setLayout(left)

        right = self._build_ini_card()

        root.addWidget(left_w)
        root.addWidget(right)

    # ── Simulation period card ─────────────────────────────────────────────────
    def _build_period_card(self):
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(0)

        layout.addWidget(_section_label('Simulation Period'))
        layout.addSpacing(14)

        grid = QGridLayout()
        grid.setSpacing(13)

        self._fields = {}
        field_defs = [
            ('startDate', 'Start date',  '2026-06-16', 0, 0),
            ('startTime', 'Start time',  '15:00:00',   0, 1),
            ('endDate',   'End date',    '2026-06-16', 1, 0),
            ('endTime',   'End time',    '21:00:00',   1, 1),
        ]
        for key, label, default, row, col in field_defs:
            col_w = QVBoxLayout()
            col_w.setSpacing(6)
            col_w.addWidget(_field_label(label))
            edit = QLineEdit(default)
            edit.setFixedHeight(theme.RH)
            edit.setStyleSheet(theme.input_qss())
            edit.textChanged.connect(self._update_computed)
            self._fields[key] = edit
            col_w.addWidget(edit)
            grid.addLayout(col_w, row, col)

        layout.addLayout(grid)
        layout.addSpacing(14)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet('background:#eef1f5;')
        layout.addWidget(sep)
        layout.addSpacing(13)

        # Duration + Timestep row
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(8)
        dur_lbl = QLabel('Duration')
        dur_lbl.setStyleSheet(f'font-size:12px;color:{theme.TEXT3};')
        bottom_row.addWidget(dur_lbl)

        self._duration_lbl = QLabel('6.0 hours')
        self._duration_lbl.setStyleSheet(f"""
            font-size:13px;font-weight:700;color:{theme.ACCENT};
            background:#eaf2fa;padding:2px 10px;border-radius:6px;
        """)
        bottom_row.addWidget(self._duration_lbl)
        bottom_row.addSpacing(14)

        ts_lbl = QLabel('Timestep')
        ts_lbl.setStyleSheet(f'font-size:12px;color:{theme.TEXT3};')
        bottom_row.addWidget(ts_lbl)

        self._timestep_combo = QComboBox()
        self._timestep_combo.addItems(['10 s', '30 s', '60 s', '120 s'])
        self._timestep_combo.setCurrentIndex(2)  # 60s default
        self._timestep_combo.setFixedHeight(30)
        self._timestep_combo.setStyleSheet(f"""
            QComboBox {{
                border:1.5px solid {theme.BORDER_INPUT};
                border-radius:6px;
                padding:0 8px;
                font-family:{theme.FONT};
                font-size:12.5px;
                background:white;
                color:{theme.TEXT};
            }}
            QComboBox::drop-down {{ border:none; }}
            QComboBox QAbstractItemView {{
                border:1px solid {theme.BORDER};
                border-radius:4px;
                font-size:12.5px;
            }}
        """)
        self._timestep_combo.currentIndexChanged.connect(self._update_ini)
        bottom_row.addWidget(self._timestep_combo)
        bottom_row.addStretch()

        layout.addLayout(bottom_row)
        layout.addSpacing(12)

        # Courant hint
        courant_row = QHBoxLayout()
        courant_row.setSpacing(7)
        dot = QLabel('●')
        dot.setStyleSheet(f'color:{theme.COLOR_OK};font-size:10px;')
        courant_lbl = QLabel('Estimated Courant number ≈ 0.31 — stable')
        courant_lbl.setStyleSheet(f'font-size:11.5px;color:{theme.TEXT_MUTED};')
        courant_row.addWidget(dot)
        courant_row.addWidget(courant_lbl)
        courant_row.addStretch()
        layout.addLayout(courant_row)

        return card

    # ── Default parameters card ───────────────────────────────────────────────
    def _build_params_card(self):
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(0)

        layout.addWidget(_section_label('Default Parameters'))
        layout.addSpacing(14)

        grid = QGridLayout()
        grid.setSpacing(12)

        params = [
            ('Friction model', 'Manning'),
            ('Manning n',      '0.035'),
            ('Infiltration',   'Green-Ampt'),
            ('Max ponding',    '0.10 m'),
        ]
        for i, (label, value) in enumerate(params):
            row, col = i // 2, i % 2
            col_w = QVBoxLayout()
            col_w.setSpacing(6)
            col_w.addWidget(_field_label(label))
            col_w.addWidget(_ro_field(value))
            grid.addLayout(col_w, row, col)

        layout.addLayout(grid)
        layout.addSpacing(14)

        apply_btn = QPushButton('Apply Default Settings')
        apply_btn.setFixedHeight(36)
        apply_btn.setCursor(Qt.PointingHandCursor)
        apply_btn.setStyleSheet(theme.ghost_btn_qss())
        layout.addWidget(apply_btn)

        return card

    # ── ITZI .ini preview card ────────────────────────────────────────────────
    def _build_ini_card(self):
        card = _card()
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(0)

        header = QHBoxLayout()
        header.addWidget(_section_label('ITZI .ini Preview'))

        self._ini_toggle = QPushButton('✎ Edit manually')
        self._ini_toggle.setFlat(True)
        self._ini_toggle.setCursor(Qt.PointingHandCursor)
        self._ini_toggle.setStyleSheet(f"""
            QPushButton {{
                color:{theme.ACCENT};
                font-size:11.5px;
                font-weight:600;
                border:none;
                background:transparent;
                padding:0;
            }}
            QPushButton:hover {{ text-decoration:underline; }}
        """)
        self._ini_toggle.clicked.connect(self._toggle_ini_edit)
        header.addStretch()
        header.addWidget(self._ini_toggle)
        layout.addLayout(header)
        layout.addSpacing(12)

        self._ini_edit = QPlainTextEdit()
        self._ini_edit.setReadOnly(True)
        self._ini_edit.setFont(QFont('Ubuntu Mono', 12))
        self._ini_edit.setStyleSheet(f"""
            QPlainTextEdit {{
                background:{theme.SURFACE_CODE};
                border-radius:8px;
                padding:14px 16px;
                font-family:{theme.FONT_MONO};
                font-size:12px;
                color:#c9d6e5;
                border:none;
                line-height:1.65;
            }}
        """)
        self._ini_edit.setMinimumHeight(330)
        layout.addWidget(self._ini_edit, stretch=1)

        layout.addSpacing(10)
        footer = QLabel('Auto-generated from the form. Generated config is saved with the run.')
        footer.setStyleSheet(f'font-size:11px;color:{theme.TEXT_FAINT};')
        footer.setWordWrap(True)
        layout.addWidget(footer)

        self._update_ini()
        return card

    # ── Computed fields ───────────────────────────────────────────────────────
    def _update_computed(self):
        start_t = self._fields['startTime'].text()
        end_t   = self._fields['endTime'].text()
        hours   = self._calc_duration(start_t, end_t)
        self._duration_lbl.setText(f'{hours} hours')
        self._update_ini()

    def _calc_duration(self, start, end):
        try:
            sh, sm = int(start.split(':')[0]), int(start.split(':')[1])
            eh, em = int(end.split(':')[0]), int(end.split(':')[1])
            mins = (eh * 60 + em) - (sh * 60 + sm)
            if mins <= 0:
                mins += 24 * 60
            hours = round(mins / 60, 1)
            return hours
        except Exception:
            return '?'

    def _update_ini(self):
        f = self._fields
        ts_vals = [10, 30, 60, 120]
        ts = ts_vals[self._timestep_combo.currentIndex()]
        start = f'{f["startDate"].text()} {f["startTime"].text()}'
        end   = f'{f["endDate"].text()} {f["endTime"].text()}'
        text = (
            f'[time]\n'
            f'start_time = {start}\n'
            f'end_time   = {end}\n'
            f'record_step = {ts}\n'
            f'\n'
            f'[input]\n'
            f'dem  = dem_5m@PERMANENT\n'
            f'friction = n_manning\n'
            f'rain = rain_6h@PERMANENT\n'
            f'\n'
            f'[output]\n'
            f'prefix = flood_run1\n'
            f'values = depth, velocity, froude\n'
            f'\n'
            f'[statistics]\n'
            f'stats_file = flood_run1_stats.csv\n'
            f'\n'
            f'[options]\n'
            f'theta = 0.7\n'
            f'hmin  = 0.005\n'
            f'swmm_inp = hcmc_d3.inp'
        )
        self._ini_edit.setPlainText(text)

    def _toggle_ini_edit(self):
        self._ini_edit_mode = not self._ini_edit_mode
        self._ini_edit.setReadOnly(not self._ini_edit_mode)
        if self._ini_edit_mode:
            self._ini_toggle.setText('● editing — click to lock')
            self._ini_edit.setStyleSheet(self._ini_edit.styleSheet().replace(
                theme.SURFACE_CODE, '#1a2232'
            ))
        else:
            self._ini_toggle.setText('✎ Edit manually')
            self._ini_edit.setStyleSheet(self._ini_edit.styleSheet().replace(
                '#1a2232', theme.SURFACE_CODE
            ))
