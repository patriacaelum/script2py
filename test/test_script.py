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
def static_lines(static_filepath):
    with open(static_filepath, "r") as file:
        script = file.readlines()

    return script


@pytest.fixture 
def branching_lines(branching_filepath):
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
def empty_script():
    return Script("")


@pytest.fixture 
def static_script(static_filepath):
    return Script(static_filepath)


@pytest.fixture
def branching_script(branching_filepath):
    return Script(branching_filepath)


class TestScriptParsers:
    def test_parse_static_sections(self, static_lines):
        parsed = Script._parse_sections(static_lines)

        titles = [
            static_lines[3], 
            static_lines[37],
        ]
        sections = [
            static_lines[5:34],
            static_lines[39:72],
        ]

        for title, section, (parsed_title, parsed_section) in zip(titles, sections, parsed.items()):
            assert title == parsed_title
            assert section == parsed_section

    def test_parse_branching_sections(self, branching_lines):
        parsed = Script._parse_sections(branching_lines)

        titles = [
            branching_lines[3],
            branching_lines[31],
            branching_lines[65],
        ]
        sections = [
            branching_lines[5:28],
            branching_lines[33:62],
            branching_lines[67:100],
        ]

        for title, section, (parsed_title, parsed_section) in zip(titles, sections, parsed.items()):
            assert title == parsed_title
            assert section == parsed_section

    def test_parse_static_blocks(self, static_lines):
        sections = [
            static_lines[5:34],
            static_lines[39:72],
        ]
        blocks = [
            [
                static_lines[8:9],
                static_lines[10:11],
                static_lines[12:15],
                static_lines[16:17],
                static_lines[18:20],
                static_lines[21:22],
                static_lines[23:24],
                static_lines[25:26],
                static_lines[27:29],
                static_lines[30:31],
                static_lines[32:33],
            ],
            [
                static_lines[43:44],
                static_lines[45:46],
                static_lines[47:48],
                static_lines[49:50],
                static_lines[51:52],
                static_lines[53:54],
                static_lines[55:56],
                static_lines[57:58],
                static_lines[59:60],
                static_lines[61:62],
                static_lines[63:65],
                static_lines[66:67],
                static_lines[68:69],
                static_lines[70:71],
            ],
        ]

        for section, block in zip(sections, blocks):
            parsed = Script._parse_blocks(section)

            assert parsed == block

    def test_parse_branching_blocks(self, branching_lines):
        sections = [
            branching_lines[5:28],
            branching_lines[33:62],
            branching_lines[67:100],
        ]
        blocks = [
            [
                branching_lines[8:9],
                branching_lines[10:12] + branching_lines[13:15],
                branching_lines[16:17],
                branching_lines[18:20] + branching_lines[21:23] + branching_lines[24:25],
                branching_lines[26:27],
            ],
            [
                branching_lines[36:37],
                branching_lines[38:39],
                branching_lines[40:43],
                branching_lines[44:45],
                branching_lines[46:48],
                branching_lines[49:50],
                branching_lines[51:52],
                branching_lines[53:54],
                branching_lines[55:57],
                branching_lines[58:59],
                branching_lines[60:61],
            ],
            [
                branching_lines[71:72],
                branching_lines[73:74],
                branching_lines[75:76],
                branching_lines[77:78],
                branching_lines[79:80],
                branching_lines[81:82],
                branching_lines[83:84],
                branching_lines[85:86],
                branching_lines[87:88],
                branching_lines[89:90],
                branching_lines[91:93],
                branching_lines[94:95],
                branching_lines[96:97],
                branching_lines[98:99],
            ],
        ]

        for section, block in zip(sections, blocks):
            parsed = Script._parse_blocks(section)

            assert parsed == block

    def test_parse_static(self, empty_script, static_lines):
        nodes = empty_script._parse(static_lines)

        for node in nodes[:-1]:
            assert isinstance(node.node_type, str)
            assert isinstance(node.node_id, str)
            assert isinstance(node.next_id, str)
            assert isinstance(node.section, str)

        last_node = nodes[-1]

        assert isinstance(last_node.node_type, str)
        assert isinstance(last_node.node_id, str)
        assert last_node.next_id is None
        assert isinstance(last_node.section, str)
        assert last_node.next_section is None

    def test_parse_branching(self, empty_script, branching_lines):
        nodes = empty_script._parse(branching_lines)

        for node in nodes[:-1]:
            assert isinstance(node.node_type, str)
            assert isinstance(node.node_id, str)
            assert isinstance(node.next_id, str)
            assert isinstance(node.section, str)

        last_node = nodes[-1]

        assert isinstance(last_node.node_type, str)
        assert isinstance(last_node.node_id, str)
        assert last_node.next_id is None
        assert isinstance(last_node.section, str)
        assert last_node.next_section is None


