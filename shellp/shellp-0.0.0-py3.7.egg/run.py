import curses
from .__init__ import __version__


def main(stdscr):
	print(__version__)


def run():
	curses.wrapper(main)

if __name__ == '__main__':
	run()
