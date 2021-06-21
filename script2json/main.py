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
        "--filepath",
        "-f",
        type=str,
        required=True,
        help="path to the script file to parse",
        dest="filepath"
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
        type=bool,
        required=False,
        help="enables rendering dot files",
        dest="render"
    )
    parser.add_argument(
        "--no-render",
        action="store_false",
        type=bool,
        required=False,
        help="disables rendering dot files",
        dest="render"
    )
    parser.set_defaults(
        interval=0,
        render=True
    )
    args = parser.parse_args()

    visualizer = Visualizer(
        filepath=args.filepath,
        interval=args.interval,
        render=args.render
    )
    visualizer.run()


if __name__ == "__main__":
    main()

