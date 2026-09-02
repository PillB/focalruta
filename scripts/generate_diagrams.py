"""
generate_diagrams.py — Python matplotlib generator for Canon 6D San Isidro photo planner.

Produces, for each shot × variant (dog/human), a single PNG containing:
  LEFT  panel : 2D overhead ("planta") with camera icon, subject icon, background,
                FoV cone (with horizontal FoV derived from focal length), DoF zone,
                distance markers, composition overlays (rule-of-thirds lines, etc.).
  RIGHT panel : 2.5D side elevation ("alzado") with camera height, camera angle
                (central/picado/contrapicado/nadir/cenital), subject pose (stick figure
                or dog silhouette), background layer, light direction arrow.

Output: <project_root>/diagrams/<plan>_<shot>_<variant>.png

Iteration log (6 passes):
  v1 initial: basic two-panel, simple FoV triangle, stick figure subject.
  v2: added DoF shaded zone, distance markers, composition overlay grid.
  v3: color-coded camera-angle tilt, light-direction arrow, ISO/aperture chips.
  v4: dog silhouette variant, pose name label, improved typography.
  v5: refined FoV cone with two zones (in-frame vs total), better palette.
  v6: added "settings chip" footer (lens/focal/aperture/shutter/iso), legend.
"""

import os
import sys
import math

import optics_physics
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
from matplotlib.patches import FancyArrowPatch, Polygon, Wedge, Rectangle, Circle, FancyBboxPatch
from matplotlib.lines import Line2D
import numpy as np

# ---------------------------------------------------------------------------
# Font setup
# ---------------------------------------------------------------------------
try:
    fm.fontManager.addfont('/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf')
except Exception:
    pass
try:
    fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
except Exception:
    pass
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Noto Sans SC', 'Liberation Sans']
plt.rcParams['axes.unicode_minus'] = False

# ---------------------------------------------------------------------------
# Color palette (color-blind safe, editorial)
# ---------------------------------------------------------------------------
PALETTE = {
    "bg":        "#FBFAF5",
    "panel_bg":  "#FFFFFF",
    "ink":       "#0F172A",
    "muted":     "#64748B",
    "soft":      "#94A3B8",
    "line":      "#CBD5E1",
    "camera":    "#0F172A",
    "fov_fill":  "#2563EB",
    "fov_line":  "#1D4ED8",
    "dof_fill":  "#16A34A",
    "dof_line":  "#15803D",
    "subject":   "#7C3AED",
    "subject_2": "#A855F7",
    "bg_layer":  "#64748B",
    "light_sun": "#F59E0B",
    "light_low": "#EF4444",
    "tripod":    "#475569",
    "rule3":     "#EF4444",
    "compose":   "#0EA5E9",
    "warning":   "#DC2626",
    "ok":        "#16A34A",
    "lens_chip": "#1E40AF",
    "chip_bg":   "#F1F5F9",
}

# Lens label lookup
LENS_LABELS = {
    35: "EF 35mm f/2 IS USM",
    50: "EF 50mm f/1.8 STM",
    85: "EF 85mm f/1.8 USM",
    "35-80": "EF 35–80mm f/4–5.6 III",
    "35-80@35": "EF 35–80mm @35mm",
    "35-80@50": "EF 35–80mm @50mm",
    "35-80@80": "EF 35–80mm @80mm",
}

# FoV table (full-frame, horizontal & vertical, degrees) for common focals
FOV_TABLE = {
    24: (73.4, 52.9),
    28: (65.1, 46.2),
    35: (54.2, 37.7),
    50: (39.4, 26.9),
    70: (28.7, 19.4),
    80: (25.2, 17.0),
    85: (23.8, 16.0),
    100: (20.3, 13.6),
    135: (15.1, 10.1),
}

def get_focal_mm(lens_focal):
    """Extract integer focal length from string like '35-80@50'."""
    if isinstance(lens_focal, int):
        return lens_focal
    if isinstance(lens_focal, str):
        if "@" in lens_focal:
            return int(lens_focal.split("@")[1])
        if "-" in lens_focal:
            return int(lens_focal.split("-")[0])  # use wide end for default
    return 35

def get_fov(focal_mm):
    """Return (h_fov_deg, v_fov_deg) for a given focal length on FF Canon 6D."""
    if focal_mm in FOV_TABLE:
        return FOV_TABLE[focal_mm]
    h_fov = optics_physics.angle_of_view_deg(focal_mm, optics_physics.CANON_6D_WIDTH_MM)
    v_fov = optics_physics.angle_of_view_deg(focal_mm, optics_physics.CANON_6D_HEIGHT_MM)
    return (h_fov, v_fov)

def aperture_to_fnum(ap_str):
    """Extract f-number from strings like 'f/1.8', 'f/11', 'f/16'."""
    if isinstance(ap_str, (int, float)):
        return float(ap_str)
    s = str(ap_str).replace("f/", "").strip()
    try:
        return float(s)
    except ValueError:
        return 4.0

def shutter_to_seconds(ss_str):
    """Convert shutter string to seconds float."""
    if isinstance(ss_str, (int, float)):
        return float(ss_str)
    s = str(ss_str).strip()
    if s.lower().startswith("bulb"):
        # Try to parse "Bulb 20\"" -> 20
        parts = s.replace('"', '').replace("'", '').split()
        for p in parts[1:]:
            try:
                return float(p)
            except ValueError:
                continue
        return 20.0
    if "/" in s:
        try:
            num, den = s.split("/")
            return float(num) / float(den)
        except ValueError:
            return 1.0
    try:
        return float(s.replace('"', '').replace("'", ''))
    except ValueError:
        return 1.0


# ---------------------------------------------------------------------------
# Geometry helpers — compute FoV cone vertices
# ---------------------------------------------------------------------------

def fov_cone_polygon(camera_xy, subject_distance_m, h_fov_deg, half_length=1.0):
    """
    Build a polygon (in scene meters) representing the FoV cone from camera position.
    camera_xy: (x, y) in meters (top of plot)
    subject_distance_m: distance to subject
    h_fov_deg: horizontal FoV in degrees
    half_length: how far BEYOND the subject to extend the cone (1.0 = same as subject distance)
    Returns list of (x, y) vertices [camera, left_far, right_far] for a triangle.
    """
    cx, cy = camera_xy
    half_angle = math.radians(h_fov_deg / 2)
    total_depth = subject_distance_m * (1 + half_length)
    left_x = cx - total_depth * math.tan(half_angle)
    right_x = cx + total_depth * math.tan(half_angle)
    far_y = cy + total_depth
    return [(cx, cy), (left_x, far_y), (right_x, far_y)]


