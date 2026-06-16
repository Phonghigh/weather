from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QObject, Signal, Slot, QUrl
from PySide6.QtGui import QColor

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWebChannel import QWebChannel
    _HAS_WEBENGINE = True
except ImportError:
    _HAS_WEBENGINE = False

from app import demo_data, theme


# ── JS↔Python bridge ─────────────────────────────────────────────────────────

class _MapBridge(QObject):
    node_selected = Signal(str)

    @Slot(str)
    def selectNode(self, node_id):
        self.node_selected.emit(node_id)


# ── SVG map HTML generator ────────────────────────────────────────────────────

def _px(x):
    return x / 100 * 880

def _py(y):
    return y / 100 * 560


def _build_html(selected_node, layers, flood_opacity):
    show_flood = layers.get('flood', True)
    show_links = layers.get('links', True)
    show_nodes = layers.get('nodes', True)

    # Flood raster ellipses
    flood_parts = []
    if show_flood:
        for nid in ['805', '804', '812', '928']:
            n = demo_data.NODES[nid]
            sz = demo_data.max_depth(nid)
            cx = _px(n['x'])
            cy = _py(n['y'])
            rx = 34 + sz * 7
            ry = 24 + sz * 4.5
            flood_parts.append(
                f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#3a78c2"/>'
            )
    flood_group_style = f'opacity:{flood_opacity / 100 * 0.62:.3f};filter:blur(7px)'
    flood_svg = f'<g id="flood-layer" style="{flood_group_style}">{"".join(flood_parts)}</g>'

    # Conduit links
    link_parts = []
    if show_links:
        for a, b in demo_data.LINKS:
            na, nb = demo_data.NODES[a], demo_data.NODES[b]
            f = (demo_data.peak_flow(a) + demo_data.peak_flow(b)) / 2
            color = '#0f4f82' if f > 0.4 else '#4a86c5' if f > 0.2 else '#9bbbd8'
            w = 5 if f > 0.4 else 4 if f > 0.2 else 3
            x1, y1 = _px(na['x']), _py(na['y'])
            x2, y2 = _px(nb['x']), _py(nb['y'])
            link_parts.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>'
            )
    links_svg = f'<g id="links-layer">{"".join(link_parts)}</g>'

    # Context nodes (background, no data)
    ctx_parts = []
    for x, y in demo_data.CTX:
        cx, cy = _px(x), _py(y)
        ctx_parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4" fill="#aeb8a8" stroke="#fff" stroke-width="1.5"/>'
        )

    # Data nodes
    node_parts = []
    if show_nodes:
        for nid in demo_data.ORDER:
            n = demo_data.NODES[nid]
            cx = _px(n['x'])
            cy = _py(n['y'])
            color = demo_data.node_color(nid)
            r = demo_data.node_radius(nid)
            is_sel = nid == selected_node
            ring_r = r + 6 if is_sel else 0
            ty = cy - r - 6
            node_parts.append(f"""
<g id="node-{nid}" class="data-node" onclick="clickNode('{nid}')" style="cursor:pointer">
  <circle id="ring-{nid}" class="node-ring" cx="{cx:.1f}" cy="{cy:.1f}" r="{ring_r}"
          data-r="{r + 6}" fill="none" stroke="{theme.ACCENT}" stroke-width="2.5"/>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{color}" stroke="#fff" stroke-width="2"/>
  <text x="{cx:.1f}" y="{ty:.1f}" text-anchor="middle"
        font-family="Ubuntu, sans-serif" font-size="11" font-weight="700"
        fill="#2b333c">{nid}</text>
</g>""")

    nodes_svg = (
        f'<g id="ctx-nodes">{"".join(ctx_parts)}</g>'
        f'<g id="data-nodes">{"".join(node_parts)}</g>'
    )

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:100%; height:100%; background:#eef1f4; overflow:hidden; }}
svg {{ display:block; width:100%; height:100%; }}
.data-node:hover {{ opacity:0.85; }}
</style>
{"<script src='qrc:///qtwebchannel/qwebchannel.js'></script>" if _HAS_WEBENGINE else ""}
</head>
<body>
<svg viewBox="0 0 880 560" preserveAspectRatio="xMidYMid meet">
  <!-- basemap -->
  <rect x="0" y="0" width="880" height="560" fill="#e9ede7"/>
  <g opacity="0.5">
    <rect x="40"  y="40"  width="150" height="110" fill="#dde3da" rx="3"/>
    <rect x="230" y="40"  width="200" height="90"  fill="#dde3da" rx="3"/>
    <rect x="470" y="60"  width="160" height="120" fill="#d7e6cf" rx="3"/>
    <rect x="680" y="40"  width="160" height="150" fill="#dde3da" rx="3"/>
    <rect x="60"  y="210" width="170" height="150" fill="#dde3da" rx="3"/>
    <rect x="270" y="220" width="150" height="120" fill="#d7e6cf" rx="3"/>
    <rect x="640" y="240" width="190" height="120" fill="#dde3da" rx="3"/>
    <rect x="120" y="410" width="180" height="110" fill="#dde3da" rx="3"/>
    <rect x="560" y="420" width="200" height="100" fill="#dde3da" rx="3"/>
  </g>
  <!-- streets -->
  <g stroke="#fbfcfb" stroke-width="9" stroke-linecap="round">
    <line x1="0"   y1="185" x2="880" y2="195"/>
    <line x1="0"   y1="385" x2="880" y2="392"/>
    <line x1="210" y1="0"   x2="220" y2="560"/>
    <line x1="450" y1="0"   x2="455" y2="560"/>
    <line x1="655" y1="0"   x2="650" y2="560"/>
  </g>
  <!-- river -->
  <path d="M-20 470 Q 250 500 460 478 T 900 486 L 900 560 L -20 560 Z"
        fill="#bcd6e8" opacity="0.8"/>
  <path d="M-20 470 Q 250 500 460 478 T 900 486"
        fill="none" stroke="#9cc2db" stroke-width="2"/>
  <!-- layers -->
  {flood_svg}
  {links_svg}
  {nodes_svg}
