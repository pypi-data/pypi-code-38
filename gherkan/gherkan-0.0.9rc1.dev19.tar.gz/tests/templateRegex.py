import re


# === X<preposition>Y ===
def prepositionRE(preposition: str):
    """
    detects constructs in the form of "X<preposition>Y"
    In regex, (?P=<X>) denotes a capturing group with the name "X". I.e. it can be easily retrieved (see example below).
    """
    return re.compile(r"(?P<X>\w+)" + preposition + r"(?P<Y>\w+)", re.IGNORECASE)


# Create regex for <X>On<Y>
reXOnY = prepositionRE("on")  # generate regex to detect "On" cases. Use any other proposition to generate other regexes.
match = reXOnY.search("part2OnTable")  # parse the string using the regex
print(match.groups())  # print all captured groups
print("Found that {} is located on {}.".format(match.group("X"), match.group("Y")))  # Demonstration of the retrieval of the capturing groups by name


# === RobotXProgramNumber
robotXProgram = re.compile(r"robot(?P<robotName>\w+)programnumber", re.IGNORECASE)
match = robotXProgram.search("robotN3ProgramNumber")  # parse the string using the regex
print("Robot name was '{}'".format(match.group("robotName")))
