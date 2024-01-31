### SPDX-License-Identifier: GPL-2.0-or-later

"""Heatmap data parsed from log messages from a single source."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class Heatmap():
    """
    Heatmap to visualize data values as a 2D grid of colored squares.
    Input parameters:
    x_ticks - x axis ticks
    y_ticks - y axis ticks
    title - heatmap title
    unallowed_cells - a list of cells to be colored in red representing a bad relationship
                      between the two axis variables.
                      row/column format: ([0,1], [1,1])
    colorbar_label - colorbar label
    xlabel - x axis label
    ylabel - y axis label
    """
    def __init__(self, x_ticks, y_ticks, title, unallowed_cells,
                 colorbar_label, xlabel, ylabel):
        self._x_ticks = x_ticks
        self._y_ticks = y_ticks
        self._title = title
        self._unallowed_cells = unallowed_cells
        self._colorbar_label = colorbar_label
        self._xlabel = xlabel
        self._ylabel = ylabel

    def plot(self, data, filename):
        np_data = np.array(data)
        fig, ax = plt.subplots()
        im = ax.imshow(np_data, cmap="cividis")

        # Add a colorbar for reference
        cbar = plt.colorbar(im)
        cbar.set_label(self._colorbar_label)

        # Show all ticks and label them with the respective list entries
        ax.set_xticks(np.arange(len(self._x_ticks)), labels=self._x_ticks)
        ax.set_yticks(np.arange(len(self._y_ticks)), labels=self._y_ticks)

        # Rotate the tick labels and set their alignment.
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                 rotation_mode="anchor")
        plt.xlabel(self._xlabel)
        plt.ylabel(self._ylabel)

        # Loop over data dimensions and create text annotations.
        for i in range(len(self._x_ticks)):
            for j in range(len(self._y_ticks)):
                ax.text(j, i, np_data[i, j],
                        ha="center", va="center", color="white")

        for row, col in self._unallowed_cells:
            if np_data[row][col] >= 1:
                rect = patches.Rectangle((col - 0.5, row - 0.5), 1, 1, linewidth=1, edgecolor='none', facecolor='red')
                ax.add_patch(rect)
        ax.set_title(self._title)
        fig.tight_layout()
        plt.savefig(filename)
