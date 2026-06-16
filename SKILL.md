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
- Use classic **`mxgraph.cisco.switches.layer_3_switch`** for L3 devices and **`workgroup_switch`** for access. These render a recognizable Cisco glyph and are enabled by default.
- **Avoid `multilayer_switch`** and the modern `mxgraph.cisco19.rect;prIcon=...` set: they render as near-blank boxes in CLI export. Distinguish device roles by **fill color + label**, not by risky stencil names.
- **Solid fills read best**: e.g. `fillColor=#1F6FA8;strokeColor=#ffffff` (Cisco blue), grey `#5D6D7E` for secondary. Pale pastel fills wash the glyph out.

### Patch panels (external port boxes)
- Every device gets small **PP boxes** (`~40x14`, dark fill `#34495E`, white text "PP"). **All links terminate on PP boxes, never on the switch stencil.**
- **One PP per link (fan-out).** A device with 4 uplinks gets 4 north PPs, not one. Fanning 4 links into a single PP causes overlap and looks like the links miss the box. This was the #1 alignment defect.
- PP centered on its link side: top PP for north links, bottom PP for south links.

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

### Labels & legend
- **No text on lines.** Edges carry empty `value`. Put every link label in a small **rounded rectangle** placed beside the link, or above the device. Lines must never cross label text.
- Device model labels go directly under the icon (`verticalLabelPosition=bottom`) or in a side label box in the zone margin.
- **Legend** bottom-right using **real colored edge swatches** (tiny edges), not `=====` text. One row per link speed/media + a PP swatch.

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
- [ ] Vertical links are straight → fix column X alignment.
- [ ] Each link lands on its own PP box, centered → add fan-out PPs.
- [ ] No central X pile-up → route cross-links via waypoint channel.
- [ ] No line crosses any label text → move labels to rounded boxes off the lines.
- [ ] Left/right mirror is exact → use the mirror-axis formula.
- [ ] Legend uses real line swatches.
