from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QProgressBar, QSizePolicy, QFileDialog,
    QScrollArea, QTextEdit,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor
from app import demo_data, theme


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


class OutputTab(QWidget):
    run_state_changed = Signal(str)  # 'idle' | 'running' | 'done'
    results_ready = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._run_state = 'idle'
        self._progress = 0
        self._elapsed = 0
        self._log_idx = 0
        self._log_timer = QTimer(self)
        self._log_timer.timeout.connect(self._step_log)
        self._elapsed_timer = QTimer(self)
        self._elapsed_timer.timeout.connect(self._tick_elapsed)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(14)

        # ── Top row ─────────────────────────────────────────────────────────
        top = QHBoxLayout()
        top.setSpacing(14)
        top.addWidget(self._build_settings_card(), stretch=1)
        top.addWidget(self._build_action_card())
        root.addLayout(top)

        # ── Run log ──────────────────────────────────────────────────────────
        root.addWidget(self._build_log_card(), stretch=1)

    # ── Output settings ───────────────────────────────────────────────────────
    def _build_settings_card(self):
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(0)

        layout.addWidget(_section_label('Output Settings'))
        layout.addSpacing(14)

        layout.addWidget(self._field_label('Output directory'))
        layout.addSpacing(6)

        row = QHBoxLayout()
        row.setSpacing(8)
        self._out_path = QLabel('~/ewm_runs/20260616_1534/')
        self._out_path.setFixedHeight(theme.RH)
        self._out_path.setStyleSheet(f"""
            border:1.5px solid {theme.BORDER_INPUT};
            border-radius:6px;
            padding:0 11px;
            font-family:{theme.FONT_MONO};
            font-size:12px;
            color:{theme.TEXT2};
            background:{theme.SURFACE_DIM};
        """)
        self._out_path.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        browse_btn = QPushButton('Browse…')
        browse_btn.setFixedHeight(theme.RH)
        browse_btn.setCursor(Qt.PointingHandCursor)
        browse_btn.setStyleSheet(theme.ghost_btn_qss())
        browse_btn.clicked.connect(self._browse_output)
        row.addWidget(self._out_path)
        row.addWidget(browse_btn)
        layout.addLayout(row)
        layout.addSpacing(13)

        layout.addWidget(self._field_label('Raster output prefix'))
        layout.addSpacing(6)
        self._prefix_edit = QLineEdit('flood_run1')
        self._prefix_edit.setFixedHeight(theme.RH)
        self._prefix_edit.setStyleSheet(theme.input_qss())
        layout.addWidget(self._prefix_edit)

        return card

    # ── Action buttons ────────────────────────────────────────────────────────
    def _build_action_card(self):
        card = _card()
        card.setFixedWidth(360)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(9)

        layout.addWidget(_section_label('Action'))
        layout.addSpacing(4)

        self._run_btn = QPushButton('▶  Run Simulation')
        self._run_btn.setFixedHeight(46)
        self._run_btn.setCursor(Qt.PointingHandCursor)
        self._run_btn.clicked.connect(self.start_run)
        layout.addWidget(self._run_btn)

        self._abort_btn = QPushButton('■  Abort')
        self._abort_btn.setFixedHeight(38)
        self._abort_btn.setCursor(Qt.PointingHandCursor)
        self._abort_btn.clicked.connect(self.abort_run)
        layout.addWidget(self._abort_btn)

        self._results_btn = QPushButton('◉  Open Results')
        self._results_btn.setFixedHeight(38)
        self._results_btn.setCursor(Qt.PointingHandCursor)
        self._results_btn.clicked.connect(self._on_open_results)
        layout.addWidget(self._results_btn)

        self._update_btn_styles()
        return card

    # ── Run log card ──────────────────────────────────────────────────────────
    def _build_log_card(self):
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(0)

        # Header row
        header = QHBoxLayout()
        header.setSpacing(12)
        header.addWidget(_section_label('Run Log'))

        self._pill_lbl = QLabel('IDLE')
        self._pill_lbl.setStyleSheet(f"""
            font-size:11.5px;font-weight:600;
            padding:2px 9px;border-radius:10px;
            background:#eef1f5;color:{theme.TEXT_MUTED};
            border:1px solid {theme.BORDER};
        """)
        header.addWidget(self._pill_lbl)
        header.addStretch()

        self._elapsed_lbl = QLabel('00:00')
        self._elapsed_lbl.setStyleSheet(
            f'font-size:12px;color:{theme.TEXT3};font-family:{theme.FONT_MONO};'
        )
        header.addWidget(self._elapsed_lbl)
        layout.addLayout(header)
        layout.addSpacing(11)

        # Log terminal
        self._log_view = QTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setFont(QFont('Ubuntu Mono', 12))
        self._log_view.setStyleSheet(f"""
            QTextEdit {{
                background:{theme.SURFACE_LOG};
                border-radius:8px;
                padding:12px 14px;
                color:#9fb4cc;
                border:none;
            }}
        """)
        self._log_view.setMinimumHeight(200)
        self._log_view.setPlaceholderText(
            'Idle — press "Run Simulation" to start the ITZI pipeline.'
        )
        layout.addWidget(self._log_view, stretch=1)
        layout.addSpacing(11)

        # Progress bar
        progress_row = QHBoxLayout()
        progress_row.setSpacing(12)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setFixedHeight(9)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background:#e3e8ee;
                border-radius:4px;
                border:none;
            }}
            QProgressBar::chunk {{
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {theme.ACCENT},stop:1 #3a8fd6);
                border-radius:4px;
            }}
        """)
        self._pct_lbl = QLabel('0%')
        self._pct_lbl.setFixedWidth(42)
        self._pct_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._pct_lbl.setStyleSheet(
            f'font-size:12px;font-weight:700;color:{theme.ACCENT};'
            f'font-family:{theme.FONT_MONO};'
        )
        progress_row.addWidget(self._progress_bar, stretch=1)
        progress_row.addWidget(self._pct_lbl)
        layout.addLayout(progress_row)

        return card

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _field_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f'font-size:12px;font-weight:500;color:{theme.TEXT3};')
        return lbl

    def _log_color(self, kind):
        return {
            'ok':   '#6fd18a',
            'warn': '#ffcf66',
            'err':  '#ff7a7a',
        }.get(kind, '#9fb4cc')

    def _append_log(self, timestamp, message, color):
        cursor = self._log_view.textCursor()
        cursor.movePosition(QTextCursor.End)

        # Timestamp in grey
        fmt_ts = QTextCharFormat()
        fmt_ts.setForeground(QColor('#566578'))
        cursor.setCharFormat(fmt_ts)
        cursor.insertText(timestamp + '  ')

        # Message in color
        fmt_msg = QTextCharFormat()
        fmt_msg.setForeground(QColor(color))
        cursor.setCharFormat(fmt_msg)
        cursor.insertText(message + '\n')

        self._log_view.setTextCursor(cursor)
        self._log_view.ensureCursorVisible()

    def _update_btn_styles(self):
        running = self._run_state == 'running'
        done    = self._run_state == 'done'

        # Run button
        if running:
            self._run_btn.setText('⏳ Running…')
            self._run_btn.setEnabled(False)
            self._run_btn.setStyleSheet(f"""
                QPushButton {{
                    background:#9aa6b2;
                    color:white;
                    border:none;
                    border-radius:8px;
                    font-size:14px;
                    font-weight:700;
                    font-family:{theme.FONT};
                }}
            """)
        elif done:
            self._run_btn.setText('▶  Run Again')
            self._run_btn.setEnabled(True)
            self._run_btn.setStyleSheet(theme.green_btn_qss())
        else:
            self._run_btn.setText('▶  Run Simulation')
            self._run_btn.setEnabled(True)
            self._run_btn.setStyleSheet(theme.green_btn_qss())

        # Abort button
        if running:
            self._abort_btn.setEnabled(True)
            self._abort_btn.setStyleSheet(f"""
                QPushButton {{
                    background:white;
                    color:{theme.COLOR_ERR};
                    border:1.5px solid #e7b3b3;
                    border-radius:8px;
                    font-size:13px;
                    font-weight:600;
                    font-family:{theme.FONT};
                }}
                QPushButton:hover {{ background:#fff5f5; }}
            """)
        else:
            self._abort_btn.setEnabled(False)
            self._abort_btn.setStyleSheet(f"""
                QPushButton {{
                    background:#f4f6f8;
                    color:{theme.TEXT_FAINT};
                    border:1.5px solid {theme.BORDER};
                    border-radius:8px;
                    font-size:13px;
                    font-weight:600;
                    font-family:{theme.FONT};
                }}
            """)

        # Results button
        can_results = done or self._run_state == 'done'
        if can_results:
            self._results_btn.setEnabled(True)
            self._results_btn.setStyleSheet(f"""
                QPushButton {{
                    background:{theme.ACCENT};
                    color:white;
                    border:none;
                    border-radius:8px;
                    font-size:13px;
                    font-weight:600;
                    font-family:{theme.FONT};
                }}
                QPushButton:hover {{ background:#1e72bc; }}
            """)
        else:
            self._results_btn.setEnabled(False)
            self._results_btn.setStyleSheet(f"""
                QPushButton {{
                    background:#f4f6f8;
                    color:{theme.TEXT_FAINT};
                    border:1.5px solid {theme.BORDER};
                    border-radius:8px;
                    font-size:13px;
                    font-weight:600;
                    font-family:{theme.FONT};
                }}
            """)

    def _update_pill(self):
        if self._run_state == 'running':
            self._pill_lbl.setText('RUNNING')
            self._pill_lbl.setStyleSheet(f"""
                font-size:11.5px;font-weight:600;
                padding:2px 9px;border-radius:10px;
                background:#fff7e6;color:#b9821f;
                border:1px solid #f0d9a8;
            """)
        elif self._run_state == 'done':
            self._pill_lbl.setText('COMPLETED')
            self._pill_lbl.setStyleSheet(f"""
                font-size:11.5px;font-weight:600;
                padding:2px 9px;border-radius:10px;
                background:#e7f4ea;color:#2e7d46;
                border:1px solid #c4e3cd;
            """)
        else:
            self._pill_lbl.setText('IDLE')
            self._pill_lbl.setStyleSheet(f"""
                font-size:11.5px;font-weight:600;
                padding:2px 9px;border-radius:10px;
                background:#eef1f5;color:{theme.TEXT_MUTED};
                border:1px solid {theme.BORDER};
            """)

    # ── Run simulation demo ───────────────────────────────────────────────────
    def start_run(self):
        if self._run_state == 'running':
            return
        self._run_state = 'running'
        self._progress = 0
        self._elapsed = 0
        self._log_idx = 0
        self._log_view.clear()
        self._progress_bar.setValue(0)
        self._pct_lbl.setText('0%')
        self._update_btn_styles()
        self._update_pill()
        self.run_state_changed.emit('running')

        self._log_timer.start(340)
        self._elapsed_timer.start(1000)

    def abort_run(self):
        if self._run_state != 'running':
            return
        self._log_timer.stop()
        self._elapsed_timer.stop()
        self._append_log('--:--:--', '■ Aborted by user. Cleaning up temp files…', '#ff7a7a')
        self._run_state = 'idle'
        self._update_btn_styles()
        self._update_pill()
        self.run_state_changed.emit('idle')

    def _step_log(self):
        script = demo_data.LOG_SCRIPT
        if self._log_idx >= len(script):
            self._log_timer.stop()
            self._elapsed_timer.stop()
            self._run_state = 'done'
            self._progress = 100
            self._progress_bar.setValue(100)
            self._pct_lbl.setText('100%')
            self._update_btn_styles()
            self._update_pill()
            self.run_state_changed.emit('done')
            self.results_ready.emit()
            return

        entry = script[self._log_idx]
        self._log_idx += 1
        color = self._log_color(entry['k'])
        self._append_log(entry['t'], entry['m'], color)

        if 'p' in entry:
            self._progress = entry['p']
            self._progress_bar.setValue(entry['p'])
            self._pct_lbl.setText(f"{entry['p']}%")

    def _tick_elapsed(self):
        self._elapsed += 1
        m = self._elapsed // 60
        s = self._elapsed % 60
        self._elapsed_lbl.setText(f'{m:02d}:{s:02d}')

    def _on_open_results(self):
        if self._run_state == 'done':
            self.results_ready.emit()

    def _browse_output(self):
        path = QFileDialog.getExistingDirectory(self, 'Select output directory')
        if path:
            self._out_path.setText(path + '/')

    def get_elapsed_str(self):
        m = self._elapsed // 60
        s = self._elapsed % 60
        return f'{m:02d}:{s:02d}'

    def get_run_state(self):
        return self._run_state
