import argparse


def main():
    parser = argparse.ArgumentParser(description='Short sample app')
    parser.add_argument('--in1', type=int)
    parser.add_argument('--in2', type=int)
    parser.add_argument('--no_mult', action="store_true", default=False)

    args = parser.parse_args()

    print(args)
    print('in 1  : {}'.format(args.in1))
    print('in 2  : {}'.format(args.in2))
    print('mult: {}'.format(args.no_mult))

    print('ADD=[{}]'.format(args.in1 + args.in2))
    if not args.no_mult:
        print('MULT=[{}]'.format(args.in1 * args.in2))


if __name__ == "__main__":
    main()