"""Reusable draw.io builders for network topology diagrams.

Import these into a per-diagram generator. They enforce the Drawio skill rules:
classic Cisco stencils, solid fills, fan-out patch boxes, box-to-box edges,
mirror symmetry, no text on lines.

Usage:
    from topology_helpers import *
    reset()
    cell("t", TITLE, "My Topology", 40, 20, 1400, 40)
    node("c1", cx=650, y=150, fc=BLUE, label="Nexus 9504")
    patch_bot("c1_bp", cx=650, ny=150)
    ...
    write_drawio("out.drawio", page_w=2600, page_h=1720)
"""
import html

CELLS = []

def reset():
    CELLS.clear()

def esc(s):
    return html.escape(s, quote=True)

# ---------- colors ----------
BLUE = "#1F6FA8"      # primary Cisco device fill
GREY = "#5D6D7E"      # secondary / optional device
NODE_STROKE = "#ffffff"

# ---------- node geometry defaults ----------
NW, NH = 64, 56       # switch icon
PW, PH = 40, 14       # patch panel box
GAP = 6

# ---------- styles ----------
TITLE = ("text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;"
         "fontSize=20;fontStyle=1;fontColor=#1F3864;")
SUBT = "text;html=1;strokeColor=none;fillColor=none;align=left;fontSize=11;fontColor=#555555;"
PP = ("rounded=0;whiteSpace=wrap;html=1;fillColor=#34495E;strokeColor=#1B2631;"
      "fontSize=6;fontColor=#FFFFFF;")

def SW(name="layer_3_switch", fc=BLUE):
    # classic Cisco stencil; layer_3_switch / workgroup_switch render a real glyph
    return (f"sketch=0;html=1;dashed=0;whiteSpace=wrap;fillColor={fc};strokeColor={NODE_STROKE};"
            f"shape=mxgraph.cisco.switches.{name};verticalLabelPosition=bottom;verticalAlign=top;"
            "fontSize=9;fontColor=#0B2545;fontStyle=1;")

def ZONE(sc, fc="none"):
    return (f"rounded=1;whiteSpace=wrap;html=1;dashed=1;dashPattern=8 4;fillColor={fc};strokeColor={sc};"
            f"verticalAlign=top;align=left;spacing=8;fontStyle=1;fontSize=13;fontColor={sc};arcSize=3;")

def MODEL(sc):
    return (f"rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor={sc};fontSize=9;"
            "fontColor=#1F3864;align=center;verticalAlign=middle;arcSize=12;")

def LL(sc, fc="#FFFFFF"):
    # link label in a rounded rect placed beside the line (never on it)
    return (f"rounded=1;whiteSpace=wrap;html=1;fillColor={fc};strokeColor={sc};fontSize=9;"
            "fontColor=#1A1A1A;align=center;verticalAlign=middle;arcSize=20;")

def NOTE(sc, fc="#FFF8EC"):
    return (f"rounded=1;whiteSpace=wrap;html=1;fillColor={fc};strokeColor={sc};fontSize=10;"
            "fontColor=#222222;align=center;verticalAlign=top;spacing=8;")

def link_style(color, width=3, dashed=False):
    d = "dashed=1;" if dashed else "dashed=0;"
    return (f"edgeStyle=none;html=1;endArrow=none;startArrow=none;"
            f"strokeColor={color};strokeWidth={width};{d}rounded=1;")

# ---------- builders ----------
def cell(cid, style, value, x, y, w, h):
    CELLS.append(
        f'<mxCell id="{cid}" parent="1" style="{style}" value="{esc(value)}" vertex="1">'
        f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')

def node(cid, cx, y, label, fc=BLUE, name="layer_3_switch", w=NW, h=NH):
    cell(cid, SW(name, fc), label, cx - w // 2, y, w, h)

def patch(cid, cx, y):
    cell(cid, PP, "PP", cx - PW // 2, y, PW, PH)

def patch_top(cid, cx, ny):
    patch(cid, cx, ny - PH - GAP)

def patch_bot(cid, cx, ny, h=NH):
    patch(cid, cx, ny + h + GAP)

def edge(eid, src, tgt, style, waypoints=None):
    """waypoints: list of (x, y) for orthogonal channel routing of cross-links."""
    if waypoints:
        pts = "".join(f'<mxPoint x="{px}" y="{py}"/>' for px, py in waypoints)
        geo = f'<mxGeometry relative="1" as="geometry"><Array as="points">{pts}</Array></mxGeometry>'
    else:
        geo = '<mxGeometry relative="1" as="geometry"/>'
    CELLS.append(f'<mxCell id="{eid}" parent="1" source="{src}" target="{tgt}" '
                 f'style="{style}" edge="1">{geo}</mxCell>')

def legend_swatch(cid_prefix, x, y, style, text):
    """Real colored line swatch + text label (never use ===== text)."""
    CELLS.append(f'<mxCell id="{cid_prefix}_l" parent="1" style="{style}" edge="1">'
                 f'<mxGeometry relative="1" as="geometry">'
                 f'<mxPoint x="{x}" y="{y}" as="sourcePoint"/>'
                 f'<mxPoint x="{x+80}" y="{y}" as="targetPoint"/></mxGeometry></mxCell>')
    cell(f"{cid_prefix}_t", SUBT, text, x + 92, y - 14, 320, 28)

def mirror_x(x, w, axis):
    """Right-side X for a left-side box of width w mirrored about axis."""
    return 2 * axis - (x + w)

# ---------- output ----------
def write_drawio(path, page_w=2600, page_h=1720, name="Topology"):
    xml = ('<mxfile host="app.diagrams.net">\n'
           f'  <diagram id="d1" name="{esc(name)}">\n'
           '    <mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" '
           'connect="1" arrows="1" fold="1" page="1" pageScale="1" '
           f'pageWidth="{page_w}" pageHeight="{page_h}" math="0" shadow="0">\n'
           '      <root>\n        <mxCell id="0"/>\n        <mxCell id="1" parent="0"/>\n'
           + "\n".join("        " + c for c in CELLS) +
           '\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n')
    with open(path, "w", encoding="utf-8") as f:
        f.write(xml)
    return len(CELLS)


def validate(path):
    import xml.dom.minidom as m
    d = m.parse(path)
    c = d.getElementsByTagName("mxCell")
    ids = {x.getAttribute("id") for x in c}
    dang = [(x.getAttribute("id"), x.getAttribute("source"), x.getAttribute("target"))
            for x in c if x.getAttribute("edge") == "1"
            and ((x.getAttribute("source") and x.getAttribute("source") not in ids)
              or (x.getAttribute("target") and x.getAttribute("target") not in ids))]
    return dang
