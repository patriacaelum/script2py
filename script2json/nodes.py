"""nodes.py

The nodes each represent a block in the script.
"""
class Node:
    """The base class."""

    node_type = None
    next_section = None

    def __init__(self, section):
        self.node_id = id(self)
        self.section = section

    def to_dot(self):
        return f"{self.node_id};"

    def to_json(self):
        return {
            "id": self.node_id,
            "type": self.node_type
        }


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
        self.text = text

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

        self.choices = choices

    def to_dot(self):
        choice_text = "\\n".join([
            f"{n}. {choice}" for n, choice in enumerate(self.choices.keys())
        ])

        return f"{self.node_id} [label=\"Choice\\n{choice_text}\", shape=box];"

    def to_json(self):
        json_node = super().to_json()
        json_node.update({"choices": self.choices})

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

