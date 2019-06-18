import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', metavar='N',
                        dest='input', type=float, required=True, nargs='+',
                        help='Values to perform min on')
    args = parser.parse_args()

    print('Minimum = {}'.format(min(args.input)))


if __name__ == '__main__':
    main()
