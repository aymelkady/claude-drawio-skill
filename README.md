# Drawio — Claude Code Skill

Build clean, professional **draw.io (diagrams.net) network topology diagrams** with Cisco stencils, then **render to PNG and visually verify** before delivering. Encodes hard-won rules on alignment, Cisco stencils, fan-out patch panels, and link routing.

See [`SKILL.md`](SKILL.md) for the full workflow and rules.

## Install on another computer

Clone into your Claude Code skills directory so the skill is discovered automatically.

**macOS / Linux**
```bash
git clone https://github.com/aymelkady/claude-drawio-skill.git ~/.claude/skills/Drawio
```

**Windows (PowerShell)**
```powershell
git clone https://github.com/aymelkady/claude-drawio-skill.git "$env:USERPROFILE\.claude\skills\Drawio"
```

Restart Claude Code (or start a new session). Invoke with `/Drawio`, or it auto-activates on requests like "draw.io diagram", "network topology", "HLD diagram", "Cisco stencil diagram".

## Requirements

- **draw.io desktop CLI** for rendering/verifying PNGs. Download: https://github.com/jgraph/drawio-desktop/releases
  - Windows path used by the skill: `C:\Program Files\draw.io\draw.io.exe`
  - macOS/Linux: `drawio` on PATH, or `npx @drawio/export`.
- **Python 3** with **Pillow** (`pip install pillow`) for cropping/zoom verification.

## Contents

- `SKILL.md` — workflow, hard rules, pitfalls checklist.
- `scripts/topology_helpers.py` — reusable builders (nodes, fan-out patch boxes, channel-routed edges, legend swatches, mirror helpers, validate, write).
- `scripts/example_campus_topology.py` — worked template (SCR → MCR → DC), with rendered `.drawio` + `.png`.

## Using image stencils (e.g. a Cisco ACI icon library)

draw.io image styles are `;`-delimited, so an embedded data URI must **not** contain `;base64`. Convert `data:image/png;base64,<B64>` to `data:image/png,<B64>` before putting it in an `image=` style, or the icon renders blank.
