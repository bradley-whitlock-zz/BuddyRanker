#!/usr/bin/python

import argparse
import csv
import logging

class BuddyRanker():
	def __init__(self, args):
		self.file = args.file

		# Setup logger
		self.logger = logging.Logger('BuddyRanker')
		console = logging.StreamHandler()
		console.setLevel('DEBUG' if args.debug else 'INFO')
		self.logger.addHandler(console)


	def read_file(self):
		with open(self.file, 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=',')
			for row in reader:
				if len(row) != 4:
					self.logger.critical('FATAL: CSV should contain rows with 4 columns only')
					exit(1)
				yield(row)

	def generate_rank(self):
		for game in self.read_file():
			print game



if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('--file', required=True, help='CSV file contining the scores of matches')
	parser.add_argument('--debug', action='store_true', help='Set logging level to DEBUG')
	args = parser.parse_args()

	ranker = BuddyRanker(args)

	ranker.generate_rank()


