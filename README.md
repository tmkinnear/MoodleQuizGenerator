# MoodleQuizGenerator
Generator for Moodle quizzes using randomised values.

The main.py script refers to a single example '.quest' format file. When run, it will turn the .quest file into a Moodle-compatible .xml question bank set.
generator.py contains all routines currently, and is incredibly messy. It was implemented quickly to get a solution up an running. That's my excuse and I'm sticking with it.

The .quest format file contains lines defining variables, calculation(s), question text and options. The hash character acts as a comment symbol, and the example file is currently commented such that the lines are explained.