def dof_zone_polygon(camera_xy, subject_distance_m, h_fov_deg, near_m, far_m):
    """
    Build a trapezoid representing the DoF zone (between near and far planes).
    If far_m is None or > 50, treat as infinity (use 6× subject distance).
    """
    cx, cy = camera_xy
    half_angle = math.radians(h_fov_deg / 2)
    far = far_m if (far_m and far_m < 50) else subject_distance_m * 6
    far = max(far, subject_distance_m + 1)

    near_left  = cx - near_m * math.tan(half_angle)
    near_right = cx + near_m * math.tan(half_angle)
    far_left   = cx - far  * math.tan(half_angle)
    far_right  = cx + far  * math.tan(half_angle)

    return [
        (near_left, cy + near_m),
        (near_right, cy + near_m),
        (far_right, cy + far),
        (far_left, cy + far),
    ]


def estimate_dof(focal_mm, fnum, subject_distance_m):
    """
    Estimate DoF near/far limits using a simplified circle-of-confusion model.
    CoC for FF = 0.030 mm. Returns (near_m, far_m, hyperfocal_m).
    """
    zone = optics_physics.depth_of_field(focal_mm, fnum, subject_distance_m)
    near = max(0.1, zone["near"])
    far = zone["far"] if zone["far"] < 1000.0 else None
    return (near, far, zone["hyperfocal"])


# ---------------------------------------------------------------------------
# Drawing primitives
# ---------------------------------------------------------------------------

def draw_camera_icon(ax, x, y, color=None, label="CÁMARA", angle_deg=0):
    """Draw a top-down camera icon at (x, y). Camera looks UP (+y direction)."""
    color = color or PALETTE["camera"]
    # Body
    body = FancyBboxPatch((x - 0.18, y - 0.12), 0.36, 0.24,
                          boxstyle="round,pad=0.02,rounding_size=0.05",
                          facecolor="white", edgecolor=color, linewidth=2.2, zorder=10)
    ax.add_patch(body)
    # Lens
    lens = Rectangle((x - 0.07, y + 0.10), 0.14, 0.08,
                     facecolor=color, edgecolor=color, linewidth=1, zorder=11)
    ax.add_patch(lens)
    # Hot shoe
    shoe = Rectangle((x - 0.05, y - 0.14), 0.10, 0.03,
                     facecolor=color, edgecolor=color, linewidth=0.5, zorder=12)
    ax.add_patch(shoe)
    ax.text(x, y - 0.30, label, ha="center", va="top",
            fontsize=8.5, fontweight="bold", color=color, zorder=11)


def draw_subject_icon(ax, x, y, variant="human", pose_key="", pose_desc="", color=None):
    """Draw a top-down subject icon. variant = 'human' or 'dog'."""
    color = color or PALETTE["subject"]
    if variant == "human":
        # Head (circle) + shoulders (ellipse)
        head = Circle((x, y + 0.15), 0.08, facecolor="white", edgecolor=color, linewidth=2, zorder=9)
        shoulders = mpatches.Ellipse((x, y), width=0.36, height=0.20,
                                     facecolor=color, edgecolor=color, alpha=0.85, zorder=8)
        ax.add_patch(shoulders)
        ax.add_patch(head)
        # Pose indicator (label placed OFFSET to the RIGHT of subject to avoid overlap)
        pose_label = pose_key.replace("_", " ").title() if pose_key else "SUJETO"
        ax.text(x + 0.55, y + 0.05, pose_label, ha="left", va="center",
                fontsize=7.5, fontweight="bold", color=color, zorder=11,
                bbox=dict(boxstyle="round,pad=0.28", facecolor="white",
                          edgecolor=color, linewidth=0.9, alpha=0.96))
        if pose_desc:
            # Truncate to 50 chars and place BELOW subject
            short_desc = pose_desc[:50] + ("…" if len(pose_desc) > 50 else "")
            ax.text(x, y - 0.40, short_desc,
                    ha="center", va="top", fontsize=6.8, color=PALETTE["muted"],
                    style="italic", zorder=11,
                    bbox=dict(boxstyle="round,pad=0.22", facecolor="white",
                              edgecolor=PALETTE["soft"], linewidth=0.4, alpha=0.92))
    else:  # dog
        # Body ellipse + head circle (smaller, in front)
        body = mpatches.Ellipse((x, y), width=0.45, height=0.22,
                                facecolor=color, edgecolor=color, alpha=0.85, zorder=8)
        head = Circle((x, y + 0.20), 0.09, facecolor=color, edgecolor=color, zorder=9)
        # Tail
        tail = Line2D([x - 0.20, x - 0.32], [y, y + 0.10],
                      color=color, linewidth=2.2, zorder=8)
        ax.add_patch(body)
        ax.add_patch(head)
        ax.add_line(tail)
        # 4 legs (small dots)
        for lx in [-0.15, -0.05, 0.05, 0.15]:
            ax.plot([x + lx, x + lx], [y - 0.05, y - 0.15], color=color, linewidth=1.2, zorder=7)
        pose_label = pose_key.replace("_", " ").title() if pose_key else "PERRO"
        ax.text(x + 0.60, y + 0.05, pose_label, ha="left", va="center",
                fontsize=7.5, fontweight="bold", color=color, zorder=11,
                bbox=dict(boxstyle="round,pad=0.28", facecolor="white",
                          edgecolor=color, linewidth=0.9, alpha=0.96))
        if pose_desc:
            short_desc = pose_desc[:50] + ("…" if len(pose_desc) > 50 else "")
            ax.text(x, y - 0.40, short_desc,
                    ha="center", va="top", fontsize=6.8, color=PALETTE["muted"],
                    style="italic", zorder=11,
                    bbox=dict(boxstyle="round,pad=0.22", facecolor="white",
                              edgecolor=PALETTE["soft"], linewidth=0.4, alpha=0.92))


