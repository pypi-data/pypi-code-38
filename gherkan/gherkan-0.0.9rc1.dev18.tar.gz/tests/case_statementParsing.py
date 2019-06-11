from gherkan.decoder.SignalParser import SignalParser

sp = SignalParser()
st = sp.parseStatement("part2OnTable == 1 && (robotN1ProgramNumber == 0 || robotN1ProgramNumber == 1 || robotN1ProgramEnded) && edge(robotN3ProgramEnded, 1)")

print(st)