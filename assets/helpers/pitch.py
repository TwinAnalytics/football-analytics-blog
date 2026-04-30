"""
Shared pitch drawing utilities used across all blog notebooks.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Arc


DATA_DIR = "/Users/stefanhofmann/Documents/Bewerbung/Interviews/Hudl/statsbomb_explorer/open-data/data"


def draw_pitch(ax, color="white", line_color="#333333", linewidth=1.5):
    """Draw a Statsbomb pitch (120x80) on the given axes."""
    ax.set_facecolor(color)
    lc, lw = line_color, linewidth
    ax.add_patch(plt.Rectangle((0, 0), 120, 80, fill=False, edgecolor=lc, linewidth=lw))
    ax.plot([60, 60], [0, 80], color=lc, linewidth=lw)
    ax.add_patch(plt.Circle((60, 40), 10, fill=False, edgecolor=lc, linewidth=lw))
    ax.plot(60, 40, "o", color=lc, markersize=2)
    # Penalty areas
    ax.add_patch(plt.Rectangle((0, 18), 18, 44, fill=False, edgecolor=lc, linewidth=lw))
    ax.add_patch(plt.Rectangle((102, 18), 18, 44, fill=False, edgecolor=lc, linewidth=lw))
    # 6-yard boxes
    ax.add_patch(plt.Rectangle((0, 30), 6, 20, fill=False, edgecolor=lc, linewidth=lw))
    ax.add_patch(plt.Rectangle((114, 30), 6, 20, fill=False, edgecolor=lc, linewidth=lw))
    # Goals
    ax.add_patch(plt.Rectangle((-2, 36), 2, 8, fill=False, edgecolor=lc, linewidth=lw, linestyle="--"))
    ax.add_patch(plt.Rectangle((120, 36), 2, 8, fill=False, edgecolor=lc, linewidth=lw, linestyle="--"))
    # Penalty spots
    ax.plot(12, 40, "o", color=lc, markersize=3)
    ax.plot(108, 40, "o", color=lc, markersize=3)
    # Penalty arcs
    ax.add_patch(Arc((12, 40), 20, 20, angle=0, theta1=307, theta2=233, color=lc, linewidth=lw))
    ax.add_patch(Arc((108, 40), 20, 20, angle=0, theta1=127, theta2=53, color=lc, linewidth=lw))
    ax.set_xlim(-3, 123)
    ax.set_ylim(-3, 83)
    ax.set_aspect("equal")
    ax.axis("off")
    return ax
