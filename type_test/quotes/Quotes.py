import random
import json
import gzip
from os import getenv


class Quote:
	def __init__(self, *args) -> None:
		self.author = args[0]
		self.title = args[1]
		self.text = args[2]
		if len(args) > 3:
			self.quote_id = args[3]


class Quotes:
	# FIXME: probably won't work once the package is built
	__database_filename = "type_test/data/examples.json.gz"

	def __init__(self, quotes) -> None:
		super().__init__()
		self.quotes = {}
		self.indices = []
		for quote in map(lambda x: Quotes.__map_to_quote(x), quotes):
			self.indices.append(quote[0])
			self.quotes[quote[0]] = quote[1]

	@staticmethod
	def __map_to_quote(quote_args):
		quote = Quote(*quote_args)
		return quote.quote_id, quote

	@staticmethod
	def load():
		args = {"filename": Quotes.__database_filename, "mode": "rt", "encoding": "utf-8"}

		with gzip.open(**args) as file_obj:
			quotes = json.load(file_obj)
			quotes = tuple(map(tuple, quotes))
			return Quotes(quotes)

	def random(self):
		if getenv("TYPE_TEST_DEBUG") is not None:
			return Quote("Author", "Title", "Text", 1)
		# Should be faster than iterating over the keys of the dict
		choice = random.choice(self.indices)
		return self.quotes[choice]
