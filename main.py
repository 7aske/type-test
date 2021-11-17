import curses
import os

from type_test.program import Program


def main(stdscr):
	program = Program(stdscr)
	program.run()


if __name__ == '__main__':
	# TERM variable is needed for curses library to work property.
	# xterm-256color should be a sane default
	if os.environ.get("TERM") is None:
		os.environ["TERM"] = "xterm-256color"
	try:
		curses.wrapper(main)
	except KeyboardInterrupt:
		pass