def draw_background_layer(ax, x_center, y, width_m, label="FONDO", kind="trees"):
    """Draw a stylized background layer at distance y."""
    if kind == "trees":
        # Row of circles (tree canopies)
        n = max(3, int(width_m / 1.5))
        for i in range(n):
            tx = x_center - width_m / 2 + (i + 0.5) * (width_m / n)
            tree = Circle((tx, y), 0.25, facecolor=PALETTE["bg_layer"],
                          edgecolor=PALETTE["bg_layer"], alpha=0.3, zorder=2)
            ax.add_patch(tree)
            # Trunk
            ax.plot([tx, tx], [y - 0.05, y - 0.15], color=PALETTE["bg_layer"], linewidth=1.5, zorder=2)
    elif kind == "horizon":
        # Sea line
        ax.plot([x_center - width_m/2, x_center + width_m/2], [y, y],
                color=PALETTE["fov_line"], linewidth=2.5, zorder=2, alpha=0.6)
        # Wavy lines below (sea)
        xs = np.linspace(x_center - width_m/2, x_center + width_m/2, 30)
        for offset in [0.5, 1.0]:
            ys = y - offset + 0.08 * np.sin(xs * 2)
            ax.plot(xs, ys, color=PALETTE["fov_line"], linewidth=0.8, alpha=0.4, zorder=2)
    elif kind == "buildings":
        # Rectangles of varying heights
        n = max(4, int(width_m / 2))
        for i in range(n):
            bx = x_center - width_m / 2 + i * (width_m / n)
            h = 0.4 + 0.5 * ((i * 37) % 7) / 7
            building = Rectangle((bx, y - 0.05), width_m/n - 0.05, h,
                                 facecolor=PALETTE["bg_layer"], edgecolor=PALETTE["bg_layer"],
                                 alpha=0.45, zorder=2)
            ax.add_patch(building)
    elif kind == "wall":
        # Horizontal bar
        rect = Rectangle((x_center - width_m/2, y - 0.05), width_m, 0.10,
                         facecolor=PALETTE["bg_layer"], edgecolor=PALETTE["bg_layer"],
                         alpha=0.5, zorder=2)
        ax.add_patch(rect)
    # Label
    ax.text(x_center, y + 0.4, label, ha="center", va="bottom",
            fontsize=8, fontweight="bold", color=PALETTE["muted"], zorder=5,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor=PALETTE["soft"], linewidth=0.6))


def draw_distance_marker(ax, x1, y1, x2, y2, label, color=None):
    """Draw a distance measurement line with end ticks and label."""
    color = color or PALETTE["muted"]
    ax.plot([x1, x2], [y1, y2], color=color, linewidth=1.2, linestyle="-", zorder=4)
    tick = 0.08
    ax.plot([x1, x1], [y1 - tick, y1 + tick], color=color, linewidth=1.2, zorder=4)
    ax.plot([x2, x2], [y2 - tick, y2 + tick], color=color, linewidth=1.2, zorder=4)
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    ax.text(mid_x + 0.15, mid_y, label, fontsize=7.5, color=color, fontweight="bold",
            zorder=5, bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                                edgecolor="none", alpha=0.92))


def _overlay_tercios(ax, x, y, width, height):
    for i in [1, 2]:
        ax.plot([x - width/2 + i*width/3, x - width/2 + i*width/3],
                [y - height/2, y + height/2], color=PALETTE["rule3"],
                linewidth=0.7, linestyle="--", alpha=0.55, zorder=3)
        ax.plot([x - width/2, x + width/2],
                [y - height/2 + i*height/3, y - height/2 + i*height/3],
                color=PALETTE["rule3"], linewidth=0.7, linestyle="--", alpha=0.55, zorder=3)
    for i in [1, 2]:
        for j in [1, 2]:
            ax.plot(x - width/2 + i*width/3, y - height/2 + j*height/3,
                    marker="o", color=PALETTE["rule3"], markersize=4, alpha=0.7, zorder=4)


def _overlay_simetria(ax, x, y, _width, height):
    ax.plot([x, x], [y - height/2, y + height/2], color=PALETTE["compose"],
            linewidth=1.0, linestyle=":", alpha=0.7, zorder=3)


def _overlay_perspectiva(ax, x, y, width, height):
    for sign in [-1, 1]:
        ax.plot([x, x + sign*width/2], [y, y + height/2], color=PALETTE["compose"],
                linewidth=0.8, linestyle="--", alpha=0.5, zorder=3)


def _overlay_enmarcado(ax, x, y, width, height):
    ax.add_patch(Rectangle((x - width/4, y - height/4), width/2, height/2,
                           facecolor="none", edgecolor=PALETTE["compose"],
                           linewidth=1.5, linestyle="-", alpha=0.6, zorder=3))


def _overlay_espacio_neg(ax, x, y, width, _height):
    ax.text(x + width/3, y, "ESPACIO\nNEGATIVO", ha="center", va="center",
            fontsize=8, color=PALETTE["compose"], fontweight="bold", alpha=0.7, zorder=4,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=PALETTE["compose"], linewidth=0.6, alpha=0.5))


def _overlay_punto_interes(ax, x, y, _width, _height):
    ax.plot(x, y, marker="+", color=PALETTE["rule3"], markersize=18,
            mew=2, alpha=0.7, zorder=4)


def _overlay_minimalismo(ax, x, y, _width, _height):
    ax.add_patch(Circle((x, y), 0.6, facecolor="none", edgecolor=PALETTE["compose"],
                        linewidth=1.0, linestyle=":", alpha=0.6, zorder=3))


def _overlay_capas(ax, x, y, width, _height):
    for offset, label in [(0.5, "FG"), (0, "MID"), (-0.5, "BG")]:
        ax.plot([x - width/3, x + width/3], [y + offset, y + offset],
                color=PALETTE["compose"], linewidth=0.7, linestyle="--", alpha=0.5, zorder=3)
        ax.text(x - width/3 - 0.1, y + offset, label, fontsize=6.5,
                color=PALETTE["compose"], fontweight="bold", alpha=0.8,
                ha="right", va="center", zorder=4)


COMPOSITION_OVERLAYS = {
    "tercios": _overlay_tercios,
    "simetria": _overlay_simetria,
    "perspectiva": _overlay_perspectiva,
    "enmarcado": _overlay_enmarcado,
    "espacio_neg": _overlay_espacio_neg,
    "punto_interes": _overlay_punto_interes,
    "minimalismo": _overlay_minimalismo,
    "capas": _overlay_capas,
}


def draw_composition_overlay(ax, x_center, y_subject, width_m, height_m, rule_key):
    """Draw subtle overlay lines indicating composition rule."""
    renderer = COMPOSITION_OVERLAYS.get(rule_key)
    if renderer:
        renderer(ax, x_center, y_subject, width_m, height_m)


def draw_fov_cone(ax, camera_xy, subject_distance_m, h_fov_deg, bg_distance_m):
    """Draw the FoV cone (filled triangle) from camera to subject and beyond."""
    # Cone extending to subject
    cone_to_subject = fov_cone_polygon(camera_xy, subject_distance_m, h_fov_deg, half_length=0)
    poly1 = Polygon(cone_to_subject, closed=True,
                    facecolor=PALETTE["fov_fill"], alpha=0.12,
                    edgecolor=PALETTE["fov_line"], linewidth=1.5, zorder=3)
    ax.add_patch(poly1)
    # Cone from subject to background
    if bg_distance_m and bg_distance_m > subject_distance_m:
        # Background cone
        cx, cy = camera_xy
        half_angle = math.radians(h_fov_deg / 2)
        subj_left  = cx - subject_distance_m * math.tan(half_angle)
        subj_right = cx + subject_distance_m * math.tan(half_angle)
        bg_left  = cx - bg_distance_m * math.tan(half_angle)
        bg_right = cx + bg_distance_m * math.tan(half_angle)
        poly2 = Polygon([(subj_left, cy + subject_distance_m),
                         (subj_right, cy + subject_distance_m),
                         (bg_right, cy + bg_distance_m),
                         (bg_left, cy + bg_distance_m)],
                        closed=True, facecolor=PALETTE["fov_fill"], alpha=0.05,
                        edgecolor="none", zorder=2)
        ax.add_patch(poly2)
    # Center axis (dashed)
    cx, cy = camera_xy
    end_y = cy + (bg_distance_m or subject_distance_m * 2)
    ax.plot([cx, cx], [cy, end_y], color=PALETTE["fov_line"], linewidth=1.0,
            linestyle="--", alpha=0.6, zorder=3)


