import os, sys, re, time, io

import argparse

from pygments import highlight
from pygments.lexers import SqlLexer
from pygments.formatters import Terminal256Formatter

#TODO: set formatter
#TODO: (don't) format queries

def rev_readlines(filename, bufsize=8192):
	"""
	Reads lines backwards from the file
	
	Based on: http://code.activestate.com/recipes/496941-simple-readlines-in-reverse-wdeque/
	"""
	f1 = open(filename, 'rb')
	f1.seek(0, 2)
	leftover = ''
	while f1.tell():
		if f1.tell() < bufsize:
			bufsize = f1.tell()
		f1.seek(-bufsize, 1)
		in_memory = f1.read(bufsize) + leftover
		f1.seek(-bufsize, 1)
		lines = in_memory.split('\n')
		for i in reversed(lines[1:]):
			yield i + '\n'
		leftover = lines[0]
	yield leftover + '\n'

class LogWatcher(object):
	"""
	Watches MySQL's general_log for changes and prints out nicely formatted SQL queries. Handy if you use ORM.
	"""
	def __init__(self, file_handle, queries, formatter=Terminal256Formatter()):
		self.file_handle = open(file_handle, 'rb')

		self.formatter = formatter
		self.parse(self.tail(queries=queries))
		self.file_handle.seek(0,2)
		self.loop()

	def loop(self, interval=1):
		"""
		Watches the log file for changes
		"""
		content = ''

		while True:
			line = self.file_handle.readline()
			if not line:
				if content != '':
					self.parse(content)
					content = ''

				time.sleep(interval)
			else:
				content += line

	def tail(self, queries):
		"""
		Returns (specified number of) lines that contains just query
		"""
		queries_count = 0
		lines = []

		for line in rev_readlines(self.file_handle.name):
			lines.append(line)
			
			if re.search(r'^(\d+\s+(\d{1,2}:){2}\d{1,2})?\s+\d+\s+Query', line):
				queries_count += 1

			if queries_count == queries:
				break

		return ''.join(reversed(lines))

	def parse(self, content):
		"""
		Parses the lines from the log file
		"""
		match =  re.finditer(r"""^(\d+\s+(?P<date>(\d{1,2}:){2}\d{1,2}))?
							 \s+(?P<content>(.+(\n(?!(\d+\s+\d+:|\s+\d+\s+\w)))?)+)""", content, re.MULTILINE | re.VERBOSE)

		last_date = None

		quit_check = False

		for m in match:
			text = m.group('content')
			date = m.group('date')
			if date:
				last_date = date

			if not quit_check:
				if re.search(r'\d+\s+?Quit', text):
					quit_check = True
					print "-" * 80

			if re.search(r'\d+\s+?Query', text):
				match2 = re.match(r"\d+\s+[A-Za-z]+\s+(?P<query>.+)", text, re.DOTALL)

				print (last_date + ' ' * (10 - len(last_date)) if last_date else ' ' * 10) + self.highlight_line(re.sub(r'\n', ' ', match2.group('query')))
				last_date = None
				quit_check = False

	def highlight_line(self, text):
		"""
		Returns highlighted line to be printed
		"""
		return highlight(text, SqlLexer(), self.formatter).rstrip()

if __name__ == "__main__":
	filename = '/var/log/mysql/mysql.log'
	try:
		parser = argparse.ArgumentParser(description="Watches MySQL's general_log for changes and prints out nicely formatted SQL queries. Handy if you use ORM.")

		parser.add_argument('--last', dest='last', default=20, help='set the number of last queries you want to see when the script starts')
		parser.add_argument('--dont-format-queries', nargs='?', const=True, dest='format', help='if you do not wish queries to be formatted')

		args = parser.parse_args()

		print args.format

		l = LogWatcher(filename, queries=int(args.last))
	except IOError:
		sys.stderr.write("Can't read file '%s' (Do you have sufficient privileges?)\n" % filename)
		sys.exit(1)
	except KeyboardInterrupt:
		sys.exit()