</svg>

<!-- map chrome: flood count overlay -->
<div style="position:absolute;top:12px;left:12px;background:rgba(255,255,255,0.92);
            border:1px solid #d4d9e0;border-radius:7px;padding:7px 11px;
            font-size:11.5px;color:#39424d;font-family:Ubuntu,sans-serif;
            backdrop-filter:blur(3px)">
  <span style="font-weight:700;color:{theme.ACCENT}">4</span>
  nodes flooded · peak depth
  <span style="font-weight:700">7.58 m</span>
</div>
<!-- zoom buttons -->
<div style="position:absolute;bottom:10px;right:12px;display:flex;flex-direction:column;gap:5px">
  <div style="width:30px;height:30px;background:#fff;border:1px solid #d4d9e0;
              border-radius:6px;display:flex;align-items:center;justify-content:center;
              font-size:17px;color:#5b6772;cursor:pointer;user-select:none;
              font-family:sans-serif">+</div>
  <div style="width:30px;height:30px;background:#fff;border:1px solid #d4d9e0;
              border-radius:6px;display:flex;align-items:center;justify-content:center;
              font-size:17px;color:#5b6772;cursor:pointer;user-select:none;
              font-family:sans-serif">−</div>
</div>
<!-- attribution -->
<div style="position:absolute;bottom:10px;left:12px;background:rgba(255,255,255,0.85);
            border-radius:5px;padding:2px 7px;font-size:10px;color:#8893a0;
            font-family:Ubuntu,sans-serif">
  OSM offline tiles · VN-2000 / TM-3
</div>

<script>
var bridge = null;
{"new QWebChannel(qt.webChannelTransport, function(ch) { bridge = ch.objects.bridge; });" if _HAS_WEBENGINE else ""}

function clickNode(id) {{
    if (bridge) bridge.selectNode(id);
}}

function setLayerVisible(groupId, visible) {{
    var el = document.getElementById(groupId);
    if (el) el.style.display = visible ? '' : 'none';
}}

function setFloodOpacity(pct) {{
    var el = document.getElementById('flood-layer');
    if (el) el.style.opacity = (pct / 100 * 0.62);
}}

function setSelectedNode(id) {{
    document.querySelectorAll('.node-ring').forEach(function(el) {{
        el.setAttribute('r', 0);
    }});
    var ring = document.getElementById('ring-' + id);
    if (ring) ring.setAttribute('r', ring.getAttribute('data-r'));
}}
</script>
</body>
</html>"""
    return html


# ── Widget ────────────────────────────────────────────────────────────────────

class MapWidget(QWidget):
    node_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._layers = {'nodes': True, 'links': True, 'flood': True, 'base': True}
        self._flood_opacity = 65
        self._selected = '805'

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if _HAS_WEBENGINE:
            self._view = QWebEngineView()
            self._bridge = _MapBridge()
            self._bridge.node_selected.connect(self.node_selected)
            self._channel = QWebChannel()
            self._channel.registerObject('bridge', self._bridge)
            self._view.page().setWebChannel(self._channel)
            layout.addWidget(self._view)
            self._reload()
        else:
            # Fallback: plain label
            lbl = QLabel('Map requires PySide6-WebEngine.\nRun: pip install PySide6-WebEngine')
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet('color:#5b6772;font-size:13px;background:#eef1f4;')
            layout.addWidget(lbl)

    def _reload(self):
        if not _HAS_WEBENGINE:
            return
        html = _build_html(self._selected, self._layers, self._flood_opacity)
        self._view.setHtml(html, QUrl('about:blank'))

    def set_selected_node(self, node_id):
        self._selected = node_id
        if _HAS_WEBENGINE:
            self._view.page().runJavaScript(f"setSelectedNode('{node_id}');")

    def set_layer_visible(self, key, visible):
        self._layers[key] = visible
        group_map = {
            'nodes': 'data-nodes',
            'links': 'links-layer',
            'flood': 'flood-layer',
        }
        if key in group_map and _HAS_WEBENGINE:
            js_bool = 'true' if visible else 'false'
            self._view.page().runJavaScript(
                f"setLayerVisible('{group_map[key]}', {js_bool});"
            )

    def set_flood_opacity(self, pct):
        self._flood_opacity = pct
        if _HAS_WEBENGINE:
            self._view.page().runJavaScript(f"setFloodOpacity({pct});")
