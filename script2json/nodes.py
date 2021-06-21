"""nodes.py

The nodes each represent a block in the script. The currently supported nodes
are:
- the base `Node`, which all nodes inherit from
- the `Line` node, which stores a a line of dialogue from a speaker
- the `Choice` node, which gives the player a choice and creates a branching
  path
- the `Setter` node, which changes a system parameter
"""


class Node:
    """The base node class.

    Each node has the following properties:
    - a `node_id`, which is created upon instantiation
    - a `section`, which groups nodes together
    - a `next_section`, which is only applicable for the last node in a section

    Each inherited class should:
    - set the `node_type`
    - format its displayed text using the `_format()` function
    - add to the `to_dot()` and `to_json()` functions with its additional
      parameters

    Parameters
    ------------
    section: (str) the name of the group this node is in.
    """
    node_type = None
    next_section = None
    textlength_max = 80

    def __init__(self, section):
        self.node_id = id(self)
        self.section = section

    def to_dot(self):
        """Formats the node parameters for a dot graph.

        Returns
        ---------
        (str) the dot graph for this node.
        """
        return f"{self.node_id};"

    def to_json(self):
        """Formats the node paramters for a JSON file.

        Returns
        ---------
        (str) the JSON data for this node.
        """
        return {
            "id": self.node_id,
            "type": self.node_type
        }

    def _format(self, text):
        """Formats text to have a a maximum of `textlength_max` characters.

        Parameters
        ------------
        text: (str) the text to be formatted.

        Returns
        ---------
        (str) the formatted text.
        """
        textlength = 0
        while len(text) - textlength > self.textlength_max:
            textlength += self.textlength_max
            
            for i in range(self.textlength_max):
                if text[textlength-i].isspace():
                    text = text[0:textlength-i] + "\n" + text[textlength-i+1:]
                    textlength += 1
                    break
            
        return text


class Line(Node):
    """Displays a line from the specified speaker.

    Script format:
    ```
    Name: Line of text.
    ```

    JSON format:
    ```
    {
        "id": "0001",
        "type": "line",
        "speaker": "Name",
        "text": "Line of text.",
        "next": "0002"
    }
    ```

    speaker: (str) name of the character speaking.
    text: (str) the line of text the character is saying.
    """

    node_type = "line"

    def __init__(self, speaker="", text="", *args):
        super().__init__(*args)

        self.speaker = speaker
        self.text = self._format(text)

    def to_dot(self):
        return f"{self.node_id} [label=\"{self.speaker}\\n{self.text}\", shape=box];"

    def to_json(self):
        json_node = super().to_json()
        json_node.update({
            "speaker": self.speaker,
            "text": self.text
        })

        return json_node


class Choice(Node):
    """Offers a choice to the player.

    Script format:
    ```
    CHOICE
        First Choice: 0001
        Second Choice: 0002
    ```

    JSON format:
    ```
    {
        "id": "0001",
        "type": "choice",
        "choices": {
            "First Choice": "0001",
            "Second Choice": "0002"
        }
    }
    ```

    choices: (list) each element is a single key-value dictionary mapping the
        choice text to the id of the next node.
    """

    node_type = "choice"

    def __init__(self, choices=dict(), *args):
        super().__init__(*args)

        self.choices = {key: self._format(value) for key, value in choices.items()}

    def to_dot(self):
        choice_text = "\\n".join([
            f"{n}. {choice}" for n, choice in enumerate(self.choices.keys())
        ])

        return f"{self.node_id} [label=\"Choice\\n{choice_text}\", shape=box];"

    def to_json(self):
        json_node = super().to_json()
        json_node.update({"choices": [choice for choice in self.choices.keys()]})

        return json_node


class Setter(Node):
    """Sets a variable to a value.

    Script format:
    ```
    VariableName: variable value
    ```

    JSON format
    ```
    {
        "id": "0001",
        "type": "setter",
        "properties": {
            "VariableName": "variable value"
        }
    }
    ```

    properties: (dict) key-value pairs of variables.
    """

    node_type = "setter"

    def __init__(self, key="", value="", *args):
        super().__init__(*args)

        self.key = key
        self.value = value

    def to_dot(self):
        return f"{self.node_id} [label=\"Set\\n{self.key} = {self.value}\", shape=box];"

    def to_json(self):
        json_node = super().to_json()
        json_node.update({
            "key": self.key,
            "value": self.value
        })

        return json_node

