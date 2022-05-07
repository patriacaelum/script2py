import os
import pytest

from script2py.nodes import Line, Choice, Setter
from script2py.script import Script
from test.fixtures import TEST_DIR


@pytest.fixture 
def static_filepath():
    return os.path.join(TEST_DIR, "scripts/static.s2py")


@pytest.fixture 
def branching_filepath():
    return os.path.join(TEST_DIR, "scripts/branching.s2py")


@pytest.fixture 
def static_script(static_filepath):
    with open(static_filepath, "r") as file:
        script = file.readlines()

    return script


@pytest.fixture 
def branching_script(branching_filepath):
    with open(branching_filepath, "r") as file:
        script = file.readlines()

    return script


@pytest.fixture 
def goto_next_section():
    return "goto_next_section"


@pytest.fixture 
def line_speaker():
    return "speaker"


@pytest.fixture 
def single_line_text():
    return "single line text"


@pytest.fixture 
def multi_line_text():
    return "multi\n    line\n    text"


@pytest.fixture 
def setter_key():
    return "key"


@pytest.fixture 
def setter_value():
    return "value"


@pytest.fixture 
def choice_block(line_speaker, single_line_text, multi_line_text, goto_next_section):
    indented_text = multi_line_text.replace("\n", "\n    ")
    return [
        f"*** {line_speaker}: {single_line_text}",
        f"    --> {goto_next_section}",
        f"*** {line_speaker}: {indented_text}",
    ]


@pytest.fixture
def goto_block(goto_next_section):
    return [f"--> {goto_next_section}"]


@pytest.fixture 
def line_block(line_speaker, multi_line_text):
    return f"{line_speaker}: {multi_line_text}".split("\n")


@pytest.fixture 
def setter_block(setter_key, setter_value):
    return [f"<<{{ {setter_key} = {setter_value} }}>>"]


@pytest.fixture 
def script(static_filepath):
    return Script(static_filepath)


class TestScriptParsers:
    def test_parse_static_sections(self, static_script):
        parsed = Script.parse_sections(static_script)

        titles = [
            static_script[3], 
            static_script[37],
        ]
        sections = [
            static_script[5:34],
            static_script[39:72],
        ]

        for title, section, (parsed_title, parsed_section) in zip(titles, sections, parsed.items()):
            assert title == parsed_title
            assert section == parsed_section

    def test_parse_branching_sections(self, branching_script):
        parsed = Script.parse_sections(branching_script)

        titles = [
            branching_script[3],
            branching_script[31],
            branching_script[65],
        ]
        sections = [
            branching_script[5:28],
            branching_script[33:62],
            branching_script[67:100],
        ]

        for title, section, (parsed_title, parsed_section) in zip(titles, sections, parsed.items()):
            assert title == parsed_title
            assert section == parsed_section

    def test_parse_static_blocks(self, static_script):
        sections = [
            static_script[5:34],
            static_script[39:72],
        ]
        blocks = [
            [
                static_script[8:9],
                static_script[10:11],
                static_script[12:15],
                static_script[16:17],
                static_script[18:20],
                static_script[21:22],
                static_script[23:24],
                static_script[25:26],
                static_script[27:29],
                static_script[30:31],
                static_script[32:33],
            ],
            [
                static_script[43:44],
                static_script[45:46],
                static_script[47:48],
                static_script[49:50],
                static_script[51:52],
                static_script[53:54],
                static_script[55:56],
                static_script[57:58],
                static_script[59:60],
                static_script[61:62],
                static_script[63:65],
                static_script[66:67],
                static_script[68:69],
                static_script[70:71],
            ],
        ]

        for section, block in zip(sections, blocks):
            parsed = Script.parse_blocks(section)

            assert parsed == block

    def test_parse_branching_blocks(self, branching_script):
        sections = [
            branching_script[5:28],
            branching_script[33:62],
            branching_script[67:100],
        ]
        blocks = [
            [
                branching_script[8:9],
                branching_script[10:12] + branching_script[13:15],
                branching_script[16:17],
                branching_script[18:20] + branching_script[21:23] + branching_script[24:25],
                branching_script[26:27],
            ],
            [
                branching_script[36:37],
                branching_script[38:39],
                branching_script[40:43],
                branching_script[44:45],
                branching_script[46:48],
                branching_script[49:50],
                branching_script[51:52],
                branching_script[53:54],
                branching_script[55:57],
                branching_script[58:59],
                branching_script[60:61],
            ],
            [
                branching_script[71:72],
                branching_script[73:74],
                branching_script[75:76],
                branching_script[77:78],
                branching_script[79:80],
                branching_script[81:82],
                branching_script[83:84],
                branching_script[85:86],
                branching_script[87:88],
                branching_script[89:90],
                branching_script[91:93],
                branching_script[94:95],
                branching_script[96:97],
                branching_script[98:99],
            ],
        ]

        for section, block in zip(sections, blocks):
            parsed = Script.parse_blocks(section)

            assert parsed == block


class TestScriptClassifiers:
    def test_classify_choice_block(self, script, choice_block, line_speaker, single_line_text, multi_line_text, goto_next_section):
        script.sections[goto_next_section] = goto_next_section
        node, next_section = script.classify_block(choice_block)

        assert isinstance(node, Choice)
        assert next_section is None

        single_line_choice = {
            "speaker": line_speaker,
            "text": single_line_text,
            "next_id": goto_next_section,
        }
        multi_line_choice = {
            "speaker": line_speaker,
            "text": multi_line_text.replace("\n    ", " "),
            "next_id": None,
        }

        assert single_line_choice in node.choices
        assert multi_line_choice in node.choices

    def test_classify_goto_block(self, script, goto_block, goto_next_section):
        node, next_section = script.classify_block(goto_block)

        assert node is None
        assert next_section == goto_next_section

    def test_classify_line_block(self, script, line_block, line_speaker, multi_line_text):
        node, next_section = script.classify_block(line_block)

        assert isinstance(node, Line)
        assert next_section is None

        assert node.speaker == line_speaker
        assert node.text == " ".join([line.strip() for line in multi_line_text.split("\n")])

    def test_classify_setter_block(self, script, setter_block, setter_key, setter_value):
        node, next_section = script.classify_block(setter_block)

        assert isinstance(node, Setter)
        assert next_section is None

        assert node.key == setter_key
        assert node.value == setter_value
