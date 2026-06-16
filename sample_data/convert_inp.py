"""
convert_inp.py
==============
Converts RUNOFF3_SW5.INP (EPA SWMM 2017 Lancaster PA example) into a
complete eWM demo dataset for Ho Chi Minh City, District 7, Vietnam.

Outputs (all written to ./output/):
  eWM_demo.inp              — SWMM .inp with geographic WGS84 coordinates
  rainfall_hcm_2026.csv     — 5-min tropical storm timeseries (mm/hr)
  node_timeseries_demo.csv  — synthetic ITZI-style node output (900 rows)

No external dependencies — uses Python stdlib only.
"""

import math
import os
import csv
from datetime import datetime, timedelta

# ── paths ────────────────────────────────────────────────────────────────────
SRC = os.path.join(os.path.dirname(__file__),
                   "../..", "Downloads", "2017RunoffSWMM5examples",
                   "RUNOFF3_SW5.INP")
SRC = os.path.abspath(SRC)
OUT = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUT, exist_ok=True)

# ── coordinate transform ─────────────────────────────────────────────────────
# Original: arbitrary local feet (centroid ~1570, 1700)
# Target:   WGS84 decimal degrees, District 7, Ho Chi Minh City
LAT0   = 10.7300   # centre lat
LON0   = 106.7100  # centre lon
XC     = 1570.5    # original x centroid (ft)
YC     = 1700.0    # original y centroid (ft)
FT_LAT = 0.3048 / 110_850   # degrees per foot (latitude)
FT_LON = 0.3048 / (110_850 * math.cos(math.radians(LAT0)))

def to_geo(x_ft, y_ft):
    lon = LON0 + (x_ft - XC) * FT_LON
    lat = LAT0 + (y_ft - YC) * FT_LAT
    return round(lon, 6), round(lat, 6)

# ── node metadata ─────────────────────────────────────────────────────────────
# (name, elevation_ft, max_depth_ft)
JUNCTIONS = {
    "804": (7.48,   20.0), "805": (5.24,   20.0), "806": (33.11,  20.0),
    "807": (19.91,  20.0), "808": (150.53, 20.0), "809": (141.88, 20.0),
    "810": (150.43, 20.0), "811": (154.27, 20.0), "812": (5.38,   20.0),
    "813": (8.92,   20.0), "814": (19.57,  20.0), "815": (21.56,  20.0),
    "816": (16.76,  20.0), "817": (12.82,  20.0), "819": (8.84,   20.0),
    "820": (11.87,  20.0), "821": (30.27,  20.0), "822": (17.93,  20.0),
    "825": (15.03,  20.0), "826": (30.76,  20.0), "827": (35.31,  20.0),
    "828": (15.49,  20.0), "829": (19.58,  20.0), "906": (12.31,  20.0),
    "907": (17.52,  20.0), "908": (126.72, 20.0), "909": (129.78, 20.0),
    "910": (133.65, 20.0), "921": (22.81,  20.0), "922": (12.70,  20.0),
    "926": (8.85,   20.0), "927": (24.66,  20.0), "928": (7.58,   20.0),
    "930": (16.76,  20.0), "508": (117.52, 20.0),
    # node 1 listed in subcatchments but is junction/outfall combined
    "1":   (3.00,   20.0),
}

# peak depth (ft) each node can reach at storm peak — tuned to elevation
# nodes < 10ft elevation: can flood (>20ft); others proportional
PEAK_DEPTH = {
    "804": 23.0, "805": 25.0, "806": 8.0,  "807": 15.0, "808": 2.0,
    "809": 2.0,  "810": 2.0,  "811": 1.5,  "812": 22.0, "813": 18.0,
    "814": 14.0, "815": 11.0, "816": 16.0, "817": 17.0, "819": 19.0,
    "820": 17.0, "821": 9.0,  "822": 15.0, "825": 16.0, "826": 9.0,
    "827": 7.0,  "828": 16.0, "829": 13.0, "906": 17.0, "907": 15.0,
    "908": 2.5,  "909": 2.0,  "910": 2.0,  "921": 11.0, "922": 17.0,
    "926": 19.0, "927": 11.0, "928": 21.0, "930": 15.0, "508": 3.0,
    "1":   20.0,
}

