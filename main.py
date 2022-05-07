"""main.py

Based on The Poor Man's Dialogue Tree, Inky, and Yarn Spinner.

This module is meant to translate a basic script to JSON and render a directed
graph using GraphViz.
"""


from argparse import ArgumentParser

from visualizer import Visualizer


def main():
    parser = ArgumentParser(
        description="Translate a basic script to JSON and render a directed"
            "graph using Graphviz"
    )

    parser.add_argument(
        "--pathdir",
        "-p",
        type=str,
        required=True,
        help="path to the directory of script files",
        dest="pathdir"
    )

    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        required=False,
        help="number of seconds between checking if the files have been updated",
        dest="interval"
    )

    parser.add_argument(
        "--wrap",
        "-w",
        type=int,
        required=False,
        help="the maximum length of a line of text",
        dest="wrap"
    )

    parser.set_defaults(
        interval=5,
        textlength_max=80
    )

    args = parser.parse_args()

    visualizer = Visualizer(
        pathdir=args.pathdir,
        interval=args.interval,
        wrap=args.wrap,
    )

    visualizer.run()


if __name__ == "__main__":
    main()
