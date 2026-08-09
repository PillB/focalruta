"""
generate_lens_comparison.py — Lens comparison diagrams.

For each of 3 standard distances (2.5m / 4m / 6m), produces ONE diagram showing
how 35mm, 50mm, and 85mm lenses frame the same subject from the same position.
This is pedagogically critical: visually demonstrates focal length effect on:
  - Framing (subject size)
  - FoV (background coverage)
  - DoF (at same aperture)
  - Perspective note: at the SAME camera position, focal length changes framing/FoV, not geometric perspective.
    The familiar “telephoto compression” appears when you move farther back to keep similar framing.
"""
import os
import sys
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_diagrams import (
    PALETTE, FOV_TABLE, get_fov, aperture_to_fnum,
    estimate_dof, draw_camera_icon, draw_subject_icon,
    draw_distance_marker, LENS_LABELS
)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon, Rectangle, Circle, FancyBboxPatch
import numpy as np

from pathlib import Path
OUT_DIR = str(Path(__file__).resolve().parents[1] / "diagrams")
os.makedirs(OUT_DIR, exist_ok=True)

# Distances to compare
DISTANCES = [
    {"d": 2.5, "label": "Corta (2.5m)", "use_case": "Retrato 3/4"},
    {"d": 4.0, "label": "Media (4.0m)", "use_case": "Half-body + entorno"},
    {"d": 6.0, "label": "Larga (6.0m)", "use_case": "Full-body ambiental"},
]

# Fair optical comparison: all primes at the common aperture f/2.
# Maximum aperture is shown elsewhere from the verified lens specs.
LENSES = [
    {"focal": 35, "aperture": "f/2", "color": "#0EA5E9"},
    {"focal": 50, "aperture": "f/2", "color": "#7C3AED"},
    {"focal": 85, "aperture": "f/2", "color": "#DC2626"},
]


