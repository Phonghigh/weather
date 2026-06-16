import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from app import demo_data, theme


class ChartWidget(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent, background='w')
        self._metric = True
        self._regions = []
        self._setup()

    def _setup(self):
        self.setContentsMargins(0, 0, 0, 0)

        pi = self.getPlotItem()
        pi.setContentsMargins(0, 0, 0, 0)
        pi.showGrid(x=False, y=True, alpha=0.35)
        pi.getAxis('bottom').setStyle(tickFont=QFont('Ubuntu Mono', 9))
        pi.getAxis('left').setStyle(tickFont=QFont('Ubuntu Mono', 9))
        pi.getAxis('bottom').setTextPen(pg.mkPen(color='#aab4c0'))
        pi.getAxis('left').setTextPen(pg.mkPen(color='#aab4c0'))
        pi.getAxis('bottom').setPen(pg.mkPen(color='#e0e4e9'))
        pi.getAxis('left').setPen(pg.mkPen(color='#e0e4e9'))
        pi.getAxis('right').setStyle(showValues=False)
        pi.getAxis('top').setStyle(showValues=False)
        pi.layout.setContentsMargins(8, 4, 8, 4)

        # Area fill curve (depth)
        self._area_curve = pg.PlotCurveItem(
            pen=None, fillLevel=0,
            brush=pg.mkBrush(QColor(21, 101, 167, 33)),
        )
        pi.addItem(self._area_curve)

        # Depth line curve
        self._line_curve = pg.PlotCurveItem(
            pen=pg.mkPen(color=theme.ACCENT, width=2.4),
        )
        pi.addItem(self._line_curve)

        # Ground/rim dashed red line
        self._rim_line = pg.InfiniteLine(
            angle=0,
            pen=pg.mkPen(color=theme.COLOR_ERR, width=1.5,
                         style=Qt.DashLine),
            movable=False,
        )
        pi.addItem(self._rim_line)

        # Rim label
        self._rim_label = pg.InfLineLabel(
            self._rim_line, text='ground level',
            position=0.95, color=theme.COLOR_ERR,
            fill=pg.mkBrush(255, 255, 255, 0),
        )

    def update_node(self, node_id, metric=True):
        self._metric = metric
        n = demo_data.NODES[node_id]
        df = 1.0 if metric else 3.28084

        dep = [v * df for v in n['dep']]
        rim = n['rimM'] * df
        xs = list(range(25))

        # Remove old flood regions
        pi = self.getPlotItem()
        for r in self._regions:
            pi.removeItem(r)
        self._regions.clear()

        # Add flood period shading
        i = 0
        fld = n['fld']
        while i < 25:
            if fld[i] > 0:
                j = i
                while j < 25 and fld[j] > 0:
                    j += 1
                region = pg.LinearRegionItem(
                    [i - 0.5, j - 0.5], movable=False,
                    brush=pg.mkBrush(QColor(248, 215, 215, 153)),
                    pen=pg.mkPen(None),
                )
                pi.addItem(region)
                self._regions.append(region)
                i = j
            else:
                i += 1

        # Update curves
        self._area_curve.setData(xs, dep)
        self._line_curve.setData(xs, dep)
        self._rim_line.setValue(rim)

        # Y range
        max_v = max(max(dep), rim) * 1.12
        self.setYRange(0, max_v, padding=0)
        self.setXRange(-0.5, 24.5, padding=0)

        # X axis ticks
        ticks = [(i, demo_data.TIMELINE[i]) for i in range(0, 25, 4)]
        self.getAxis('bottom').setTicks([ticks, []])

        # Y label
        unit = 'm' if metric else 'ft'
        self.getAxis('left').setLabel(f'Depth ({unit})')
