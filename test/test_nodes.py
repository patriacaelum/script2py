import pytest

import test.fixtures

from script2py.nodes import Node, Line, Choice, Setter


@pytest.fixture 
def section():
    return "All About Eve"


@pytest.fixture 
def speaker():
    return "Eve Harrington"


@pytest.fixture 
def short_line():
    return "I don't know that I'd take you anywhere."


@pytest.fixture 
def long_block():
    return """
So little? So little, did you say? Oh why, if there's nothing else, there's
applause; I've listened backstage to people applaud. It's like... like waves of
love coming over the footlights and wrapping you up. Imagine, to know every
night different hundreds of people love you; they smile, their eyes shine, you
please them, they want you, you belong. Just that alone is worth anything.
"""


@pytest.fixture 
def long_line():
    return "So little? So little, did you say? Oh why, if there's nothing " \
        "else, there's applause; I've listened backstage to people applaud. " \
        "It's like... like waves of love coming over the footlights and " \
        "wrapping you up. Imagine, to know every night different hundreds " \
        "of people love you; they smile, their eyes shine, you please them, " \
        "they want you, you belong. Just that alone is worth anything."


@pytest.fixture 
def choices(speaker, short_line, long_block):
    return [
        {
            "speaker": speaker,
            "text": short_line,
        },
        {
            "speaker": speaker,
            "text": long_block,
        }
    ]


@pytest.fixture 
def key():
    return "mood"


@pytest.fixture 
def value():
    return "tense"


@pytest.fixture 
def base_node(section):
    return Node(section=section)


@pytest.fixture
def short_line_node(speaker, short_line):
    return Line(speaker=speaker, text=short_line)


@pytest.fixture 
def long_line_node(speaker, long_line):
    return Line(speaker=speaker, text=long_line)


@pytest.fixture 
def choice_node(choices):
    return Choice(choices=choices)

@pytest.fixture 
def setter_node(key, value):
    return Setter(key=key, value=value)


class TestNode:
    def test_init(self, base_node, section):
        assert isinstance(base_node.node_id, str)
        assert base_node.next_id is None
        assert base_node.section == section
        assert base_node.next_section is None
        assert isinstance(base_node.wrap, int)

    def test_to_json(self, base_node):
        json_output = base_node.to_json()

        assert isinstance(json_output.get("node_id"), str)
        assert isinstance(json_output.get("type"), str)
        assert json_output.get("next_id") is None

    def test_clean_short_line(self, base_node, short_line):
        assert base_node._clean(short_line) == short_line

    def test_clean_long_line(self, base_node, long_block, long_line):
        cleaned = base_node._clean(long_block)

        for line in cleaned.split("\n"):
            assert len(line) < base_node.wrap


class TestLine:
    def test_init_short_line(self, short_line_node, speaker, short_line):
        assert short_line_node.node_type == "line"
        assert short_line_node.speaker == speaker
        assert short_line_node.text == short_line

    def test_init_long_line(self, long_line_node, speaker, long_line):
        assert long_line_node.node_type == "line"
        assert long_line_node.speaker == speaker
        
        for line in long_line_node.text.split("\n"):
            assert len(line) < long_line_node.wrap

    def test_short_line_to_json(self, short_line_node, speaker, short_line):
        json_output = short_line_node.to_json()

        assert json_output.get("speaker") == speaker
        assert len(json_output.get("text")) < short_line_node.wrap
        assert json_output.get("text") == short_line

    def test_long_line_to_json(self, long_line_node, speaker, long_line):
        json_output = long_line_node.to_json()

        assert json_output.get("speaker") == speaker
        
        for line in json_output.get("text").split("\n"):
            assert len(line) < long_line_node.wrap


class TestChoice:
    def test_init(self, choice_node, speaker, choices):
        for choice in choice_node.choices:
            assert choice.get("speaker") == speaker
            
            for line in choice.get("text"):
                assert len(line) < choice_node.wrap

    def test_to_json(self, choice_node, speaker, choices):
        json_output = choice_node.to_json()

        for choice in json_output.get("choices"):
            assert choice.get("speaker") == speaker

            for line in choice.get("text"):
                assert len(line) < choice_node.wrap

            assert choice.get("next_id") is None


class TestSetter:
    def test_init(self, setter_node, key, value):
        assert setter_node.key == key
        assert setter_node.value == value

    def test_to_json(self, setter_node, key, value):
        json_output = setter_node.to_json()

        assert json_output.get("key") == key
        assert json_output.get("value") == value
