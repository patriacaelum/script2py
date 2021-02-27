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
    """
    def __init__(self, filepath):
        self.filepath = os.path.abspath(filepath)

        self.jsonfile = self.filepath.replace(".s2j", ".json")
        self.dotfile = self.filepath.replace(".s2j", ".dot")
        self.graphfile = self.filepath.replace(".s2j", ".png")

    def run(self):
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

