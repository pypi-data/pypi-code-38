from psd2html import psd2html
import argparse
import os


def main():
    parser = argparse.ArgumentParser(description='Convert PSD file to HTML')

    parser.add_argument(
        'input', type=str, help='Input PSD file path or URL')
    parser.add_argument(
        'output', type=str, nargs='?', default='',
        help='Output file or directory. When directory is specified, filename'
             ' is automatically inferred from input')

    args = parser.parse_args()

    prefix, ext = os.path.splitext(args.output)
    if ext.lower() != '.html':
        if not prefix:
            prefix, ext = os.path.splitext(args.input)
        html_file = prefix + ".html"
        psd2html(args.input, html_file)
    else:
        psd2html(args.input, args.output)


if __name__ == '__main__':
    main()
