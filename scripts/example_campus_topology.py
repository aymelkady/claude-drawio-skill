"""Worked example: campus physical topology using topology_helpers.

SCR access (bottom) -> MCR1/MCR2 aggregation (middle) -> DC1/DC2 (top, each:
Core/Border -> Fusion -> DC Core). Demonstrates the Drawio skill rules:
mirror symmetry, column-aligned stacks, fan-out PPs (one per link),
channel-routed cross-links, real legend swatches, no text on lines.

Run:  python example_campus_topology.py
Then render + verify the PNG (see SKILL.md).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from topology_helpers import *   # noqa

reset()
AXIS = 1300
C10  = link_style("#1F6FBF", 2.5)
C10R = link_style("#1F6FBF", 2.5, dashed=True)
C50  = link_style("#E67E22", 3)
C100 = link_style("#C0392B", 3)

cell("title", TITLE, "Campus Physical Network Topology — SCR / MCR / DC Core-Border / Fusion / DC Core",
     40, 18, 1600, 40)
cell("subt", SUBT, "Physical HLD only: device models, quantities, locations, link speeds and media.", 40, 56, 1400, 22)

# ---- DC column: Core/Border (bottom) -> Fusion -> DC Core (top), all on 2 aligned X columns
DCC_Y, FU_Y, CB_Y = 150, 320, 500
def dc(p, C, title):
    cell(p + "_z", ZONE("#117A65"), title, C - 350, 110, 700, 470)
    L, R = C - 90, C + 90
    for tag, y, lbl, fc in [("dcc", DCC_Y, "Nexus 9504", BLUE),
                            ("fu", FU_Y, "C9550-24L4CD", BLUE),
                            ("cb", CB_Y, "C9550-96L4D", BLUE)]:
        node(f"{p}_{tag}_l", L, y, lbl, fc); node(f"{p}_{tag}_r", R, y, lbl, fc)
    # PPs: dcc bottom; fusion top+bottom; cb top + two bottom (fan-out to 2 MCRs)
    patch_bot(f"{p}_dcc_l_bp", L, DCC_Y); patch_bot(f"{p}_dcc_r_bp", R, DCC_Y)
    patch_top(f"{p}_fu_l_tp", L, FU_Y);   patch_top(f"{p}_fu_r_tp", R, FU_Y)
    patch_bot(f"{p}_fu_l_bp", L, FU_Y);   patch_bot(f"{p}_fu_r_bp", R, FU_Y)
    patch_top(f"{p}_cb_l_tp", L, CB_Y);   patch_top(f"{p}_cb_r_tp", R, CB_Y)
    # two south PPs per CB node: one for local MCR, one for cross MCR
    patch(f"{p}_cb_l_bp1", L - 14, CB_Y + NH + GAP); patch(f"{p}_cb_l_bp2", L + 14, CB_Y + NH + GAP)
    patch(f"{p}_cb_r_bp1", R - 14, CB_Y + NH + GAP); patch(f"{p}_cb_r_bp2", R + 14, CB_Y + NH + GAP)
dc("dc1", 650, "Data Center 1 / DC1")
dc("dc2", 1950, "Data Center 2 / DC2")

# DC internal 100G cross-connects (straight, box-to-box)
def dc_int(p):
    for s in ("cb_l", "cb_r"):
        for t in ("fu_l", "fu_r"):
            edge(f"e_{p}_{s}_{t}", f"{p}_{s}_tp", f"{p}_{t}_bp", C100 + "exitX=0.5;exitY=0;entryX=0.5;entryY=1;")
    for s in ("fu_l", "fu_r"):
        for t in ("dcc_l", "dcc_r"):
            edge(f"e_{p}_{s}_{t}", f"{p}_{s}_tp", f"{p}_{t}_bp", C100 + "exitX=0.5;exitY=0;entryX=0.5;entryY=1;")
dc_int("dc1"); dc_int("dc2")

# ---- MCR aggregation (middle), one representative AGG per MCR
MCR_Y = 760
def mcr(p, C, title):
    cell(p + "_z", ZONE("#1F3864"), title, C - 210, 700, 420, 150)
    node(p + "_agg", C, MCR_Y, "C9550-96L4D")
    cell(p + "_n", NOTE("#1F3864", "#EAF0FB"), "16 × C9550-96L4D (1 shown, representative)", C + 30, MCR_Y - 6, 180, 40)
    # fan-out north PPs: one per uplink bundle (local DC + cross DC), south PP for SCR
    patch(p + "_np_loc", C - 24, MCR_Y - PH - GAP)
    patch(p + "_np_x",   C + 24, MCR_Y - PH - GAP)
    patch_bot(p + "_sp", C, MCR_Y)
mcr("mcr1", 650, "MCR1 — Aggregation / Distribution")
mcr("mcr2", 1950, "MCR2 — Aggregation / Distribution")

cell("note_tot", NOTE("#B9770E"), "Total AGG/DIST: 32 × C9550-96L4D across MCR1 and MCR2", 790, 70, 620, 28)

# MCR -> DC 50G. Local = straight to near DC; cross = channel-routed waypoints (no central X)
edge("e_m1_d1l", "mcr1_np_loc", "dc1_cb_l_bp1", C50 + "exitX=0.5;exitY=0;entryX=0.5;entryY=1;")
edge("e_m1_d1r", "mcr1_np_loc", "dc1_cb_r_bp1", C50 + "exitX=0.5;exitY=0;entryX=0.5;entryY=1;")
edge("e_m2_d2l", "mcr2_np_loc", "dc2_cb_l_bp1", C50 + "exitX=0.5;exitY=0;entryX=0.5;entryY=1;")
edge("e_m2_d2r", "mcr2_np_loc", "dc2_cb_r_bp1", C50 + "exitX=0.5;exitY=0;entryX=0.5;entryY=1;")
edge("e_m1_d2", "mcr1_np_x", "dc2_cb_l_bp2", C50 + "exitX=0.5;exitY=0;entryX=0.5;entryY=1;",
     waypoints=[(674, 650), (1936, 650)])
edge("e_m2_d1", "mcr2_np_x", "dc1_cb_r_bp2", C50 + "exitX=0.5;exitY=0;entryX=0.5;entryY=1;",
     waypoints=[(1974, 670), (664, 670)])

cell("l_m1d1", LL("#E67E22"), "Each DIST: 2 × 50G LR to DC1 Core/Border Pair", 90, 600, 215, 34)
cell("l_m2d2", LL("#E67E22"), "Each DIST: 2 × 50G LR to DC2 Core/Border Pair", mirror_x(90, 215, AXIS), 600, 215, 34)
cell("l_m1d2", LL("#E67E22"), "MCR1 DIST: 2 × 50G LR to DC2 (cross-link)", 1040, 612, 230, 34)
cell("l_m2d1", LL("#E67E22"), "MCR2 DIST: 2 × 50G LR to DC1 (cross-link)", mirror_x(1040, 230, AXIS), 672, 230, 34)

# ---- SCR access (bottom, center): C9350 access + IE-3500 ring
SCR_Y = 980
cell("scr_z", ZONE("#2E6CA4", "#F4F9FF"), "SCR Access Layer", 940, 940, 720, 160)
node("scr_acc", 1180, SCR_Y, "C9350-48U", name="workgroup_switch")
node("scr_ie", 1420, SCR_Y, "IE-3500-8U3X-A", name="workgroup_switch", fc=GREY)
patch_top("scr_acc_p1", 1180 - 14, SCR_Y); patch_top("scr_acc_p2", 1180 + 14, SCR_Y)
patch_top("scr_ie_p1", 1420 - 14, SCR_Y); patch_top("scr_ie_p2", 1420 + 14, SCR_Y)

edge("e_acc_m1", "scr_acc_p1", "mcr1_sp", C10 + "exitX=0.5;exitY=0;entryX=0.5;entryY=1;", waypoints=[(1166, 910)])
edge("e_acc_m2", "scr_acc_p2", "mcr2_sp", C10 + "exitX=0.5;exitY=0;entryX=0.5;entryY=1;", waypoints=[(1194, 910)])
edge("e_ie_m1", "scr_ie_p1", "mcr1_sp", C10R + "exitX=0.5;exitY=0;entryX=0.5;entryY=1;", waypoints=[(1406, 924)])
edge("e_ie_m2", "scr_ie_p2", "mcr2_sp", C10R + "exitX=0.5;exitY=0;entryX=0.5;entryY=1;", waypoints=[(1434, 924)])

cell("scr_n", NOTE("#2E6CA4", "#EAF2FB"), "Representative SCR Access Block — Multiple SCR Access Switches", 950, 1058, 700, 30)
cell("l_acc", LL("#1F6FBF"), "Each SCR Access: 1 × 10G LR to MCR1 + 1 × 10G LR to MCR2", 720, 890, 250, 30)
cell("l_ie", LL("#1F6FBF"), "IE-3500 Industrial Ring: 10G LR ring to MCR1 & MCR2", 1560, 890, 250, 30)

# ---- legend (bottom-right) with real swatches
LX, LY = 1740, 1000
cell("leg", "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#333;verticalAlign=top;"
     "align=center;fontStyle=1;fontSize=12;fontColor=#333;arcSize=4;", "Legend — Link Speed / Media", LX, LY, 420, 230)
legend_swatch("lg0", LX + 22, LY + 46, C10,  "10G LR (blue solid) — SCR Access → MCR")
legend_swatch("lg1", LX + 22, LY + 92, C10R, "10G LR Ring (blue dashed) — IE-3500 ring")
legend_swatch("lg2", LX + 22, LY + 138, C50, "50G LR (orange) — MCR DIST → DC Core/Border")
legend_swatch("lg3", LX + 22, LY + 184, C100,"100G (red thick) — DC internal cross-connect")

n = write_drawio(os.path.join(os.path.dirname(os.path.abspath(__file__)), "example_campus_topology.drawio"),
                 page_w=2300, page_h=1260, name="Campus Physical Topology")
print("cells:", n)
