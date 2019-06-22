import argparse

parser = argparse.ArgumentParser()

parser.add_argument('name', type=str, default='Human',
        help='A special someone to say hello to')

args = parser.parse_args()

def main():
    print(f'Hello {args.name}!')

if __name__ == '__main__':
    main()

