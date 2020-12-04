import unittest

from script_parser import ScriptParser


class TestScriptParser(unittest.TestCase):
    def setUp(self):
        with open("sample.scrpy", "r") as file:
            self.parser = ScriptParser(file.read())

    def test_parse(self):
        print(self.parser.sections)
        for node in self.parser.parse():
            print(node.to_script())

        for node in self.parser.parse():
            print(node.to_json())


if __name__ == "__main__":
    unittest.main()
