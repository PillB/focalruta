"""
generate_composition_examples.py — Mini-diagrams illustrating each of the 8 composition rules.

Each diagram is a small frame (3:2 aspect ratio mimicking the camera's viewfinder)
showing WHERE to place the subject and supporting elements for each rule.
"""
import os
import sys
import math
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_diagrams import PALETTE

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon, Rectangle, Circle, FancyBboxPatch, FancyArrowPatch
import numpy as np

OUT_DIR = str(Path(__file__).resolve().parents[1] / "diagrams")
os.makedirs(OUT_DIR, exist_ok=True)


def render_composition_example(rule_key, title, description, output_path):
    """Render a single composition rule mini-diagram."""
    fig, ax = plt.subplots(figsize=(8, 6), facecolor=PALETTE["bg"], dpi=110)
    ax.set_facecolor("#F8FAFC")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor(PALETTE["soft"])
        spine.set_linewidth(1.5)

    # Title
    ax.text(0.5, 0.97, title, transform=ax.transAxes, fontsize=14, fontweight="bold",
            color=PALETTE["ink"], ha="left", va="top")
    ax.text(0.5, 0.91, description, transform=ax.transAxes, fontsize=9, color=PALETTE["muted"],
            ha="left", va="top", style="italic")

    # Frame border
    frame = Rectangle((0.5, 0.5), 11, 7, facecolor="white", edgecolor=PALETTE["ink"],
                      linewidth=2, zorder=1)
    ax.add_patch(frame)

    # Subject (always centered around middle, position varies by rule)
    subj_x, subj_y = 6, 4

    if rule_key == "tercios":
        # Rule of thirds grid
        for i in [1, 2]:
            ax.plot([0.5 + i*11/3, 0.5 + i*11/3], [0.5, 7.5],
                    color=PALETTE["rule3"], linewidth=1, linestyle="--", alpha=0.6, zorder=2)
            ax.plot([0.5, 11.5], [0.5 + i*7/3, 0.5 + i*7/3],
                    color=PALETTE["rule3"], linewidth=1, linestyle="--", alpha=0.6, zorder=2)
        # Power points (4 intersections)
        for i in [1, 2]:
            for j in [1, 2]:
                px = 0.5 + i*11/3
                py = 0.5 + j*7/3
                ax.plot(px, py, marker="o", color=PALETTE["rule3"], markersize=10, zorder=4)
                ax.plot(px, py, marker="o", color="white", markersize=5, zorder=5)
        # Subject on UPPER-LEFT power point (intersection of left vertical third + upper horizontal third)
        subj_x = 0.5 + 1*11/3  # = 4.17 (left vertical third)
        subj_y = 0.5 + 2*7/3   # = 5.17 (upper horizontal third — third from bottom)
        # The power points are at intersections:
        #   (0.5 + 1*11/3, 0.5 + 1*7/3) = lower-left
        #   (0.5 + 1*11/3, 0.5 + 2*7/3) = upper-left  <-- THIS is where subject should be
        #   (0.5 + 2*11/3, 0.5 + 1*7/3) = lower-right
        #   (0.5 + 2*11/3, 0.5 + 2*7/3) = upper-right
        ax.add_patch(Circle((subj_x, subj_y), 0.45, facecolor=PALETTE["subject"],
                            edgecolor=PALETTE["subject"], zorder=7))
        # Outer ring to highlight
        ax.add_patch(Circle((subj_x, subj_y), 0.7, facecolor="none",
                            edgecolor=PALETTE["subject"], linewidth=2, linestyle="--", zorder=6))
        ax.text(subj_x, subj_y - 1.0, "SUJETO en punto\nde poder", ha="center", fontsize=8,
                fontweight="bold", color=PALETTE["subject"], zorder=7,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                          edgecolor=PALETTE["subject"], linewidth=0.6))

    elif rule_key == "perspectiva":
        # Converging lines
        for sign in [-1, 1]:
            ax.plot([6, 6 + sign*5], [4, 7], color=PALETTE["compose"], linewidth=2, alpha=0.6, zorder=2)
            ax.plot([6, 6 + sign*5], [4, 1], color=PALETTE["compose"], linewidth=2, alpha=0.6, zorder=2)
        # Vanishing point
        ax.add_patch(Circle((6, 4), 0.15, facecolor=PALETTE["compose"], zorder=5))
        ax.text(6.3, 4, "Punto de fuga", fontsize=7, color=PALETTE["compose"], fontweight="bold")
        # Subject on vanishing point
        ax.add_patch(Circle((6, 4), 0.4, facecolor=PALETTE["subject"],
                            edgecolor=PALETTE["subject"], alpha=0.7, zorder=4))
        ax.text(6, 3.2, "SUJETO en punto de fuga", ha="center", fontsize=8, fontweight="bold",
                color=PALETTE["subject"], zorder=6)
        # Floor tiles (perspective)
        for i in range(1, 5):
            offset = i * 0.7
            ax.plot([6 - 5 + offset, 6 + 5 - offset], [1 + i*0.15, 1 + i*0.15],
                    color=PALETTE["muted"], linewidth=0.5, alpha=0.4)

    elif rule_key == "simetria":
        # Vertical axis
        ax.plot([6, 6], [0.5, 7.5], color=PALETTE["compose"], linewidth=1.5,
                linestyle=":", alpha=0.7, zorder=2)
        # Mirror subjects
        for sign in [-1, 1]:
            sx = 6 + sign * 2
            ax.add_patch(Circle((sx, 4), 0.4, facecolor=PALETTE["subject"],
                                edgecolor=PALETTE["subject"], zorder=4))
        # Mirror buildings (simple rects)
        for sign in [-1, 1]:
            for offset in [1.5, 2.5]:
                bx = 6 + sign * offset
                ax.add_patch(Rectangle((bx - 0.3, 0.5), 0.6, 2.5,
                                       facecolor=PALETTE["bg_layer"],
                                       edgecolor=PALETTE["bg_layer"], alpha=0.3, zorder=2))
        ax.text(6, 7, "EJE de SIMETRÍA", ha="center", fontsize=8, color=PALETTE["compose"],
                fontweight="bold", zorder=5,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor=PALETTE["compose"]))

    elif rule_key == "enmarcado":
        # Frame (arch)
        arch_x_left = 1.5
        arch_x_right = 10.5
        arch_y_top = 7
        arch_y_bot = 0.5
        # Arch shape (rectangle + half circle on top)
        rect = Rectangle((arch_x_left, arch_y_bot), arch_x_right - arch_x_left, arch_y_top - arch_y_bot - 1.5,
                         facecolor="none", edgecolor=PALETTE["compose"], linewidth=3, zorder=3)
        ax.add_patch(rect)
        arch = mpatches.Arc(((arch_x_left + arch_x_right)/2, arch_y_top - 1.5),
                            arch_x_right - arch_x_left, 3, angle=0, theta1=0, theta2=180,
                            color=PALETTE["compose"], linewidth=3, zorder=3)
        ax.add_patch(arch)
        ax.text(arch_x_left - 0.3, arch_y_top - 1.5, "Marco", fontsize=8, color=PALETTE["compose"],
                fontweight="bold", ha="right", va="center")
        # Subject inside frame
        ax.add_patch(Circle((6, 3.5), 0.5, facecolor=PALETTE["subject"],
                            edgecolor=PALETTE["subject"], zorder=4))
        ax.text(6, 2.7, "SUJETO enmarcado", ha="center", fontsize=8, fontweight="bold",
                color=PALETTE["subject"], zorder=5)

    elif rule_key == "espacio_neg":
        # Hatched negative space (right side)
        for x in np.arange(7, 11.5, 0.3):
            ax.plot([x, x + 0.2], [0.5, 7.5], color=PALETTE["compose"], linewidth=0.4, alpha=0.3)
        ax.text(9.25, 4, "ESPACIO\nNEGATIVO", ha="center", va="center", fontsize=9,
                color=PALETTE["compose"], fontweight="bold", alpha=0.7)
        # Subject on left third
        subj_x = 3.5
        ax.add_patch(Circle((subj_x, 4), 0.4, facecolor=PALETTE["subject"],
                            edgecolor=PALETTE["subject"], zorder=4))
        # Direction arrow (subject looking into negative space)
        arrow = FancyArrowPatch((subj_x + 0.5, 4.3), (subj_x + 2, 4.3),
                                arrowstyle="->", color=PALETTE["subject"], linewidth=2, zorder=5)
        ax.add_patch(arrow)
        ax.text(subj_x, 3.2, "SUJETO", ha="center", fontsize=8, fontweight="bold",
                color=PALETTE["subject"], zorder=6)

    elif rule_key == "punto_interes":
        # Background pattern (subtle)
        for i in range(8):
            for j in range(5):
                ax.add_patch(Circle((1 + i*1.4, 1 + j*1.5), 0.08,
                                    facecolor=PALETTE["soft"], alpha=0.4, zorder=2))
        # Single bright subject in center
        ax.add_patch(Circle((6, 4), 0.5, facecolor=PALETTE["rule3"],
                            edgecolor=PALETTE["rule3"], zorder=5))
        # Highlight ring
        ax.add_patch(Circle((6, 4), 0.8, facecolor="none",
                            edgecolor=PALETTE["rule3"], linewidth=2, linestyle="--", zorder=4))
        ax.text(6, 3, "ÚNICO PUNTO DE INTERÉS", ha="center", fontsize=9, fontweight="bold",
                color=PALETTE["rule3"], zorder=6,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=PALETTE["rule3"]))

    elif rule_key == "minimalismo":
        # Empty frame with single small subject
        ax.add_patch(Circle((7, 4), 0.25, facecolor=PALETTE["subject"],
                            edgecolor=PALETTE["subject"], zorder=4))
        ax.text(7, 3.4, "sujeto mínimo", ha="center", fontsize=7, color=PALETTE["subject"],
                fontweight="bold", style="italic")
        # Annotation
        ax.text(2, 6, "Vacío\nintencional", fontsize=8, color=PALETTE["muted"],
                style="italic", ha="center", va="center", alpha=0.6)
        ax.text(2, 2, "Aire", fontsize=8, color=PALETTE["muted"], style="italic",
                ha="center", va="center", alpha=0.6)
        ax.text(10, 6, "Sólo\nlo esencial", fontsize=8, color=PALETTE["muted"],
                style="italic", ha="center", va="center", alpha=0.6)

    elif rule_key == "capas":
        # Three horizontal layer lines
        layer_colors = [PALETTE["fov_line"], PALETTE["compose"], PALETTE["dof_line"]]
        layer_labels = ["FG (primer plano)", "MID (medio)", "BG (fondo)"]
        for i, (color, label) in enumerate(zip(layer_colors, layer_labels)):
            y = 2 + i * 2
            ax.plot([1, 11], [y, y], color=color, linewidth=1.5, linestyle="--", alpha=0.6, zorder=2)
            ax.text(0.5, y, label, fontsize=7, color=color, fontweight="bold",
                    ha="right", va="center")
            # Element on each layer
            if i == 0:  # FG
                ax.add_patch(Rectangle((1.5, y - 0.3), 0.6, 0.6, facecolor=color, alpha=0.5, zorder=3))
            elif i == 1:  # MID — subject
                ax.add_patch(Circle((6, y), 0.4, facecolor=PALETTE["subject"],
                                    edgecolor=PALETTE["subject"], zorder=4))
                ax.text(6, y - 0.7, "SUJETO", ha="center", fontsize=8, fontweight="bold",
                        color=PALETTE["subject"], zorder=5)
            else:  # BG
                for j in range(3):
                    ax.add_patch(Circle((4 + j*1.5, y), 0.25, facecolor=color, alpha=0.5, zorder=3))

    # Save
    fig.savefig(output_path, dpi=110, facecolor=PALETTE["bg"],
                bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


def main():
    rules = [
        ("tercios", "Regla de Tercios", "Divide el encuadre en 9 zonas; coloca al sujeto en un punto de poder (intersección)."),
        ("perspectiva", "Perspectiva", "Líneas convergentes hacia un punto de fuga; da profundidad real a la escena."),
        ("simetria", "Simetría", "Especular elementos alrededor de un eje central (vertical, horizontal o diagonal)."),
        ("enmarcado", "Enmarcado", "Usa elementos del entorno (arcos, ramas, ventanas) para enmarcar al sujeto."),
        ("espacio_neg", "Espacio Negativo", "Deja aire alrededor del sujeto; dirige la mirada hacia el sujeto aislado."),
        ("punto_interes", "Punto de Interés", "Un único foco visual claro; elimina elementos que compitan por atención."),
        ("minimalismo", "Minimalismo", "Resta elementos hasta lo esencial; el vacío es parte activa de la composición."),
        ("capas", "Capas", "Foreground + Midground + Background = profundidad real, no solo por perspectiva."),
    ]
    print("Generating 8 composition example diagrams...")
    for key, title, desc in rules:
        out = os.path.join(OUT_DIR, f"composition_{key}.png")
        render_composition_example(key, title, desc, out)
        print(f"  ✓ composition_{key}.png")
    print("\nAll composition examples generated.")


if __name__ == "__main__":
    main()
