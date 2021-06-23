import json
import os
import subprocess

from collections import defaultdict, namedtuple

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
    def __init__(self, filedir, render=True, **kwargs):
        self.filedir = os.path.abspath(filedir)
        self.render = render
        self.kwargs = kwargs

        self.filepaths = dict()
        self.json_output = defaultdict(dict)
        self.subscenes = dict()

    def write_master(self):
        """Writes the master JSON output for this directory.

        Since this method writes the JSON output for all the files in the
        directory and for all subdirectories, it should be called only once by
        the `Visualizer`.
        """
        masterfile = self.filedir + ".json"
        with open(masterfile, "w") as file:
            json.dump(self.json_output, file)

        print(f"Successfully updated master JSON to: {masterfile}")
    
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
                entry_updated = self._update_entry(entry)

                if entry_updated:
                    updated = True

        for dirpath in self.subscenes.keys():
            scene_updated = self.subscenes[dirpath].update()

            if scene_updated:
                self.json_output[dirpath] = self.subscenes[dirpath].json_output

                updated = True

        return updated

    def _add_filepath(self, entry):
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

    def _update_entry(self, entry):
        """Updates a single file entry.

        A file entry is only considered updated if it falls under the one of the
        following conditions:

        - It is a file entry that is already being tracked and the time the file
          was last modified has changed
        - It is a file entry that is not being tracked and has a `.s2j`
          extension

        All other files are ignored and all directories are treated as
        subscenes.

        Parameters
        ------------
        entry: (os.DirEntry) the file entry to be updated.

        Returns
        ---------
        (bool) `True` if the file entry was updated.
        """
        updated = False

        key = entry.path
        file_exists = self.filepaths.get(key) is not None
        subscene_exists = self.subscenes.get(key) is not None

        if file_exists and entry.stat().st_mtime != self.filepaths[key].last_modified:
            self.filepaths[key].last_modified = entry.stat().st_mtime
            self._write(self.filepaths[key])

            updated = True
        elif not file_exists:
            if entry.is_file() and entry.name.lower().endswith(".s2j"):
                self._add_filepath(entry)
                self._write(self.filepaths[key])

                updated = True
            elif not subscene_exists and entry.is_dir():
                self.subscenes[key] = Scene(key, self.render, **self.kwargs)

        return updated

    def _update_master(self, script):
        """Updates the master JSON data.

        Each script is added with the first two speakers as the keys. If the
        script is a monologue and there is only one speaker, then both keys will
        be the same speaker.

        Parameters
        ------------
        script: (script2json.Script) the script to be updated in the master JSON
                output.
        """
        speaker0 = script.speakers[0]

        if len(script.speakers) > 1:
            speaker1 = script.speakers[1]
        else:
            speaker1 = script.speakers[0]

        self.json_output[speaker0][speaker1] = script.to_json()

    def _write(self, filepath):
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
            script = Script(file.read(), **self.kwargs)

        self._update_master(script)

        self._write_json(script.to_json(), filepath.json)
        self._write_dot(script.to_dot(), filepath.dot)

        if self.render:
            self._write_graph(filepath.dot, filepath.graph)

    def _write_dot(self, data, filepath):
        """Writes the local dot output.

        Parameters
        ------------
        data:     (str) the dot formatted data to write.
        filepath: (str) the location of the output file.
        """
        with open(filepath, "w") as file:
            try:
                file.write(data)
                print(f"Successfully update dot output to: {filepath}")
            except Exception as dot_error:
                print(f"Warning: dot output not updated due to error: {dot_error}")

    def _write_graph(self, dotfile, graphfile):
        """Writes the local graph output using GraphViz.

        Parameters
        ------------
        dotfile:   (str) the location of the dot input file.
        graphfile: (str) the location of the output file.
        """
        process = subprocess.run(
            [
                "dot",
                "-Tpng",
                dotfile,
                "-o",
                graphfile
            ],
            check=True
        )

        if process.returncode == 1:
            print(f"Warning: graph output not updated due to error: {process.stderr}")
        else:
            print(f"Successfully updated GraphViz output to: {graphfile}")

    def _write_json(self, data, filepath):
        """Writes the local JSON output.

        Parameters
        ------------
        data:     (dict) the JSON formatted data to write.
        filepath: (str) the location of the output file.
        """
        with open(filepath, "w") as file:
            try:
                json.dump(data, file)
                print(f"Successfully updated JSON output to: {filepath}")
            except Exception as json_error:
                print(f"Warning: JSON output not updated due to error: {json_error}")

