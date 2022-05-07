"""visualizer.py

The visualizer monitors a script file and creates the JSON file and renders the
dot graph whenever the script file changes.
- everytime the script file changes, a new `Script` object is created and the
  file is reanalyzed, so that large scripts may take longer to process
- everytime the script file is processed, there are three outputs, which is the
  JSON file, the dot file, and the PNG file (if GraphViz is installed)
"""


import os
import time

from scene import Scene


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
    """
    def __init__(self, dirpath, interval=5):
        self.dirpath = os.path.abspath(dirpath)
        self.interval = interval

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
                self._update_json()
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
            self.subvisualizers[dirpath] = Visualizer(filedir=dirpath)

        visualizer = self.subvisualizers[dirpath]

        updated = visualizer._update()

        if updated:
            visualizer._write_json()

        return updated

    def _write_json(self):
        """Updates the JSON data in the root directory.

        Each script in the root directory and subdirectories are used. The first
        two speakers are used as the keys. If the script is a monologue, then
        both keys will be the same speaker.
        """
        json_output = dict()
        for script in self.scripts.values():
            speakers = script.speakers
            speaker_0 = speakers[0]

            if len(script.speakers) > 1:
                speaker_1 = speakers[1]
            
            else:
                speaker_1 = speakers[0]

            json_output[speaker_0][speaker_1] = script.to_json()

        jsonfile = self.dirpath + ".json"

        with open(jsonfile, "w") as file:
            try:
                json.dump(json_output)
                print(f"Successfully updated JSON output: {jsonfile}")
            
            except Exception as error:
                print(f"Failed to update JSON output: {error}")
