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
    def __init__(self, filedir, interval=0, render=True):
        self.filedir = os.path.abspath(filedir)
        self.interval = interval
        self.render = render

        self.filepaths = dict()

    def run(self):
        """Runs the visualizer.

        The visualizer runs on an infinite loop and continually checks if the
        script file has been updated by comparing the time the file was last
        modified.
        """
        # Check if the file has been modified in timed intervals and render
        while True:
            self._update_filedir(self.filedir)
            time.sleep(self.interval)

    def render(self, key):
        """Creates the file outputs.

        All three outputs are attempted to be created. This includes the JSON
        file, the dot file, and running GraphViz to create a PNG of the graph.
        """
        with open(self.filepaths.script, "r") as file:
            script = Script(file.read())

        with open(self.filepaths.json, "w") as file:
            try:
                json.dump(script.to_json(), file)
                print(f"Successfully updated JSON output to: {self.jsonfile}")
            except Exception as json_error:
                print(f"Warning: JSON output not updated due to error: {json_error}")

        with open(self.filpaths.dot, "w") as file:
            try:
                file.write(script.to_dot())
                print(f"Successfully update dot output to: {self.dotfile}")
            except Exception as dot_error:
                print(f"Warning: dot output not updated due to error: {dot_error}")

        if self.render:
            process = subprocess.run(
                ["dot", "-Tpng", self.filepaths.dot, "-o", self.filepaths.graph],
                check=True
            )

            if process.returncode == 1:
                print(f"Warning: graph output not updated due to error: {process.stderr}")
            else:
                print(f"Successfully updated GraphViz output to: {self.graphfile}")

        print("\nScript2JSON Visualizer running...press CTRL-C to stop")

    def _update_filedir(self, filedir):
        """Updates the dictionary of filepaths with the files in the directory.

        Parameters
        ------------
        filedir: (str) the absolute path to the directory.
        """
        with os.scandir(filedir) as entries:
            for entry in entries:
                key = entry.path
                
                if self.filepaths.get(key) is None:
                    self._add_filepath(entry)
                    self.render(key)
                elif entry.stat().st_mtime != self.filepaths[key].last_modified:
                    self.filepaths[key].last_modified = entry.stat.st_mtime
                    self.render(key)

    def _add_filepath(self, entry):
        """Adds an entry to the dictionary of filepaths.

        If the entry is a directory, then this will recursively call the
        `_update_filedir()` method.

        Parameters
        ------------
        entry: (os.DirEntry) the entry to be added. If the entry is a
               directory, then the `_update_filedir()` method will be
               recursively called.
        """
        key = entry.path
        
        if entry.isFile() and entry.name.lower().endswith(".s2j"):
            self.filepaths[key] = Filepath(
                script=key,
                json=key.replace(".s2j", ".json"),
                dot=key.replace(".s2j", ".dot"),
                graph=key.replace(".s2j", ".png"),
                last_modified=entry.stat().st_mtime
            )
        elif entry.isDir():
            self._update_filedir(key)

