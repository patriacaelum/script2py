"""script.py

Each script represents a full conversation consisting of multiple nodes (see
`nodes.py`).

- Each script may use any number of nodes that are grouped into sections, which
  are determined by the branching paths in the script by using the `Choice` node
- The script is responsible for ordering and linking the nodes together
- The script also contains basic information about the conversation, such as a
  list of speakers

"""


from collections import defaultdict
from itertools import groupby

from script2py.nodes import Line, Choice, Setter


class Script:
    """Converts a script into nodes that are used to create a dot graph and JSON
    file.

    Parameters
    ------------
    script: (str) the script file (see `nodes.py` for formatting for each node).
    """
    def __init__(self, filepath: str):
        self.filepath = filepath

        self.nodes = list()
        self.speakers = list()
        self.sections = dict()

    def clear(self):
        """Clears the parsed data."""
        self.nodes = list()
        self.speakers = list()
        self.sections = dict()

    def update(self):
        self.clear()

        with open(self.filepath, "r") as file:
            script = file.readlines()

        self.nodes = self.parse(script)

    def parse(self, script: list):
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
        next_section_id = None
        sections = self.parse_sections(script)

        for title, section in reversed(sections.items()):
            blocks = self.parse_blocks(section)

            for block in reversed(blocks):
                node, next_section = self.classify_block(block)

                if node is not None:
                    if next_section_id is not None:
                        node.next_id = next_section_id

                    else:
                        node.next_id = nodes[-1].node_id

                    nodes.append(node)

                # The next section id should be `None` unless the block is a
                # goto block
                next_section_id = self.sections.get(next_section)

            # The node id of each section is the first node in that section
            self.sections[title] = nodes[-1].node_id

        return list(reversed(nodes))
        
    def to_dot(self):
        """Creates the dot graph for the script.

        Returns
        ---------
        (str) the dot graph for this script.
        """
        # Define all nodes with their sections as subgraphs
        dot_subgraphs = "\n".join([
            "\n".join([
                f"subgraph cluster_{s}" + "{",
                f"label = \"{section}\";",
                "\n".join([node.to_dot() for node in group]),
                "}"
            ])
            for s, (section, group) in enumerate(groupby(self.nodes, key=lambda x: x.section))
        ])

        # Relate node edges
        dot_edges = list()
        for n, node in enumerate(self.nodes):
            next_ids = self._next_node(n)

            if next_ids is not None:
                for n, next_id in enumerate(next_ids):
                    if node.node_type == "choice":
                        dot_edges.append(f"{node.node_id} -> {next_id} [label={n}];")
                    else:
                        dot_edges.append(f"{node.node_id} -> {next_id};")

        dot_output = "\n".join([
            "digraph G {",
            dot_subgraphs,
            "\n".join(dot_edges),
            "}"
        ])

        return dot_output
    
    def to_json(self):
        """Creates the JSON data for the script.

        Returns
        ---------
        (str) the JSON data for this script.
        """
        json_output = list()
        
        for n, node in enumerate(self.nodes):
            json_node = node.to_json()
            json_node.update({"next_id": self._next_node(n)})

            json_output.append(json_node)

        return json_output

    @staticmethod
    def parse_sections(script: list):
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
                sections[section_title] = script[section_start : line_num]

                section_title = None
                section_start = None

        return sections

    @staticmethod
    def parse_blocks(section: list):
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

            elif line[0].isspace():
                # Blocks with multiple lines should be indented
                block.append(line)

                continue

            else:
                block.append(line)
                block = list(reversed(block))

                # Join consecutive choice blocks
                if block[0][:3] == "***" and blocks[-1][0][:3] == "***":
                    blocks[-1] = block + blocks[-1]
                
                else:
                    blocks.append(block)

                block = list()

        return list(reversed(blocks))

    def classify_block(self, block: list):
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
            # Choice block
            choices = list()

            for line in block:
                line = line.strip()
                prefix = line[:3]

                if prefix == "***":
                    speaker, text = line[3:].split(":", maxsplit=1)
                    choices.append(
                        {
                            "speaker": speaker.strip(), 
                            "text": text.strip(),
                        }
                    )

                elif prefix == "-->":
                    # Optional goto block
                    goto_section = line[3:].strip()
                    choices[-1]["next_id"] = self.sections[goto_section]

                else:
                    # Multi-line choice
                    choices[-1]["text"] += " " + line

            node = Choice(choices=choices)

        elif prefix == "-->":
            # Goto block
            next_section = block[0][3:].strip()

        elif prefix == "<<{":
            # Setter block
            key, value = block[0][3:-3].split("=")

            node = Setter(key=key.strip(), value=value.strip())

        else:
            # Line block
            block = "\n".join(block)
            speaker, text = block.split(":", maxsplit=1)

            node = Line(speaker=speaker.strip(), text=text.strip())

        return node, next_section
