import unittest

from script import Script


class TestScript(unittest.TestCase):
    def setUp(self):
        with open("sample.scrpy", "r") as file:
            self.script = Script(file.read())

    def test_to_dot(self):
        print(self.script.to_dot())

    def test_to_json(self):
        print(self.script.to_json())


if __name__ == "__main__":
    unittest.main()
