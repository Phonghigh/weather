# eWM — eWater Warning Model
## Complete Project Plan: Architecture · Features · Timeline · Budget · Risk

> **Version:** 1.0 | **Date:** June 16, 2026 | **Status:** Pitch / Pre-kickoff

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement & Market Context](#2-problem-statement--market-context)
3. [Solution Overview](#3-solution-overview)
4. [Technical Architecture](#4-technical-architecture)
   - 4.1 [System Architecture Diagram](#41-system-architecture-diagram)
   - 4.2 [Engine Layer](#42-engine-layer)
   - 4.3 [Application Layer](#43-application-layer)
   - 4.4 [Data Layer](#44-data-layer)
   - 4.5 [Packaging & Distribution](#45-packaging--distribution)
5. [Feature Scope](#5-feature-scope)
   - 5.1 [Phase 1 — MVP](#51-phase-1--mvp-this-contract)
   - 5.2 [Phase 2 — Enhanced GIS](#52-phase-2--enhanced-gis)
   - 5.3 [Phase 3 — Production & Enterprise](#53-phase-3--production--enterprise)
   - 5.4 [Out of Scope](#54-out-of-scope-phase-1)
6. [User Flow](#6-user-flow)
7. [Screen Specifications](#7-screen-specifications)
8. [Team Composition](#8-team-composition)
9. [Implementation Timeline](#9-implementation-timeline)
   - 9.1 [Week-by-Week Plan](#91-week-by-week-plan)
   - 9.2 [Milestones](#92-milestones)
   - 9.3 [Man-Day Allocation](#93-man-day-allocation)
10. [Budget Breakdown](#10-budget-breakdown)
    - 10.1 [Human Resources](#101-human-resources)
    - 10.2 [Infrastructure & Tools](#102-infrastructure--tools)
    - 10.3 [Phase Summary](#103-phase-summary)
11. [Risk Register](#11-risk-register)
12. [Technical Deep Dive](#12-technical-deep-dive)
    - 12.1 [ITZI + GRASS GIS Integration](#121-itzi--grass-gis-integration)
    - 12.2 [SWMM Parsing Strategy](#122-swmm-parsing-strategy)
    - 12.3 [Run Workflow Engine](#123-run-workflow-engine)
    - 12.4 [Map Rendering Strategy](#124-map-rendering-strategy)
    - 12.5 [License System](#125-license-system)
13. [Acceptance Criteria](#13-acceptance-criteria)
14. [Deliverables & Handover](#14-deliverables--handover)
15. [Pitch Summary Card](#15-pitch-summary-card)

---

## 1. Executive Summary

**eWM (eWater Warning Model)** is a professional desktop application for Ubuntu that enables urban flood simulation without requiring expertise in command-line GIS tools. It wraps three best-in-class open-source engines — **EPA SWMM** (1D drainage network), **ITZI** (2D hydrodynamic surface flow), and **GRASS GIS** (spatial raster processing) — into a guided, tab-based PySide6 GUI that any trained engineer can operate.

The result: a reproducible, auditable flood simulation pipeline from raw drainage-network data to flood-depth maps and time-series water level charts — in under 10 clicks, on a standard Ubuntu workstation.

### Key Numbers at a Glance

| Item | Value |
|---|---|
| **Phase 1 Duration** | 8 calendar weeks |
| **Phase 1 Effort** | 48 man-days |
| **Phase 1 Team** | 3.5 FTE across 6 roles |
| **Phase 1 Budget** | ~209,000,000 VND / ~$8,200 USD |
| **Full Product (3 phases)** | 18 calendar weeks / ~$18,800 USD |
| **Technology license cost** | $0 (100% open-source stack) |
| **Target OS** | Ubuntu 22.04 LTS & 24.04 LTS |

---

## 2. Problem Statement & Market Context

### The Pain Points

Engineers working in urban flood risk assessment currently operate a fragmented, command-line-heavy toolchain. Each tool must be set up, run, and post-processed independently. There is no single interface that:

- Connects a drainage model (SWMM) to a 2D surface model (ITZI)
- Manages GIS data (GRASS GIS) without CLI expertise
- Stores simulation history and makes runs reproducible
- Displays results visually without ArcGIS or QGIS knowledge

| Pain Point | Current Reality | eWM Fix |
|---|---|---|
| Fragmented toolchain | SWMM, ITZI, GRASS run separately in terminal | Single GUI orchestrates the entire pipeline |
| No reproducibility | Commands typed manually, lost after session ends | All configs saved as `.ewm` project files + SQLite |
| Long feedback loops | Results need manual GIS post-processing | Instant map + chart in Results Viewer |
| High skill barrier | Requires GRASS GIS + ITZI CLI expertise | Guided tab-by-tab wizard workflow |
| Commercial licensing cost | ArcGIS / HEC-RAS license fees | 100% open-source engine stack — zero license cost |
| Audit trail | No record of what settings produced which output | Every run logged with timestamp, inputs, and outputs |

### Target Users

| User Type | Use Case | Organization |
|---|---|---|
| Urban Drainage Engineer | Design and validate drainage networks for new developments | Engineering consultancies |
| Municipal Hydrologist | Model flood risk under extreme rainfall scenarios | City/provincial water authorities |
| Disaster Risk Analyst | Rapid flood extent mapping for emergency planning | Disaster management agencies |
| University Researcher | Teaching and research with coupled 1D-2D models | Universities and research institutes |

### Market Context — Vietnam & Southeast Asia

- Vietnam has 63 provinces; most lack dedicated flood simulation software
- Current tools used: MIKE FLOOD (~$20,000–$50,000/license), HEC-RAS (free but US Army format, limited 2D coupling), SWMM standalone
- eWM offers **professional-grade 1D-2D coupling at zero engine licensing cost** — a compelling value proposition for government and mid-size consultancies
- ITZI is the only open-source tool that natively couples SWMM 1D with GRASS GIS 2D raster hydraulics

---

## 3. Solution Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          eWM Desktop Application                            │
│                         (PySide6 on Ubuntu Linux)                           │
│                                                                             │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  Login   │  │  Input Tab   │  │ Simulation   │  │   Output Tab    │   │
│  │ & License│→ │ SWMM + Raster│→ │    Tab       │→ │  Run + Logs +   │   │
│  │  Check   │  │  + GRASS     │  │ Time Config  │  │  Results Viewer │   │
│  └──────────┘  └──────────────┘  └──────────────┘  └─────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Engine Orchestration Layer                        │   │
│  │   swmm_api (parse .inp) │ GRASS session │ ITZI subprocess runner   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────┐  ┌─────────────┐  ┌─────────────────────────────────┐   │
│  │  SWMM Engine │  │ GRASS GIS   │  │          ITZI Engine            │   │
│  │  (pyswmm)    │  │  8.4+       │  │  (2D hydrodynamic raster model) │   │
│  └──────────────┘  └─────────────┘  └─────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       Data Layer                                    │   │
│  │   SQLite (Phase 1) → PostgreSQL/PostGIS (Phase 2)                  │   │
│  │   Tables: runs · nodes · links · timeseries · raster_exports       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Technical Architecture

### 4.1 System Architecture Diagram

```
User
 │
 ▼
┌─────────────────────────────────────────────────────────────┐
│                    PySide6 Application                       │
│                                                             │
│  LoginWindow ──→ MainWindow                                 │
│                    ├── InputTab                             │
│                    │     ├── SWMMFileSelector               │
│                    │     ├── RasterImportWizard             │
│                    │     ├── GRASSMapsetSelector            │
│                    │     └── ValidationPanel                │
│                    ├── SimulationTab                        │
│                    │     ├── DateTimeRangePicker            │
│                    │     ├── TimestepSelector               │
│                    │     └── IniPreviewWidget               │
│                    └── OutputTab                            │
│                          ├── OutputPathSelector             │
│                          ├── RunButton                      │
│                          ├── LogStreamPanel (QThread)       │
│                          └── ResultsButton ──→ ResultsWindow│
│                                                             │
│  ResultsWindow                                              │
│    ├── MapPanel (Folium + QWebEngineView)                   │
│    ├── LayerTreePanel                                       │
│    ├── NodePropertiesPanel                                  │
│    └── BottomPanel                                          │
│          ├── TimeseriesTable (QTableWidget)                 │
│          └── WaterLevelChart (pyqtgraph)                    │
│                                                             │
│  EngineOrchestrator                                         │
│    ├── GRASSSession (grass-session library)                 │
│    ├── SWMMParser (swmm_api)                                │
│    ├── IniGenerator                                         │
│    └── ITZIRunner (QThread → subprocess)                    │
│                                                             │
│  DataLayer                                                  │
│    ├── SQLiteDB (SQLAlchemy ORM)                            │
│    ├── RunRepository                                        │
│    ├── NodeRepository                                       │
│    └── TimeseriesRepository                                 │
└─────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
    SWMM Engine          GRASS GIS 8.4+        ITZI v25.8
    (pyswmm v2.0)     (grass.script API)    (uv venv install)
```

### 4.2 Engine Layer

#### ITZI — 2D Hydrodynamic Model

| Property | Detail |
|---|---|
| **Version** | 25.8 (August 2025, actively maintained) |
| **Installation** | `pip install itzi` inside project venv (NOT `uv tool install` — avoids isolation issues) |
| **GRASS dependency** | GRASS GIS 8.4+ mandatory; enforced at import time |
| **SWMM coupling** | Uses `pyswmm` BMI interface internally; no separate SWMM binary required |
| **Input** | GRASS raster maps (DEM, rainfall), SWMM `.inp`, ITZI `.ini` config |
| **Output** | Raster time-series: water depth, velocity X/Y, Froude number; tabular node results |
| **Performance** | Single-thread by default; CUDA GPU extension available for large domains |
| **Known gotcha** | Must be run inside an active GRASS session with correct `GISBASE` and `GISDBASE` env vars |

#### SWMM — 1D Drainage Model

| Property | Detail |
|---|---|
| **Runtime wrapper** | `pyswmm` v2.0 (EPA-maintained, C API via SWIG) |
| **File I/O** | `swmm_api` v0.4.73 — full read/write of `.inp`; GeoPandas output for GIS export |
| **Why two libraries** | `pyswmm` for runtime simulation control; `swmm_api` for pre-processing/metadata extraction |
| **Data extractable** | Nodes (junctions, outfalls, storage units), links (conduits, weirs), subcatchments, timeseries |
| **Format support** | SWMM 5.1 and 5.2 `.inp` files |

#### GRASS GIS — Spatial Engine

| Property | Detail |
|---|---|
| **Version required** | 8.4+ (latest stable as of 2026) |
| **Python API** | `grass.script` module — `run_command()`, `read_command()`, `parse_command()` |
| **Session management** | `grass-session` library (0.5+) for headless/embedded initialization |
| **Location/Mapset** | Hierarchical data organization; must be initialized before any raster operation |
| **Raster time-series** | Stored as sequentially named raster maps with timestamp metadata |
| **Key modules used** | `r.in.gdal` (import TIF), `r.info` (validate raster), `g.region` (set computation region) |
| **Critical env vars** | `GISBASE`, `GISDBASE`, `LOCATION_NAME`, `MAPSET`, `GRASS_PYTHON_SKIP_IMPORT_CHECKS` |

### 4.3 Application Layer

| Component | Library | Version | License | Reason |
|---|---|---|---|---|
| GUI Framework | **PySide6** | 6.8+ | LGPL v3 | No fee for commercial apps; Qt Company official support |
| Map Display (Ph1) | **Folium** + `QWebEngineView` | 0.19+ | MIT | Leaflet.js in Qt WebEngine; offline tile support |
| Map Display (Ph2) | **PyQGIS API** | QGIS 3.36+ | GPL v2 | Full raster rendering, layer tree, native GIS |
| Realtime Charts | **pyqtgraph** | 0.13+ | MIT | 75–150× faster than matplotlib for streaming data |
| Export Charts | **matplotlib** | 3.9+ | PSF | Publication-quality PNG/PDF/SVG output |
| Data Processing | **pandas** + **numpy** | 2.x / 2.x | BSD | Standard; used internally by ITZI and swmm_api |
| ORM | **SQLAlchemy** | 2.x | MIT | Clean ORM for SQLite → PostgreSQL migration |
| Config | **configparser** | stdlib | PSF | `.ini` file generation for ITZI |
| Packaging | **AppImage** / **PyInstaller** | — | — | Single-file Ubuntu distribution |

### 4.4 Data Layer

#### Phase 1 — SQLite Schema

```sql
-- Core run tracking
CREATE TABLE runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_uuid    TEXT UNIQUE NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    status      TEXT CHECK(status IN ('running','completed','failed')),
    swmm_inp    TEXT,           -- absolute path to .inp file
    grass_mapset TEXT,
    start_time  DATETIME,
    end_time    DATETIME,
    timestep_s  INTEGER,
    itzi_ini    TEXT,           -- generated .ini content snapshot
    output_dir  TEXT,
    duration_s  REAL,
    error_msg   TEXT
);

-- SWMM network nodes
CREATE TABLE nodes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id      INTEGER REFERENCES runs(id),
    node_id     TEXT NOT NULL,
    node_type   TEXT,           -- JUNCTION, OUTFALL, STORAGE
    x           REAL,
    y           REAL,
    elevation   REAL,
    max_depth   REAL,
    UNIQUE(run_id, node_id)
);

-- SWMM network links
CREATE TABLE links (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id      INTEGER REFERENCES runs(id),
    link_id     TEXT NOT NULL,
    link_type   TEXT,           -- CONDUIT, WEIR, ORIFICE
    from_node   TEXT,
    to_node     TEXT,
    length      REAL
);

-- Water level timeseries per node
CREATE TABLE timeseries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id_fk  INTEGER REFERENCES nodes(id),
    timestamp   DATETIME NOT NULL,
    depth_m     REAL,
    flow_cms    REAL,
    flooding_cms REAL
);

-- Raster outputs registry
CREATE TABLE raster_exports (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id      INTEGER REFERENCES runs(id),
    raster_type TEXT,           -- depth, velocity_x, velocity_y
    file_path   TEXT,
    timestep_index INTEGER,
    sim_time    DATETIME
);
```

#### Phase 2 — PostgreSQL/PostGIS Schema Extension

- Nodes gain `geom GEOMETRY(POINT, 4326)` column
- Links gain `geom GEOMETRY(LINESTRING, 4326)` column
- Raster exports reference PostGIS raster type
- `timeseries` table partitioned by `run_id` for performance
- TimescaleDB hypertable on `timeseries` for fast range queries

### 4.5 Packaging & Distribution

```
Distribution Package (AppImage)
├── eWM.AppImage                    ← single executable, no install required
│   ├── Python 3.11 runtime
│   ├── PySide6 (bundled Qt 6.8)
│   ├── All Python dependencies (itzi, pyswmm, swmm_api, ...)
│   ├── eWM application source
│   └── OSM offline tiles (Vietnam region, ~200MB .mbtiles)
│
├── install.sh                      ← installs GRASS GIS 8.4 via apt
└── README.md                       ← quick-start in Vietnamese + English
```

> **Note:** GRASS GIS is NOT bundled in the AppImage (too large, ~2GB). It is installed separately via `sudo apt install grass` as a one-time setup step handled by `install.sh`.

---

## 5. Feature Scope

### 5.1 Phase 1 — MVP (This Contract)

#### Module 1: Security & License System

- [x] Password login screen (bcrypt-hashed, stored in encrypted local config)
- [x] License token file (encrypted JSON: issue date, expiry date, machine fingerprint)
- [x] On valid login → Main Window
- [x] On expired license → Read-only mode; simulation locked; results still viewable; expiry message displayed
- [x] "Days remaining" shown in status bar
- [x] License check repeated each time "Run" is clicked (not only at startup)

#### Module 2: Input Tab

- [x] **SWMM File Selector** — `QFileDialog` filtered to `.inp`; path displayed with validation tick
- [x] **SWMM Validator** — runs `swmm_api` parse; displays node count, link count, subcatchment count, CRS if embedded
- [x] **Raster Import Wizard** — browse TIF/ASC/IMG; preview resolution and extent; import via `r.in.gdal` into active GRASS mapset
- [x] **GRASS Mapset Selector** — create new location or open existing; displays current location name and CRS
- [x] **CRS Warning** — alert if SWMM node coordinates don't overlap raster extent
- [x] **Validation Summary Panel** — green/yellow/red status for each input; "Ready to simulate" indicator
- [x] **Open GRASS GUI** button — launches full GRASS GIS GUI as external process for power users

#### Module 3: Simulation Tab

- [x] **Start Date/Time picker** (QDateTimeEdit)
- [x] **End Date/Time picker** with validation: end > start, minimum 1 hour, maximum bounded by rainfall data duration
- [x] **Timestep selector** (seconds, dropdown: 10s / 30s / 60s / 120s / custom)
- [x] **Stability hint** — calculated Courant number estimate displayed in tooltip
- [x] **Apply Default Settings** button — fills sensible defaults based on loaded raster resolution
- [x] **ITZI .ini auto-generator** — builds complete `.ini` from form values; shows preview in collapsible `QPlainTextEdit`
- [x] **Manual .ini override** — user can edit the preview before running
- [x] Simulation settings saved to SQLite on confirmation

#### Module 4: Output Tab + Run Workflow

- [x] **CSV/TXT output path** selector with default `~/ewm_runs/{timestamp}/`
- [x] **Raster output prefix** input field
- [x] **Run Button** — triggers full simulation pipeline:

```
Click Run
    │
    ├─ 1. License check (re-validate)
    ├─ 2. Input validation (all green required)
    ├─ 3. Write final .ini to temp directory
    ├─ 4. Start ITZIRunner (QThread)
    │       ├─ Initialize GRASS session (grass-session)
    │       ├─ Launch ITZI as subprocess
    │       └─ Stream stdout line-by-line → LogStreamPanel signal
    ├─ 5. LogStreamPanel updates in real-time
    │       ├─ Current command highlighted
    │       ├─ ITZI progress % shown in progress bar
    │       ├─ Warnings shown in amber
    │       └─ Errors shown in red
    └─ On completion:
            ├─ SUCCESS → enable Results button, save run metadata, parse outputs
            └─ FAILURE → error dialog with last 50 log lines, stderr in red
```

- [x] **Loading overlay** with animated spinner while simulation runs
- [x] **Abort button** — sends SIGTERM to subprocess; cleans up temp files
- [x] **Elapsed time counter** in status bar during run

#### Module 5: Results Viewer Window

**Map Panel (Folium + QWebEngineView)**
- [x] SWMM nodes rendered as circle markers, color-coded by max flood depth (green → yellow → red)
- [x] SWMM links rendered as polylines, color-coded by flow velocity
- [x] Flood raster overlay (ITZI output exported as PNG tiles, overlaid as `L.imageOverlay`)
- [x] OSM base map from local `.mbtiles` (offline) or OpenStreetMap CDN (online)
- [x] Click node → fires JavaScript → Python bridge via `QWebChannel` → populates right panel

**Layer Control Panel (left)**
- [x] Layer tree: Nodes layer | Links layer | Flood Raster | Base Map
- [x] Toggle visibility per layer
- [x] Opacity slider for flood raster

**Node Properties Panel (right)**
- [x] Node ID, type, ground elevation, invert elevation
- [x] Max simulated depth, max simulated flow
- [x] Flood duration (hours above ground level)

**Bottom Split Panel**
- [x] **Timeseries Table** (left) — `QTableWidget`: columns = Timestamp | Depth (m) | Flow (m³/s) | Flooding (m³/s)
- [x] **Water Level Chart** (right) — `pyqtgraph.PlotWidget`: x = time, y = depth; ground level shown as dashed red line; flooding periods shaded

**Toolbar**
- [x] Pan | Zoom In | Zoom Out | Fit to Extent | Export Map PNG | Export Chart PNG | Export CSV

#### Module 6: Application Shell

- [x] **Menu bar**: Project (New / Open / Save `.ewm`) | View | Settings | License | Help
- [x] **Status bar**: state indicator (Ready / Running / Completed / Error) + elapsed time + active mapset name
- [x] **Settings dialog**: default output directory, default timestep, map tile source, GRASS GIS path
- [x] **Project file** (`.ewm`): JSON containing all form values, input paths, last run UUID — reopenable
- [x] **Application log**: rotated log files in `~/.ewm/logs/` with DEBUG level for troubleshooting
- [x] **About dialog**: version, license info, technology credits

---

### 5.2 Phase 2 — Enhanced GIS

> **Estimated effort:** 30 man-days | **Duration:** 6 weeks | **Budget:** ~160M VND / ~$6,300 USD

| Feature | Description |
|---|---|
| PostgreSQL/PostGIS backend | Migrate from SQLite; spatial queries on node/link geometry |
| PyQGIS map integration | Replace Folium with full QGIS canvas: proper raster rendering, symbology, print layout |
| Flood animation | Time slider across ITZI raster snapshots; animated flood progression |
| Multi-run comparison | Side-by-side chart overlay for 2–4 simulation runs on same node |
| Run history browser | Table of all past runs with filter/sort; re-open any run's results |
| PDF report generator | Auto-generate formatted report: inputs, map, charts, statistics |
| Raster export | Export flood depth raster as GeoTIFF with correct CRS for external GIS use |
| Shapefile export | Export nodes/links as shapefile or GeoPackage |
| Batch run mode | Queue multiple `.ini` configurations and run sequentially overnight |

---

### 5.3 Phase 3 — Production & Enterprise

> **Estimated effort:** 20 man-days | **Duration:** 4 weeks | **Budget:** ~110M VND / ~$4,300 USD

| Feature | Description |
|---|---|
| AppImage packager | Single-file Ubuntu distributable with bundled Python + deps |
| Auto-updater | Delta update mechanism — check version on launch, download patch |
| License server | Central license validation server; supports floating licenses |
| GRASS GIS auto-install | `install.sh` script detects and installs correct GRASS version |
| Multi-user session | PostgreSQL backend supports concurrent users with separate run isolation |
| Performance profiling | Identify bottlenecks in large-domain runs; ITZI CUDA integration guide |
| Comprehensive docs | Full Vietnamese + English user manual (30+ pages), admin guide, developer guide |
| Training materials | Slide deck + exercise datasets for user onboarding |

---

### 5.4 Out of Scope (Phase 1)

The following are explicitly **not** included in Phase 1:

- Real-time rainfall data ingestion (API to weather stations)
- Web browser interface
- Mobile app
- QGIS integration (Phase 2)
- Multi-user / concurrent access
- Windows or macOS support
- Cloud/server deployment
- Automated report generation
- Custom SWMM model editor (users prepare `.inp` externally)
- Real-time flood forecasting / operational warning system

---

## 6. User Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                          APPLICATION FLOW                               │
└────────────────────────────────────────────────────────────────────────┘

Launch App
    │
    ▼
┌──────────────────────────────────────┐
│           LOGIN SCREEN                │
│  ┌─────────────────────────────────┐ │
│  │ Password: [________________]   │ │
│  │ [          Login          ]    │ │
│  └─────────────────────────────────┘ │
└──────────────────────────────────────┘
    │                    │
    │ Valid + Licensed    │ Invalid / Expired
    ▼                    ▼
MAIN WINDOW          ERROR MESSAGE
    │                (expired: read-only
    │                 if prior results exist)
    ▼
┌──────────────────────────────────────────────────────────────────────┐
│  MAIN WINDOW                                                          │
│  Header: eWM - eWater Warning Model     [Status: Ready]              │
│  Menu: Project | View | Settings | License | Help                    │
│  ┌────────────┬───────────────────┬───────────────────────────────┐  │
│  │ INPUT TAB  │  SIMULATION TAB   │       OUTPUT TAB              │  │
│  └────────────┴───────────────────┴───────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘

INPUT TAB
    │
    ├─ Select SWMM .inp → validate → show node/link counts
    ├─ Select/Import Raster → GRASS r.in.gdal → confirm mapset
    ├─ Validation Panel shows green/red for each input
    └─ All green → "Ready" indicator
    │
    ▼
SIMULATION TAB
    │
    ├─ Set Start Time / End Time
    ├─ Set Timestep
    ├─ Review auto-generated ITZI .ini
    └─ Confirm settings
    │
    ▼
OUTPUT TAB
    │
    ├─ Set output directory
    ├─ Set raster output prefix
    └─ Click [RUN]
         │
         ▼
    ┌──────────────────────────────────────────┐
    │  LOADING STATE                            │
    │  ┌──────────────────────────────────────┐│
    │  │  ● Running ITZI simulation...        ││
    │  │  Progress: [████████░░░░] 67%        ││
    │  │                                      ││
    │  │  [LOG PANEL]                         ││
    │  │  12:34:01 Starting GRASS session     ││
    │  │  12:34:03 Loading DEM raster...      ││
    │  │  12:34:08 Coupling SWMM model...     ││
    │  │  12:34:12 Time step 0:00:30 / 6:00  ││
    │  │  ...                                 ││
    │  └──────────────────────────────────────┘│
    │  [Abort]             Elapsed: 00:02:34   │
    └──────────────────────────────────────────┘
         │                     │
         │ SUCCESS             │ FAILURE
         ▼                     ▼
    [Results]            ERROR DIALOG
    button enabled       (last 50 log lines)
         │
         ▼
┌──────────────────────────────────────────────────────────────────────┐
│  RESULTS WINDOW                                                        │
│  Toolbar: [Pan] [Zoom+] [Zoom-] [Fit] [Export Map] [Export CSV]      │
│                                                                        │
│  ┌──────────┬─────────────────────────────────┬───────────────────┐  │
│  │  LAYER   │         GIS MAP                  │  NODE PROPERTIES  │  │
│  │  TREE    │                                  │                   │  │
│  │          │   [Node markers on OSM base]     │  ID: J_001        │  │
│  │ ✓ Nodes  │   [Link polylines]               │  Type: Junction   │  │
│  │ ✓ Links  │   [Flood raster overlay]         │  Elev: 12.3m      │  │
│  │ ✓ Raster │                                  │  Max Depth: 0.45m │  │
│  │ ✓ OSM    │   ← Click any node →             │  Flood Duration:  │  │
│  │          │      populates right panel        │  2h 15min         │  │
│  └──────────┴─────────────────────────────────┴───────────────────┘  │
│                                                                        │
│  ┌────────────────────────────┬───────────────────────────────────┐   │
│  │     TIMESERIES TABLE       │       WATER LEVEL CHART           │   │
│  │  Time  | Depth | Flow | ..│                                    │   │
│  │  00:00 | 0.00  | 0.21 | ..│   depth  ▲                        │   │
│  │  00:30 | 0.12  | 0.45 | ..│   (m)    │    ╭──╮               │   │
│  │  01:00 | 0.38  | 0.89 | ..│          │   ╭╯  ╰╮              │   │
│  │  01:30 | 0.45  | 0.92 | ..│  ground  ├───────────────────────│   │
│  │  ...   | ...   | ...  | ..│  level   │              ╰──╯      │   │
│  └────────────────────────────┴───────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 7. Screen Specifications

### 7.1 Login Screen

```
┌─────────────────────────────────────────────────┐
│                                                   │
│         eWM — eWater Warning Model               │
│         Urban Flood Simulation Platform           │
│                                                   │
│              [APPLICATION LOGO]                   │
│                                                   │
│    Password:  [________________________]          │
│                                                   │
│               [       Login       ]               │
│                                                   │
│    ─────────────────────────────────────────     │
│    License status: Valid until 2027-06-16         │
│    Version: 1.0.0                                 │
│                                                   │
└─────────────────────────────────────────────────┘
```

**Behaviors:**
- Password field is `QLineEdit` with `EchoMode = Password`
- Enter key submits (same as clicking Login)
- After 3 failed attempts: 30-second lockout with countdown
- Expired license shows: "License expired on YYYY-MM-DD. Contact administrator."

---

### 7.2 Main Window — Input Tab

```
┌──────────────────────────────────────────────────────────────────────────┐
│  eWM - eWater Warning Model                            [Status: Ready]   │
│  File | View | Settings | License | Help                                 │
├───────────────────────────────────────────────────────────────────────── │
│  [ INPUT ]      [ SIMULATION ]      [ OUTPUT ]                           │
├────────────────────────────────────┬─────────────────────────────────────┤
│  INPUT CONFIGURATION               │  VALIDATION STATUS                  │
│                                    │                                      │
│  SWMM Input File                   │  ✓ SWMM File: Valid                 │
│  [/path/to/model.inp        ] [..] │    Nodes: 147  Links: 189           │
│                                    │    Subcatchments: 52                │
│  GRASS GIS Mapset                  │                                      │
│  Location: [urban_flood_2026  ]    │  ✓ Raster: Imported                 │
│  Mapset:   [PERMANENT         ]    │    Resolution: 5m × 5m              │
│  [Create New] [Open Existing]      │    Extent: 10.5km × 8.2km          │
│                                    │    CRS: VN-2000                     │
│  Raster Data                       │                                      │
│  DEM:       [dem_5m.tif   ] [..]   │  ✓ CRS Match: OK                   │
│  Rainfall:  [rain_2h.tif  ] [..]   │    SWMM nodes within raster extent  │
│  [Import to GRASS]                 │                                      │
│                                    │  ─────────────────────────────────  │
│  [Open GRASS GUI]                  │  ● All inputs valid                  │
│                                    │    Ready to configure simulation     │
└────────────────────────────────────┴─────────────────────────────────────┘
│  Status: Ready │ Mapset: urban_flood_2026/PERMANENT │ License: 365 days  │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### 7.3 Main Window — Simulation Tab

```
┌──────────────────────────────────────────────────────────────────────────┐
│  [ INPUT ]      [ SIMULATION ]      [ OUTPUT ]                           │
├─────────────────────────────────┬────────────────────────────────────────┤
│  SIMULATION PERIOD              │  DEFAULT PARAMETERS                    │
│                                 │                                         │
│  Start Time:                    │  Friction model:  [Manning    ▼]       │
│  [2026-06-16] [06:00:00]        │  Manning n:       [0.035       ]       │
│                                 │  Infiltration:    [Green-Ampt  ▼]      │
│  End Time:                      │  Max ponding:     [0.10 m      ]       │
│  [2026-06-16] [12:00:00]        │  Slope threshold: [0.0001      ]       │
│                                 │                                         │
│  Duration: 6 hours              │  [Apply Default Settings]              │
│                                 │                                         │
│  Timestep:  [60 s ▼]            │  ─────────────────────────────────    │
│  Courant hint: ≈ 0.3 (stable)   │  ITZI .ini Preview                    │
│                                 │  ┌─────────────────────────────────┐  │
│                                 │  │ [time]                          │  │
│                                 │  │ start = 2026-06-16 06:00        │  │
│                                 │  │ end   = 2026-06-16 12:00        │  │
│                                 │  │ duration = 21600                │  │
│                                 │  │ record_step = 60                │  │
│                                 │  │                                 │  │
│                                 │  │ [input]                         │  │
│                                 │  │ dem = dem_5m                    │  │
│                                 │  │ rain = rain_2h                  │  │
│                                 │  │ ...                             │  │
│                                 │  └─────────────────────────────────┘  │
└─────────────────────────────────┴────────────────────────────────────────┘
```

---

### 7.4 Main Window — Output Tab (During Run)

```
┌──────────────────────────────────────────────────────────────────────────┐
│  [ INPUT ]      [ SIMULATION ]      [ OUTPUT ]                           │
├────────────────────────────────────────────────────────────────────────── │
│  OUTPUT SETTINGS              ACTION                                      │
│                               ┌───────────────────────────────────────┐  │
│  Output directory:            │  [  ▶  RUN SIMULATION  ]              │  │
│  [~/ewm_runs/20260616_0834]   │                                       │  │
│                               │  [  ■  ABORT           ]  (disabled)  │  │
│  Raster prefix: [flood_run1]  │                                       │  │
│                               │  [  ◉  RESULTS         ]  (disabled)  │  │
│  ─────────────────────────────┴───────────────────────────────────────┘  │
│                                                                            │
│  RUN LOG                                              Elapsed: 00:03:47   │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ [08:34:01] Validating license...                                ✓   │ │
│  │ [08:34:01] Initializing GRASS session: urban_flood_2026/PERMANENT   │ │
│  │ [08:34:03] Loading SWMM model: model.inp (147 nodes, 189 links)     │ │
│  │ [08:34:05] Setting GRASS computation region to DEM extent           │ │
│  │ [08:34:07] Starting ITZI engine...                                  │ │
│  │ [08:34:09] Simulation time: 0:10:00 / 6:00:00 (2.8%)    ████░░░    │ │
│  │ [08:35:12] Simulation time: 1:00:00 / 6:00:00 (16.7%)   ████░░░    │ │
│  │ [08:36:44] Simulation time: 2:00:00 / 6:00:00 (33.3%)   ████░░░    │ │
│  │ [08:37:51]  ⚠ WARNING: ponding at node J_023              ~~~~~~    │ │
│  │ [08:38:12] Simulation time: 3:00:00 / 6:00:00 (50.0%)   ████░░░    │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│  Progress: [██████████████░░░░░░░░░░░░░░] 50%                            │
└──────────────────────────────────────────────────────────────────────────┘
│  Status: RUNNING │ Mapset: urban_flood_2026/PERMANENT │ License: 365 days │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### 7.5 Results Window

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Results — Run: 20260616_0834    [Pan][+][-][Fit][Export Map][Export CSV] │
├──────────────┬───────────────────────────────────────┬────────────────────┤
│  LAYERS      │         GIS MAP                        │  NODE PROPERTIES  │
│              │                                        │                   │
│  ✓ Nodes     │  ┌─────────────────────────────────┐  │  Node: J_023      │
│  ✓ Links     │  │                                 │  │  Type: Junction   │
│  ✓ Flood     │  │  [OpenStreetMap tiles as base]  │  │  Elevation: 8.2m  │
│  ✓ Base Map  │  │                                 │  │  Max Depth: 0.82m │
│              │  │  ● ● ● ●  (nodes, color-coded)  │  │  Flooding: YES    │
│  Opacity:    │  │  ─────── (links)                │  │  Duration: 1h 45m │
│  Flood: 70%  │  │  ░▒▓█    (flood raster)         │  │                   │
│  [──●──────] │  │                                 │  │  Peak Flow:       │
│              │  │              ↑                  │  │  2.34 m³/s        │
│  Legend      │  │    [Clicked node: J_023]        │  │  @ 08:45:00       │
│  ■ >0.5m     │  │                                 │  │                   │
│  ■ 0.2-0.5m  │  └─────────────────────────────────┘  │                   │
│  ■ 0-0.2m    │                                        │                   │
│  ○ Dry       │                                        │                   │
├──────────────┴───────────────────────────────────────┴────────────────────┤
│  TIME SERIES TABLE                     │  WATER LEVEL CHART              │
│                                        │                                  │
│  Time     Depth(m)  Flow(m³/s)  Flood  │  Depth ▲                        │
│  06:00:00   0.00      0.21       0.00  │  (m)   │    ╭──╮                │
│  06:30:00   0.12      0.45       0.00  │  0.8   │   ╭╯  │                │
│  07:00:00   0.38      0.89       0.00  │  0.6   │  ╭╯   ╰╮              │
│  07:30:00   0.82      1.23       0.42  │  0.4   │ ─╯     │              │
│  08:00:00   0.71      1.05       0.28  │  0.2   │        ╰──────        │
│  08:30:00   0.45      0.67       0.00  │  0.0   └──────────────────→   │
│  ...        ...       ...        ...   │       06:00  08:00  10:00      │
└────────────────────────────────────────┴──────────────────────────────────┘
```

---

## 8. Team Composition

| Role | Allocation | Key Responsibilities |
|---|---|---|
| **Lead Developer** (Senior Python + PySide6 + Backend) | **1.0 FTE** | Architecture design; GRASS GIS session management; ITZI subprocess integration; QThread run engine; SQLite schema and ORM; license system; `.ewm` project file format; code review |
| **Frontend Developer** (Mid Python + PySide6) | **1.0 FTE** | All UI widget implementation; Input/Simulation/Output tabs; Folium map panel + QWebChannel bridge; pyqtgraph charts; timeseries table; export functions; UI polish and responsiveness |
| **GIS / Hydraulics Consultant** | **0.5 FTE** | GRASS GIS environment setup scripts; SWMM test data preparation; ITZI `.ini` specification validation; simulation output interpretation; acceptance testing with real hydrological data |
| **UI/UX Designer** | **0.3 FTE** | Screen wireframes; high-fidelity mockups for all 5 screens; color palette and typography; icon set (SVG); component style guide |
| **QA Engineer** | **0.5 FTE** | Test plan and test cases; regression testing after each sprint; Ubuntu 22.04 + 24.04 compatibility testing; performance benchmarking; bug reporting and verification |
| **Project Manager** | **0.2 FTE** | Sprint planning and tracking; client communication; risk monitoring; weekly status reports; milestone sign-off coordination |

**Effective capacity:** 3.5 FTE

**Recommended hiring profile for Lead Developer:**
- 4+ years Python desktop app development
- Experience with PySide6 or PyQt5/6
- Comfortable with subprocess management and IPC
- Bonus: any GIS or scientific computing experience

---

## 9. Implementation Timeline

### 9.1 Week-by-Week Plan

```
WEEK 1 — June 16–20: Foundation & Environment Spike
═══════════════════════════════════════════════════

Lead Dev     │ Set up project structure, venv, pre-commit hooks
             │ CRITICAL SPIKE: Install ITZI in venv; initialize GRASS
             │ session headlessly via grass-session; confirm ITZI
             │ runs and produces output from Python script
             │ → Go/No-Go decision on this architecture by Friday EOD

Frontend Dev │ Bootstrap PySide6 app skeleton (main.py, config, logging)
             │ Implement Login screen (password, license token parse)
             │ Implement MainWindow shell with 3 tab placeholders

GIS Consult  │ Prepare sample data: SWMM .inp (EPA example, adapted)
             │ DEM raster (SRTM 30m, resampled to 5m via GRASS)
             │ Rainfall raster time-series for 6-hour storm event
             │ Run ITZI manually via CLI to verify sample data is valid

Designer     │ Deliver all wireframes (5 screens)
             │ Define color palette and typography system

Milestone M1 │ ITZI runs headlessly in Python on Ubuntu 22.04 ✓

───────────────────────────────────────────────────────────────────

WEEK 2 — June 23–27: Input Pipeline
═════════════════════════════════════

Lead Dev     │ SWMM parser module using swmm_api:
             │   parse_swmm_inp() → SWMMModel dataclass
             │   extract_nodes(), extract_links(), extract_subcatchments()
             │ GRASS import wrappers:
             │   GRASSSession.import_raster(path, name)
             │   GRASSSession.set_region(raster_name)
             │   GRASSSession.validate_crs_match(nodes, raster)

Frontend Dev │ Input Tab full UI:
             │   SWMMFileSelector with validation feedback
             │   GRASSMapsetSelector (create/open)
             │   RasterImportWizard (browse → preview → import)
             │   ValidationPanel (green/red per item)

GIS Consult  │ Document exact GRASS module sequence for DEM import
             │ Test r.in.gdal with VN-2000 CRS raster
             │ Confirm GRASS region covers SWMM model extent

Designer     │ Deliver high-fidelity mockups for all screens
             │ Deliver icon set (PNG + SVG, 16px/24px/32px)

───────────────────────────────────────────────────────────────────

WEEK 3 — June 30 – July 4: Simulation Configuration
═════════════════════════════════════════════════════

Lead Dev     │ ITZI .ini generator:
             │   IniGenerator.from_form_values(start, end, timestep,
             │     dem_map, rain_map, swmm_inp, output_prefix) → str
             │ Validation logic:
             │   end > start, timestep valid, time range ≤ rainfall data
             │   Courant number estimation
             │ Write .ini to temp directory; round-trip parse test

Frontend Dev │ Simulation Tab UI:
             │   QDateTimeEdit pickers with constraint validation
             │   Timestep dropdown + custom input
             │   Courant hint label
             │   .ini preview widget (QPlainTextEdit, read/edit toggle)
             │   Apply Default Settings button

GIS Consult  │ Review IniGenerator output against ITZI docs
             │ Validate all ITZI .ini section keys and valid value ranges
             │ Document: which .ini params are mandatory vs optional

Milestone M2 │ Can load .inp + raster, generate valid .ini file ✓

───────────────────────────────────────────────────────────────────

WEEK 4 — July 7–11: Run Engine
════════════════════════════════

Lead Dev     │ ITZIRunner (QThread):
             │   Start GRASS session in thread
             │   Launch ITZI as subprocess with .ini
             │   Read stdout line-by-line via QTextStream
             │   Emit signals: log_line(str), progress(int), finished(bool)
             │   Handle SIGTERM for abort
             │   Clean up temp files on success/failure/abort

Frontend Dev │ Output Tab UI:
             │   OutputPathSelector with default ~/ewm_runs/{timestamp}
             │   Run / Abort / Results buttons with correct enabled states
             │   LogStreamPanel: QPlainTextEdit auto-scroll, color lines
             │   Progress bar connected to ITZIRunner.progress signal
             │   Loading overlay with spinner animation
             │   Elapsed time counter (QTimer, 1-second tick)

GIS Consult  │ Document expected ITZI stdout format for log parsing
             │ Identify progress percentage pattern in ITZI output
             │ Note any ITZI error codes and their meanings

Milestone M3 │ End-to-end simulation runs with live logs in GUI ✓

───────────────────────────────────────────────────────────────────

WEEK 5 — July 14–18: Map & Database
════════════════════════════════════

Lead Dev     │ SQLite schema and SQLAlchemy models
             │ RunRepository: save_run(), get_run(), list_runs()
             │ NodeRepository: save_nodes(), get_nodes_for_run()
             │ On simulation complete: parse SWMM node coordinates
             │   from swmm_api, save to DB
             │ Raster to PNG tile export for map overlay
             │   (gdal.Translate .tif → colored PNG with colormap)

Frontend Dev │ Folium map panel:
             │   Generate HTML: OSM base + node markers + links
             │   Color-code nodes by max depth (green→yellow→red)
             │   QWebChannel bridge: JS click → Python slot
             │   Load HTML into QWebEngineView
             │   MBTiles local tile server (threading.Thread + http.server)

GIS Consult  │ Run full simulation with sample data end-to-end
             │ Validate ITZI output rasters in GRASS
             │ Confirm water depth values are physically plausible

───────────────────────────────────────────────────────────────────

WEEK 6 — July 21–25: Results Viewer
═════════════════════════════════════

Lead Dev     │ TimeseriesRepository: save_timeseries(), get_for_node()
             │ SWMM output parser: read .txt/.csv ITZI node results
             │ Parse timestamps, depth, flow, flooding columns
             │ Store in timeseries table

Frontend Dev │ Results Window:
             │   WaterLevelChart (pyqtgraph.PlotWidget)
             │     x = datetime, y = depth
             │     Ground level dashed red line
             │     Flooding periods shaded yellow
             │   TimeseriesTable (QTableWidget, sortable)
             │   NodePropertiesPanel (right panel)
             │   LayerTreePanel with visibility toggles
             │   Flood raster overlay on map

GIS Consult  │ Validate Results viewer shows correct values
             │ Cross-check chart data vs ITZI raw output files
             │ Confirm node coordinates display correctly on map

Milestone M4 │ Map + chart working with real simulation output ✓

───────────────────────────────────────────────────────────────────

WEEK 7 — July 28 – August 1: Polish & Integration
════════════════════════════════════════════════════

Lead Dev     │ License system:
             │   generate_license_token(expiry, machine_id) → encrypted JSON
             │   validate_license_token(path) → LicenseStatus
             │   Machine fingerprint (CPU id + MAC address hash)
             │ .ewm project file (JSON save/open)
             │ Settings dialog backend
             │ Application log rotation (~/.ewm/logs/)
             │ About dialog, version info

Frontend Dev │ Export functions:
             │   Map screenshot (QWebEngineView.grab())
             │   Chart PNG (pyqtgraph.exporters.ImageExporter)
             │   CSV export (pandas.DataFrame.to_csv())
             │ Layer control panel (opacity slider, toggle)
             │ Toolbar complete implementation
             │ Menu bar complete (File / View / Settings / License / Help)
             │ Status bar: state + elapsed + mapset

Milestone M5 │ All modules integrated; license system working ✓

───────────────────────────────────────────────────────────────────

WEEK 8 — August 4–8: Testing & Handover
═════════════════════════════════════════

Lead Dev     │ Ubuntu 24.04 compatibility testing + fixes
             │ Code review and cleanup
             │ Resolve any GRASS session edge cases found in testing

Frontend Dev │ Ubuntu 22.04 regression testing
             │ UI polish from QA feedback
             │ Fix any rendering issues in QWebEngineView

GIS Consult  │ Full acceptance test with real Vietnamese DEM + rainfall data
             │ Verify all acceptance criteria (13 functional + 6 performance)
             │ Sign off on simulation accuracy

QA Engineer  │ Execute full test suite (all 13 acceptance criteria)
             │ Performance benchmark (startup, parse, import, run, chart)
             │ Bug report and re-test cycle

PM           │ Prepare handover package
             │ Schedule demo session
             │ Collect sign-off from client

Milestone M6 │ Tested on Ubuntu 22.04 + 24.04; handover package delivered ✓
```

---

### 9.2 Milestones

| # | Milestone | Target Date | Criteria |
|---|---|---|---|
| **M1** | Environment Verified | June 20, 2026 | ITZI runs headlessly in Python venv on Ubuntu 22.04; GRASS session initializes without CLI |
| **M2** | Input Pipeline Ready | July 4, 2026 | Load .inp, import raster to GRASS, generate valid .ini |
| **M3** | Simulation Runs | July 11, 2026 | Full run from GUI with live log streaming; output files produced |
| **M4** | Results Visible | July 25, 2026 | Map shows nodes/links; click node shows chart; data matches ITZI output |
| **M5** | MVP Complete | August 1, 2026 | All modules integrated; license system active; .ewm project file works |
| **M6** | Handover | August 8, 2026 | Passes all acceptance criteria on Ubuntu 22.04 + 24.04; docs delivered |

---

### 9.3 Man-Day Allocation

| Work Group | Client Doc M/D | Our Allocation | Team Roles |
|---|---|---|---|
| 1. Requirements & proposal | 2 | 2 | PM + Lead |
| 2. ITZI/GRASS/SWMM feasibility spike | 3 | **4** | Lead + GIS (+1 for GRASS session risk) |
| 3. UX flow & wireframes | 2 | 2 | Designer |
| 4. App framework (shell + login) | 5 | **6** | Lead + Frontend |
| 5. Input & simulation setup | 4 | **5** | Both Devs |
| 6. Output & run workflow | 5 | **6** | Both Devs |
| 7. Results viewer | 6 | **8** | Both Devs + GIS |
| 8. Testing & bug fix | 4 | **5** | QA + Both Devs |
| 9. Handover documentation | 2 | 2 | Lead + PM |
| 10. Progress reports & coordination | 3 | 3 | PM |
| 11. Risk buffer | 4 | **5** | All |
| **Total** | **40** | **48** | |

> **Why +8 M/D over the client document?**
> The 20% uplift addresses three consistently underestimated areas:
> 1. GRASS GIS session management in embedded Python context (no existing PySide6 example to copy)
> 2. QWebChannel JS↔Python bridge for map node click events
> 3. Ubuntu 22.04 vs 24.04 PySide6 Qt library compatibility edge cases

---

## 10. Budget Breakdown

### 10.1 Human Resources

*Based on Vietnamese IT market rates, 2026. 1 USD ≈ 25,400 VND.*

| Role | Daily Rate (VND) | Daily Rate (USD) | Days | Total VND | Total USD |
|---|---|---|---|---|---|
| Lead Developer (Senior) | 2,500,000 | $98 | 28 | 70,000,000 | $2,756 |
| Frontend Developer (Mid) | 1,800,000 | $71 | 28 | 50,400,000 | $1,985 |
| GIS/Hydraulics Consultant | 2,000,000 | $79 | 12 | 24,000,000 | $945 |
| UI/UX Designer | 1,500,000 | $59 | 6 | 9,000,000 | $354 |
| QA Engineer | 1,200,000 | $47 | 10 | 12,000,000 | $472 |
| Project Manager | 2,200,000 | $87 | 5 | 11,000,000 | $433 |
| **Labor Subtotal** | | | **89** | **176,400,000** | **$6,945** |

> Note: "Days" per role reflects calendar-allocated work effort including meetings, review, and integration. Total productive M/D = 48; overhead (standups, reviews, coordination) accounts for the remaining ~41 person-days across all roles.

### 10.2 Infrastructure & Tools

| Item | VND | USD | Notes |
|---|---|---|---|
| Cloud dev/test VM (8 weeks, Ubuntu 22.04) | 3,500,000 | $138 | Shared between Lead + Frontend |
| Ubuntu 24.04 compatibility test instance | 1,500,000 | $59 | 2-week spot instance |
| OSM offline tile bundle (Vietnam region) | 0 | $0 | Free export from openstreetmap.org |
| Software licenses | 0 | $0 | All tools are open-source / LGPL / MIT |
| **Infra Subtotal** | **5,000,000** | **$197** | |

### 10.3 Phase Summary

| Phase | Scope | Duration | Labor (VND) | Infra (VND) | Buffer 15% (VND) | **Total VND** | **Total USD** |
|---|---|---|---|---|---|---|---|
| **Phase 1 — MVP** | Login + 3 tabs + run + basic results | 8 weeks | 176,400,000 | 5,000,000 | 27,210,000 | **~208,610,000** | **~$8,213** |
| **Phase 2 — Enhanced GIS** | PostGIS + QGIS map + animation + reports | 6 weeks | ~135,000,000 | 3,500,000 | 20,775,000 | **~159,275,000** | **~$6,270** |
| **Phase 3 — Production** | Packaging + updater + license server | 4 weeks | ~92,000,000 | 2,000,000 | 14,100,000 | **~108,100,000** | **~$4,256** |
| **Total — All Phases** | | **18 weeks** | ~403,400,000 | 10,500,000 | 62,085,000 | **~475,985,000** | **~$18,739** |

### 10.4 International Rate Comparison

For clients benchmarking against international freelance/agency rates:

| Metric | Value |
|---|---|
| Blended hourly rate (team average) | $55–65/hour |
| Total billable hours (Phase 1, 89 person-days) | ~712 hours |
| Phase 1 at international rates | $39,000–$46,000 USD |
| **Phase 1 at Vietnamese rates** | **~$8,200 USD** |
| Cost advantage | **~80% lower than Western market** |

---

## 11. Risk Register

| ID | Risk | Probability | Impact | Score | Mitigation | Owner | Trigger |
|---|---|---|---|---|---|---|---|
| **R1** | ITZI GRASS session fails in embedded PySide6 context — `grass-session` can't initialize headlessly | High | Critical | 🔴 | Week 1 spike test. Fallback: run ITZI in a pre-initialized GRASS shell subprocess; pass `.ini` via file instead of Python API | Lead Dev | M1 deadline |
| **R2** | SWMM `.inp` format variation breaks `swmm_api` parser | Medium | High | 🟠 | Use `swmm_api` which handles all SWMM 5.x variants; add pre-parse validation; show raw parse error to user | Lead Dev | Week 2 |
| **R3** | Client provides no real test data until Week 5+ | High | Medium | 🟠 | Build and test with EPA public example datasets; keep data layer generic; accept any valid SWMM 5.x .inp | PM | Week 1 kickoff |
| **R4** | PySide6 `QWebEngineView` segfault on Ubuntu 24.04 (Qt version mismatch) | Medium | High | 🟠 | Ship PySide6 wheels that bundle Qt 6.8 — do NOT rely on system Qt; test on clean Ubuntu 24.04 VM in Week 1 | Frontend Dev | Week 1 |
| **R5** | ITZI simulation takes >30 minutes on client hardware | Medium | High | 🟠 | Cap demo raster at 200×200 cells, 2-hour simulation window; document hardware requirements (8+ CPU cores, 16GB RAM for production runs) | GIS Consult | Week 4 |
| **R6** | Scope creep: client requests QGIS integration, animations, or reports in Phase 1 | High | Medium | 🟠 | Lock Phase 1 scope in signed SoW before development starts; maintain change log; offer Phase 2 as formal upgrade | PM | Ongoing |
| **R7** | `QWebChannel` JS↔Python bridge unreliable for node click events | Medium | Medium | 🟡 | Test in Week 5; fallback: use URL scheme interception (`QWebEngineView.urlChanged`) to pass node ID | Frontend Dev | Week 5 |
| **R8** | License token file can be copied across machines | Low | Medium | 🟡 | Add machine fingerprint (SHA-256 of CPU model + MAC address) to token; warn if mismatch | Lead Dev | Week 7 |
| **R9** | GRASS GIS 8.4 not available in Ubuntu 22.04 default apt repos | Medium | High | 🟠 | Use UbuntuGIS PPA: `sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable`; document in `install.sh` | Lead Dev | Week 1 |
| **R10** | Team member availability disruption (illness, other project) | Low | Medium | 🟡 | 15% budget buffer; modular design allows parallel work to continue independently | PM | Ongoing |

---

## 12. Technical Deep Dive

### 12.1 ITZI + GRASS GIS Integration

The most complex and risky technical element in the project is embedding the ITZI/GRASS stack inside a PySide6 process. The correct approach:

```python
# engine/grass_session.py

import os
import subprocess
from pathlib import Path

class GRASSSession:
    def __init__(self, gisdb: Path, location: str, mapset: str = "PERMANENT"):
        self.gisdb = gisdb
        self.location = location
        self.mapset = mapset
        self._process = None

    def initialize(self) -> bool:
        """
        Initialize a GRASS session using grass-session library.
        Must be called before any grass.script operations.
        """
        import grass_session
        grass_session.Session()
        os.environ["GISDBASE"] = str(self.gisdb)
        os.environ["LOCATION_NAME"] = self.location
        os.environ["MAPSET"] = self.mapset
        os.environ["GRASS_PYTHON_SKIP_IMPORT_CHECKS"] = "1"
        grass_session.init(str(self.gisdb / self.location / self.mapset))
        return True

    def import_raster(self, tif_path: Path, map_name: str) -> None:
        import grass.script as gscript
        gscript.run_command(
            "r.in.gdal",
            input=str(tif_path),
            output=map_name,
            overwrite=True
        )

    def set_region_to_raster(self, raster_name: str) -> None:
        import grass.script as gscript
        gscript.run_command("g.region", raster=raster_name, flags="a")


# engine/itzi_runner.py (QThread)

from PySide6.QtCore import QThread, Signal
import subprocess
import re

class ITZIRunner(QThread):
    log_line = Signal(str)
    progress = Signal(int)
    finished = Signal(bool, str)  # success, output_dir

    def __init__(self, ini_path: str, grass_session: GRASSSession):
        super().__init__()
        self.ini_path = ini_path
        self.grass_session = grass_session
        self._abort = False

    def run(self):
        self.grass_session.initialize()
        cmd = ["python", "-m", "itzi", "run", self.ini_path]
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1
        )
        for line in proc.stdout:
            if self._abort:
                proc.terminate()
                self.finished.emit(False, "Aborted by user")
                return
            self.log_line.emit(line.rstrip())
            m = re.search(r"(\d+\.?\d*)\s*%", line)
            if m:
                self.progress.emit(int(float(m.group(1))))
        proc.wait()
        success = proc.returncode == 0
        self.finished.emit(success, "output_dir_from_ini")

    def abort(self):
        self._abort = True
```

---

### 12.2 SWMM Parsing Strategy

```python
# engine/swmm_parser.py

from swmm_api import read_inp_file
from dataclasses import dataclass
from typing import List

@dataclass
class SWMMNode:
    node_id: str
    node_type: str   # JUNCTION, OUTFALL, STORAGE
    x: float
    y: float
    elevation: float

@dataclass
class SWMMLink:
    link_id: str
    link_type: str
    from_node: str
    to_node: str

@dataclass
class SWMMModel:
    nodes: List[SWMMNode]
    links: List[SWMMLink]
    crs: str | None

def parse_swmm_inp(inp_path: str) -> SWMMModel:
    inp = read_inp_file(inp_path)
    nodes = []
    # Junctions
    for node_id, j in inp["JUNCTIONS"].items():
        coord = inp["COORDINATES"].get(node_id)
        nodes.append(SWMMNode(
            node_id=node_id,
            node_type="JUNCTION",
            x=coord.x if coord else 0.0,
            y=coord.y if coord else 0.0,
            elevation=j.elevation,
        ))
    # Links (conduits)
    links = [
        SWMMLink(
            link_id=link_id,
            link_type="CONDUIT",
            from_node=c.from_node,
            to_node=c.to_node,
        )
        for link_id, c in inp["CONDUITS"].items()
    ]
    return SWMMModel(nodes=nodes, links=links, crs=None)
```

---

### 12.3 Run Workflow Engine

```
Click [RUN]
    │
    ├─ 1. LicenseValidator.check() → raise if expired
    ├─ 2. InputValidator.validate_all() → raise if any red
    ├─ 3. IniGenerator.write_to_temp(form_values) → ini_path
    ├─ 4. RunRepository.create_run(metadata) → run_id
    ├─ 5. ITZIRunner(ini_path, grass_session).start()
    │       │
    │       │  QThread (non-blocking — UI stays responsive)
    │       │
    │       ├─ grass_session.initialize()
    │       ├─ subprocess.Popen(["python", "-m", "itzi", "run", ini_path])
    │       ├─ foreach stdout line:
    │       │     emit log_line(line)       → LogStreamPanel.append()
    │       │     emit progress(pct)        → ProgressBar.setValue()
    │       └─ emit finished(success, output_dir)
    │
    └─ On finished signal (main thread):
            ├─ SUCCESS:
            │     RunRepository.mark_completed(run_id, output_dir)
            │     SWMMOutputParser.parse(output_dir) → timeseries data
            │     NodeRepository.save_all(run_id, nodes)
            │     TimeseriesRepository.save_all(node_timeseries)
            │     ResultsButton.setEnabled(True)
            └─ FAILURE:
                  RunRepository.mark_failed(run_id, error_msg)
                  ErrorDialog(log_tail=last_50_lines).exec()
```

---

### 12.4 Map Rendering Strategy

**Phase 1 — Folium + QWebEngineView**

```python
# ui/map_panel.py

import folium
import json
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel

def build_map_html(nodes: list, links: list, tile_url: str) -> str:
    m = folium.Map(location=[lat_center, lon_center], zoom_start=14,
                   tiles=tile_url, attr="OSM")

    for node in nodes:
        color = depth_to_color(node.max_depth)
        folium.CircleMarker(
            location=[node.y, node.x],
            radius=8,
            color=color,
            fill=True,
            tooltip=node.node_id,
            popup=f"<b>{node.node_id}</b><br>Max depth: {node.max_depth:.2f}m",
        ).add_to(m)

    # Inject QWebChannel JS for node click → Python signal
    js = """
    <script src="qwebchannel.js"></script>
    <script>
    new QWebChannel(qt.webChannelTransport, function(channel) {
        window.bridge = channel.objects.bridge;
    });
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('node-marker')) {
            window.bridge.nodeClicked(e.target.dataset.nodeId);
        }
    });
    </script>
    """
    return m._repr_html_() + js
```

**Phase 2 — PyQGIS canvas (replaces Folium)**
- Instantiate `QgsApplication` before `QApplication`
- Embed `QgsMapCanvas` as a Qt widget
- Load GRASS output raster via `QgsRasterLayer`
- Load nodes/links as `QgsVectorLayer` from in-memory GeoPackage
- Full layer tree (`QgsLayerTreeView`) and symbology

---

### 12.5 License System

```python
# core/license.py

import json
import hashlib
import uuid
from datetime import date
from cryptography.fernet import Fernet

LICENSE_KEY = b"..."  # 32-byte key embedded at build time (obfuscated)

def get_machine_fingerprint() -> str:
    import platform, uuid as u
    data = platform.processor() + str(u.getnode())
    return hashlib.sha256(data.encode()).hexdigest()[:16]

def validate_license(token_path: str) -> tuple[bool, str]:
    """Returns (is_valid, message)."""
    try:
        with open(token_path, "rb") as f:
            payload = Fernet(LICENSE_KEY).decrypt(f.read())
        data = json.loads(payload)
        expiry = date.fromisoformat(data["expiry"])
        fingerprint = data.get("machine_id", "")
        if fingerprint and fingerprint != get_machine_fingerprint():
            return False, "License is not valid for this machine."
        if date.today() > expiry:
            days_expired = (date.today() - expiry).days
            return False, f"License expired {days_expired} days ago."
        days_left = (expiry - date.today()).days
        return True, f"Valid — {days_left} days remaining."
    except Exception as e:
        return False, f"Invalid license file: {e}"
```

---

## 13. Acceptance Criteria

### Functional Acceptance Checklist

| # | Criterion | Test Method |
|---|---|---|
| F01 | Login validates password; wrong password shows error | Manual: 3 wrong attempts → lockout |
| F02 | Expired license blocks Run button; shows expiry message | Manual: set expiry to yesterday |
| F03 | SWMM `.inp` loads without crash; node + link counts displayed | Automated: EPA example .inp files |
| F04 | Raster import into GRASS completes; confirms mapset + resolution | Manual: import 50MB TIF |
| F05 | CRS mismatch between .inp and raster shows warning | Manual: mismatched test pair |
| F06 | ITZI `.ini` auto-generated with correct values from form | Automated: compare generated vs expected |
| F07 | Run launches simulation; log streams within 2 seconds | Manual + stopwatch |
| F08 | Successful run enables Results button; failed run shows error with log | Manual: run with valid + broken data |
| F09 | Results map displays nodes as colored markers and links as lines | Manual: visual check |
| F10 | Clicking a node populates timeseries table with correct data | Automated: compare DB values vs ITZI output CSV |
| F11 | Water level chart renders within 1 second for 1,000 timesteps | Automated: benchmark with generated data |
| F12 | CSV export writes correct timeseries data | Automated: compare exported CSV vs source |
| F13 | App does not crash on Ubuntu 22.04 LTS and 24.04 LTS | QA: full regression on both versions |

### Performance Targets

| Metric | Target |
|---|---|
| Cold start time | < 5 seconds |
| SWMM `.inp` parse (200-node model) | < 3 seconds |
| GRASS raster import (50MB TIF) | < 30 seconds |
| Log streaming latency from ITZI stdout | < 500 ms |
| Results map initial render | < 3 seconds |
| Node click → chart display | < 500 ms |
| Chart render (1,000 timesteps) | < 1 second |

---

## 14. Deliverables & Handover

| # | Deliverable | Format | Delivered |
|---|---|---|---|
| D1 | Source code repository | Git (structured Python package with pyproject.toml) | End of Week 8 |
| D2 | Sample dataset | SWMM .inp + 5m DEM TIF + rainfall raster (6-hour event) | End of Week 4 |
| D3 | `install.sh` setup script | Bash, tested on Ubuntu 22.04 + 24.04 | End of Week 7 |
| D4 | User manual | PDF, 15–20 pages, Vietnamese + English, with screenshots | End of Week 8 |
| D5 | Technical architecture document | Markdown (this document + code comments) | End of Week 8 |
| D6 | QA test report | Markdown table: test case → result → pass/fail | End of Week 8 |
| D7 | License token generator script | Python CLI script (for admin use) | End of Week 7 |
| D8 | Demo session | 1-hour live walkthrough via video call + recording | End of Week 8 |
| D9 | Phase 2 scoping document | PDF, feature list + estimates for next phase | End of Week 8 |

### Handover Package Structure

```
ewm-handover/
├── source/
│   ├── ewm/                    ← main application package
│   │   ├── core/               ← license, config, logging
│   │   ├── engine/             ← grass_session, itzi_runner, swmm_parser
│   │   ├── data/               ← SQLAlchemy models, repositories
│   │   ├── ui/                 ← all PySide6 widgets
│   │   └── main.py
│   ├── tests/
│   ├── pyproject.toml
│   └── README.md
├── sample-data/
│   ├── example.inp
│   ├── dem_5m.tif
│   └── rainfall_6h.tif
├── install.sh
├── docs/
│   ├── user-manual-vi.pdf
│   ├── user-manual-en.pdf
│   └── architecture.md
├── tools/
│   └── generate_license_token.py
└── qa-report.md
```

---

## 15. Pitch Summary Card

```
╔══════════════════════════════════════════════════════════════════════╗
║              eWM — eWater Warning Model                              ║
║         Urban Flood Simulation Desktop App for Ubuntu                ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  PHASE 1 — MVP                                                       ║
║  ┌─────────────────┬────────────────────────────────────────────┐   ║
║  │  Duration       │  8 calendar weeks                          │   ║
║  │  Start          │  June 16, 2026                             │   ║
║  │  Delivery       │  August 8, 2026                            │   ║
║  │  Team           │  3.5 FTE (6 roles)                         │   ║
║  │  Effort         │  48 man-days (40 productive + 20% uplift)  │   ║
║  │  Budget         │  ~209,000,000 VND  /  ~$8,200 USD          │   ║
║  │  License cost   │  $0 — 100% open-source engine stack        │   ║
║  └─────────────────┴────────────────────────────────────────────┘   ║
║                                                                      ║
║  FULL PRODUCT (3 phases)                                             ║
║  ┌─────────────────┬────────────────────────────────────────────┐   ║
║  │  Duration       │  18 calendar weeks                         │   ║
║  │  Budget         │  ~476,000,000 VND  /  ~$18,700 USD         │   ║
║  │  Delivery       │  October 2026                              │   ║
║  └─────────────────┴────────────────────────────────────────────┘   ║
║                                                                      ║
║  TECHNOLOGY STACK (all open-source / LGPL)                          ║
║  ┌──────────────────────────────────────────────────────────────┐   ║
║  │  GUI:       PySide6 (Qt 6.8, LGPL — no commercial fee)      │   ║
║  │  1D Model:  SWMM via pyswmm v2.0 + swmm_api v0.4.73         │   ║
║  │  2D Model:  ITZI v25.8 (BMI-coupled, active development)     │   ║
║  │  GIS:       GRASS GIS 8.4+ with grass.script Python API      │   ║
║  │  Map:       Folium + QWebEngineView (Phase 1 / offline OSM)  │   ║
║  │  Charts:    pyqtgraph (realtime) + matplotlib (export)       │   ║
║  │  Database:  SQLite → PostgreSQL/PostGIS (Phase 2)            │   ║
║  │  OS Target: Ubuntu 22.04 LTS + 24.04 LTS                    │   ║
║  └──────────────────────────────────────────────────────────────┘   ║
║                                                                      ║
║  KEY RISK + MITIGATION                                               ║
║  GRASS GIS headless session in PySide6 → Week 1 spike test          ║
║  Go/No-Go decision by June 20, 2026                                  ║
║                                                                      ║
║  VS COMMERCIAL ALTERNATIVES                                          ║
║  MIKE FLOOD:   $20,000–$50,000/license                              ║
║  HEC-RAS 2D:   Free but no Python API, US Army format               ║
║  eWM:          $8,200 development cost, $0 ongoing license           ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

*Document prepared June 16, 2026. All estimates include a 15% contingency buffer.*
*Technologies validated against latest versions available as of June 2026.*
*Vietnamese market labor rates used. Contact for international rate variants.*
