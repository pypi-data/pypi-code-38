from os import path
import sys

here = path.abspath(path.dirname(__file__))
sys.path.append(here)

def main():
    import nauta
    nauta.main()

if __name__ == "__main__":
    main()
