"""
Testing of functionalities from class RawNLParser
"""


from gherkan.encoder.RawNLParser import RawNLParser


text_raw = "scenario given that robot r3 picks up box and robot r3 collects cubes. scenario when robot r3 picks up cube one, robot r3 puts " \
           "the cube on the shuttle XY on position two. scenario when robot r4 puts cubes on chassi, then cube five is picked up by robot r2"

raw_parser = RawNLParser()
raw_parser.parse(text_raw)

## Generation of list of robot actions. Make_new = True - overwrites the current RobotPrograms_en, False only updates it
raw_parser.generate_program_dict(make_new=False)

