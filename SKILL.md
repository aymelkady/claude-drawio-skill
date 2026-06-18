---
name: Drawio
description: Build clean, professional draw.io (diagrams.net) network topology diagrams with Cisco stencils, then render and visually verify them. Use when the user asks for a draw.io / .drawio diagram, an HLD/LLD network topology, a physical or logical network diagram, a campus/DC/data-center topology, or wants Cisco-style switch/router stencils laid out symmetrically with patch panels and link legends. Triggers on "draw.io", "drawio", "network topology diagram", "HLD diagram", "Cisco stencil diagram".
---

# Drawio — Network Topology Diagrams

Generate clean physical/logical network HLD topologies as `.drawio` XML, render to PNG with the draw.io CLI, and visually verify before delivering. Built from hard lessons on alignment, Cisco stencils, and link routing.

## Golden workflow (always)

1. **Generate the `.drawio` with a Python script**, not by hand. Coordinates must be computed (centers, mirror axis, patch offsets) so alignment and symmetry are exact. Hand-edited XML drifts.
2. **Validate XML + edge refs** before rendering (parse, check no dangling source/target).
3. **Render to PNG** with the draw.io CLI and **Read the image** to verify. Never deliver unseen.
4. **Crop and zoom** problem regions (PIL) to confirm patch-box alignment and that links touch boxes, not icons.
5. Iterate the generator, re-render, re-verify. Deliver `.drawio` (editable) + `.png` (preview).

### Render command (Windows)

```bash
"/c/Program Files/draw.io/draw.io.exe" -x -f png -o OUT.png --width 2600 IN.drawio 2>/dev/null
```
Cache/GPU errors on stderr are benign. Other platforms: `drawio` on PATH, or `npx @drawio/export`.

### Validate before render

```python
import xml.dom.minidom as m
d = m.parse("file.drawio"); c = d.getElementsByTagName("mxCell")
ids = {x.getAttribute("id") for x in c}
dang = [(x.getAttribute("id"), x.getAttribute("source"), x.getAttribute("target"))
        for x in c if x.getAttribute("edge") == "1"
        and ((x.getAttribute("source") and x.getAttribute("source") not in ids)
          or (x.getAttribute("target") and x.getAttribute("target") not in ids))]
print("dangling:", dang)   # must be []
```

## Hard rules (learned the hard way)

### Stencils

**Device → stencil mapping (mandatory):**

| Device type | Stencil family to use |
|---|---|
| Router | `mxgraph.cisco.routers.*` — e.g. `mxgraph.cisco.routers.router` |
| NGFW / Firewall | `mxgraph.cisco.firewalls.*` — e.g. `mxgraph.cisco.firewalls.firewall` |
| Switch (access / distribution) | `mxgraph.cisco.switches.*` — e.g. `workgroup_switch`, `layer_3_switch` |
| Spine / Leaf (DC fabric) | `mxgraph.cisco.switches.cisco_spine` / `mxgraph.cisco.switches.cisco_leaf` |

- Always search for a **relevant shape** that matches the actual device type. Do not default to a generic switch icon for routers, firewalls, or fabric nodes — use the correct family.
- **Avoid `multilayer_switch`** and the modern `mxgraph.cisco19.rect;prIcon=...` set: they render as near-blank boxes in CLI export. Distinguish device roles by **fill color + label**, not by risky stencil names.
- **Solid fills read best**: e.g. `fillColor=#1F6FA8;strokeColor=#ffffff` (Cisco blue), grey `#5D6D7E` for secondary. Pale pastel fills wash the glyph out.

### Patch panels (external port boxes)
- Every device gets small **PP boxes** (`~40x14`, dark fill `#34495E`, white text "PP"). **All links terminate on PP boxes, never on the switch stencil.**
- **One PP per link (fan-out).** A device with 4 uplinks gets 4 north PPs, not one. Fanning 4 links into a single PP causes overlap and looks like the links miss the box. This was the #1 alignment defect.
- **If a device has 2 separate port groups (e.g. dual uplink planes, management + data), use 2 separate PP boxes** — one per port group. Never merge distinct port groups into one PP.
- PP centered on its link side: top PP for north links, bottom PP for south links.
- PP boxes are always **brought to front** (see Z-ordering rules).

### Alignment & symmetry
- Define a **mirror axis** (e.g. `MIRROR = 1300`) and place left/right mirror pairs as `x` and `2*MIRROR-(x+w)`.
- **Column-align stacked rows.** All devices in a vertical stack (DC Core / Fusion / Core-Border) must share the **same X centers** so vertical links are straight, not slanted. Compute once: `L = C-90`, `R = C+90`.
- Patch box X center == device X center, exactly.

### Link routing
- Use **straight** (`edgeStyle=none`) for short verticals and same-column fans.
- For **cross-links** (e.g. MCR1 to far DC), route through a **horizontal channel with explicit waypoints** so they go up-across-up orthogonally instead of forming a messy central X:
  ```xml
  <mxGeometry relative="1" as="geometry">
    <Array as="points"><mxPoint x="300" y="628"/><mxPoint x="1640" y="628"/></Array>
  </mxGeometry>
  ```
- Set explicit `exitX/exitY/entryX/entryY` (e.g. `exitX=0.5;exitY=0;entryX=0.5;entryY=1`) so lines attach at box edge centers.
- **All cabling is brought to back** (see Z-ordering rules) — emit edge cells before device and PP cells in the XML `<root>` block.

### X-connections for full-mesh pairs (mandatory rule)

When you have a **full mesh** between exactly **2 devices on one side and 2 devices on the other side** (2↔2) or **2 devices to 4 devices** (2↔4) — for example, two NGFWs connecting to two Core Switches — use the **X-connection pattern**: each left device connects to both right devices, and the two cross-cables form a visible X shape in the diagram.

