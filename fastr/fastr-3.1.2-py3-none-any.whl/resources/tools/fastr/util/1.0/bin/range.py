import argparse


def main():
    parser = argparse.ArgumentParser(description='Short sample app that create a range (in the cardinality)')
    parser.add_argument('--input', type=int)

    args = parser.parse_args()

    print('arguments: {}'.format(args))
    print('input: {}'.format(args.input))

    print('RESULT_1={}'.format(list(range(args.input))))


if __name__ == "__main__":
    main()
