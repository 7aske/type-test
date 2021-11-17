import random


class Quotes:
	# TODO: read quotes from file
	def __init__(self) -> None:
		self.quotes = [
			"The curses.ascii module supplies ASCII class membership functions that take either integer or 1-character string arguments."
		]

	def random(self):
		return random.choice(self.quotes)