# ── original coordinates (x_ft, y_ft) ────────────────────────────────────────
COORDS_FT = {
    "804":  (-330.306, 1192.030), "805":  (200.0,    200.0),
    "806":  (300.0,    300.0),    "807":  (400.0,    400.0),
    "808":  (500.0,    500.0),    "809":  (600.0,    600.0),
    "810":  (700.0,    700.0),    "811":  (800.0,    800.0),
    "812":  (900.0,    900.0),    "813":  (1000.0,   1000.0),
    "814":  (1100.0,   1100.0),   "815":  (1200.0,   1200.0),
    "816":  (1300.0,   1300.0),   "817":  (1400.0,   1400.0),
    "819":  (1500.0,   1500.0),   "820":  (1600.0,   1600.0),
    "821":  (1700.0,   1700.0),   "822":  (1800.0,   1800.0),
    "825":  (1900.0,   1900.0),   "826":  (2000.0,   2000.0),
    "827":  (2100.0,   2100.0),   "828":  (2200.0,   2200.0),
    "829":  (2300.0,   2300.0),   "906":  (2402.201, 2393.582),
    "907":  (2500.0,   2500.0),   "908":  (2600.0,   2600.0),
    "909":  (2700.0,   2700.0),   "910":  (2800.0,   2800.0),
    "921":  (2900.0,   2900.0),   "922":  (3000.0,   3000.0),
    "926":  (3100.0,   3100.0),   "927":  (3200.0,   3200.0),
    "928":  (3300.0,   3300.0),   "930":  (3400.0,   3400.0),
    "508":  (2557.351, 2560.224),
    "4":    (-296.813, 924.090),  "5":    (533.153,  233.043),
    "12":   (657.622,  1205.087), "13":   (1300.0,   1300.0),
    "14":   (1400.0,   1400.0),   "16":   (1600.0,   1600.0),
    "19":   (1900.0,   1900.0),   "20":   (2166.377, 2680.346),
    "25":   (2740.765, 3310.878),
    "Out1": (447.532,  84.804),   "Out2": (438.894,  89.122),
    "Out3": (2986.931, 3440.439), "Out4": (2313.213, 2533.510),
    "Out5": (2313.213, 2533.510), "Out6": (1946.123, 2520.554),
    "GAGE1":(1991.843, 2319.612),
    # nodes referenced by subcatchments as outlets (also junctions)
    "1":    (0.0,      0.0),      "18":   (1700.0,   1700.0),
    "23":   (1400.0,   1400.0),   "24":   (1800.0,   1800.0),
    "2":    (200.0,    200.0),    "3":    (300.0,    300.0),
}

