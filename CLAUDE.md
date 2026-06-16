# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Always use the project venv — never the system Python:

```bash
# Create venv (first time only)
python3 -m venv .venv

# Install dependencies
.venv/bin/pip install -r requirements.txt

# Run the application
.venv/bin/python main.py

# Headless smoke test (no display required)
QT_QPA_PLATFORM=offscreen .venv/bin/python -c "
from PySide6.QtWidgets import QApplication; import sys
app = QApplication(sys.argv)
from app.main_window import MainWindow; MainWindow()
print('OK')
"

# Regenerate sample data (stdlib only, no venv needed)
python3 sample_data/convert_inp.py
```

## Architecture

**Entry point:** `main.py` — creates `QApplication`, shows `LoginWindow`, then `MainWindow` on login.

**Screen flow:**
```
LoginWindow (QDialog, frameless)
  └─ on login_accepted signal → MainWindow (QMainWindow, frameless)
       ├─ InputTab        (app/tabs/input_tab.py)
       ├─ SimulationTab   (app/tabs/simulation_tab.py)
       ├─ OutputTab       (app/tabs/output_tab.py)
       │    └─ results_ready signal → ResultsWindow
       └─ ResultsWindow   (app/results_window.py)  ← QDialog overlay
```

**Key design decisions:**

- **Frameless windows** — both `LoginWindow` and `MainWindow` use `Qt.FramelessWindowHint` with custom title bars and `mousePressEvent`/`mouseMoveEvent` for drag-to-move.
- **No native menu/status bar** — all chrome (title bar, menu strip, tab strip, status bar) are plain `QFrame`/`QWidget` with manual layouts, because native Qt bars can't be styled to match the dark/light mixed design.
- **Tab switching** — `MainWindow` uses a `QStackedWidget` (not `QTabWidget`) so the tab strip can be fully custom. `_switch_tab(key)` sets the stacked index and re-applies QSS to the tab buttons.
- **Run simulation demo** — `OutputTab` plays through `demo_data.LOG_SCRIPT` via two `QTimer`s (340 ms log step, 1 s elapsed tick), identical to the prototype's JS animation. Real ITZI/GRASS execution is stubbed — replace `_step_log` with a `QThread` subprocess runner when integrating.
- **Map widget** — `app/widgets/map_widget.py` builds a full SVG basemap as an inline HTML string and loads it into `QWebEngineView`. Node clicks go through a `QWebChannel` bridge (`_MapBridge` QObject with `@Slot`). Falls back gracefully if `PySide6-WebEngine` is absent.
- **Chart widget** — `app/widgets/chart_widget.py` is a `pyqtgraph.PlotWidget`. `update_node(node_id)` replaces all plot items: depth `PlotCurveItem` with `fillLevel=0`, flood-period `LinearRegionItem`s, and a dashed `InfiniteLine` at `rimM`.

**Styling convention** — `app/theme.py` is the single source of truth for colors, font names, and row height. All QSS strings are built from those constants. `box-shadow` is **not** valid Qt QSS — use `QGraphicsDropShadowEffect` instead.

**Demo data** (`app/demo_data.py`) — all 12 nodes, 25 TIMELINE steps, LINKS topology, and LOG_SCRIPT are ported verbatim from the HTML prototype's JS `D{}` object. This is what drives the entire UI until real ITZI output is wired in.

**Reference prototype:** `desktop-prototype-application/project/eWM.dc.html` — the authoritative visual spec. The `support.js` next to it is the DC runtime (not used at runtime, reference only).

**Sample data** (`sample_data/`):
- `convert_inp.py` — stdlib-only script that generates all three output files from the Lancaster PA SWMM example, re-projected to District 7, Ho Chi Minh City (WGS84).
- `output/eWM_demo.inp` — 36-node SWMM network, coordinates in WGS84, simulation 2026-06-16 15:00–21:00.
- `output/node_timeseries_demo.csv` — synthetic ITZI-format node output (36 nodes × 25 timesteps), the expected shape of real ITZI output.
- `output/rainfall_hcm_2026.csv` — 5-min tropical storm, peak 58 mm/hr at 17:05.