def draw_dof_zone(ax, camera_xy, subject_distance_m, h_fov_deg, near_m, far_m):
    """Draw the DoF zone (shaded trapezoid)."""
    if near_m is None or far_m is None:
        return
    poly = dof_zone_polygon(camera_xy, subject_distance_m, h_fov_deg, near_m, far_m)
    p = Polygon(poly, closed=True, facecolor=PALETTE["dof_fill"], alpha=0.32,
                edgecolor=PALETTE["dof_line"], linewidth=1.4, linestyle=":", zorder=2)
    ax.add_patch(p)
    # Labels for near/far — place at the SIDE, not over the subject
    cx, cy = camera_xy
    half_angle = math.radians(h_fov_deg / 2)
    near_label_x = cx + near_m * math.tan(half_angle) + 0.2
    ax.text(near_label_x, cy + near_m,
            f"near {near_m:.2f}m", fontsize=7.5, color=PALETTE["dof_line"],
            fontweight="bold", ha="left", va="bottom", zorder=5,
            bbox=dict(boxstyle="round,pad=0.22", facecolor="white",
                      edgecolor=PALETTE["dof_line"], linewidth=0.6, alpha=0.95))
    # Far label (only if finite)
    if far_m and far_m < 50:
        far_label_x = cx + far_m * math.tan(half_angle) + 0.2
        ax.text(far_label_x, cy + far_m,
                f"far {far_m:.1f}m", fontsize=7.5, color=PALETTE["dof_line"],
                fontweight="bold", ha="left", va="bottom", zorder=5,
                bbox=dict(boxstyle="round,pad=0.22", facecolor="white",
                          edgecolor=PALETTE["dof_line"], linewidth=0.6, alpha=0.95))
    else:
        ax.text(near_label_x, cy + near_m + 0.4,
                "→ ∞ (infinito)", fontsize=7.5, color=PALETTE["dof_line"],
                fontweight="bold", ha="left", va="bottom", zorder=5,
                bbox=dict(boxstyle="round,pad=0.22", facecolor="white",
                          edgecolor=PALETTE["dof_line"], linewidth=0.6, alpha=0.95))


# ---------------------------------------------------------------------------
# Subject policy shared by every diagram
# ---------------------------------------------------------------------------
def effective_subject_variant(shot, requested_variant):
    """Return human/dog/None after field-card safety rules.

    In dog mode the ghost shot still uses a HUMAN mover (dog stays out), while
    urban long-exposure shots intentionally have no animal/person subject.
    """
    if requested_variant == "dog" and shot.get("technique") == "fantasma":
        return "human"
    if requested_variant == "dog" and shot.get("technique") == "larga_exp":
        return None
    return requested_variant

# ---------------------------------------------------------------------------
# 2D Overhead panel (planta)
# ---------------------------------------------------------------------------