# ── rainfall timeseries (tropical storm, 5-min intervals, mm/hr) ──────────────
# Peak ~58 mm/hr at 17:05-17:10, total ~125mm over 6h
RAIN_MM_HR = [
    ("15:00", 2.0),  ("15:05", 3.0),  ("15:10", 4.0),  ("15:15", 5.0),
    ("15:20", 7.0),  ("15:25", 8.0),  ("15:30", 10.0), ("15:35", 12.0),
    ("15:40", 15.0), ("15:45", 18.0), ("15:50", 22.0), ("15:55", 25.0),
    ("16:00", 28.0), ("16:05", 32.0), ("16:10", 35.0), ("16:15", 38.0),
    ("16:20", 42.0), ("16:25", 45.0), ("16:30", 48.0), ("16:35", 50.0),
    ("16:40", 52.0), ("16:45", 54.0), ("16:50", 55.0), ("16:55", 56.0),
    ("17:00", 57.0), ("17:05", 58.0), ("17:10", 58.0), ("17:15", 57.0),
    ("17:20", 56.0), ("17:25", 55.0), ("17:30", 54.0), ("17:35", 52.0),
    ("17:40", 48.0), ("17:45", 45.0), ("17:50", 42.0), ("17:55", 38.0),
    ("18:00", 34.0), ("18:05", 30.0), ("18:10", 26.0), ("18:15", 22.0),
    ("18:20", 18.0), ("18:25", 15.0), ("18:30", 12.0), ("18:35", 10.0),
    ("18:40", 8.0),  ("18:45", 6.0),  ("18:50", 5.0),  ("18:55", 4.0),
    ("19:00", 3.0),  ("19:05", 3.0),  ("19:10", 2.0),  ("19:15", 2.0),
    ("19:20", 2.0),  ("19:25", 1.5),  ("19:30", 1.5),  ("19:35", 1.0),
    ("19:40", 1.0),  ("19:45", 0.5),  ("19:50", 0.5),  ("19:55", 0.5),
    ("20:00", 0.0),  ("20:05", 0.0),  ("20:10", 0.0),  ("20:15", 0.0),
    ("20:20", 0.0),  ("20:25", 0.0),  ("20:30", 0.0),  ("20:35", 0.0),
    ("20:40", 0.0),  ("20:45", 0.0),  ("20:50", 0.0),  ("20:55", 0.0),
    ("21:00", 0.0),
]

def rain_in_hr(mm_hr):
    """Convert mm/hr to in/hr (SWMM CFS units expect in/hr for INTENSITY)."""
    return round(mm_hr / 25.4, 5)

# ── Gaussian factor for synthetic node timeseries ────────────────────────────
# Peak at t=2.67h after start (17:40), sigma=0.8h
T_PEAK = 2.67
SIGMA  = 0.8

def gauss(t_hours):
    return math.exp(-0.5 * ((t_hours - T_PEAK) / SIGMA) ** 2)

# 25 timesteps: 15:00, 15:15, ..., 21:00
TIMESTEPS = [datetime(2026, 6, 16, 15, 0) + timedelta(minutes=15 * i)
             for i in range(25)]

