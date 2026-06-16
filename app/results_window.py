from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSlider, QTableWidget, QTableWidgetItem, QHeaderView,
    QSizePolicy, QWidget, QAbstractItemView, QScrollArea,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from app import demo_data, theme
from app.widgets.map_widget import MapWidget
from app.widgets.chart_widget import ChartWidget


def _section_label(text):
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f'font-size:10.5px;font-weight:700;letter-spacing:0.8px;'
        f'color:{theme.TEXT_MUTED};text-transform:uppercase;'
    )
    return lbl


class ResultsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._selected_node = '805'
        self._metric = True
        self._layers = {'nodes': True, 'links': True, 'flood': True, 'base': True}
        self._flood_opacity = 65
        self._drag_pos = None
        self._build()

    # ── open/resize to parent ─────────────────────────────────────────────────
    def open_over(self, parent_geom):
        self.setGeometry(parent_geom)
        self.show()
        self.raise_()

    # ── drag (via title bar) ──────────────────────────────────────────────────
    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            self._drag_pos = ev.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, ev):
        if self._drag_pos and ev.buttons() == Qt.LeftButton:
            self.move(ev.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, ev):
        self._drag_pos = None

    # ── paint: semi-transparent overlay ──────────────────────────────────────
    def paintEvent(self, ev):
        from PySide6.QtGui import QPainter, QColor
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(10, 18, 28, 115))

    # ── UI construction ───────────────────────────────────────────────────────
    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        # Inner panel (96% × 95% of window)
        inner = QFrame(self)
        inner.setObjectName('resultsInner')
        inner.setStyleSheet(f"""
            QFrame#resultsInner {{
                background:{theme.WIN_BG};
                border-radius:11px;
            }}
        """)
        inner.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(0)

        inner_layout.addWidget(self._build_title_bar())

        # Three-panel row: layers | map | properties
        mid = QHBoxLayout()
        mid.setSpacing(0)
        mid.setContentsMargins(0, 0, 0, 0)
        mid.addWidget(self._build_layers_panel())
        mid.addWidget(self._build_map_panel(), stretch=1)
        mid.addWidget(self._build_properties_panel())

        mid_widget = QWidget()
        mid_widget.setLayout(mid)
        inner_layout.addWidget(mid_widget, stretch=1)

        # Bottom: table + chart
        inner_layout.addWidget(self._build_bottom_panel())

        # Wrap inner in outer with margins
        outer.addWidget(inner, alignment=Qt.AlignCenter)
        outer.setContentsMargins(
            int(self.width() * 0.02), int(self.height() * 0.025),
            int(self.width() * 0.02), int(self.height() * 0.025),
        )

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        # Keep inner panel at 96% × 95%
        w, h = self.width(), self.height()
        mw = int(w * 0.02)
        mh = int(h * 0.025)
        self.layout().setContentsMargins(mw, mh, mw, mh)

    # ── Title bar ─────────────────────────────────────────────────────────────
    def _build_title_bar(self):
        bar = QFrame()
        bar.setFixedHeight(40)
        bar.setStyleSheet(f'background:{theme.TITLEBAR_BG};border-radius:11px 11px 0 0;')

        row = QHBoxLayout(bar)
        row.setContentsMargins(14, 0, 14, 0)
        row.setSpacing(0)

        title = QLabel('Results')
        title.setStyleSheet('font-size:13px;font-weight:600;color:#cdd3da;')
        row.addWidget(title)
        row.addSpacing(9)

        run_id = QLabel('run 20260616_1534 · flood_run1')
        run_id.setStyleSheet(
            f'font-size:12px;color:#8a929c;font-family:{theme.FONT_MONO};'
        )
        row.addWidget(run_id)
        row.addSpacing(18)

        for tool_name in ['Pan', 'Zoom +', 'Zoom −', 'Fit', 'Export Map', 'Export CSV']:
            btn = QPushButton(tool_name)
            btn.setFlat(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    font-size:11.5px;
                    color:#b9c0c9;
                    background:transparent;
                    border:none;
                    padding:4px 9px;
                    border-radius:5px;
                }}
                QPushButton:hover {{ background:#3a3f47;color:white; }}
            """)
            row.addWidget(btn)
            row.addSpacing(3)

        row.addStretch()

        close_btn = QPushButton('✕')
        close_btn.setFlat(True)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                font-size:16px;
                color:#aeb6c0;
                background:transparent;
                border:none;
                padding:4px 8px;
            }}
            QPushButton:hover {{ color:#ff6b6b; }}
        """)
        close_btn.clicked.connect(self.close)
        row.addWidget(close_btn)

        return bar

    # ── Layers panel (left) ───────────────────────────────────────────────────
    def _build_layers_panel(self):
        panel = QFrame()
        panel.setFixedWidth(206)
        panel.setStyleSheet(f'background:white;border-right:1px solid {theme.BORDER};')

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(theme.scrollbar_qss())

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(0)

        layout.addWidget(_section_label('Layers'))
        layout.addSpacing(10)

        self._layer_btns = {}
        layer_defs = [
            ('nodes', 'Nodes'),
            ('links', 'Links (conduits)'),
            ('flood', 'Flood raster'),
            ('base',  'OSM base map'),
        ]
        for key, label in layer_defs:
            btn_row = QHBoxLayout()
            btn_row.setSpacing(9)
            checked = self._layers.get(key, True)

            check_lbl = QLabel('✓' if checked else '')
            check_lbl.setFixedSize(15, 15)
            check_lbl.setAlignment(Qt.AlignCenter)
            check_lbl.setStyleSheet(
                f'border-radius:4px;border:1.5px solid {theme.ACCENT};'
                f'background:{theme.ACCENT};color:white;font-size:10px;font-weight:700;'
                if checked else
                f'border-radius:4px;border:1.5px solid {theme.BORDER_INPUT};'
                f'background:white;font-size:10px;'
            )
            self._layer_btns[key] = check_lbl

            text_lbl = QLabel(label)
            text_lbl.setStyleSheet(f'font-size:12.5px;color:{theme.TEXT2};')

            row_widget = QWidget()
            row_widget.setLayout(btn_row)
            row_widget.setCursor(Qt.PointingHandCursor)
            row_widget.setStyleSheet('QWidget:hover { background:#f3f6f9; border-radius:6px; }')
            btn_row.addWidget(check_lbl)
            btn_row.addWidget(text_lbl)
            btn_row.addStretch()

            row_widget.mousePressEvent = (lambda e, k=key: self._toggle_layer(k))
            layout.addWidget(row_widget)

        layout.addSpacing(14)
        opacity_lbl = QLabel('Flood raster opacity')
        opacity_lbl.setStyleSheet(f'font-size:12px;color:{theme.TEXT3};')
        layout.addWidget(opacity_lbl)
        layout.addSpacing(8)

        self._opacity_slider = QSlider(Qt.Horizontal)
        self._opacity_slider.setRange(0, 100)
        self._opacity_slider.setValue(self._flood_opacity)
        self._opacity_slider.setStyleSheet(f'accent-color:{theme.ACCENT};')
        self._opacity_slider.valueChanged.connect(self._on_opacity_change)
        layout.addWidget(self._opacity_slider)

        self._opacity_lbl = QLabel(f'{self._flood_opacity}%')
        self._opacity_lbl.setAlignment(Qt.AlignRight)
        self._opacity_lbl.setStyleSheet(f'font-size:11px;color:{theme.TEXT_MUTED};')
        layout.addWidget(self._opacity_lbl)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f'background:#eef1f5;')
        layout.addSpacing(15)
        layout.addWidget(sep)
        layout.addSpacing(15)

        layout.addWidget(_section_label('Legend'))
        layout.addSpacing(10)

        legend_items = [
            ('#d64545', 'Flooding'),
            ('#e8a33d', 'High (surcharged)'),
            ('#3f9d52', 'Normal'),
            ('#5b6772', 'Outfall'),
        ]
        for color, label in legend_items:
            leg_row = QHBoxLayout()
            leg_row.setSpacing(9)
            dot = QLabel()
            dot.setFixedSize(13, 13)
            dot.setStyleSheet(f'border-radius:6px;background:{color};')
            text = QLabel(label)
            text.setStyleSheet(f'font-size:12px;color:{theme.TEXT3};')
            leg_row.addWidget(dot)
            leg_row.addWidget(text)
            leg_row.addStretch()
            w = QWidget()
            w.setLayout(leg_row)
            layout.addWidget(w)
            layout.addSpacing(8)

        layout.addStretch()
        scroll.setWidget(content)

        outer = QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        panel.setLayout(outer)
        return panel

    # ── Map panel (center) ────────────────────────────────────────────────────
    def _build_map_panel(self):
        self._map_widget = MapWidget()
        self._map_widget.node_selected.connect(self._on_node_selected)
        return self._map_widget

    # ── Node properties panel (right) ─────────────────────────────────────────
    def _build_properties_panel(self):
        panel = QFrame()
        panel.setFixedWidth(236)
        panel.setStyleSheet(f'background:white;border-left:1px solid {theme.BORDER};')

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(theme.scrollbar_qss())

        self._props_content = QWidget()
        self._props_layout = QVBoxLayout(self._props_content)
        self._props_layout.setContentsMargins(16, 15, 16, 15)
        self._props_layout.setSpacing(0)

        scroll.setWidget(self._props_content)

        outer = QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        panel.setLayout(outer)

        self._refresh_properties()
        return panel

    def _refresh_properties(self):
        layout = self._props_layout
        # Clear
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        nid = self._selected_node
        n = demo_data.NODES[nid]
        df = 1.0 if self._metric else 3.28084
        qf = 1.0 if self._metric else 35.3147
        du = 'm' if self._metric else 'ft'
        qu = 'm³/s' if self._metric else 'cfs'

        layout.addWidget(_section_label('Node Properties'))
        layout.addSpacing(12)

        # Node ID row
        id_row = QHBoxLayout()
        id_row.setSpacing(9)
        dot = QLabel()
        dot.setFixedSize(13, 13)
        dot.setStyleSheet(f'border-radius:6px;background:{demo_data.node_color(nid)};')
        id_lbl = QLabel(f'Node {nid}')
        id_lbl.setStyleSheet(f'font-size:18px;font-weight:700;color:{theme.TEXT};')
        id_row.addWidget(dot, alignment=Qt.AlignVCenter)
        id_row.addWidget(id_lbl)
        id_row.addStretch()
        layout.addLayout(id_row)
        layout.addSpacing(6)

        # Status badge
        st = n['st']
        badge_bg = '#fdeaea' if st == 'FLOODING' else '#fdf3e3' if st == 'HIGH' else '#e9f5ec'
        badge_color = '#c0392b' if st == 'FLOODING' else '#b9821f' if st == 'HIGH' else '#2e7d46'
        badge = QLabel(st)
        badge.setStyleSheet(f"""
            font-size:10.5px;font-weight:700;letter-spacing:0.5px;
            padding:2px 9px;border-radius:10px;
            background:{badge_bg};color:{badge_color};
        """)
        layout.addWidget(badge)
        layout.addSpacing(14)

        # Property rows
        peak_idx = demo_data.peak_flow_idx(nid)
        flood_steps = demo_data.flood_step_count(nid)
        max_dep = demo_data.max_depth(nid)
        peak_flo = demo_data.peak_flow(nid)

        rows = [
            ('Type',          n['type']),
            ('Ground elev.',  f'{n["invFt"] * df:.2f} {du}'),
            ('Max depth',     f'{max_dep * df:.2f} {du}'),
            ('Surcharge limit', f'{n["rimM"] * df:.2f} {du}'),
            ('Peak flow',     f'{peak_flo * qf:.3f} {qu}'),
            ('Peak time',     demo_data.TIMELINE[peak_idx]),
            ('Flood duration', f'{flood_steps * 15} min' if flood_steps else '—'),
        ]
        for key, val in rows:
            sep = QFrame()
            sep.setFixedHeight(1)
            sep.setStyleSheet('background:#f1f3f6;')
            layout.addWidget(sep)
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 8, 0, 8)
            k_lbl = QLabel(key)
            k_lbl.setStyleSheet(f'font-size:12px;color:{theme.TEXT_MUTED};')
            v_lbl = QLabel(val)
            v_lbl.setStyleSheet(
                f'font-size:12.5px;font-weight:600;color:{theme.TEXT};'
                f'font-family:{theme.FONT_MONO};'
            )
            row_layout.addWidget(k_lbl)
            row_layout.addStretch()
            row_layout.addWidget(v_lbl)
            layout.addLayout(row_layout)

        layout.addSpacing(14)
        hint = QLabel('Click any node on the map to inspect its hydrograph.')
        hint.setStyleSheet(f'font-size:11px;color:{theme.TEXT_FAINT};')
        hint.setWordWrap(True)
        layout.addWidget(hint)
        layout.addStretch()

    # ── Bottom panel: table + chart ───────────────────────────────────────────
    def _build_bottom_panel(self):
        panel = QFrame()
        panel.setFixedHeight(266)
        panel.setStyleSheet(f'background:white;border-top:1px solid {theme.BORDER};')

        row = QHBoxLayout(panel)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        # Table (46%)
        table_frame = QFrame()
        table_frame.setStyleSheet(f'border-right:1px solid {theme.BORDER};')
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        self._table_header_lbl = QLabel(f'Time Series — Node {self._selected_node}')
        table_header = QFrame()
        table_header.setFixedHeight(36)
        table_header.setStyleSheet(f'border-bottom:1px solid #eef1f5;')
        th_layout = QHBoxLayout(table_header)
        th_layout.setContentsMargins(14, 0, 14, 0)
        self._table_header_lbl.setStyleSheet(
            f'font-size:10.5px;font-weight:700;letter-spacing:0.8px;color:{theme.TEXT_MUTED};'
        )
        th_layout.addWidget(self._table_header_lbl)
        th_layout.addStretch()
        unit_note = QLabel('Metric (m, m³/s)')
        unit_note.setStyleSheet(f'font-size:11px;color:{theme.TEXT_FAINT};font-weight:400;')
        th_layout.addWidget(unit_note)
        table_layout.addWidget(table_header)

        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(['Time', 'Depth (m)', 'Flow (m³/s)', 'Flooding', 'Status'])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(False)
        self._table.verticalHeader().setVisible(False)
        self._table.setStyleSheet(f"""
            QTableWidget {{
                border:none;
                font-size:11.5px;
                font-family:{theme.FONT_MONO};
                background:white;
                gridline-color:#f4f6f8;
            }}
            QHeaderView::section {{
                background:#f7f8fa;
                border:none;
                border-bottom:1px solid #e3e8ee;
                padding:7px 10px;
                font-size:10.5px;
                font-weight:700;
                color:{theme.TEXT_MUTED};
                text-transform:uppercase;
                letter-spacing:0.4px;
            }}
            QTableWidget::item {{
                padding:5px 10px;
                border-bottom:1px solid #f4f6f8;
            }}
            {theme.scrollbar_qss()}
        """)
        self._table.setFont(QFont('Ubuntu Mono', 11))
        table_layout.addWidget(self._table)

        # Chart (54%)
        chart_frame = QFrame()
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_layout.setSpacing(0)

        chart_header = QFrame()
        chart_header.setFixedHeight(36)
        chart_header.setStyleSheet(f'border-bottom:1px solid #eef1f5;')
        ch_layout = QHBoxLayout(chart_header)
        ch_layout.setContentsMargins(14, 0, 14, 0)
        ch_lbl = QLabel('Water Level Hydrograph')
        ch_lbl.setStyleSheet(
            f'font-size:10.5px;font-weight:700;letter-spacing:0.8px;color:{theme.TEXT_MUTED};'
        )
        ch_layout.addWidget(ch_lbl)
        chart_layout.addWidget(chart_header)

        self._chart = ChartWidget()
        chart_layout.addWidget(self._chart, stretch=1)

        row.addWidget(table_frame, stretch=46)
        row.addWidget(chart_frame, stretch=54)

        self._refresh_table()
        self._chart.update_node(self._selected_node, self._metric)
        return panel

    def _refresh_table(self):
        nid = self._selected_node
        n = demo_data.NODES[nid]
        df = 1.0 if self._metric else 3.28084
        qf = 1.0 if self._metric else 35.3147

        self._table_header_lbl.setText(f'Time Series — Node {nid}')
        self._table.setRowCount(25)

        for i, t in enumerate(demo_data.TIMELINE):
            dep = n['dep'][i] * df
            flo = n['flo'][i] * qf
            fld = n['fld'][i]
            has_flood = fld > 0
            st = 'FLOODING' if has_flood else ('HIGH' if n['dep'][i] > n['rimM'] * 0.86 else 'NORMAL')
            st_color = '#c0392b' if st == 'FLOODING' else '#b9821f' if st == 'HIGH' else '#3f9d52'
            fld_str = f'{fld * qf:.3f}' if has_flood else '—'

            items = [
                (t, theme.TEXT_MUTED, Qt.AlignLeft),
                (f'{dep:.2f}', theme.TEXT, Qt.AlignRight),
                (f'{flo:.3f}', theme.TEXT, Qt.AlignRight),
                (fld_str, '#c0392b' if has_flood else '#c0c7d0', Qt.AlignRight),
                (st, st_color, Qt.AlignLeft),
            ]
            for col, (text, color, align) in enumerate(items):
                item = QTableWidgetItem(text)
                item.setForeground(QColor(color))
                item.setTextAlignment(align | Qt.AlignVCenter)
                if has_flood:
                    item.setBackground(QColor('#fdf4f4'))
                self._table.setItem(i, col, item)

    # ── Event handlers ────────────────────────────────────────────────────────
    def _on_node_selected(self, node_id):
        if node_id not in demo_data.NODES:
            return
        self._selected_node = node_id
        self._map_widget.set_selected_node(node_id)
        self._refresh_properties()
        self._refresh_table()
        self._chart.update_node(node_id, self._metric)

    def _toggle_layer(self, key):
        self._layers[key] = not self._layers[key]
        checked = self._layers[key]
        lbl = self._layer_btns[key]
        lbl.setText('✓' if checked else '')
        lbl.setStyleSheet(
            f'border-radius:4px;border:1.5px solid {theme.ACCENT};'
            f'background:{theme.ACCENT};color:white;font-size:10px;font-weight:700;'
            if checked else
            f'border-radius:4px;border:1.5px solid {theme.BORDER_INPUT};'
            f'background:white;font-size:10px;'
        )
        self._map_widget.set_layer_visible(key, checked)

    def _on_opacity_change(self, value):
        self._flood_opacity = value
        self._opacity_lbl.setText(f'{value}%')
        self._map_widget.set_flood_opacity(value)