def render_topdown_panel(fig, rect, shot, variant, focal_mm, h_fov, v_fov, near_m, far_m, H):
    """Render the 2D overhead view (planta) in the given axes rect."""
    ax = fig.add_axes(rect)
    ax.set_facecolor(PALETTE["bg"])
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    sd = shot["subject_distance_m"]
    bd = shot["background_distance_m"]
    cam_x = 0
    cam_y = 0

    # Scene extent
    scene_w = max(8, sd * 2, bd * 0.5)
    scene_h = max(8, bd * 1.2 + 2)
    ax.set_xlim(-scene_w/2 - 1, scene_w/2 + 1)
    ax.set_ylim(-1.5, scene_h + 1)

    # Title
    ax.text(0.02, 0.97, f"PLANTA 2D · {shot['composition_label']} · FoV H ≈ {h_fov:.1f}°",
            transform=ax.transAxes, fontsize=11, fontweight="bold",
            color=PALETTE["ink"], va="top")
    ax.text(0.02, 0.93, f"Lente: {LENS_LABELS.get(shot['lens_focal'], shot['lens_focal'])}  ·  Cámara→sujeto {sd:.1f} m  ·  Sujeto→fondo {max(0, bd - sd):.1f} m",
            transform=ax.transAxes, fontsize=8.5, color=PALETTE["muted"], va="top")

    # Ground / surface
    ground = Rectangle((-scene_w/2 - 1, -1.5), scene_w + 2, scene_h + 2.5,
                       facecolor=PALETTE["bg"], edgecolor="none", zorder=0)
    ax.add_patch(ground)

    # Subject X position (centered on camera axis)
    subj_x = 0
    subj_y = sd

    # Composition overlay (drawn first, behind everything)
    draw_composition_overlay(ax, subj_x, subj_y, scene_w * 0.8, scene_h * 0.6,
                              shot["composition"])

    # FoV cone
    draw_fov_cone(ax, (cam_x, cam_y), sd, h_fov, bd)

    # DoF zone
    draw_dof_zone(ax, (cam_x, cam_y), sd, h_fov, near_m, far_m)

    # Background layer
    bg_kind = "trees"
    if "Malecón" in shot.get("scene_notes", "") or "horizonte" in shot.get("scene_notes", "").lower() or "mar" in shot.get("scene_notes", "").lower():
        bg_kind = "horizon"
    elif "Centro" in shot.get("scene_notes", "") or "Plaza" in shot.get("scene_notes", "") or "arquitect" in shot.get("scene_notes", "").lower():
        bg_kind = "buildings"
    elif "casa" in shot.get("scene_notes", "").lower() or "sala" in shot.get("scene_notes", "").lower():
        bg_kind = "wall"
    draw_background_layer(ax, 0, bd, scene_w, label=f"FONDO · {bd:.0f} m", kind=bg_kind)

    # Distance markers
    draw_distance_marker(ax, -scene_w/2 + 0.3, 0, -scene_w/2 + 0.3, sd,
                         f"{sd:.1f} m", color=PALETTE["muted"])
    draw_distance_marker(ax, -scene_w/2 + 0.6, sd, -scene_w/2 + 0.6, bd,
                         f"{bd-sd:.1f} m", color=PALETTE["muted"])

    # Subject icon after global field-card safety/clarity policy.
    eff_variant = effective_subject_variant(shot, variant)
    if eff_variant is not None:
        pose_data = shot["subjects"][eff_variant]
        draw_subject_icon(ax, subj_x, subj_y, variant=eff_variant,
                          pose_key=pose_data["pose"], pose_desc=pose_data["action"])
        if eff_variant != variant:
            ax.text(subj_x, subj_y + 0.75, "PERSONA · PERRO FUERA", fontsize=7.5,
                    color=PALETTE["warning"], ha="center", fontweight="bold", zorder=12)
    else:
        ax.text(subj_x, subj_y, "PERRO FUERA · SIN SUJETO", fontsize=8,
                color=PALETTE["warning"], ha="center", va="center", fontweight="bold", zorder=12,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=PALETTE["warning"], linewidth=0.8))

    # Camera icon
    draw_camera_icon(ax, cam_x, cam_y)

    # Settings chips at bottom
    chip_y = -1.0
    chips = [
        (f"  {LENS_LABELS.get(shot['lens_focal'], shot['lens_focal'])}  ", PALETTE["lens_chip"]),
        (f"  {shot['aperture']}  ", PALETTE["ok"]),
        (f"  {shot['shutter']}  ", PALETTE["warning"]),
        (f"  ISO {shot['iso']}  ", PALETTE["muted"]),
    ]
    chip_x = -scene_w/2 + 0.3
    for label, color in chips:
        ax.text(chip_x, chip_y, label, fontsize=8, color="white", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor=color, edgecolor="none"),
                va="center", ha="left", zorder=10)
        chip_x += len(label) * 0.16 + 0.4

    # Legend (top-right)
    legend_items = [
        ("FoV cone", PALETTE["fov_fill"], 0.12),
        ("DoF zone", PALETTE["dof_fill"], 0.18),
        ("Subject",  PALETTE["subject"], 0.85),
    ]
    for i, (lbl, col, alpha) in enumerate(legend_items):
        ly = 0.97 - i * 0.035
        rect = Rectangle((0.78, ly - 0.012), 0.04, 0.025, facecolor=col, alpha=alpha,
                         edgecolor=col, linewidth=0.6, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(0.84, ly, lbl, fontsize=7, color=PALETTE["ink"],
                transform=ax.transAxes, va="center")

    return ax


# ---------------------------------------------------------------------------
# 2.5D side view panel (alzado) with camera angle + pose
# ---------------------------------------------------------------------------

def draw_human_side(ax, x, y_ground, pose_key, color, scale=1.0):
    """Draw a stick-figure human in side view at (x, y_ground)."""
    s = scale
    poses = {
        "s_curve_standing":  [(0, 0), (0, 0.45*s), (0, 0.85*s), (0, 1.30*s), (0.10*s, 1.55*s)],  # spine curve
        "walking_candid":    [(0, 0), (0, 0.50*s), (0, 1.00*s), (0, 1.40*s), (0.05*s, 1.65*s)],
        "looking_back":      [(0, 0), (0, 0.50*s), (0, 1.00*s), (0, 1.40*s), (-0.10*s, 1.55*s)],
        "thinking_seated":   [(0.30*s, 0), (0.20*s, 0.20*s), (0.15*s, 0.40*s), (0.10*s, 0.55*s), (0.05*s, 0.70*s)],
        "candid_laugh":      [(0, 0), (0, 0.50*s), (0, 1.00*s), (0, 1.40*s), (-0.05*s, 1.60*s)],
        "arms_crossed":      [(0, 0), (0, 0.50*s), (0, 1.00*s), (0, 1.40*s), (0, 1.55*s)],
        "leaning_wall":      [(0, 0), (0, 0.50*s), (0, 1.00*s), (0, 1.40*s), (0, 1.55*s)],
        "running_dynamic":   [(-0.30*s, 0.05*s), (-0.10*s, 0.50*s), (0.05*s, 1.00*s), (-0.10*s, 1.40*s), (0.10*s, 1.60*s)],
        "jumping_joy":       [(0, 0.20*s), (0, 0.60*s), (0, 1.05*s), (0, 1.45*s), (0, 1.65*s)],
        "portrait_3_4":      [(0, 0), (0, 0.50*s), (0, 1.00*s), (0, 1.40*s), (0.08*s, 1.55*s)],
    }
    pts = poses.get(pose_key, poses["arms_crossed"])
    # Hip, shoulder, head
    hip = (x + pts[1][0], y_ground + pts[1][1])
    shoulder = (x + pts[3][0], y_ground + pts[3][1])
    head = (x + pts[4][0], y_ground + pts[4][1])
    feet_l = (x + pts[0][0] - 0.10*s, y_ground + pts[0][1])
    feet_r = (x + pts[0][0] + 0.10*s, y_ground + pts[0][1])
    # Spine
    ax.plot([hip[0], shoulder[0]], [hip[1], shoulder[1]], color=color, linewidth=2.5, zorder=8)
    # Legs
    ax.plot([hip[0], feet_l[0]], [hip[1], feet_l[1]], color=color, linewidth=2.5, zorder=8)
    ax.plot([hip[0], feet_r[0]], [hip[1], feet_r[1]], color=color, linewidth=2.5, zorder=8)
    # Arms
    if pose_key == "arms_crossed":
        ax.plot([shoulder[0]-0.18*s, shoulder[0]+0.18*s], [shoulder[1]-0.05*s, shoulder[1]-0.05*s],
                color=color, linewidth=2.5, zorder=8)
    elif pose_key == "jumping_joy":
        ax.plot([shoulder[0], shoulder[0]-0.25*s], [shoulder[1], shoulder[1]+0.30*s],
                color=color, linewidth=2.5, zorder=8)
        ax.plot([shoulder[0], shoulder[0]+0.25*s], [shoulder[1], shoulder[1]+0.30*s],
                color=color, linewidth=2.5, zorder=8)
    else:
        ax.plot([shoulder[0], shoulder[0]-0.22*s], [shoulder[1], shoulder[1]-0.30*s],
                color=color, linewidth=2.5, zorder=8)
        ax.plot([shoulder[0], shoulder[0]+0.22*s], [shoulder[1], shoulder[1]-0.30*s],
                color=color, linewidth=2.5, zorder=8)
    # Head circle
    head_circle = Circle(head, 0.10*s, facecolor="white", edgecolor=color, linewidth=2, zorder=10)
    ax.add_patch(head_circle)


def draw_dog_side(ax, x, y_ground, pose_key, color, scale=1.0):
    """Draw a dog silhouette in side view."""
    s = scale
    poses = {
        "sit_stay":             {"body_y": 0.30*s, "body_w": 0.55*s, "body_h": 0.18*s, "head_offset": (0.30*s, 0.10*s), "legs": "folded"},
        "lying_down":           {"body_y": 0.10*s, "body_w": 0.70*s, "body_h": 0.12*s, "head_offset": (0.35*s, 0.05*s), "legs": "folded"},
        "running_fetch":        {"body_y": 0.45*s, "body_w": 0.65*s, "body_h": 0.18*s, "head_offset": (0.35*s, 0.05*s), "legs": "extended"},
        "standing_alert":       {"body_y": 0.45*s, "body_w": 0.60*s, "body_h": 0.20*s, "head_offset": (0.32*s, 0.10*s), "legs": "straight"},
        "jumping_catch":        {"body_y": 0.65*s, "body_w": 0.60*s, "body_h": 0.18*s, "head_offset": (0.32*s, 0.05*s), "legs": "tucked"},
        "walking_candid":       {"body_y": 0.45*s, "body_w": 0.62*s, "body_h": 0.18*s, "head_offset": (0.33*s, 0.08*s), "legs": "walking"},
        "head_tilt":            {"body_y": 0.30*s, "body_w": 0.55*s, "body_h": 0.18*s, "head_offset": (0.30*s, 0.10*s), "legs": "folded"},
        "play_bow":             {"body_y": 0.40*s, "body_w": 0.65*s, "body_h": 0.18*s, "head_offset": (0.35*s, -0.15*s), "legs": "mixed"},
        "backlit_silhouette":   {"body_y": 0.45*s, "body_w": 0.60*s, "body_h": 0.20*s, "head_offset": (0.32*s, 0.10*s), "legs": "straight"},
        "treat_focus":          {"body_y": 0.30*s, "body_w": 0.55*s, "body_h": 0.18*s, "head_offset": (0.30*s, 0.10*s), "legs": "folded"},
    }
    p = poses.get(pose_key, poses["sit_stay"])
    body_cx = x
    body_cy = y_ground + p["body_y"]
    body_w = p["body_w"]
    body_h = p["body_h"]
    # Body ellipse
    body = mpatches.Ellipse((body_cx, body_cy), width=body_w, height=body_h,
                            facecolor=color, edgecolor=color, alpha=0.85, zorder=8)
    ax.add_patch(body)
    # Head
    head_x = body_cx + p["head_offset"][0]
    head_y = body_cy + p["head_offset"][1]
    head = Circle((head_x, head_y), 0.10*s, facecolor=color, edgecolor=color, zorder=9)
    ax.add_patch(head)
    # Snout
    snout = Circle((head_x + 0.08*s, head_y - 0.02*s), 0.05*s, facecolor=color, edgecolor=color, zorder=9)
    ax.add_patch(snout)
    # Ear (triangle)
    ear = Polygon([(head_x - 0.05*s, head_y + 0.08*s),
                   (head_x - 0.10*s, head_y + 0.18*s),
                   (head_x, head_y + 0.10*s)], facecolor=color, edgecolor=color, zorder=9)
    ax.add_patch(ear)
    # Tail
    tail_base_x = body_cx - body_w/2 + 0.05*s
    tail_base_y = body_cy + 0.02*s
    tail_end_x = tail_base_x - 0.18*s
    tail_end_y = tail_base_y + (0.15*s if pose_key != "lying_down" else 0)
    ax.plot([tail_base_x, tail_end_x], [tail_base_y, tail_end_y],
            color=color, linewidth=2.5, zorder=8)
    # Legs
    if p["legs"] == "straight":
        for sign in [-1, 1]:
            ax.plot([body_cx + sign*0.18*s, body_cx + sign*0.18*s],
                    [body_cy - body_h/2, y_ground], color=color, linewidth=2, zorder=8)
    elif p["legs"] == "extended":
        # Front legs forward, back legs back
        ax.plot([body_cx + 0.20*s, body_cx + 0.30*s], [body_cy - body_h/2, y_ground - 0.05*s],
                color=color, linewidth=2, zorder=8)
        ax.plot([body_cx - 0.20*s, body_cx - 0.30*s], [body_cy - body_h/2, y_ground - 0.05*s],
                color=color, linewidth=2, zorder=8)
    elif p["legs"] == "folded":
        # Sitting — back legs folded under
        ax.plot([body_cx + 0.15*s, body_cx + 0.15*s], [body_cy - body_h/2, body_cy - body_h/2 - 0.08*s],
                color=color, linewidth=2, zorder=8)
    elif p["legs"] == "tucked":
        # Jumping — legs tucked
        ax.plot([body_cx + 0.18*s, body_cx + 0.22*s], [body_cy - body_h/2, body_cy - body_h/2 - 0.05*s],
                color=color, linewidth=2, zorder=8)
        ax.plot([body_cx - 0.18*s, body_cx - 0.22*s], [body_cy - body_h/2, body_cy - body_h/2 - 0.05*s],
                color=color, linewidth=2, zorder=8)
    elif p["legs"] == "walking":
        # Walking — alternating
        ax.plot([body_cx + 0.20*s, body_cx + 0.25*s], [body_cy - body_h/2, y_ground], color=color, linewidth=2, zorder=8)
        ax.plot([body_cx - 0.20*s, body_cx - 0.25*s], [body_cy - body_h/2, y_ground], color=color, linewidth=2, zorder=8)


def draw_camera_side(ax, x, y, angle_tilt_deg, color=None, height_label=""):
    """Draw side-view camera. 0° = horizontal/right, + = up, − = down."""
    color = color or PALETTE["camera"]
    body = FancyBboxPatch((x - 0.20, y - 0.10), 0.40, 0.20,
                          boxstyle="round,pad=0.02,rounding_size=0.04",
                          facecolor="white", edgecolor=color, linewidth=2, zorder=10)
    ax.add_patch(body)
    angle_rad = math.radians(angle_tilt_deg)
    lens_len = 0.22
    # Horizontal/right is the zero reference — this was reversed in the legacy diagram.
    lens_x = x + lens_len * math.cos(angle_rad)
    lens_y = y + lens_len * math.sin(angle_rad)
    perp_x = -math.sin(angle_rad)
    perp_y = math.cos(angle_rad)
    lens_w = 0.055
    poly = Polygon([
        (x - perp_x*lens_w, y - perp_y*lens_w),
        (x + perp_x*lens_w, y + perp_y*lens_w),
        (lens_x + perp_x*lens_w, lens_y + perp_y*lens_w),
        (lens_x - perp_x*lens_w, lens_y - perp_y*lens_w),
    ], facecolor=color, edgecolor=color, zorder=11)
    ax.add_patch(poly)
    if y > 0.5:
        for sign in [-1, 1]:
            ax.plot([x, x + sign*0.25], [y - 0.10, max(0, y - 0.40)],
                    color=PALETTE["tripod"], linewidth=1.5, zorder=8)
    if height_label:
        ax.text(x - 0.30, y, height_label, fontsize=7.5, color=color, fontweight="bold",
                ha="right", va="center", zorder=11,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor=color, linewidth=0.6))