# ── 1. Write eWM_demo.inp ─────────────────────────────────────────────────────
def write_demo_inp():
    # Build TIMESERIES block (CFS → in/hr)
    ts_lines = []
    for i, (time_str, mm) in enumerate(RAIN_MM_HR):
        date_str = "06/16/2026" if time_str in ("15:00", "15:25", "16:00",
                   "16:25", "17:00", "17:25", "18:00", "18:25", "19:00",
                   "19:25", "20:00", "20:25", "21:00") else ""
        ts_lines.append(
            f"RainSeries1      {date_str:<10} {time_str:<10} {rain_in_hr(mm):.5f}   "
        )

    # Build COORDINATES block (geographic WGS84)
    coord_lines = []
    for node, (xft, yft) in sorted(COORDS_FT.items()):
        lon, lat = to_geo(xft, yft)
        coord_lines.append(f"{node:<16} {lon:<18.6f} {lat:<18.6f}")

    inp = f"""\
[TITLE]
;;Project Title/Notes
 eWM Demo - Ho Chi Minh City District 7 Drainage System
 Tropical Storm Simulation: 2026-06-16 15:00-21:00 (6 hours)
 Source: RUNOFF3 Lancaster PA (EPA SWMM 2017 examples), adapted for eWM demo
 Network: 36 junctions, 36 conduits, 29 subcatchments
 CRS: WGS84 decimal degrees (EPSG:4326), District 7, Ho Chi Minh City, Vietnam
 Units: CFS (flow), feet (length/depth), in/hr (rainfall intensity)

[OPTIONS]
;;Option             Value
FLOW_UNITS           CFS
INFILTRATION         GREEN_AMPT
FLOW_ROUTING         DYNWAVE
LINK_OFFSETS         DEPTH
MIN_SLOPE            0
ALLOW_PONDING        YES
SKIP_STEADY_STATE    NO

START_DATE           06/16/2026
START_TIME           15:00:00
REPORT_START_DATE    06/16/2026
REPORT_START_TIME    15:00:00
END_DATE             06/16/2026
END_TIME             21:00:00
SWEEP_START          01/01
SWEEP_END            12/31
DRY_DAYS             2
REPORT_STEP          00:15:00
WET_STEP             00:01:00
DRY_STEP             01:00:00
ROUTING_STEP         0:00:30

INERTIAL_DAMPING     NONE
NORMAL_FLOW_LIMITED  BOTH
FORCE_MAIN_EQUATION  H-W
VARIABLE_STEP        0.75
LENGTHENING_STEP     0
MIN_SURFAREA         12.566
MAX_TRIALS           0
HEAD_TOLERANCE       0
SYS_FLOW_TOL         5
LAT_FLOW_TOL         5
MINIMUM_STEP         0.5
THREADS              1

[EVAPORATION]
;;Data Source    Parameters
;;-------------- ----------------
CONSTANT         0.1
DRY_ONLY         NO

[RAINGAGES]
;;Name           Format    Interval SCF      Source
;;-------------- --------- ------ ------ ----------
GAGE1            INTENSITY 0.08333  1.0      TIMESERIES RainSeries1

[SUBCATCHMENTS]
;;Name           Rain Gage        Outlet           Area     %Imperv  Width    %Slope   CurbLen  SnowPack
;;-------------- ---------------- ---------------- -------- -------- -------- -------- -------- ----------------
1                GAGE1            1                26.82    48.0     2785.0   6.1      0
2                GAGE1            2                10.55    48.0     817.0    5.1      0
3                GAGE1            3                3.721    48.0     542.1    4.2      0
4                GAGE1            804              7.332    48.0     690.0    4.1      0
5                GAGE1            805              6.972    51.0     605.7    3.4      0
6                GAGE1            806              3.735    47.0     746.5    4.6      0
7                GAGE1            807              4.604    57.0     517.0    2.2      0
8                GAGE1            808              3.902    53.0     786.5    3.6      0
9                GAGE1            809              2.261    53.0     773.5    2.4      0
10               GAGE1            810              2.212    53.0     576.2    4.5      0
11               GAGE1            811              3.284    53.8     551.5    4.4      0
12               GAGE1            812              5.165    48.0     688.5    2.7      0
13               GAGE1            813              5.552    44.4     499.2    5.2      0
14               GAGE1            814              8.545    49.6     536.6    4.6      0
15               GAGE1            815              3.834    34.0     667.8    3.8      0
16               GAGE1            816              3.665    34.0     306.7    4.8      0
17               GAGE1            817              3.919    54.0     686.8    4.1      0
18               GAGE1            18               3.337    53.0     297.2    3.6      0
19               GAGE1            819              3.642    48.8     468.2    2.5      0
20               GAGE1            820              6.826    48.0     676.6    5.2      0
21               GAGE1            821              2.293    37.9     387.0    2.0      0
22               GAGE1            822              2.206    33.1     537.9    2.6      0
23               GAGE1            23               5.283    29.0     314.9    4.6      0
24               GAGE1            24               5.153    29.0     584.1    2.8      0
25               GAGE1            825              5.392    51.3     903.1    6.8      0
26               GAGE1            826              7.676    46.7     662.5    5.4      0
27               GAGE1            827              5.14     53.7     673.9    4.8      0
28               GAGE1            828              8.633    57.0     592.2    5.3      0
29               GAGE1            829              3.763    62.0     686.0    2.7      0

[SUBAREAS]
;;Subcatchment   N-Imperv   N-Perv     S-Imperv   S-Perv     PctZero    RouteTo    PctRouted
;;-------------- ---------- ---------- ---------- ---------- ---------- ---------- ----------
1                0.1        0.3        0.015      0.06       25         OUTLET
2                0.015      0.3        0.015      0.06       25         OUTLET
3                0.015      0.3        0.015      0.06       25         OUTLET
4                0.015      0.3        0.015      0.06       25         OUTLET
5                0.015      0.3        0.015      0.06       25         OUTLET
6                0.015      0.3        0.015      0.06       25         OUTLET
7                0.015      0.3        0.015      0.06       25         OUTLET
8                0.015      0.3        0.015      0.06       25         OUTLET
9                0.015      0.3        0.015      0.06       25         OUTLET
10               0.015      0.3        0.015      0.06       25         OUTLET
11               0.015      0.3        0.015      0.06       25         OUTLET
12               0.015      0.3        0.015      0.06       25         OUTLET
13               0.015      0.3        0.015      0.06       25         OUTLET
14               0.015      0.3        0.015      0.06       25         OUTLET
15               0.015      0.3        0.015      0.06       25         OUTLET
16               0.015      0.3        0.015      0.06       25         OUTLET
17               0.015      0.3        0.015      0.06       25         OUTLET
18               0.015      0.3        0.015      0.06       25         OUTLET
19               0.015      0.3        0.015      0.06       25         OUTLET
20               0.015      0.3        0.015      0.06       25         OUTLET
21               0.015      0.3        0.015      0.06       25         OUTLET
22               0.015      0.3        0.015      0.06       25         OUTLET
23               0.015      0.3        0.015      0.06       25         OUTLET
24               0.015      0.3        0.015      0.06       25         OUTLET
25               0.015      0.3        0.015      0.06       25         OUTLET
26               0.015      0.3        0.015      0.06       25         OUTLET
27               0.015      0.3        0.015      0.06       25         OUTLET
28               0.015      0.3        0.015      0.06       25         OUTLET
29               0.015      0.3        0.015      0.06       25         OUTLET

[INFILTRATION]
;;Subcatchment   Suction    Ksat       IMD
;;-------------- ---------- ---------- ----------
1                12.0       0.15       0.01
2                12.0       0.15       0.01
3                12.0       0.15       0.01
4                12.0       0.15       0.01
5                12.0       0.15       0.01
6                12.0       0.15       0.01
7                12.0       0.15       0.01
8                12.0       0.15       0.01
9                12.0       0.15       0.01
10               12.0       0.15       0.01
11               12.0       0.15       0.01
12               12.0       0.15       0.01
13               12.0       0.15       0.01
14               12.0       0.15       0.01
15               12.0       0.15       0.01
16               12.0       0.15       0.01
17               12.0       0.15       0.01
18               12.0       0.15       0.01
19               12.0       0.15       0.01
20               12.0       0.15       0.01
21               12.0       0.15       0.01
22               12.0       0.15       0.01
23               12.0       0.15       0.01
24               12.0       0.15       0.01
25               12.0       0.15       0.01
26               12.0       0.15       0.01
27               12.0       0.15       0.01
28               12.0       0.15       0.01
29               12.0       0.15       0.01

[JUNCTIONS]
;;Name           Elevation  MaxDepth   InitDepth  SurDepth   Aponded
;;-------------- ---------- ---------- ---------- ---------- ----------
804              7.48       20.00      0.00       0          0
805              5.24       20.00      0.00       0          0
806              33.11      20.00      0.00       0          0
807              19.91      20.00      0.00       0          0
808              150.53     20.00      0.00       0          0
809              141.88     20.00      0.00       0          0
810              150.43     20.00      0.00       0          0
811              154.27     20.00      0.00       0          0
812              5.38       20.00      0.00       0          0
813              8.92       20.00      0.00       0          0
814              19.57      20.00      0.00       0          0
815              21.56      20.00      0.00       0          0
816              16.76      20.00      0.00       0          0
817              12.82      20.00      0.00       0          0
819              8.84       20.00      0.00       0          0
820              11.87      20.00      0.00       0          0
821              30.27      20.00      0.00       0          0
822              17.93      20.00      0.00       0          0
825              15.03      20.00      0.00       0          0
826              30.76      20.00      0.00       0          0
827              35.31      20.00      0.00       0          0
828              15.49      20.00      0.00       0          0
829              19.58      20.00      0.00       0          0
906              12.31      20.00      0.00       0          0
907              17.52      20.00      0.00       0          0
908              126.72     20.00      0.00       0          0
909              129.78     20.00      0.00       0          0
910              133.65     20.00      0.00       0          0
921              22.81      20.00      0.00       0          0
922              12.70      20.00      0.00       0          0
926              8.85       20.00      0.00       0          0
927              24.66      20.00      0.00       0          0
928              7.58       20.00      0.00       0          0
930              16.76      20.00      0.00       0          0
508              117.52     20.00      0.00       0          0

[OUTFALLS]
;;Name           Elevation  Type       Stage Data       Gated    Route To
;;-------------- ---------- ---------- ---------------- -------- ----------------
4                0.00       FREE                        NO
5                0.00       FREE                        NO
12               0.00       FREE                        NO
13               0.00       FREE                        NO
14               0.00       FREE                        NO
16               0.00       FREE                        NO
19               0.00       FREE                        NO
20               0.00       FREE                        NO
25               0.00       FREE                        NO
Out1             0.00       FREE                        NO
Out2             0          FREE                        NO
Out3             0.00       FREE                        NO
Out4             0.00       FREE                        NO
Out5             0          FREE                        NO
Out6             0.00       FREE                        NO

[CONDUITS]
;;Name           From Node        To Node          Length     Roughness  InOffset   OutOffset  InitFlow   MaxFlow
;;-------------- ---------------- ---------------- ---------- ---------- ---------- ---------- ---------- ----------
508              508              907              101        0.012      0.0        0.0        0          0
804              804              4                409.0      0.013      0.0        0.0        0          0
805              805              Out1             280.0      0.013      0.0        0.0        0          0
806              806              906              428.0      0.013      0.0        0.0        0          0
807              807              907              230.0      0.013      0.0        0.0        0          0
808              808              908              481.0      0.013      0.0        0.0        0          0
809              809              909              360.0      0.013      0.0        0.0        0          0
810              810              910              341.0      0.013      0.0        0.0        0          0
811              811              808              231.0      0.013      0.0        0.0        0          0
812              812              12               430.5      0.013      0.0        0.0        0          0
813              813              13               367.0      0.013      0.0        0.0        0          0
814              814              14               420.0      0.013      0.0        0.0        0          0
815              815              814              75.0       0.013      0.0        0.0        0          0
816              816              16               277.0      0.013      0.0        0.0        0          0
817              817              813              394.0      0.013      0.0        0.0        0          0
819              819              19               254.0      0.013      0.0        0.0        0          0
820              820              Out6             210.0      0.013      0.0        0.0        0          0
821              821              921              336.0      0.013      0.0        0.0        0          0
822              822              922              208.0      0.013      0.0        0.0        0          0
825              825              Out4             244.0      0.013      0.0        0.0        0          0
826              826              926              358.0      0.013      0.0        0.0        0          0
827              827              927              236.0      0.013      0.0        0.0        0          0
828              828              928              256.0      0.013      0.0        0.0        0          0
829              829              828              249.5      0.013      0.0        0.0        0          0
906              906              5                270.0      0.013      0.0        0.0        0          0
907              907              906              148.0      0.013      0.0        0.0        0          0
908              908              508              434.0      0.013      0.0        0.0        0          0
909              909              908              195.0      0.013      0.0        0.0        0          0
910              910              908              274.0      0.013      0.0        0.0        0          0
921              921              820              210.0      0.013      0.0        0.0        0          0
922              922              20               278.0      0.013      0.0        0.0        0          0
926              926              25               280.0      0.013      0.0        0.0        0          0
927              927              930              260.0      0.013      0.0        0.0        0          0
928              928              Out3             312.0      0.013      0.0        0.0        0          0
930              930              926              256.0      0.013      0.0        0.0        0          0

[XSECTIONS]
;;Link           Shape        Geom1            Geom2      Geom3      Geom4      Barrels    Culvert
;;-------------- ------------ ---------------- ---------- ---------- ---------- ---------- ----------
508              CIRCULAR     4.0              0          0          0          1
804              CIRCULAR     1.5              0          0          0          1
805              CIRCULAR     1.0              0          0          0          1
806              CIRCULAR     0.67             0          0          0          1
807              CIRCULAR     1.0              0          0          0          1
808              CIRCULAR     2.0              0          0          0          1
809              CIRCULAR     0.67             0          0          0          1
810              CIRCULAR     0.87             0          0          0          1
811              CIRCULAR     1.25             0          0          0          1
812              CIRCULAR     0.67             0          0          0          1
813              CIRCULAR     0.67             0          0          0          1
814              CIRCULAR     1.0              0          0          0          1
815              CIRCULAR     1.0              0          0          0          1
816              CIRCULAR     1.5              0          0          0          1
817              CIRCULAR     1.25             0          0          0          1
819              CIRCULAR     1.0              0          0          0          1
820              CIRCULAR     2.0              0          0          0          1
821              CIRCULAR     1.0              0          0          0          1
822              CIRCULAR     1.0              0          0          0          1
825              CIRCULAR     1.0              0          0          0          1
826              CIRCULAR     1.0              0          0          0          1
827              CIRCULAR     1.5              0          0          0          1
828              CIRCULAR     2.0              0          0          0          1
829              CIRCULAR     2.0              0          0          0          1
906              CIRCULAR     2.0              0          0          0          1
907              CIRCULAR     2.0              0          0          0          1
908              CIRCULAR     2.0              0          0          0          1
909              CIRCULAR     0.87             0          0          0          1
910              CIRCULAR     1.0              0          0          0          1
921              CIRCULAR     2.0              0          0          0          1
922              CIRCULAR     1.5              0          0          0          1
926              CIRCULAR     2.0              0          0          0          1
927              CIRCULAR     2.0              0          0          0          1
928              CIRCULAR     2.5              0          0          0          1
930              CIRCULAR     2.0              0          0          0          1

[TIMESERIES]
;;Name           Date       Time       Value
;;-------------- ---------- ---------- ----------
;;  Tropical storm, Ho Chi Minh City, 2026-06-16
;;  Intensity in in/hr (CFS units). Peak 58 mm/hr = 2.28 in/hr at 17:05-17:10
;;  Total: ~125 mm (4.92 inches) over 6 hours
{chr(10).join(ts_lines)}

[REPORT]
;;Reporting Options
INPUT      YES
CONTROLS   NO
SUBCATCHMENTS ALL
NODES ALL
LINKS ALL

[MAP]
DIMENSIONS 106.703 10.724 106.717 10.736
Units      Degrees

[COORDINATES]
;;Node           X-Coord (lon)      Y-Coord (lat)
;;-------------- ------------------ ------------------
{chr(10).join(coord_lines)}

[VERTICES]
;;Link           X-Coord            Y-Coord
;;-------------- ------------------ ------------------

[SYMBOLS]
;;Gage           X-Coord            Y-Coord
;;-------------- ------------------ ------------------
GAGE1            106.711179         10.731704
"""
    path = os.path.join(OUT, "eWM_demo.inp")
    with open(path, "w") as f:
        f.write(inp)
    print(f"[OK] {path}")
    return path

