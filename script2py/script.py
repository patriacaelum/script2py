"""script.py

Each script represents a full conversation consisting of multiple nodes (see
`nodes.py`).

- Each script may use any number of nodes that are grouped into sections, which
  are determined by the branching paths in the script by using the `Choice` node
- The script is responsible for ordering and linking the nodes together
- The script also contains basic information about the conversation, such as a
  list of speakers

"""


import json
import os
import subprocess

from itertools import groupby

from script2py.nodes import Line, Choice, Setter


class Script:
    """Converts a script into nodes that are used to create a dot graph and JSON
    file.

    Parameters
    ------------
    filepath: str
        the path to the script file.
    last_modified: float
        Time of the most recent content modification (in seconds).
    wrap: int
        the maximum number of characters per line of text. Default wrapping
        width is 80.
    """

    def __init__(self, filepath: str, last_modified: float = 0, wrap: int = 80):
        self.filepath = filepath
        self.last_modified = last_modified
        self.wrap = wrap

        self.jsonfile = filepath.replace(".s2py", ".json")
        self.dotfile = filepath.replace(".s2py", ".dot")
        self.graphfile = filepath.replace(".s2py", ".png")

        self.nodes = list()
        self.speakers = set()
        self.sections = dict()

    def to_dot(self):
        """Creates the dot graph for the script.

        Returns
        ---------
        str
            the dot graph for this script.
        """
        # Define all nodes with their sections as subgraphs
        subgraphs = list()

        for s, (section, group) in enumerate(
            groupby(self.nodes, key=lambda x: x.section)
        ):
            subgraphs.append(
                "\n".join(
                    [
                        f"subgraph cluster_{s}" + " {",
                        f'label=<<b>{section}</b>> fontsize="24pt";',
                        "\n".join([node.to_dot() for node in group]),
                        "}",
                    ]
                )
            )

        dot_subgraphs = "\n".join(subgraphs)

        # Define node edges with labelled choices
        dot_edges = list()

        for node in self.nodes:
            if isinstance(node, Choice):
                for n, choice in enumerate(node.choices):
                    next_id = choice.get("next_id", node.next_id)

                    if next_id is not None:
                        dot_edges.append(f"{node.node_id} -> {next_id} [label = {n}];")

            else:
                if node.next_id is not None:
                    dot_edges.append(f"{node.node_id} -> {node.next_id};")

        # Define directional graph
        dot_output = "\n".join(
            ["digraph G {", dot_subgraphs, "\n".join(dot_edges), "}"]
        )

        return dot_output

    def to_json(self):
        """Creates the JSON data for the script.

        Returns
        ---------
        list
            a list of nodes in JSON format.
        """
        nodes = list()
        first_node = None

        for node in self.nodes:
            nodes.append(node.to_json())

        if len(nodes) > 0:
            first_node = self.nodes[0].node_id

        json_output = {
            "speakers": list(self.speakers),
            "first_node": first_node,
            "nodes": nodes,
        }

        return json_output

    def update(self):
        """Loads the script file from disk and writes the updated output to
        json and dot files.

        Returns
        ---------
        bool
            `True` if the script was updated, `False` otherwise.
        """
        updated = False
        last_modified = os.stat(self.filepath).st_mtime

        if self.last_modified != last_modified:
            self._clear()

            with open(self.filepath, "r", encoding="utf-8") as file:
                script = file.readlines()

            self.nodes = self._parse(script)
            self._write_json()
            self._write_dot()
            self._write_graphviz()

            self.last_modified = last_modified
            updated = True

        return updated

    def _classify_block(self, block: list):
        """Classifies a block of text as one of the nodes.

        Parameters
        ------------
        text: list(str)
            the block of text to classify.

        Returns
        ---------
        Node
            The `Node` class that fits the block of text.
        """
        node = None
        next_section = None

        prefix = block[0][:3]

        if prefix == "***":
            node = self._classify_choice_block(block)

        elif prefix == "-->":
            # Goto block
            next_section = block[0][3:].strip()

        elif prefix == "<<{":
            node = self._classify_setter_block(block)

        else:
            node = self._classify_line_block(block)

        return node, next_section

    def _classify_choice_block(self, block: list):
        """Creates a ``Choice`` node from a block of text.

        Parameters
        ------------
        block: list(str)
            the block of text making up a choice block.

        Returns
        ---------
        Choice
            a ``Choice`` node.
        """
        choices = list()

        for line in block:
            line = line.strip()
            prefix = line[:3]

            if prefix == "***":
                try:
                    speaker, text = line[3:].split(":", maxsplit=1)

                except ValueError as error:
                    block = " ".join(block).replace("\n", " ")

                    raise SyntaxError(
                        f"Choice block is missing colon (:) in: '{block}'"
                    ) from error

                choices.append(
                    {
                        "speaker": speaker.strip(),
                        "text": text.strip(),
                    }
                )
                self.speakers.add(choices[-1]["speaker"])

            elif prefix == "-->":
                # Optional goto block
                goto_section = line[3:].strip()

                try:
                    choices[-1]["next_id"] = self.sections[goto_section]

                except KeyError as error:
                    block = " ".join(block).replace("\n", " ")

                    raise SyntaxError(
                        f"Choice block goto {goto_section} does not exist in: '{block}'"
                    ) from error

            else:
                # Multi-line choice
                choices[-1]["text"] += " " + line

        node = Choice(
            choices=choices,
            wrap=self.wrap,
        )

        return node

    def _classify_line_block(self, block: list):
        """Creates a ``Line`` node from a block of text.

        Parameters
        ------------
        block: list(str)
            the block of text making up a line block.

        Returns
        ---------
        Line
            a ``Line`` node.
        """
        block = "\n".join(block)

        try:
            speaker, text = block.split(":", maxsplit=1)
            self.speakers.add(speaker)

        except ValueError as error:
            block = block.replace("\n", " ")

            raise SyntaxError(
                f"Line block is missing colon (:) in: '{block}'"
            ) from error

        node = Line(speaker=speaker.strip(), text=text.strip(), wrap=self.wrap)

        return node

    def _classify_setter_block(self, block: list):
        """Creates a ``Setter`` node from a block of text.

        Parameters
        ------------
        block: list(str)
            the block of text making up a setter block. The block should only be
            one line long.

        Returns
        ---------
        Setter
            a ``Setter`` node.
        """
        line = block[0].strip()

        if line[-3:] != "}>>":
            raise SyntaxError(f"Setter block missing closing brackets in: '{line}'")

        try:
            key, value = line[3:-3].split("=")

        except ValueError as error:
            raise SyntaxError(
                f"Setter block missing assignment (=) in: '{line}'"
            ) from error

        try:
            value = int(value)

        except ValueError:
            if value.lower() == "true":
                value = True

            elif value.lower() == "false":
                value = False

        node = Setter(
            key=key.strip(),
            value=value.strip(),
            wrap=self.wrap,
        )

        return node

    def _clear(self):
        """Clears the parsed data."""
        self.nodes = list()
        self.speakers = set()
        self.sections = dict()

    def _parse(self, script: list):
        """Parses the contents of a script2py file (*.s2py) into nodes.

        Parameters
        ------------
        script: list(str)
            a list of lines of text.

        Returns
        ---------
        list(Node)
            a list of `Node` objects that work like a linked list.
        """
        nodes = list()
        next_section_id = None
        sections = self._parse_sections(script)

        for title, section in reversed(sections.items()):
            title = title.strip()
            blocks = self._parse_blocks(section)

            for block in reversed(blocks):
                node, next_section = self._classify_block(block)

                if node is not None:
                    if next_section_id is not None:
                        node.next_id = next_section_id

                    elif len(nodes) > 0:
                        node.next_id = nodes[-1].node_id

                    node.section = title
                    nodes.append(node)

                # The next section id should be `None` unless the block is a
                # goto block
                next_section_id = self.sections.get(next_section)

            if len(nodes) > 0:
                # The node id of each section is the first node in that section
                self.sections[title] = nodes[-1].node_id

        return list(reversed(nodes))

    @staticmethod
    def _parse_blocks(section: list):
        """Parses a section of text into blocks.

        The parsing algorithm is bottom up and determines where a block begins
        by looking for if a line starts with whitespace or a `#`, which denotes
        a comment.

        Parameters
        ------------
        section: list(str)
            a section of text. The section should already be separated from its
            delimiters using the `parse_sections()` method.

        Returns
        ---------
        list(str)
            a list of blocks of text.
        """
        blocks = list()
        block = list()

        for line in reversed(section):
            if len(line.strip()) == 0 or line[0] == "#":
                # Ignore blanklines and comments
                continue

            if line[0].isspace():
                # Blocks with multiple lines should be indented
                block.append(line)

                continue

            block.append(line)
            block = list(reversed(block))

            # Join consecutive choice blocks
            if block[0][:3] == "***" and len(blocks) > 0 and blocks[-1][0][:3] == "***":
                blocks[-1] = block + blocks[-1]

            else:
                blocks.append(block)

            block = list()

        return list(reversed(blocks))

    @staticmethod
    def _parse_sections(script: list):
        """Parses the contents of a scrip2py file (*.s2py) into sections.

        Parameters
        ------------
        script: list(str)
            a list of lines of text.

        Returns
        ---------
        dict(list(str))
            a dictionary with section titles as keys and the blocks of text that
            are under that section.
        """
        sections = dict()
        section_title = None
        section_start = None

        for line_num, line in enumerate(script):
            if line[:3] == "---":
                section_title = script[line_num - 1]
                section_start = line_num + 1

            elif line[:3] == "===":
                sections[section_title] = script[section_start:line_num]

                section_title = None
                section_start = None

        return sections

    def _write_dot(self):
        """Writes the script as a dot file."""
        with open(self.dotfile, "w", encoding="utf-8") as file:
            try:
                file.write(self.to_dot())
                print(f"Successfully updated dot output: {self.dotfile}")

            except Exception as error:
                print(f"Warning: failed to updated dot output: {error}")

    def _write_graphviz(self):
        """Writes the script as a graph using GraphViz."""
        process = subprocess.run(
            [
                "dot",
                "-Tpng",
                self.dotfile,
                "-o",
                self.graphfile,
            ],
            check=True,
        )

        if process.returncode == 0:
            print(f"Successfully updated graph output: {self.graphfile}")

        else:
            print(f"Warning: failed to updated graph output: {process.stderr}")

    def _write_json(self):
        """Writes the script as a JSON file."""
        with open(self.jsonfile, "w", encoding="utf-8") as file:
            try:
                json.dump(self.to_json(), file)
                print(f"Successfully updated JSON output: {self.jsonfile}")

            except Exception as error:
                print(f"Warning: failed to updated JSON output: {error}")
