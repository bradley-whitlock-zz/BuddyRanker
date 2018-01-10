#!/usr/bin/python

import argparse
import csv
import logging
import pandas as pd

class BuddyRanker():
	def __init__(self, args):
		self.file = args.file

		# Setup logger
		self.logger = logging.Logger('BuddyRanker')
		console = logging.StreamHandler()
		console.setLevel('DEBUG' if args.debug else 'INFO')
		self.logger.addHandler(console)

		self.source_keys = ['Player1', 'Player2', 'Score1', 'Score2']


	def read_file(self):
		lst_dict = []
		
		self.logger.info('Reading from CSV: %s', self.file)	
		df = pd.read_csv(self.file, delimiter=',', names=self.source_keys, header=0, error_bad_lines=False)
		self.logger.debug('Successfully read CSV')
		return df
				

	def generate_game_stats(self):
		df_data = self.read_file()

		df_win_p1 = df_data[df_data.Score1 > df_data.Score2].groupby(['Player1', 'Player2']).size().reset_index(name='count').rename(columns={'Player1':'Winner','Player2':'Loser'})
		df_win_p2 = df_data[df_data.Score1 < df_data.Score2].groupby(['Player1', 'Player2']).size().reset_index(name='count').rename(columns={'Player1':'Loser','Player2':'Winner'})
		
		df = df_win_p1.append(df_win_p2, ignore_index=True).groupby(['Winner', 'Loser']).sum().reset_index()

		self.logger.debug('Winners results: \n %s', df)
		self.logger.info('Gathered data on players records')
		return df

	def train_ranking(self):
		df = self.generate_game_stats()

		df_wins = df.groupby(['Winner']).sum(axis=1).drop('Loser', 1).reset_index()
		
		players = list(set(df['Winner']) | set(df['Loser']))
		
		
		for player in players:

			total_wins = df_wins[df_wins['Winner'] == row['Winner']][['count']].iloc[0]
			
			exit(0)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('--file', required=True, help='CSV file contining the scores of matches')
	parser.add_argument('--debug', action='store_true', help='Set logging level to DEBUG')
	args = parser.parse_args()

	ranker = BuddyRanker(args)

	ranker.train_ranking()


