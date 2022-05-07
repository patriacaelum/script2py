"""nodes.py

The nodes each represent a block in the script. The currently supported nodes
are:

- the base `Node`, which all nodes inherit from
- the `Line` node, which stores a a line of dialogue from a speaker
- the `Choice` node, which gives the player a choice and creates a branching
  path
- the `Setter` node, which changes a system parameter

"""


import textwrap


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
    next_id: str
        the node id of the next node. The last node should be left as None.
    section: str
        the name of the group this node is in.
    next_section: str
        the name of the next section. If the next node is in the same section,
        this should be None.
    wrap: int
        the maximum number of characters per line of text. Default wrapping
        width is 80.
    """
    node_type = "node"
    
    def __init__(
        self, 
        next_id: str = None, 
        section: str = "", 
        next_section: str = None, 
        wrap: int = 80
    ):
        self.node_id = str(id(self))
        self.next_id = next_id

        self.section = section
        self.next_section = next_section

        self.wrap = wrap

    def to_dot(self):
        """Formats the node parameters for a dot graph.

        Returns
        ---------
        str
            the dot graph for this node.
        """
        return f"{self.node_id};"

    def to_json(self):
        """Formats the node paramters for a JSON file.

        Returns
        ---------
        str
            the JSON data for this node.
        """
        return {
            "node_id": self.node_id,
            "type": self.node_type,
            "next_id": self.next_id,
        }

    def _clean(self, text: str):
        """Cleans a block of text by removing the newlines and applying the
        correct wrapping.

        Parameters
        ------------
        text: str
            the block of text.

        Returns
        ---------
        str
            the cleaned line of text.
        """
        cleaned =  " ".join([line.strip() for line in text.strip().split("\n")])
        wrapped = "\n".join(textwrap.wrap(text=cleaned, width=self.wrap))

        return wrapped


class Line(Node):
    """Displays a line from the specified speaker.

    Script format:

    ```
    SpeakerName: Line of text.
    SpeakerName: Another line of text. This one extends to
        more than one line.
    ```

    JSON format:

    ```
    {
        "node_id": "0001",
        "type": "line",
        "speaker": "SpeakerName",
        "text": "Line of text.",
        "next_id": "0002"
    },
    {
        "node_id": "0002",
        "type": "line",
        "speaker": "SpeakerName",
        "text": "Another line of text. This one extends to more than one line.",
        "next_id": null
    }
    ```

    Parameters
    ------------
    speaker: str
        name of the character speaking.
    text: str
        the line of text the character is saying.
    kwargs:
        keyword arguments passed to the base class `Node`.
    """
    node_type = "line"

    def __init__(self, speaker: str = "", text: str = "", **kwargs):
        super().__init__(**kwargs)

        self.speaker = speaker
        self.text = self._clean(text)

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
    *** SpeakerName: First Choice
        --> Branch1
    *** SpeakerName: Second Choice
    ```

    JSON format:

    ```
    {
        "node_id": "0001",
        "type": "choice",
        "choices": [
            {
                "speaker": "SpeakerName",
                "choice": "First Choice",
                "next_id": "0002"
            },
            {
                "speaker": "SpeakerName",
                "choice": "Second Choice",
                "next_id": "0003"
            }
        ],
        "next_id": "0003"
    }
    ```

    If no branch is specified, the next node will be assumed to be the next
    node in the script.

    Parameters
    ------------
    choices: list(dict)
        each element is a dictionary with keys "speaker", "text", and
        (optionally) "next_id".
    kwargs:
        keyword arguments passed to the base class `Node`.
    """
    node_type = "choice"

    def __init__(self, choices: list = list(), **kwargs):
        super().__init__(**kwargs)

        self.choices = choices

        for choice in self.choices:
            choice["speaker"] = choice.get("speaker", "")
            choice["text"] = self._clean(choice.get("text", ""))
            choice["next_id"] = choice.get("next_id")

    def to_dot(self):
        choice_text = "\\n".join([
            f"{n}. {choice}" for n, choice in enumerate(self.choices)
        ])

        return f"{self.node_id} [label=\"Choice\\n{choice_text}\", shape=box];"

    def to_json(self):
        json_node = super().to_json()
        json_node.update({"choices": [choice for choice in self.choices]})

        return json_node


class Setter(Node):
    """Sets a variable to a value.

    Script format:

    ```
    <<{ variable_name = "variable value" }>>
    <<{ variable_name = 10 }>>
    ```

    JSON format
    ```
    {
        "node_id": "0001",
        "type": "setter",
        "setter": {
            "variable_name": "variable value"
        },
        "next_id": "0002"
    },
    {
        "node_id": "0002",
        "type": "setter",
        "setter": {
            "variable_name": 10
        },
        "next_id": null
    }
    ```

    Parameters
    ------------
    key: str
        the variable name.
    value: str or int or bool
        the value of the variable name.
    kwargs:
        keyword arguments passed to the base class `Node`.
    """
    node_type = "setter"

    def __init__(self, key: str = "", value: str | int | bool = "", **kwargs):
        super().__init__(**kwargs)

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
