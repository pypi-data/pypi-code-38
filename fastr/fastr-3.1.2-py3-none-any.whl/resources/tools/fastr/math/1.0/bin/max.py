import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', metavar='N',
                        dest='input', type=float, required=True, nargs='+',
                        help='Values to perform max on')
    args = parser.parse_args()

    print('Maximum = {}'.format(max(args.input)))


if __name__ == '__main__':
    main()
