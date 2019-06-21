"""Check the syntax and execute Pikachu commands.

Methods:
run -- The main context for the pikachu vm.
"""

from pykachu.utils import pika_error, pika_print
from pykachu.reader import PikaReader
from pykachu.stack import PikaStack


def run(file_name, args, debug):
    """
    Run a specified Pikachu file in a virtual environment.

    Arguments:
    file_name -- the name and path of a file containing a pikachu program.
    args -- the command line arguments specified when the pikachu interpreter was
    run.
    """
    pi_stack = PikaStack()
    pika_stack = PikaStack()

    stacks_dict = {
        "pi pikachu": pi_stack,
        "pika pikachu": pika_stack
    }

    for a in args:
        pi_stack.PUSH(a)

    reader = PikaReader(file_name)
    while True:
        try:
            if debug:
                try:
                    print "\nline {}: {}\npi    {}\npika  {}".format(reader.line_num, reader.lines[reader.line_num],
                                                                     pi_stack.elements, pika_stack.elements)
                except KeyError:
                    pass
            command = next(reader)
        except StopIteration:
            print ''
            break
        command = command.split(' chu')[0]
        terms = command.split()
        if len(terms) == 0:
            continue
        if len(terms) == 1:
            pika_error(reader.line_num, 'unknown command "{}"'.format(terms[0]))
        elif len(terms) < 3:
            command = " ".join(terms)
            if command == "pi pikachu":
                pi_stack.POP()
            elif command == "pika pikachu":
                pika_stack.POP()
            elif command == "pi pika":
                if not pi_stack.EMPTY():
                    pika_stack.PUSH(pi_stack.PEEK())
            elif command == "pika pi":
                if not pika_stack.EMPTY():
                    pi_stack.PUSH(pika_stack.PEEK())
            elif command == "pi pi":
                if not pika_stack.EMPTY():
                    pika_stack.RAND()
            elif command == "pikachu pikachu":
                try:
                    line_num = len(next(reader).split())
                except StopIteration:
                    pika_error(reader.line_num - 1, "unexpected EoF, expected new line")
                if pi_stack.PEEK() != pika_stack.PEEK():
                    continue
                reader.goto(line_num)
            elif command == "pika pika":
                try:
                    line_num = len(next(reader).split())
                except StopIteration:
                    pika_error(reader.line_num - 1, "unexpected EoF, expected new line")
                if pi_stack.PEEK() == pika_stack.PEEK():
                    continue
                reader.goto(line_num)
            else:
                pika_error(reader.line_num, 'unknown command "{}"'.format(reader.lines[reader.line_num]))
        elif len(terms) < 4:
            try:
                current_stack = stacks_dict[" ".join(terms[-2:])]
            except KeyError:
                pika_error(reader.line_num, 'unknown pikachu "{}"'.format(" ".join(terms[-2:])))
            command = terms[0]
            if command == "pikachu":
                current_stack.DIV()
                if current_stack.PEEK() == float('NaN'):
                    pika_error(reader.line_num, 'cannot divide by 0')
            else:
                current_stack.PUSH(1)
        elif len(terms) < 5:
            try:
                current_stack = stacks_dict[" ".join(terms[-2:])]
            except KeyError:
                pika_error(reader.line_num, 'unknown pikachu "{}"'.format(" ".join(terms[-2:])))
            command = " ".join(terms[:-2])
            if command == "pi pika":
                current_stack.ADD()
            elif command == "pika pi":
                current_stack.SUB()
            elif command == "pi pikachu":
                current_stack.MULT()
            elif command == "pika pikachu":
                if not current_stack.EMPTY():
                    pika_print(current_stack.POP())
                else:
                    pika_print("undefined")
            elif command == "pikachu pikachu":
                n = current_stack.POP()
                if n and type(n) == int:
                    pika_print(chr(n))
                else:
                    pika_print("undefined")
            else:
                current_stack.PUSH(2)
        else:
            try:
                current_stack = stacks_dict[" ".join(terms[-2:])]
            except KeyError:
                pika_error(reader.line_num, 'unknown pikachu "{}"'.format(" ".join(terms[-2:])))
            current_stack.PUSH(len(terms) - 2)
