from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QScrollArea,
    QSizePolicy, QFileDialog,
)
from PySide6.QtCore import Qt, Signal
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


def _path_display(text=''):
    lbl = QLabel(text)
    lbl.setFixedHeight(theme.RH)
    lbl.setStyleSheet(f"""
        border:1.5px solid {theme.BORDER_INPUT};
        border-radius:6px;
        padding:0 11px;
        font-family:{theme.FONT_MONO};
        font-size:12px;
        color:{theme.TEXT2};
        background:{theme.SURFACE_DIM};
    """)
    lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    return lbl


def _browse_btn(text='Browse…'):
    btn = QPushButton(text)
    btn.setFixedHeight(theme.RH)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet(theme.ghost_btn_qss())
    return btn


def _stat_chip(value, unit=''):
    lbl = QLabel()
    lbl.setText(f'{value} <span style="color:{theme.TEXT_MUTED};font-weight:400">{unit}</span>')
    lbl.setTextFormat(Qt.RichText)
    lbl.setStyleSheet(f"""
        background:#f3f6f9;
        border:1px solid #e3e8ee;
        border-radius:6px;
        padding:5px 11px;
        font-size:13px;
        font-weight:700;
        color:{theme.TEXT};
    """)
    return lbl


def _validation_dot(color):
    dot = QLabel()
    dot.setFixedSize(20, 20)
    dot.setAlignment(Qt.AlignCenter)
    dot.setStyleSheet(f"""
        border-radius:10px;
        background:{color};
        font-size:11px;
        font-weight:700;
        color:white;
    """)
    dot.setText('✓')
    return dot


