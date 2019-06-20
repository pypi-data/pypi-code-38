from gherkan.decoder.SignalParser import SignalParser

if __name__ == "__main__":
    # Parse statement into the SignalStatementTree
    sp = SignalParser()
    signalTree = sp.parseStatement("(robotN1ProgramNumber == 1 && edge(robotN3ProgramStart, 1)) && (robotN1ProgramNumber == 1 && edge(robotN3ProgramStart, 1))")
    print(signalTree)