def _side_angle_tilt(angle):
    return {"picado": -20, "contrapicado": 20, "nadir": 90, "cenital": -90}.get(angle, 0)


def _draw_side_background(ax, shot, bg_x):
    notes = shot.get("scene_notes", "")
    if "horizonte" in notes.lower() or "mar" in notes.lower():
        ax.plot([bg_x - 2, bg_x + 2], [1.5, 1.5], color=PALETTE["fov_line"], linewidth=2.5, alpha=0.7, zorder=2)
        for x in np.arange(bg_x - 2, bg_x + 2, 0.3):
            ax.plot([x, x + 0.15], [1.3, 1.4], color=PALETTE["fov_line"], linewidth=0.6, alpha=0.5, zorder=2)
        label, label_y = "HORIZONTE / MAR", 1.7
    elif "Plaza" in notes or "arquitect" in notes.lower() or "Jirón" in notes:
        for i, height in enumerate([2.0, 2.5, 2.2, 2.8, 2.4]):
            bx = bg_x - 1 + i * 0.6
            ax.add_patch(Rectangle((bx, 0), 0.55, height, facecolor=PALETTE["bg_layer"],
                                   edgecolor=PALETTE["bg_layer"], alpha=0.4, zorder=2))
        label, label_y = "FACHADAS", 3.1
    else:
        for i in range(5):
            tx = bg_x - 1.5 + i * 0.6
            ax.add_patch(Circle((tx, 1.7), 0.30, facecolor=PALETTE["bg_layer"],
                                edgecolor=PALETTE["bg_layer"], alpha=0.4, zorder=2))
            ax.plot([tx, tx], [1.4, 0], color=PALETTE["bg_layer"], linewidth=1.5, zorder=2)
        label, label_y = "FONDO", 2.4
    ax.text(bg_x, label_y, label, fontsize=8, color=PALETTE["muted"], ha="center",
            fontweight="bold", zorder=5,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                      edgecolor=PALETTE["soft"], linewidth=0.6))


