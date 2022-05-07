"""visualizer.py

The visualizer monitors a script file and creates the JSON file and renders the
dot graph whenever the script file changes.

- Every time the script file changes, the `Script` object is updated and the
  file is reanalyzed, so large scripts may take longer to process.
- Every time the script file is processed, there are three outputs: the JSON
  file, the dot file, and the PNG file (if GraphViz is installed)
"""


import os
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
    filepath: str
        the filepath where the script files (*.s2py) are.
    interval: int
        the number of seconds between checking if the files in the `filepath`
        has been updated. Default value is `5` seconds.
    wrap: int
        the maximum number of characters per line of text. Default wrapping
        width is 80.
    """
    def __init__(self, dirpath, interval: int = 5, wrap: int = 80):
        self.dirpath = os.path.abspath(dirpath)
        self.interval = interval
        self.wrap = wrap

        self.scripts = dict()
        self.subvisualizers = dict()

    def run(self):
        """Runs the visualizer.

        The visualizer runs on an infinite loop and continually checks if the
        script file has been updated by comparing the time the file was last
        modified.
        """
        while True:
            updated = self._update()

            if updated:
                print("\nscript2json visualizer running...press CTRL-C to stop\n")
                
            time.sleep(self.interval)

    def _update(self):
        """Updates the scripts from the root directory and its subdirectories.

        This method is also called to update the visualizers in the
        subdirectories.

        Returns
        ---------
        bool
            `True` if one of the scripts was updated, `False` otherwise.
        """
        updated = False

        with os.scandir(self.dirpath) as entries:
            for entry in entries:
                entry_updated = False

                if entry.is_file() and entry.name.endswith(".s2py"):
                    entry_updated = self._update_script(entry)
                
                elif entry.is_dir():
                    entry_updated = self._update_subvisualizer(entry)

                if entry_updated:
                    updated = True

        return updated

    def _update_script(self, entry):
        """Updates a script in the root directory.

        A script is created if one doesn't exist.

        Parameters
        ------------
        entry: os.DirEntry
            the script file (*.s2py) to be updated.

        Returns
        ---------
        bool
            `True` if the script was updated, `False` otherwise.
        """
        updated = False
        filepath = entry.path
        last_modified = entry.stat().st_mtime

        if filepath not in self.scripts.keys():
            self.scripts[filepath] = Script(
                filepath=filepath,
                last_modified=last_modified,
                wrap=self.wrap,
            )

        script = self.scripts[filepath]

        if last_modified != script.last_modified:
            updated = script.update()

        return updated

    def _update_subvisualizer(self, entry):
        """Updates a visualizer for a subdirectory.

        A visualizer is created if one doesn't exist.

        Parameters
        ------------
        entry: os.DirEntry
            the subdirectory to be updated.

        Returns
        ---------
        bool
            `True` if a script in the subdirectory was updated, `False`
            otherwise.
        """
        dirpath = entry.path

        if dirpath not in self.subvisulizers.keys():
            self.subvisualizers[dirpath] = Visualizer(
                pathdir=dirpath,
                wrap=self.wrap,
            )

        visualizer = self.subvisualizers[dirpath]

        updated = visualizer._update()

        if updated:
            visualizer._write_json()

        return updated
