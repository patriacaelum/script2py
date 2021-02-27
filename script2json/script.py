from collections import defaultdict
from itertools import groupby

from nodes import Line, Choice, Setter


class Script:
    """TODO wrap text with a line limit as an argument"""
    def __init__(self, script=""):
        self.nodes = list()

        lines = script.split("\n")

        # Create an index of section names
        sections = list()

        for line in lines:
            # Sections are not indented, thus the first character is always
            # alphanumeric
            if line and line[0].isalpha():
                sections.append(line.strip(" :"))

        # Parse lines into nodes
        current_section = ""
        n = 0

        while n < len(lines):
            # Skip empty lines
            if not lines[n]:
                n += 1
                continue

            # Set the current section
            if lines[n].strip(" :") in sections:
                current_section = lines[n].strip(" :")
                n += 1
                continue

            first_word = lines[n].split()[0].strip(":")

            # Jump statements retroactively set the previous node to the
            # specified section
            if first_word == "JUMP":
                self.nodes[-1].next_section = " ".join(lines[n].split()[1:])

                n += 1
            # Setter nodes are a single line that begin with the keyword `SET` in
            # the format `SET variable_name: variable_value`
            elif first_word == "SET":
                key = lines[n].split("=")[0].split()[1]
                value = "=".join(lines[n].split("=")[1:]).strip()

                self.nodes.append(Setter(key, value, current_section))

                n += 1
            # Choice blocks span multiple lines and begin with the keyword
            # `CHOICE` with the choices in the format `SectionName: "Dialogue"`
            elif first_word == "CHOICE":
                self.nodes.append(Choice(dict(), current_section))

                n += 1
                first_word = lines[n].split()[0].strip(":")

                while first_word in sections:
                    key = ":".join(lines[n].split(":")[1:]).strip()
                    value = lines[n].split(":")[0].strip()

                    self.nodes[-1].choices[key] = value

                    n+= 1

                    if not lines[n]:
                        break

                    first_word = lines[n].split()[0].strip(":")
            # Line nodes are a single line in the format `Speaker: "Dialogue"`
            else:
                speaker = lines[n].split(":")[0].strip()
                text = ":".join(lines[n].split(":")[1:]).strip()

                self.nodes.append(Line(speaker, text, current_section))

                n += 1
        
    def to_dot(self):
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
        json_output = list()
        
        for n, node in enumerate(self.nodes):
            json_node = node.to_json()
            json_node.update({"next_id": self._next_node(n)})

            json_output.append(json_node)

        return json_output

    def _next_node(self, n):
        """Searches for the id of the next node.
        
        \param n (int) the index of the node in question.
        \return (list or None) the id of the next node.
        """
        next_id = list()

        # Last node does not have a next node
        if n + 1 == len(self.nodes):
            pass
        # Choice nodes have multiple possible next nodes
        elif self.nodes[n].node_type == "choice":
            for choice in self.nodes[n].choices.values():
                next_id.append(self._next_section_id(choice))
        # By default, assume the next node
        elif self.nodes[n].next_section is None:
            next_id.append(self.nodes[n + 1].node_id)
        # Search for the next node with the specified section
        else:
            next_id.append(self._next_section_id(self.nodes[n].next_section))

        if len(next_id) == 0:
            next_id = None
            
        return next_id

    def _next_section_id(self, section):
        for i in range(len(self.nodes)):
            if section == self.nodes[i].section:
                return self.nodes[i].node_id
        else:
            raise RuntimeError(f"No future node with section name '{section}' could be found")

