"""main.py
Based on The Poor Man's Dialogue Tree.

This module is meant to translate a basic script to JSON and render a directed
graph using graphviz.
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
    args = parser.parse_args()

    visualizer = Visualizer(args.filepath)
    visualizer.run()


if __name__ == "__main__":
    main()
