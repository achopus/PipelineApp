import numpy as np
from pandas import DataFrame
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import LineCollection


def colored_line_between_pts(x, y, c, ax, **lc_kwargs):
    # Default the capstyle to butt so that the line segments smoothly line up
    default_kwargs = {"capstyle": "butt"}
    default_kwargs.update(lc_kwargs)

    # Compute the midpoints of the line segments. Include the first and last points
    # twice so we don't need any special syntax later to handle them.
    x = np.asarray(x)
    y = np.asarray(y)
    x_midpts = np.hstack((x[0], 0.5 * (x[1:] + x[:-1]), x[-1]))
    y_midpts = np.hstack((y[0], 0.5 * (y[1:] + y[:-1]), y[-1]))

    # Determine the start, middle, and end coordinate pair of each line segment.
    # Use the reshape to add an extra dimension so each pair of points is in its
    # own list. Then concatenate them to create:
    # [
    #   [(x1_start, y1_start), (x1_mid, y1_mid), (x1_end, y1_end)],
    #   [(x2_start, y2_start), (x2_mid, y2_mid), (x2_end, y2_end)],
    #   ...
    # ]
    coord_start = np.column_stack((x_midpts[:-1], y_midpts[:-1]))[:, np.newaxis, :]
    coord_mid = np.column_stack((x, y))[:, np.newaxis, :]
    coord_end = np.column_stack((x_midpts[1:], y_midpts[1:]))[:, np.newaxis, :]
    segments = np.concatenate((coord_start, coord_mid, coord_end), axis=1)

    lc = LineCollection(segments, **default_kwargs) # type: ignore
    lc.set_array(c)  # set the colors of each segment

    return ax.add_collection(lc)

def plot_trajectory_figure(df: DataFrame, save_path: str, arena_side_cm: float = 80,
                           start_time: float = 0, end_time: float = np.inf) -> None:
    df = df[(df['timestamps'] >= start_time) & (df['timestamps'] <= end_time)]
    X, Y, T = df['x'].values, df['y'].values, df['timestamps'].values

    # Setup
    fig, ax = plt.subplots()
    plt.rcParams.update({'font.weight': 'normal', 'font.size': 14})
    fig.set_size_inches((7.95, 7.3))
    b = 8

    # Arena creation
    rectangle_outer = patches.Rectangle((-b, -b), arena_side_cm + 2 * b, arena_side_cm + 2 * b, linewidth=1, edgecolor='black', facecolor='gray')
    ax.add_patch(rectangle_outer)
    rectangle_inner = patches.Rectangle((0, 0), arena_side_cm, arena_side_cm, linewidth=1, edgecolor='black', facecolor='gainsboro')
    ax.add_patch(rectangle_inner)
    plt.scatter([arena_side_cm / 2], [arena_side_cm / 2], marker='o', c='gray')
    plt.plot([0, -b], [0, -b], c='black', linewidth=1)
    plt.plot([arena_side_cm, arena_side_cm + b], [arena_side_cm, arena_side_cm + b], c='black', linewidth=1)
    plt.plot([arena_side_cm, arena_side_cm + b], [0, -b], linewidth=1, color='black')
    plt.plot([0, -b], [arena_side_cm, arena_side_cm + b], linewidth=1, color='black')
    
    # Trajectory
    line = colored_line_between_pts(X, Y, T / 60, ax, linewidth=1.5, cmap='plasma', antialiased=True) # type: ignore
    
    # Writing
    fig.colorbar(line, ax=ax, label="Time [min]", fraction=0.04)
    plt.xticks(ticks=[0, arena_side_cm / 2, arena_side_cm], labels=[f"{-arena_side_cm / 2:.0f} cm", f"{0} cm", f"{arena_side_cm / 2:.0f} cm"])
    plt.yticks(ticks=[0, arena_side_cm / 2, arena_side_cm], labels=[f"{-arena_side_cm / 2:.0f} cm", f"{0} cm", f"{arena_side_cm / 2:.0f} cm"])
    ax.tick_params(axis='both', which='both', length=6, width=2)

    # Geometry
    plt.axis('equal')
    #plt.xlim(-b-0.1, arena_side_cm+b+0.1)
    #plt.ylim(-b-0.1, arena_side_cm+b+0.1)
    for spine in ax.spines.values():
        spine.set_linewidth(3)  # Set the thickness of the border

    plt.savefig(save_path, dpi=600)
    plt.close(fig)