class TestScriptClassifiers:
    def test_classify_choice_block(self, empty_script, choice_block, line_speaker, single_line_text, multi_line_text, goto_next_section):
        empty_script.sections[goto_next_section] = goto_next_section
        node, next_section = empty_script._classify_block(choice_block)

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
        assert line_speaker in empty_script.speakers

    def test_classify_goto_block(self, empty_script, goto_block, goto_next_section):
        node, next_section = empty_script._classify_block(goto_block)

        assert node is None
        assert next_section == goto_next_section

    def test_classify_line_block(self, empty_script, line_block, line_speaker, multi_line_text):
        node, next_section = empty_script._classify_block(line_block)

        assert isinstance(node, Line)
        assert next_section is None

        assert node.speaker == line_speaker
        assert node.text == " ".join([line.strip() for line in multi_line_text.split("\n")])
        assert line_speaker in empty_script.speakers

    def test_classify_setter_block(self, empty_script, setter_block, setter_key, setter_value):
        node, next_section = empty_script._classify_block(setter_block)

        assert isinstance(node, Setter)
        assert next_section is None

        assert node.key == setter_key
        assert node.value == setter_value


class TestScript:
    def test_update_static(self, static_script):
        static_script.update()
        nodes = static_script.nodes

        for node in nodes[:-1]:
            assert isinstance(node.node_type, str)
            assert isinstance(node.node_id, str)
            assert isinstance(node.next_id, str)
            assert isinstance(node.section, str)

        last_node = nodes[-1]

        assert isinstance(last_node.node_type, str)
        assert isinstance(last_node.node_id, str)
        assert last_node.next_id is None
        assert isinstance(last_node.section, str)
        assert last_node.next_section is None

        speakers = ["Addison", "Eve", "Brick", "Margaret"]

        for speaker in speakers:
            assert speaker in static_script.speakers

        sections = ["Exerpt from All About Eve", "Exerpt from Cat on a Hot Tin Roof"]

        for section in sections:
            assert section in static_script.sections.keys()

    def test_update_branching(self, branching_script):
        branching_script.update()
        nodes = branching_script.nodes

        for node in nodes[:-1]:
            assert isinstance(node.node_type, str)
            assert isinstance(node.node_id, str)
            assert isinstance(node.next_id, str)
            assert isinstance(node.section, str)

        last_node = nodes[-1]

        assert isinstance(last_node.node_type, str)
        assert isinstance(last_node.node_id, str)
        assert last_node.next_id is None
        assert isinstance(last_node.section, str)
        assert last_node.next_section is None

        speakers = ["Addison", "Eve", "Brick", "Margaret"]

        for speaker in speakers:
            assert speaker in branching_script.speakers

        sections = [
            "Making A Decision",
            "Exerpt from All About Eve", 
            "Exerpt from Cat on a Hot Tin Roof",
        ]

        for section in sections:
            assert section in branching_script.sections.keys()

    def test_static_to_dot(self, static_script):
        static_script.update()
        dot_output = static_script.to_dot()

        assert isinstance(dot_output, str)

    def test_branching_to_dot(self, branching_script):
        branching_script.update()
        dot_output = branching_script.to_dot()

        assert isinstance(dot_output, str)

    def test_static_to_json(self, static_script):
        static_script.update()
        json_output = static_script.to_json()

        for node in json_output[:-1]:
            node_type = node.get("type")

            assert isinstance(node_type, str)
            assert isinstance(node.get("node_id"), str)
            assert isinstance(node.get("next_id"), str)

            if node_type == "line":
                assert isinstance(node.get("speaker"), str)
                assert isinstance(node.get("text"), str)

            elif node_type == "choice":
                assert isinstance(node.get("choices"), list)

            elif node_type == "setter":
                value = node.get("value")

                assert isinstance(node.get("key"), str)
                assert isinstance(value, (str, int, bool))

    def test_branching_to_json(self, branching_script):
        branching_script.update()
        json_output = branching_script.to_json()

        for node in json_output[:-1]:
            node_type = node.get("type")

            assert isinstance(node_type, str)
            assert isinstance(node.get("node_id"), str)
            assert isinstance(node.get("next_id"), str)

            if node_type == "line":
                assert isinstance(node.get("speaker"), str)
                assert isinstance(node.get("text"), str)

            elif node_type == "choice":
                assert isinstance(node.get("choices"), list)

            elif node_type == "setter":
                value = node.get("value")

                assert isinstance(node.get("key"), str)
                assert isinstance(value, (str, int, bool))
