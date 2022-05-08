# script2py

[![Linting][pylintbadge]][pylintworkflow]
[![Documentation][documentationbadge]][documentationworkflow]
[![Tests][testsbadge]][testsworkflow]

Script2Py is a simple terminal-based program that converts a script format
(like for a theatre play or film screenplay) into JSON, dot, and PNG formats.
This is specially tailored as a tool for a personal project.

The syntax and structure are inspired by
[The Poor Man's Dialogue Tree][etodd], [Ink][inkle], and
[YarnSpinner][yarnspinnertool].

### Usage

```text
Usage: python main.py [-h] --dirpath DIRPATH [--interval INTERVAL] [--wrap WRAP]

Translate a basic script to JSON and render a directed graph using Graphviz

Optional arguments:

  -h, --help            show this help message and exit
  --dirpath DIRPATH, -d DIRPATH
                        path to the directory of script files
  --interval INTERVAL, -i INTERVAL
                        number of seconds between checking if the files have been updated
  --wrap WRAP, -w WRAP
                        the maximum length of a line of text
```

### Tutorial

The script format consists of four types of statements:

1. A `Line`, which consists of a speaker and dialogue. This takes the format

   ```text
   SpeakerName: This is the line of dialogue.
   ```

1. A `Choice`, which consists of a delimiter and the possible branching paths.
   This takes the format

   ```text
   *** SpeakerName: This is the first choice.
       --> Branch1
   *** SpeakerName: This is the second choice.
       --> Branch2
   ```

   The branches will denote where the script continues depending on which choice
   is selected.

1. A `Goto` statement, which consists of a delimiter and the name of the target
   branch. This may be useful for rejoining branches further down in the
   conversation or for splitting a linear conversation into smaller segments.
   This take the format

   ```text
   --> NextBranch
   ```

1. A `Setter`, which consists of a delimiter, followed by a variable name and
   its new assigned value.

   ```text
   <<{ variable_name = new_value }>>
   ```
   
We can combine these statements within different branches, which are not
indented. Each of the statements follow and are indented with two spaces. Each
branch may end with any statement, but only the `Choice` statement will lead
to another branch.

Let's take one of the simple examples, which you can find in
[samples/short_story/sample1.s2py](/sample/short_story/sample1.s2py).

```text
StartBranch
-------------
Me: Hello
You: Hey there, partner.

*** Me: How are you this fine morning?
    --> FriendlyBranch
*** Me: What do you want from me?
    --> AggressiveBranch
=============


FriendlyBranch
----------------
You: Why, I'm doing just fine.
Me: That's wonderful.

<<{ you.mood = calm }>>

--> EndBranch
================


AggressiveBranch
------------------
You: Hey, no need for hostility.
Me: Well, mind your own business then.

<<{ you.mood = annoyed }>>

--> EndBranch
==================


EndBranch
-----------
You: Goodbye. Have a good day.
===========
```

Here, there are three different branches. The first branch is the `Start`
branch. The statements follow are self explanatory until we get to the `Choice`
block, where there are two choices. Each of the branches are then located below
and they can be in any order.

In the terminal, we can then run the command

```bash
python main.py -d sample/short_story -i 5
```

This runs the main program with the files in the `sample/short_story`
directory and rechecks the files for modifications in that directory every five
seconds.

We can visually see the structure of the script through the GraphViz output.

![sample graph output](/sample/short_story/sample1.png)

This command will also create the JSON outputs, where each statement is treated
as a node in a graph and will contain the information about the statement as
well as the next node. There is also a master JSON outside of the specified
directory, which aggregates all the scripts in the directory.

[documentationbadge]: https://github.com/patriacaelum/script2py/actions/workflows/sphinx.yaml/badge.svg
[documentationworkflow]: https://github.com/patriacaelum/script2py/actions/workflows/sphinx.yaml
[etodd]: https://github.com/etodd/Lemma/tree/master/Dialogger
[inkle]: https://github.com/inkle/ink
[pylintbadge]: https://github.com/patriacaelum/script2py/actions/workflows/pylint.yaml/badge.svg
[pylintworkflow]: https://github.com/patriacaelum/script2py/actions/workflows/pylint.yaml
[testsbadge]: https://github.com/patriacaelum/script2py/actions/workflows/pytest.yaml/badge.svg
[testsworkflow]: https://github.com/patriacaelum/script2py/actions/workflows/pytest.yaml
[yarnspinnertool]: https://github.com/YarnSpinnerTool/YarnSpinner