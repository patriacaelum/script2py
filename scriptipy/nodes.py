"""nodes.py

The nodes each represent a block in the script.
"""
class Node:
    """The base class."""

    type = None

    def __init__(self, next=None):
        self.id = id(self)
        self.next = next

    def to_json(self):
        return {
            "id": self.id,
            "type": self.type,
            "next": self.next
        }

    def to_script(self):
        return list()



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

    type = "line"

    def __init__(self, speaker, text, *args):
        super().__init__(*args)

        self.speaker = speaker
        self.text = text

    def to_json(self):
        return {
            **super().to_json(),
            "speaker": self.speaker,
            "text": self.text
        }

    def to_script(self):
        return [f"{self.speaker}: {self.text}"]


class Choice(Node):
    """Offers a choice to the player.

    Script format:
    ```
    CHOICE
        0001: First choice
        0002: Second choice
    ```

    JSON format:
    ```
    {
        "id": "0001",
        "type": "choice",
        "choices": {
            "0001": "First choice",CA

            "0002": "Second choice"
        }
    }
    ```

    choices: (list) each element is a single key-value dictionary mapping the
        choice text to the id of the next node.
    """

    type = "choice"

    def __init__(self, choices=dict(), *args):
        super().__init__(*args)

        self.choices = choices

    def to_json(self):
        return {
            **super().to_json(),
            "choices": self.choices
        }

    def to_script(self):
        return [
            "CHOICE",
            *[f"{key}: {value}" for key, value in self.choices.items()]
        ]


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

    type = "setter"

    def __init__(self, key, value, *args):
        super().__init__(*args)

        self.key = key
        self.value = value

    def to_json(self):
        return {
            **super().to_json(),
            "property": {
                f"{self.key}": f"{self.value}"
            }
        }

    def to_script(self):
        return [f"SET {self.key}: {self.value}"]
