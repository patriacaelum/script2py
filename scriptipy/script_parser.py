from nodes import Line, Choice, Setter


class ScriptParser:
    script = dict()
    sections = dict()

    def __init__(self, script=""):
        for index, line in enumerate(script.split("\n")):
            if line:
                self.script[index] = line.strip(" :")

                # Sections are not indented, so the first character is always
                # alphanumeric
                if line[0].isalpha():
                    self.sections[line.strip(" :")] = index

    def parse(self):
        """Parses the entire script."""
        nodes = list()

        for index in sorted(self.script.keys()):
            line = self.script[index]
            first_word = line.split()[0].strip(":")

            if line in self.sections.keys() or first_word == "JUMP":
                # Skip sections and jump statements
                continue
            elif first_word == "CHOICE":
                # Start of a choice block
                nodes.append(Choice())
            elif first_word in self.sections.keys():
                # A choice in a choice block
                key = line.split(":")[0]
                value = ":".join(line.split(":")[1:]).strip()

                nodes[-1].choices[key] = value
            elif first_word == "SET":
                key = line.split(":")[0].split()[1]
                value = ":".join(line.split(":")[1:]).strip()

                nodes.append(Setter(key, value))
            else:
                speaker = line.split(":")[0]
                text = ":".join(line.split(":")[1:]).strip()

                nodes.append(Line(speaker, text))

            if len(nodes) > 1 and not isinstance(nodes[-2], Choice):
                nodes[-2].next = nodes[-1].id

        return nodes
