import curses
from time import sleep
import threading

from type_test.quotes import Quotes
from type_test.timer import Timer

TEXT_POS = (2, 0)
HEADER_POS = (0, 0)


class Colors:
	"""
	Class representing valid color pairs for use in
	"""
	# @formatter:off
	__COLOR_RED    = 71
	__COLOR_GREEN  = 72
	__COLOR_ERROR  = 73
	__COLOR_HEADER = 74
	# @formatter:on

	# Must not be instantiated before setting up curses
	def __init__(self) -> None:
		# @formatter:off
		curses.init_pair(self.__COLOR_RED,   curses.COLOR_RED,    curses.COLOR_BLACK)
		curses.init_pair(self.__COLOR_GREEN, curses.COLOR_GREEN,  curses.COLOR_BLACK)
		curses.init_pair(self.__COLOR_ERROR, curses.COLOR_BLACK,  curses.COLOR_RED)
		curses.init_pair(self.__COLOR_HEADER, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
		self.RED    = curses.color_pair(self.__COLOR_RED)
		self.GREEN  = curses.color_pair(self.__COLOR_GREEN)
		self.ERROR  = curses.color_pair(self.__COLOR_ERROR)
		self.HEADER = curses.color_pair(self.__COLOR_HEADER)
		# @formatter:on


class Program:
	def __init__(self, stdscr) -> None:
		self.stdscr = stdscr
		self.colors = Colors()
		self.quotes = Quotes()
		self.running = False
		self.typed = ""
		self.selected_quote = None
		# Cursor position
		self.cur_pos = TEXT_POS
		self.size = self.stdscr.getmaxyx()
		self.timer = None
		self.time = (0, 0)
		self.lock = threading.Lock()

	def restart(self):
		self.running = True
		self.typed = ""
		self.selected_quote = self.quotes.random()
		self.start_timer()

	def run(self):
		self.restart()
		self.loop()

	def loop(self):
		while self.running:
			self.render()
			self.update_cursor()
			self.check_win()
			self.refresh_screen()
			self.read_input()

	def update_cursor(self):
		self.stdscr.move(*self.cur_pos)

	def render_header(self):
		with self.lock:
			seconds, millis = self.time
			# Draw background for the header
			self.stdscr.chgat(*HEADER_POS, self.size[1], self.colors.HEADER)
			header_string = "{} wpm {} cps {}.{:02d}s {}% acc".format(0, 0, seconds, millis, 0)
			# Draw current data
			self.stdscr.addstr(*HEADER_POS, header_string, self.colors.HEADER)
			# Return the cursor to its original position
			self.update_cursor()

	def render(self):
		with self.lock:
			# Pointers used to track current cursor position to be written on the screen
			cur_y, cur_x = TEXT_POS
			errored = False
			color = self.colors.GREEN
			self.stdscr.addstr(*TEXT_POS, self.selected_quote)
			for typed, selected in zip(self.typed, self.selected_quote):
				valid = typed == selected
				if not valid:
					# We don't reset errored flag unless we re-render the whole text in
					# next frame. This way we show errors since the first occurrence of
					# the mistyped letter.
					errored = True
				if errored:
					color = self.colors.ERROR
				self.stdscr.addch(cur_y, cur_x, ord(selected), color)

				# This is done to prevent us from running off of the screen.
				if cur_x == self.size[1] - 1:
					cur_y += 1
					cur_x = TEXT_POS[1]  # in case we have some padding
				else:
					cur_x += 1

			# After drawing on the screen we need to set cur_pos to allow
			# update_cursor to move it to the valid position
			self.cur_pos = (cur_y, cur_x)

	def read_input(self):
		c = self.stdscr.getch()
		if c == curses.KEY_BACKSPACE:
			self.typed = self.typed[:-1]
		elif c == curses.KEY_RESIZE:
			self.update_size()
		# FIXME: can this be better?
		elif 32 <= c <= 126:
			self.typed += chr(c)

	def check_win(self):
		if self.selected_quote == self.typed:
			# TODO: handle win
			self.stop_timer()

	def update_size(self):
		self.size = self.stdscr.getmaxyx()

	def __timer_callback(self):
		# We avoid initializing the values to 0
		# in order to allow showing previous time after
		# the timer stops
		seconds, millis = self.time
		if self.timer is not None:
			elapsed = self.timer.get_time()
			seconds = elapsed // 100
			millis = elapsed - seconds * 100
		# We save the data
		self.time = (seconds, millis)
		self.render_header()
		self.refresh_screen()

	def stop_timer(self):
		if self.timer is not None:
			self.timer.join()

	def start_timer(self):
		if self.timer is not None:
			self.timer.join()
		self.timer = Timer(callback=self.__timer_callback)
		self.timer.start()

	def stop(self):
		if self.timer is not None:
			self.timer.join()

	def refresh_screen(self):
		with self.lock:
			self.stdscr.refresh()
