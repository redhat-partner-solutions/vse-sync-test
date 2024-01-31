### SPDX-License-Identifier: GPL-2.0-or-later

"""Plot data parsed from log messages from a single source."""

from argparse import ArgumentParser

import numpy as np
import matplotlib.pyplot as plt
from collections import namedtuple

from .common import open_input

from .parsers import PARSERS


Axis = namedtuple("Axis", ["desc", "attr", "scale", "scale_kwargs"], defaults=[None, None, None, None])
TIMESERIES = Axis("Time (s)", "timestamp")


class Plotter():
    """Rudimentary plotter of data values against timestamp"""
    def __init__(self, x, y):
        self._x = x
        self._y = y
        self._x_data = []
        self._y_data = []

    @staticmethod
    def _extract_attr(axis, data):
        return getattr(data, axis.attr)

    def _set_yscale(self, ax):
        if self._y.scale is not None:
            ax.set_yscale(self._y.scale, **(self._y.scale_kwargs or {}))
        elif any((abs(v) > 10 for v in self._y_data)):
            ax.set_yscale("symlog", linthresh=10)

    def append(self, data):
        """Append x and y data points extracted from `data`"""
        self._x_data.append(self._extract_attr(self._x, data))
        self._y_data.append(self._extract_attr(self._y, data))

    def _plot_scatter(self, ax):
        ax.axhline(0, color='black')
        self._set_yscale(ax)
        if self._x.scale is not None:
            ax.set_xscale(self._x.scale, **(self._x.scale_kwargs or {}))
        ax.plot(self._x_data, self._y_data, '.')
        ax.grid()
        ax.set_title(f'{self._x.desc} vs {self._y.desc}')

    def _plot_hist(self, ax):
        counts, bins = np.histogram(
            np.array(self._y_data, dtype=float),
            bins='scott'
        )
        ax.hist(bins[:-1], bins, weights=counts)
        self._set_yscale(ax)
        if self._x.scale is not None:
            ax.set_xscale(self._x.scale, **(self._x.scale_kwargs or {}))
        ax.set_title(f'Histogram of {self._y.desc}')

    def plot(self, filename):
        """Plot data to `filename`"""
        fig, (ax1, ax2) = plt.subplots(2, constrained_layout=True)
        fig.set_size_inches(10, 8)
        self._plot_scatter(ax1)
        self._plot_hist(ax2)
        ax3 = ax2.twinx()
        ax3.set_ylabel('CDF')
        ax3.ecdf(np.array(self._y_data, dtype=float), color="black", linewidth=2)
        plt.savefig(filename)
        return fig, (ax1, ax2, ax3)

    def plot_scatter(self, filename):
        fig, ax = plt.subplots(1, constrained_layout=True)
        fig.set_size_inches(10, 4)
        self._plot_scatter(ax)
        plt.savefig(filename)
        return fig, ax

    def plot_histogram(self, filename):
        fig, ax = plt.subplots(1, constrained_layout=True)
        fig.set_size_inches(10, 4)
        self._plot_hist(ax)
        plt.savefig(filename)
        return fig, ax


def main():
    """Plot data parsed from log messages from a single source.

    Plot data parsed from the log messages in input to an image file.
    """
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument(
        '-c', '--canonical', action='store_true',
        help="input contains canonical data",
    )
    aparser.add_argument(
        'input',
        help="input file, or '-' to read from stdin",
    )
    aparser.add_argument(
        'parser', choices=tuple(PARSERS),
        help="data to parse from input",
    )
    aparser.add_argument(
        'output',
        help="output image filename",
    )
    args = aparser.parse_args()
    parser = PARSERS[args.parser]()
    plotter = Plotter(TIMESERIES, Axis(parser.y_name, parser.y_name))
    with open_input(args.input) as fid:
        method = parser.canonical if args.canonical else parser.parse
        for parsed in method(fid):
            plotter.append(parsed)
    plotter.plot(args.output)


if __name__ == '__main__':
    main()