def render_lens_comparison(distance_m, label, use_case, output_path):
    """Render a 3-lens side-by-side comparison at a fixed distance."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 7), facecolor=PALETTE["bg"], dpi=110)
    fig.suptitle(f"Comparativa de Lentes · Distancia cámara→sujeto = {distance_m} m  ·  {use_case}",
                 fontsize=14, fontweight="bold", color=PALETTE["ink"], y=0.97)
    fig.text(0.5, 0.93, "Misma posición de cámara, mismo sujeto — solo cambia el lente. Observa cómo el FoV, el encuadre y el desenfoque del fondo cambian.",
             ha="center", fontsize=10, color=PALETTE["muted"], style="italic")

    for ax_idx, lens in enumerate(LENSES):
        ax = axes[ax_idx]
        ax.set_facecolor(PALETTE["bg"])
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

        focal = lens["focal"]
        h_fov, v_fov = get_fov(focal)
        fnum = aperture_to_fnum(lens["aperture"])
        near_m, far_m, H = estimate_dof(focal, fnum, distance_m)

        # Subject at distance_m, background at distance_m + 8m
        bg_d = distance_m + 8
        scene_w = max(8, bg_d * 0.8)
        ax.set_xlim(-scene_w/2 - 1, scene_w/2 + 1)
        ax.set_ylim(-1.5, bg_d + 2)

        # Title with lens info
        ax.text(0.5, 0.97, f"{focal}mm  {lens['aperture']}",
                transform=ax.transAxes, fontsize=13, fontweight="bold",
                color=lens["color"], ha="center", va="top")
        ax.text(0.5, 0.92, f"FoV H {h_fov:.1f}°  ·  V {v_fov:.1f}°",
                transform=ax.transAxes, fontsize=9, color=PALETTE["muted"],
                ha="center", va="top")
        ax.text(0.5, 0.88, f"DoF: {near_m:.2f}m → {'∞' if far_m is None or far_m > 50 else f'{far_m:.1f}m'}",
                transform=ax.transAxes, fontsize=9, color=PALETTE["dof_line"],
                fontweight="bold", ha="center", va="top")

        # Camera at origin
        cam_x = 0
        cam_y = 0

        # FoV cone (lighter for visualization)
        half_angle = math.radians(h_fov / 2)
        cone_to_bg = [
            (cam_x, cam_y),
            (cam_x - bg_d * math.tan(half_angle), cam_y + bg_d),
            (cam_x + bg_d * math.tan(half_angle), cam_y + bg_d),
        ]
        poly_cone = Polygon(cone_to_bg, closed=True,
                            facecolor=lens["color"], alpha=0.08,
                            edgecolor=lens["color"], linewidth=1.2, zorder=2)
        ax.add_patch(poly_cone)

        # Cone to subject (more saturated)
        cone_to_subj = [
            (cam_x, cam_y),
            (cam_x - distance_m * math.tan(half_angle), cam_y + distance_m),
            (cam_x + distance_m * math.tan(half_angle), cam_y + distance_m),
        ]
        poly_subj = Polygon(cone_to_subj, closed=True,
                            facecolor=lens["color"], alpha=0.18,
                            edgecolor=lens["color"], linewidth=1.5, zorder=3)
        ax.add_patch(poly_subj)

        # Center axis
        ax.plot([cam_x, cam_x], [cam_y, bg_d], color=lens["color"],
                linewidth=0.8, linestyle="--", alpha=0.6, zorder=3)

        # Background (trees)
        for i in range(7):
            tx = -scene_w/2 + 1 + i * (scene_w / 7)
            tree = Circle((tx, bg_d), 0.30, facecolor=PALETTE["bg_layer"],
                          edgecolor=PALETTE["bg_layer"], alpha=0.35, zorder=2)
            ax.add_patch(tree)
            ax.plot([tx, tx], [bg_d - 0.05, bg_d - 0.20],
                    color=PALETTE["bg_layer"], linewidth=1.5, zorder=2)
        ax.text(0, bg_d + 0.6, f"FONDO ({bg_d:.0f}m)", ha="center", va="bottom",
                fontsize=8, color=PALETTE["muted"], fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                          edgecolor=PALETTE["soft"], linewidth=0.6))

        # DoF zone
        if near_m and far_m and far_m < 50:
            dof_poly = [
                (cam_x - near_m * math.tan(half_angle), cam_y + near_m),
                (cam_x + near_m * math.tan(half_angle), cam_y + near_m),
                (cam_x + far_m * math.tan(half_angle), cam_y + far_m),
                (cam_x - far_m * math.tan(half_angle), cam_y + far_m),
            ]
        else:
            # Infinite DoF — show as extended cone
            far_show = bg_d
            dof_poly = [
                (cam_x - near_m * math.tan(half_angle), cam_y + near_m),
                (cam_x + near_m * math.tan(half_angle), cam_y + near_m),
                (cam_x + far_show * math.tan(half_angle), cam_y + far_show),
                (cam_x - far_show * math.tan(half_angle), cam_y + far_show),
            ]
        poly_dof = Polygon(dof_poly, closed=True,
                           facecolor=PALETTE["dof_fill"], alpha=0.25,
                           edgecolor=PALETTE["dof_line"], linewidth=1.0,
                           linestyle=":", zorder=2)
        ax.add_patch(poly_dof)
        # DoF label
        ax.text(cam_x + distance_m * math.tan(half_angle) + 0.3, cam_y + near_m,
                f"near {near_m:.2f}m", fontsize=7.5, color=PALETTE["dof_line"],
                fontweight="bold", ha="left", va="bottom", zorder=5,
                bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                          edgecolor=PALETTE["dof_line"], linewidth=0.5, alpha=0.95))

        # Subject (always human for comparison consistency)
        draw_subject_icon(ax, 0, distance_m, variant="human",
                          pose_key="arms_crossed", pose_desc="Pose estándar para comparativa",
                          color=lens["color"])

        # Camera
        draw_camera_icon(ax, cam_x, cam_y, color=PALETTE["camera"], label=f"6D · {focal}mm")

        # Distance marker
        draw_distance_marker(ax, -scene_w/2 + 0.4, 0, -scene_w/2 + 0.4, distance_m,
                             f"{distance_m}m", color=PALETTE["muted"])

        # Pedagogical footer in each subplot
        insights = {
            35: f"Amplio: sujeto pequeño, mucho fondo visible. PDC más profunda → fondo también nítido.",
            50: f"Natural: encuadre medio, fondo aún visible. PDC media → fondo suavemente desenfocado.",
            85: f"Estrecho: sujeto grande dentro del cuadro. Misma posición = misma perspectiva; PDC muy corta → bokeh fuerte.",
        }
        ax.text(0.5, 0.04, insights[focal],
                transform=ax.transAxes, fontsize=8, color=PALETTE["muted"],
                ha="center", va="bottom", style="italic", wrap=True,
                bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                          edgecolor=PALETTE["soft"], linewidth=0.5, alpha=0.95))

    # Bottom legend with key insight
    fig.text(0.5, 0.02,
             "INSIGHT: Desde la MISMA posición, la focal cambia FoV/encuadre, NO la perspectiva. La ‘compresión tele’ aparece al alejar la cámara para conservar un encuadre parecido.",
             ha="center", fontsize=10, color=PALETTE["ink"], fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#FEF3C7",
                       edgecolor="#F59E0B", linewidth=1.5))

    fig.savefig(output_path, dpi=110, facecolor=PALETTE["bg"],
                bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    return output_path


def main():
    print("Generating 3 lens comparison diagrams...")
    for d in DISTANCES:
        fname = f"lens_comparison_{int(d['d']*10)}cm.png"
        out = os.path.join(OUT_DIR, fname)
        render_lens_comparison(d["d"], d["label"], d["use_case"], out)
        print(f"  ✓ {fname}")
    print("\nAll lens comparison diagrams generated.")


if __name__ == "__main__":
    main()