# ── 2. Write rainfall CSV ─────────────────────────────────────────────────────
def write_rainfall_csv():
    path = os.path.join(OUT, "rainfall_hcm_2026.csv")
    cumulative_mm = 0.0
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["datetime", "intensity_mm_hr", "depth_mm_5min",
                    "cumulative_mm", "note"])
        for time_str, mm_hr in RAIN_MM_HR:
            depth = round(mm_hr * 5 / 60, 3)
            cumulative_mm = round(cumulative_mm + depth, 2)
            dt = f"2026-06-16 {time_str}:00"
            note = "PEAK" if mm_hr >= 57.0 else ("FLOODING RISK" if mm_hr >= 40.0 else "")
            w.writerow([dt, mm_hr, depth, cumulative_mm, note])
    print(f"[OK] {path}")
    return path

# ── 3. Write synthetic node timeseries ────────────────────────────────────────
def write_node_timeseries():
    path = os.path.join(OUT, "node_timeseries_demo.csv")
    # Nodes to include (junctions only, not outfalls)
    nodes = [n for n in PEAK_DEPTH if n not in
             ("4","5","12","13","14","16","19","20","25",
              "Out1","Out2","Out3","Out4","Out5","Out6")]

    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "node_id", "datetime",
            "depth_ft", "depth_m",
            "flow_cfs", "flow_cms",
            "flooding_cfs", "flooding_cms",
            "head_ft", "status"
        ])
        for node in sorted(nodes):
            elev_ft   = JUNCTIONS.get(node, (0, 20))[0]
            max_d_ft  = JUNCTIONS.get(node, (0, 20))[1]
            peak      = PEAK_DEPTH.get(node, 5.0)
            for i, ts in enumerate(TIMESTEPS):
                t_hr = i * 0.25
                g    = gauss(t_hr)
                depth_ft = round(peak * g, 3)
                depth_m  = round(depth_ft * 0.3048, 3)
                flow_cfs = round(depth_ft * 0.8, 3)
                flow_cms = round(flow_cfs * 0.0283168, 4)
                flood_ft = round(max(0.0, depth_ft - max_d_ft) * 3.0, 3)
                flood_cms = round(flood_ft * 0.0283168, 4)
                head_ft  = round(elev_ft + depth_ft, 3)
                status = "FLOODING" if flood_ft > 0 else ("HIGH" if depth_ft > max_d_ft * 0.8 else "NORMAL")
                w.writerow([
                    node, ts.strftime("%Y-%m-%d %H:%M:%S"),
                    depth_ft, depth_m,
                    flow_cfs, flow_cms,
                    flood_ft, flood_cms,
                    head_ft, status
                ])
    print(f"[OK] {path}")
    return path