def _draw_side_subject(ax, shot, variant, sd):
    subj_x = 0 if shot["angle"] in ("nadir", "cenital") else sd
    effective = effective_subject_variant(shot, variant)
    if effective == "human":
        draw_human_side(ax, subj_x, 0, shot["subjects"]["human"]["pose"], PALETTE["subject"], scale=1.2)
    elif effective == "dog":
        draw_dog_side(ax, subj_x, 0, shot["subjects"]["dog"]["pose"], PALETTE["subject"], scale=1.2)
    if effective is not None:
        ax.add_patch(Circle((subj_x, 0.85), 0.55, facecolor="none",
                            edgecolor=PALETTE["subject"], linewidth=1.2,
                            linestyle=":", alpha=0.6, zorder=6))
    else:
        ax.text(subj_x, 0.75, "PERRO FUERA\nSIN SUJETO", fontsize=8,
                color=PALETTE["warning"], ha="center", va="center",
                fontweight="bold", zorder=8)
    return subj_x, effective


def _draw_side_angle_indicator(ax, cam_x, cam_y, angle_tilt, angle_label):
    if angle_tilt != 0:
        arc_r = 0.4
        limits = (angle_tilt, 0) if angle_tilt < 0 else (0, angle_tilt)
        ax.add_patch(mpatches.Arc((cam_x, cam_y), arc_r*2, arc_r*2, angle=0,
                                 theta1=limits[0], theta2=limits[1],
                                 color=PALETTE["warning"], linewidth=2, zorder=12))
        label_angle = math.radians(angle_tilt/2)
        lx = cam_x + 0.6 * math.cos(label_angle)
        ly = cam_y + 0.6 * math.sin(label_angle)
        text, color, align = f"{angle_label}\n{abs(angle_tilt)}°", PALETTE["warning"], "center"
    else:
        lx, ly = cam_x + 0.5, cam_y
        text, color, align = f"{angle_label}\n0° (eye-level)", PALETTE["ok"], "left"
    ax.text(lx, ly, text, fontsize=7, color=color, fontweight="bold",
            ha=align, va="center", zorder=12,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor=color, linewidth=0.6))


