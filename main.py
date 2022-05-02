"""main.py

Based on The Poor Man's Dialogue Tree.

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
        "--filedir",
        "-f",
        type=str,
        required=True,
        help="path to the directory of script files",
        dest="filedir"
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
        "--render",
        action="store_true",
        required=False,
        help="enables rendering dot files",
        dest="render"
    )
    parser.add_argument(
        "--no-render",
        action="store_false",
        required=False,
        help="disables rendering dot files",
        dest="render"
    )
    parser.add_argument(
        "--text-length",
        "-t",
        type=int,
        required=False,
        help="the maximum length of a line of text",
        dest="textlength_max"
    )
    parser.set_defaults(
        interval=0,
        render=True,
        textlength_max=80
    )
    args = parser.parse_args()

    visualizer = Visualizer(
        filedir=args.filedir,
        interval=args.interval,
        render=args.render,
        textlength_max=args.textlength_max
    )
    visualizer.run()


if __name__ == "__main__":
    main()