# ── 4. Print summary ──────────────────────────────────────────────────────────
def print_summary():
    total_mm = sum(mm * 5 / 60 for _, mm in RAIN_MM_HR)
    peak_mm  = max(mm for _, mm in RAIN_MM_HR)
    flood_nodes = [n for n, pd in PEAK_DEPTH.items()
                   if n in JUNCTIONS and pd > JUNCTIONS[n][1]]
    print()
    print("=== eWM Demo Dataset Summary ===")
    print(f"  Network:         35 junctions, 36 conduits, 29 subcatchments")
    print(f"  Location:        District 7, Ho Chi Minh City, Vietnam")
    print(f"  CRS:             WGS84 (EPSG:4326), decimal degrees")
    print(f"  Simulation:      2026-06-16 15:00 → 21:00 (6 hours)")
    print(f"  Storm total:     {total_mm:.1f} mm ({total_mm/25.4:.2f} in)")
    print(f"  Peak intensity:  {peak_mm:.0f} mm/hr ({peak_mm/25.4:.2f} in/hr) at 17:05–17:10")
    print(f"  Flooding nodes:  {len(flood_nodes)} → {', '.join(sorted(flood_nodes))}")
    print(f"  Timeseries rows: {len([n for n in PEAK_DEPTH if n in JUNCTIONS]) * 25}")
    print()
    print("  Coordinate range:")
    lons = [to_geo(x,y)[0] for x,y in COORDS_FT.values()]
    lats = [to_geo(x,y)[1] for x,y in COORDS_FT.values()]
    print(f"    Lon: {min(lons):.6f} → {max(lons):.6f}")
    print(f"    Lat: {min(lats):.6f} → {max(lats):.6f}")
    print(f"    Area: ~{(max(lons)-min(lons))*111000*math.cos(math.radians(LAT0)):.0f}m × "
          f"~{(max(lats)-min(lats))*111000:.0f}m")
    print()

if __name__ == "__main__":
    write_demo_inp()
    write_rainfall_csv()
    write_node_timeseries()
    print_summary()