def render_side_panel(fig, rect, shot, variant, focal_mm, v_fov):
    """Render the 2.5D side elevation view."""
    ax = fig.add_axes(rect)
    ax.set_facecolor(PALETTE["panel_bg"])
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor(PALETTE["line"])
        spine.set_linewidth(1)

    # Scene setup
    sd = shot["subject_distance_m"]
    bd = shot["background_distance_m"]
    cam_h = shot["camera_height_m"]
    # Map distances to plot coords: 1m horizontal = 1 unit, 1m vertical = 1 unit (exaggerated x2 for visibility)
    vert_scale = 1.5

    scene_w = max(8, bd * 1.2 + 4)
    ax.set_xlim(-1, scene_w)
    ax.set_ylim(-0.5, 4)

    # Title
    ax.text(0.02, 0.97, f"ELEVACIÓN 2.5D · {shot['angle_label']} · FoV V ≈ {v_fov:.1f}°",
            transform=ax.transAxes, fontsize=11, fontweight="bold",
            color=PALETTE["ink"], va="top")
    ax.text(0.02, 0.93, f"Altura cámara: {cam_h:.2f} m  ·  Altura sujeto: ~1.65 m",
            transform=ax.transAxes, fontsize=8.5, color=PALETTE["muted"], va="top")

    # Ground line
    ax.plot([-1, scene_w], [0, 0], color=PALETTE["ink"], linewidth=1.5, zorder=2)
    # Ground hatching
    for x in np.arange(-0.5, scene_w, 0.4):
        ax.plot([x, x - 0.15], [0, -0.15], color=PALETTE["soft"], linewidth=0.6, zorder=1)

    # Camera position (x=0, y=cam_h*vert_scale)
    cam_x = 0
    cam_y = cam_h * vert_scale
    angle_tilt = _side_angle_tilt(shot["angle"])

    # Background layer (drawn first, in background)
    bg_x = bd
    _draw_side_background(ax, shot, bg_x)

    # Direction-aware vertical FoV cone. The legacy diagram always drew it
    # horizontally even for picado/contrapicado/nadir/cenital.
    half_v_deg = v_fov / 2
    ray_len = min(max(sd * 1.25, 4.0), max(scene_w - 1, 5.0))
    center_rad = math.radians(angle_tilt)
    p_center = (cam_x + ray_len * math.cos(center_rad),
                cam_y + ray_len * math.sin(center_rad))
    pts = []
    for ray_angle in (angle_tilt - half_v_deg, angle_tilt + half_v_deg):
        rr = math.radians(ray_angle)
        pts.append((cam_x + ray_len * math.cos(rr), cam_y + ray_len * math.sin(rr)))
    fov_poly = Polygon([(cam_x, cam_y), pts[0], pts[1]], closed=True,
                       facecolor=PALETTE["fov_fill"], alpha=0.10,
                       edgecolor=PALETTE["fov_line"], linewidth=1.2, zorder=3)
    ax.add_patch(fov_poly)
    ax.plot([cam_x, p_center[0]], [cam_y, p_center[1]], color=PALETTE["fov_line"],
            linewidth=0.9, linestyle="--", alpha=0.65, zorder=4)

    # Subject after shared field-card policy.
    # For vertical views, align the represented subject/canopy with the camera axis.
    subj_x, eff_variant = _draw_side_subject(ax, shot, variant, sd)

    # Camera
    draw_camera_side(ax, cam_x, cam_y, angle_tilt, height_label=f"{cam_h:.2f} m")

    # Angle indicator referenced to the horizontal optical axis (0°).
    _draw_side_angle_indicator(ax, cam_x, cam_y, angle_tilt, shot["angle_label"])

    # Distance markers (horizontal)
    draw_distance_marker(ax, -0.5, -0.35, sd, -0.35,
                         f"{sd:.1f} m", color=PALETTE["muted"])
    if bd > sd:
        draw_distance_marker(ax, sd + 0.1, -0.35, bd, -0.35,
                             f"{bd-sd:.1f} m", color=PALETTE["muted"])

    # Pose name chip
    pose_chip_x = sd
    pose_chip_y = 2.7
    _eff = effective_subject_variant(shot, variant)
    pose_label = (shot["subjects"][_eff]["pose"].replace("_", " ").title() if _eff else "Sin sujeto · perro fuera")
    ax.text(pose_chip_x, pose_chip_y, f"POSE: {pose_label}",
            fontsize=7.5, color=PALETTE["subject"], fontweight="bold",
            ha="center", va="center", zorder=11,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=PALETTE["subject"], linewidth=0.8))

    # Light direction indicator (top-right corner)
    light_x = scene_w - 1.5
    light_y = 3.5
    # Sun icon
    sun = Circle((light_x, light_y), 0.15, facecolor=PALETTE["light_sun"],
                 edgecolor=PALETTE["light_sun"], zorder=10)
    ax.add_patch(sun)
    # Rays
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        ax.plot([light_x + 0.20*math.cos(rad), light_x + 0.35*math.cos(rad)],
                [light_y + 0.20*math.sin(rad), light_y + 0.35*math.sin(rad)],
                color=PALETTE["light_sun"], linewidth=1.5, zorder=10)
    # Light direction arrow (toward subject)
    arrow = FancyArrowPatch((light_x - 0.15, light_y - 0.15),
                            (subj_x + 0.3, 1.8),
                            arrowstyle="->", color=PALETTE["light_sun"],
                            linewidth=1.5, alpha=0.6, zorder=9,
                            connectionstyle="arc3,rad=-0.2")
    ax.add_patch(arrow)
    ax.text(light_x, light_y + 0.45, "LUZ", fontsize=7, color=PALETTE["light_sun"],
            fontweight="bold", ha="center", zorder=10)

    # Settings chips at bottom
    chip_y = -0.45
    chips_text = [
        (f"{shot['technique_label']}", PALETTE["ok"]),
        (f"{shot['composition_label']}", PALETTE["compose"]),
        (f"{shot['angle_label']}", PALETTE["warning"]),
    ]
    cx = -0.5
    for label, color in chips_text:
        ax.text(cx, chip_y, f" {label} ", fontsize=7, color="white", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor=color, edgecolor="none"),
                va="center", ha="left", zorder=10)
        cx += len(label) * 0.13 + 0.5

    return ax


# ---------------------------------------------------------------------------
# Main renderer
# ---------------------------------------------------------------------------

def render_diagram(shot, plan, variant, output_path):
    """Render a single diagram for a shot × variant."""
    focal_mm = get_focal_mm(shot["lens_focal"])
    h_fov, v_fov = get_fov(focal_mm)
    fnum = aperture_to_fnum(shot["aperture"])
    near_m, far_m, H = estimate_dof(focal_mm, fnum, shot["subject_distance_m"])

    # Figure with two panels side by side — taller figure to fit footer
    fig = plt.figure(figsize=(16, 9.5), facecolor=PALETTE["bg"], dpi=110)
    # Use GridSpec for cleaner layout
    fig.suptitle(f"{plan['name']} · {shot['id']} — {shot['technique_label']}  [{variant.upper()}]",
                 fontsize=14, fontweight="bold", color=PALETTE["ink"], y=0.975)

    # Topdown panel (left, ~55%) — leave more room at bottom for footer
    render_topdown_panel(fig, [0.02, 0.10, 0.55, 0.83], shot, variant,
                         focal_mm, h_fov, v_fov, near_m, far_m, H)
    # Side panel (right, ~45%)
    render_side_panel(fig, [0.60, 0.10, 0.38, 0.83], shot, variant, focal_mm, v_fov)

    # Footer with reasoning snippet — wrap text properly
    import textwrap
    reason_text = shot['reasoning']
    if len(reason_text) > 320:
        reason_text = reason_text[:317] + "…"
    wrapped = textwrap.fill(f"RAZÓN: {reason_text}", width=180)
    fig.text(0.02, 0.045, wrapped, fontsize=8, color=PALETTE["muted"],
             ha="left", va="top", style="italic", wrap=True,
             fontfamily='DejaVu Sans')
    fig.text(0.98, 0.045, "Diagrama v7 · Python/matplotlib",
             fontsize=7.5, color=PALETTE["soft"], ha="right", va="top")

    fig.savefig(output_path, dpi=110, facecolor=PALETTE["bg"],
                bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    return output_path


# ---------------------------------------------------------------------------
# Main — generate all diagrams
# ---------------------------------------------------------------------------

def main():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from plans_data import PLANS

    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    out_dir = str(root / "diagrams")
    os.makedirs(out_dir, exist_ok=True)

    count = 0
    for plan in PLANS:
        for shot in plan["shots"]:
            for variant in ["dog", "human"]:
                fname = f"{plan['id']}_{shot['id']}_{variant}.png"
                out_path = os.path.join(out_dir, fname)
                try:
                    render_diagram(shot, plan, variant, out_path)
                    count += 1
                    print(f"  ✓ {fname}")
                except Exception as e:
                    print(f"  ✗ {fname}: {e}")
    print(f"\nTotal: {count} diagrams written to {out_dir}")


if __name__ == "__main__":
    main()