class InputTab(QWidget):
    goto_simulation = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._raster_imported = True
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(14)

        # ── left column ──────────────────────────────────────────────────────
        left = QVBoxLayout()
        left.setSpacing(13)
        left.addWidget(self._build_swmm_card())
        left.addWidget(self._build_grass_card())
        left.addWidget(self._build_raster_card())
        left.addStretch()

        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ── right column: validation ──────────────────────────────────────────
        right = self._build_validation_panel()
        right.setFixedWidth(380)
        right.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        root.addWidget(left_widget)
        root.addWidget(right, alignment=Qt.AlignTop)

    # ── SWMM card ─────────────────────────────────────────────────────────────
    def _build_swmm_card(self):
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(0)

        layout.addWidget(_section_label('SWMM Drainage Model'))
        layout.addSpacing(13)

        layout.addWidget(_field_label('Input file (.inp)'))
        layout.addSpacing(6)

        row = QHBoxLayout()
        self._swmm_path = _path_display('/data/hcmc/hcmc_d3.inp')
        btn = _browse_btn()
        btn.clicked.connect(self._browse_swmm)
        row.addWidget(self._swmm_path)
        row.addSpacing(8)
        row.addWidget(btn)
        layout.addLayout(row)
        layout.addSpacing(13)

        chips = QHBoxLayout()
        chips.setSpacing(9)
        chips.addWidget(_stat_chip('147', 'nodes'))
        chips.addWidget(_stat_chip('189', 'links'))
        chips.addWidget(_stat_chip('52', 'subcatch.'))
        chips.addWidget(_stat_chip('SWMM', '5.2'))
        chips.addStretch()
        layout.addLayout(chips)

        return card

    # ── GRASS card ────────────────────────────────────────────────────────────
    def _build_grass_card(self):
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(0)

        layout.addWidget(_section_label('GRASS GIS Mapset'))
        layout.addSpacing(13)

        grid = QGridLayout()
        grid.setSpacing(11)

        loc_lbl = _field_label('Location')
        self._grass_location = _path_display('urban_flood_2026')
        self._grass_location.setStyleSheet(
            self._grass_location.styleSheet() +
            'font-family:Ubuntu,sans-serif;font-size:12.5px;'
        )
        ms_lbl = _field_label('Mapset')
        self._grass_mapset = _path_display('PERMANENT')
        self._grass_mapset.setStyleSheet(
            self._grass_mapset.styleSheet() +
            'font-family:Ubuntu,sans-serif;font-size:12.5px;'
        )
        grid.addWidget(loc_lbl, 0, 0)
        grid.addWidget(ms_lbl, 0, 1)
        grid.addWidget(self._grass_location, 1, 0)
        grid.addWidget(self._grass_mapset, 1, 1)
        layout.addLayout(grid)
        layout.addSpacing(12)

        btns = QHBoxLayout()
        btns.setSpacing(8)
        btns.addWidget(_browse_btn('Create New…'))
        btns.addWidget(_browse_btn('Open Existing…'))
        spacer_btn = _browse_btn('Open GRASS GUI ↗')
        btns.addStretch()
        btns.addWidget(spacer_btn)
        layout.addLayout(btns)

        return card

    # ── Raster card ───────────────────────────────────────────────────────────
    def _build_raster_card(self):
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(0)

        layout.addWidget(_section_label('Raster Data'))
        layout.addSpacing(13)

        for label_text, default_path in [
            ('DEM (terrain)', 'dem_5m.tif'),
            ('Rainfall (6-hour event)', 'rain_6h.tif'),
        ]:
            layout.addWidget(_field_label(label_text))
            layout.addSpacing(6)
            row = QHBoxLayout()
            path_lbl = _path_display(default_path)
            btn = _browse_btn()
            row.addWidget(path_lbl)
            row.addSpacing(8)
            row.addWidget(btn)
            layout.addLayout(row)
            layout.addSpacing(10)

        # Import button
        self._import_btn = QPushButton('✓ Imported to GRASS')
        self._import_btn.setFixedHeight(36)
        self._import_btn.setCursor(Qt.PointingHandCursor)
        self._import_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._update_import_btn()
        self._import_btn.clicked.connect(self._on_import)
        layout.addWidget(self._import_btn)

        return card

    def _update_import_btn(self):
        if self._raster_imported:
            self._import_btn.setText('✓ Imported to GRASS')
            self._import_btn.setStyleSheet(f"""
                QPushButton {{
                    background:#3f9d52;
                    color:white;
                    border:none;
                    border-radius:7px;
                    font-size:13px;
                    font-weight:600;
                    font-family:{theme.FONT};
                }}
                QPushButton:hover {{ background:#2e8040; }}
            """)
        else:
            self._import_btn.setText('Import to GRASS')
            self._import_btn.setStyleSheet(f"""
                QPushButton {{
                    background:{theme.ACCENT};
                    color:white;
                    border:none;
                    border-radius:7px;
                    font-size:13px;
                    font-weight:600;
                    font-family:{theme.FONT};
                }}
                QPushButton:hover {{ background:{theme.ACCENT2}; }}
            """)

    # ── Validation panel ──────────────────────────────────────────────────────
    def _build_validation_panel(self):
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(0)

        layout.addWidget(_section_label('Validation Status'))
        layout.addSpacing(14)

        items = [
            (theme.COLOR_OK, 'SWMM model valid',
             '147 nodes · 189 links · 52 subcatchments · SWMM 5.2'),
            (theme.COLOR_OK, 'Raster imported',
             'dem_5m.tif · 5 m × 5 m · extent 10.5 × 8.2 km · VN-2000'),
            (theme.COLOR_OK, 'Rainfall loaded',
             'rain_6h.tif · 6-hour design storm · 24 steps'),
            (theme.COLOR_OK, 'CRS match OK',
             'All SWMM nodes fall within the raster extent'),
        ]

        for color, title, detail in items:
            item_row = QHBoxLayout()
            item_row.setSpacing(11)
            item_row.setAlignment(Qt.AlignTop)

            dot = _validation_dot(color)
            dot.setAlignment(Qt.AlignCenter)

            text_col = QVBoxLayout()
            text_col.setSpacing(2)
            title_lbl = QLabel(title)
            title_lbl.setStyleSheet(
                f'font-size:13px;font-weight:600;color:{theme.TEXT};'
            )
            detail_lbl = QLabel(detail)
            detail_lbl.setStyleSheet(
                f'font-size:11.5px;color:{theme.TEXT_MUTED};line-height:1.5;'
            )
            detail_lbl.setWordWrap(True)
            text_col.addWidget(title_lbl)
            text_col.addWidget(detail_lbl)

            item_row.addWidget(dot, alignment=Qt.AlignTop)
            item_row.addLayout(text_col)
            layout.addLayout(item_row)

            sep = QFrame()
            sep.setFixedHeight(1)
            sep.setStyleSheet('background:#eef1f5;')
            layout.addWidget(sep)

        layout.addSpacing(15)

        # Ready banner
        banner = QFrame()
        banner.setStyleSheet(f"""
            QFrame {{
                background:#e9f5ec;
                border:1px solid #c4e3cd;
                border-radius:8px;
            }}
        """)
        banner_row = QHBoxLayout(banner)
        banner_row.setContentsMargins(14, 13, 14, 13)
        banner_row.setSpacing(10)

        dot2 = QLabel()
        dot2.setFixedSize(9, 9)
        dot2.setStyleSheet(
            'border-radius:4px;background:#3f9d52;'
        )

        text_col2 = QVBoxLayout()
        text_col2.setSpacing(1)
        ready_title = QLabel('All inputs valid')
        ready_title.setStyleSheet(
            f'font-size:13px;font-weight:700;color:#2e7d46;'
        )
        ready_sub = QLabel('Ready to configure the simulation.')
        ready_sub.setStyleSheet(f'font-size:11.5px;color:{theme.TEXT_MUTED};')
        text_col2.addWidget(ready_title)
        text_col2.addWidget(ready_sub)

        banner_row.addWidget(dot2, alignment=Qt.AlignVCenter)
        banner_row.addLayout(text_col2)
        layout.addWidget(banner)
        layout.addSpacing(13)

        go_btn = QPushButton('Configure Simulation →')
        go_btn.setFixedHeight(38)
        go_btn.setCursor(Qt.PointingHandCursor)
        go_btn.setStyleSheet(f"""
            QPushButton {{
                background:{theme.ACCENT};
                color:white;
                border:none;
                border-radius:7px;
                font-size:13px;
                font-weight:600;
                font-family:{theme.FONT};
            }}
            QPushButton:hover {{ background:#1e72bc; }}
        """)
        go_btn.clicked.connect(self.goto_simulation)
        layout.addWidget(go_btn)

        return card

    # ── Handlers ──────────────────────────────────────────────────────────────
    def _browse_swmm(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Select SWMM input file', '', 'SWMM Files (*.inp);;All Files (*)'
        )
        if path:
            self._swmm_path.setText(path)

    def _on_import(self):
        self._raster_imported = True
        self._update_import_btn()
