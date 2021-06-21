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

from script import Script


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
    """
    def __init__(self, filepath):
        self.filepath = os.path.abspath(filepath)

        self.jsonfile = self.filepath.replace(".s2j", ".json")
        self.dotfile = self.filepath.replace(".s2j", ".dot")
        self.graphfile = self.filepath.replace(".s2j", ".png")

    def run(self):
        """Runs the visualizer.

        The visualizer runs on an infinite loop and continually checks if the
        script file has been updated by comparing the time the file was last
        modified.
        """
        # Initial render
        last_modified = os.stat(self.filepath).st_mtime
        self.render_graph()

        # Check if the file has been modified in timed intervals and render
        while True:
            check_last_modified = os.stat(self.filepath).st_mtime

            if check_last_modified != last_modified:
                last_modified = check_last_modified
                self.render_graph()

    def render_graph(self):
        """Creates the file outputs.

        All three outputs are attempted to be created. This includes the JSON
        file, the dot file, and running GraphViz to create a PNG of the graph.
        """
        with open(self.filepath, "r") as file:
            script = Script(file.read())

        with open(self.jsonfile, "w") as file:
            try:
                json.dump(script.to_json(), file)
                print(f"Successfully updated JSON output to: {self.jsonfile}")
            except Exception as json_error:
                print(f"Warning: JSON output not updated due to error: {json_error}")

        with open(self.dotfile, "w") as file:
            try:
                file.write(script.to_dot())
                print(f"Successfully update dot output to: {self.dotfile}")
            except Exception as dot_error:
                print(f"Warning: dot output not updated due to error: {dot_error}")
            
        process = subprocess.run(
            ["dot", "-Tpng", self.dotfile, "-o", self.graphfile],
            check=True
        )

        if process.returncode == 1:
            print(f"Warning: graph output not updated due to error: {process.stderr}")
        else:
            print(f"Successfully updated GraphViz output to: {self.graphfile}")

        print("\nScript2JSON Visualizer running...press CTRL-C to stop")

