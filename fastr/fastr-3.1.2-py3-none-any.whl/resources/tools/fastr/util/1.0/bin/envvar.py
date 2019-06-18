import argparse
import os
import shutil


def main():
    parser = argparse.ArgumentParser(description='Copy file to output directory')
    parser.add_argument('--infile', type=str)
    parser.add_argument('--outdir', type=str)

    args = parser.parse_args()

    print(args)
    print('infile: {}'.format(args.infile))
    print('outdir: {}'.format(args.outdir))

    print('\n\nENVIRONMENT VARIABLES')
    print('=====================')
    for key, value in os.environ.items():
        print(f'{key}: {value}')

    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)

    shutil.copy2(args.infile, args.outdir)


if __name__ == "__main__":
    main()
