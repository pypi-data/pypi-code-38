from .parser import Parser
from .handle_invalid_scenarios import ParserError


def ganit():
    p = Parser()
    print("Type quit to exit")
    while True:
        print()
        exp = input("Ganit>>> ")
        if exp == 'quit':
            break
        try:
            print("Prescanned Expression:", p.prescan(exp))
            print("Postfix Notation:", p.convert(exp))
            print("Evaluation Result:", p.evaluate(exp))
        except ParserError as e:
            print("ParserError:",str(e))
