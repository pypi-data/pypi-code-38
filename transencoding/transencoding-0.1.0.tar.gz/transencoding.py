import os
import io
import click

VERSION = "0.1.0"
BUFFER_SIZE = 1024 * 1024

def do_trans(input_file, output_file, input_encoding, output_encoding):
    close_input_flag = False
    close_output_flag = False
    try:
        if input_file == "-":
            file_input_raw = os.sys.stdin.buffer
        else:
            file_input_raw = io.open(input_file, "rb")
            close_input_flag = True
        if output_file == "-":
            file_output_raw = os.sys.stdout.buffer
        else:
            file_output_raw = io.open(output_file, "wb")
            close_output_flag = True
        file_input = io.TextIOWrapper(file_input_raw, encoding=input_encoding, newline="")
        file_output = io.TextIOWrapper(file_output_raw, encoding=output_encoding, newline="")
        while True:
            buffer = file_input.read(BUFFER_SIZE)
            if not buffer:
                break
            file_output.write(buffer)
        file_output.flush()
    finally:
        if close_output_flag:
            file_output_raw.close()
        if close_input_flag:
            file_input_raw.close()

@click.command()
@click.option("-f", "--from-code", help="Encoding of original text", required=True)
@click.option("-t", "--to-code", help="encoding for output", required=True)
@click.option("-o", "--output", help="output file", default="-", required=False)
@click.argument("input", default="-", nargs=1, required=False)
def trans(from_code, to_code, output, input):
    """Convert encoding of given file from one encoding to another.
    """
    do_trans(input, output, from_code, to_code)


def main():
    trans()

if __name__ == "__main__":
    main()
