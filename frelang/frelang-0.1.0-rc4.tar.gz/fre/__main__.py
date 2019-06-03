from . import vm


def main():
    import sys

    data = sys.stdin.read()
    
    env = vm.FreEnvironment('the program')
    env.execute_code(data)

if __name__ == '__main__':
    main()