```
NGFW-A ──────────── Core-SW-1
       ╲          ╱
        ╲        ╱
         ╲      ╱      ← X visual cross
        ╱ ╲  ╱ ╲
       ╱    ╲╱    ╲
NGFW-B ──────────── Core-SW-2
```

**Rules:**
- Route the two crossing cables through a shared midpoint so the X is intentional and legible, not accidental clutter.
- Both cross cables are sent to the back layer.
- **Before drawing an X-connection, always ask the user to confirm.** If during design you predict that a full-mesh 2↔2 or 2↔4 pattern exists (or should exist), pause and ask: *"This looks like a full mesh between [device group A] and [device group B] — shall I use an X-connection layout?"* Do not assume; user confirms first.
- Do NOT use X-connections for partial meshes or for topologies with more than 4 devices on either side — use explicit waypoint channels instead.

### Labels & legend

**Core rule: every piece of text must live inside a filled shape.** Transparent text boxes let cables bleed through the letters and become unreadable. No exceptions.

#### Device name / model labels
- **Icon value is always `""`** — the stencil shape carries no text.
- Place the device name + model in a **separate rounded rectangle with a solid fill** (`rounded=1;fillColor=...;strokeColor=...`) positioned **symmetrically beside the device icon**:
  - Left-column devices → label to the **left** of the icon, vertically centered on the device center Y.
  - Right-column devices → label to the **right** of the icon, vertically centered on the device center Y.
- Use a tinted fill that matches the device color family (e.g. light orange `#FDF3E7` for routers, light blue `#EBF5FB` for core switches) with a border matching the device fill color.
- These label boxes are always **brought to front** (last in XML, highest z-index).
- Never place the label below the icon — cables frequently run there and will cross through it.

```python
# Symmetric placement formula
LBL_W, LBL_H = 130, 40
LBL_GAP       = 14                          # gap from device edge to label box

LBL_LEFT_X  = LC - DEV_W//2 - LBL_GAP - LBL_W   # left column: label goes left
LBL_RIGHT_X = RC + DEV_W//2 + LBL_GAP            # right column: label goes right
LBL_Y       = lambda device_center_y: device_center_y - LBL_H // 2
```

#### Annotation / speed labels
- Every link-speed or topology annotation must also be a **filled rounded rectangle** with a colored border matching the link color. `fillColor=#FFFFFF;strokeColor=<link_color>`.
- Never use `fillColor=none` for any label that sits in the diagram body where cables run.

#### Legend
- **No text on lines.** Edges carry empty `value=""`.
- **Legend** bottom-right using **real colored edge swatches** (tiny floating edges), not `=====` text. One row per link speed/media.
- Legend text labels inside the legend box can use `fillColor=none` because the legend container itself has a white fill — cables do not enter the legend box.

### Z-ordering rules (layer stacking)

These rules determine draw order and must be enforced in the generator:

| Element | Z-order |
|---|---|
| Cabling / edges | **Bring to back** — all links are sent to the back layer so they never overlap devices or labels |
| PP (patch panel) boxes | **Bring to front** — PPs must always be visible above cables |
| Device name / model text boxes | **Bring to front** — labels float above everything |

In draw.io XML this is controlled with `style="...;zOrderIndex=..."` or by cell ordering in the `<root>` block. Emit cabling cells first (lowest index), then devices, then PPs and text labels last (highest index).

### Layout
- **Zones as large dashed containers** for physical locations (DC1/DC2/MCR/SCR).
- Hierarchy bottom-to-top by Y: access at largest Y (bottom), core/DC at smallest Y (top).
- **Representative blocks** when quantity is large: draw one device + a note "N x Model (1 shown, representative of N)". Do not draw all.
- Color/style per link speed: e.g. 10G blue solid, 10G-ring blue dashed, 50G orange, 100G purple thick.

## Reference assets

- `scripts/topology_helpers.py` — reusable cell/edge/patch/node builders + style factories. Import or copy into a per-diagram generator.
- `scripts/example_campus_topology.py` — full worked example (SCR access → MCR aggregation → DC Core/Border → Fusion → DC Core), symmetric, fan-out PPs, channel-routed cross-links, legend. Use as a starting template.

## Common pitfalls checklist (verify in the rendered PNG)

- [ ] Every Cisco icon shows a glyph (not a blank box) → fix stencil/fill.
- [ ] Correct stencil family used per device type: router → `cisco.routers`, NGFW → `cisco.firewalls`, spine/leaf → `cisco.switches.cisco_spine/leaf`.
- [ ] Vertical links are straight → fix column X alignment.
- [ ] Each link lands on its own PP box, centered → add fan-out PPs.
- [ ] Devices with 2 port groups have 2 separate PP boxes.
- [ ] All cabling is at the back layer (behind devices, PPs, labels).
- [ ] PP boxes are in front (visible above cables).
- [ ] Device name/model labels are **filled rounded boxes** (not transparent), brought to front.
- [ ] Device labels placed **beside** the icon (left col → left, right col → right), vertically centered — never below the icon.
- [ ] No device has its name/model typed directly on the shape stencil (icon value="").
- [ ] All annotation/speed labels are filled shapes — `fillColor=none` is forbidden in the diagram body.
- [ ] No central X pile-up → route cross-links via waypoint channel.
- [ ] Full-mesh 2↔2 or 2↔4 topologies use the X-connection pattern (confirmed with user first).
- [ ] No line crosses any label text → move labels to rounded boxes off the lines.
- [ ] Left/right mirror is exact → use the mirror-axis formula.
- [ ] Legend uses real line swatches.
