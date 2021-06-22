"""visualizer.py

The visualizer monitors a script file and creates the JSON file and renders the
dot graph whenever the script file changes.
- everytime the script file changes, a new `Script` object is created and the
  file is reanalyzed, so that large scripts may take longer to process
- everytime the script file is processed, there are three outputs, which is the
  JSON file, the dot file, and the PNG file (if GraphViz is installed)
"""


import json
import os
import subprocess
import time

from collections import namedtuple

from script import Script


Filepath = namedtuple(
    "Filepath",
    ["script", "json", "dot", "graph", "last_modified"]
)


class Visualizer:
    """Outputs a file for graphviz to turn into a directed graph.

    digraph G {
        subgraph S0 {
            label = "Branch Name";
            a0 -> a1 -> a2;
        }
        subgraph S1 {
            label = "Branch Name";
            b0 -> b1;
        }
        start -> a0;
        start -> a1;
        a2 -> end;
        b1 -> end;
    }

    Parameters
    ------------
    filepath: (str) the filepath where the script file is, with an `.s2j`
              extension.
    interval: (int) the number of seconds between checking if the files in the
              `filepath` has been updated.
    render:   (bool) renders the dot files using GraphViz if set to `True`.
    """
    interval = 0
    filedir = None
    scene = None

    def __init__(self, filedir, interval=0, **kwargs):
        self.filedir = os.path.abspath(filedir)
        self.interval = interval
        self.scene = Scene(filedir, **kwargs)

    def run(self):
        """Runs the visualizer.

        The visualizer runs on an infinite loop and continually checks if the
        script file has been updated by comparing the time the file was last
        modified.
        """
        while True:
            updated = self.scene.update()

            if updated:
                self.scene.write_master()
                
            time.sleep(self.interval)

