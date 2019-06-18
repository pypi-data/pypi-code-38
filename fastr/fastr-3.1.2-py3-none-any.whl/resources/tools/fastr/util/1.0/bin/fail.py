import argparse


def main():
    parser = argparse.ArgumentParser(description='Short sample app')
    parser.add_argument('--in_1', type=int)
    parser.add_argument('--in_2', type=int)
    parser.add_argument('--fail_1', action="store_true", default=False)
    parser.add_argument('--fail_2', action="store_true", default=False)

    args = parser.parse_args()

    print(args)
    print('in 1  : {}'.format(args.in_1))
    print('in 2  : {}'.format(args.in_2))
    print('fail_1: {}'.format(args.fail_1))
    print('fail_2: {}'.format(args.fail_2))

    if not args.fail_1:
        print('RESULT_1=[{}]'.format(args.in_1 + 1))
    if not args.fail_2:
        print('RESULT_2=[{}]'.format(args.in_2 + 1))


if __name__ == "__main__":
    main()
