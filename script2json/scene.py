import json
import os

from collections import namedtuple

from script import Script


Filepath = namedtuple(
    "Filepath",
    ["script", "json", "dot", "graph", "last_modified"]
)


class Scene:
    """A scene contains multiple scripts and subscenes.

    Each `.s2j` file in the directory is parsed as a script and is stored in
    JSON with the first two speakers as the keys. If there is only one speaker,
    then both speakers will be the same.

    Each directory in the directory will be parsed as a subscene.

    Parameters
    ------------
    filedir: (str) the directory where the scene files are stored.
    render:  (bool) renders the dot files using GraphViz if set to `True`.
    """
    filedir = None
    filepaths = dict()
    json_output = dict()
    render = True
    subscenes = dict()
    
    def __init__(self, filedir, render=True):
        self.filedir = os.path.abspath(filedir)
        self.render = render

    def add_filepath(self, entry):
        """Adds an entry to the dictionary of filepaths.

        Parameters
        ------------
        entry: (os.DirEntry) the entry to be added.
        """
        key = entry.path

        self.filepaths[key] = Filepath(
            script=key,
            json=key.replace(".s2j", ".json"),
            dot=key.replace(".s2j", ".dot"),
            graph=key.replace(".s2j", ".png"),
            last_modified=entry.stat().st_mtime
        )

    def write_master(self):
        """Writes the master JSON output for this directory.

        Since this method writes the JSON output for all the files in the
        directory and for all subdirectories, it should be called only once by
        the `Visualizer`.
        """
        with open(self.filedir + ".json", "w") as file:
            json.dump(self.json_output)
    
    def update(self):
        """Updates the dictionary of filepaths with the files in the directory
        and subscenes.

        Returns
        ---------
        (bool) `True` if one of the scripts was updated.
        """
        updated = False
        
        with os.scandir(self.filedir) as entries:
            for entry in entries:
                key = entry.path
                file_exists = self.filepaths.get(key) is not None
                subscene_exists = self.subscenes.get(key) is not NOne

                if file_exists and entry.stat().st_mtime != self.filepaths[key].last_modified:
                    self.filepaths[key].last_modified = entry.stat().st_mtime
                    self.write(self.filepaths[key])

                    updated = True
                elif not file_exists:
                    if entry.is_file() and entry.name.lower().endswith(".s2j"):
                        self.add_filepath(entry)
                        self.write(self.filepaths[key])

                        updated = True
                    elif not subscene_exists and entry.is_dir():
                        self.subscens[key] = Scene(key, self.render)

        for dirpath, subscene in self.subscenes.items():
            scene_updated = subscene.update()

            if scene_updated:
                self.json_output[dirpath] = subscene.to_json()

                upated = True

        return updated

    def write(self, filepath):
        """Writes the local file outputs.

        All three ouptuts are created. This includes the JSON file, the dot
        file, and running GraphViz to create the PNG of the graph. However,
        this excludes the master JSON, which is created by the `Visualizer`.

        Parameters
        ------------
        filepath: (namedtuple) the filepath that contains the output locations.
        """
        # Create the most recent version of the script
        with open(filepath.script, "r") as file:
            script = Script(file.read())

        # Create master JSON with the first two speakers as the first two keys
        speaker0 = script.speakers[0]
        if len(script.speakers) > 1:
            speaker1 = script.speakers[1]
        else:
            speaker1 = script.speakers[0]

        self.json_output[speaker0][speaker1] = script.to_json()

        # Write local output files
        with open(filepath.json, "w") as file:
            try:
                json.dump(script.to_json(), file)
                print(f"Successfully updated JSON output to: {filepath.json}")
            except Exception as json_error:
                print(f"Warning: JSON output not updated due to error: {json_error}")

        with open(filepath.dot, "w") as file:
            try:
                file.write(script.to_dot())
                print(f"Successfully update dot output to: {filepath.dot}")
            except Exception as dot_error:
                print(f"Warning: dot output not updated due to error: {dot_error}")

        if self.render:
            process = subprocess.run(
                [
                    "dot",
                    "-Tpng",
                    filepath.dot,
                    "-o",
                    filepath.graph
                ],
                check=True
            )

            if process.returncode == 1:
                print(f"Warning: graph output not updated due to error: {process.stderr}")
            else:
                print(f"Successfully updated GraphViz output to: {filepath.graph}")

