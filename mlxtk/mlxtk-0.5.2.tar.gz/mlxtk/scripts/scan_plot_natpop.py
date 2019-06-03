#!/usr/bin/env python
import argparse
from functools import partial
from pathlib import Path
from typing import Callable

from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .. import inout, log, plot, units
from ..parameter_selection import load_scan
from ..parameters import Parameters

LOGGER = log.get_logger(__name__)
plot.make_headless()


def plot_natpop(index: int,
                path: Path,
                parameters: Parameters,
                file_path: Path,
                dof: int = 1,
                node: int = 1,
                extension: str = ".pdf",
                modfunc: Callable[[Figure, Axes, Parameters], None] = None):
    total_path = path / file_path
    try:
        fig, ax = plot.create_subplots(1, 1)
        plot.plot_natpop(ax,
                         *inout.read_natpop(total_path, dof=dof, node=node))
        ax.set_xlabel(units.get_time_label())
        ax.set_ylabel(r"$\lambda_i(t)$")
        if modfunc:
            modfunc(fig, ax, parameters)
        plot.save(fig, str(index) + extension)
        plot.close_figure(fig)
    except FileNotFoundError:
        LOGGER.warning("file does not exist: %s", total_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "scan_dir",
        type=Path,
        help="directory of the scan containing the file scan.pickle")
    parser.add_argument("-f",
                        "--file",
                        type=Path,
                        default=Path("propagate") / "natpop",
                        help="relative path within each simulation")
    parser.add_argument("-d",
                        "--dof",
                        type=int,
                        default=1,
                        help="degree of freedom")
    parser.add_argument("-n", "--node", type=int, default=1, help="node")
    parser.add_argument("-e",
                        "--extension",
                        type=str,
                        default=".pdf",
                        help="file extensions for the plots")
    parser.add_argument("-o",
                        "--output",
                        type=str,
                        help="name of the output directory")
    plot.add_argparse_2d_args(parser)
    args = parser.parse_args()

    if not args.output:
        args.output = "natpop_{}_{}".format(args.dof, args.node)

    def apply_args(fig: Figure, ax: Axes, parameters: Parameters):
        del fig
        del parameters
        plot.apply_2d_args(ax, args)

    load_scan(args.scan_dir).plot_foreach(
        args.output,
        partial(plot_natpop,
                file_path=args.file,
                modfunc=apply_args,
                dof=args.dof,
                node=args.node,
                extension=args.extension))


if __name__ == "__main__":
    main()
