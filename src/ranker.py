#!/usr/bin/python

import argparse
import csv
import logging
from spreadsheet import SpreadSheet

class BuddyRanker():
	def __init__(self, args):

		# Setup logger
		self.logger = logging.Logger('BuddyRanker')
		console = logging.StreamHandler()
		console.setLevel('DEBUG' if args.debug else 'INFO')
		self.logger.addHandler(console)

		# Setup Goggle Sheets Credentials and options
		self.SpreadSheet = SpreadSheet(gsecrets=args.g_secrets, url=args.g_url)
		self.g_scores_sheet = "Scores"
		self.g_ranking_sheet = "Rankings"
		self.g_headers = ['Player 1', 'Player 2', 'Wins Player 1', 'Wins Player 2']
		self.g_rank_header = ["Player", "Rank"]
		self.ignore_upload = args.g_ignore_upload
		self.localdata = args.localdata

		# Bradley Terry related parameters
		self.init_rank = args.init_rank
		self.tol = args.tol
		self.max_itt = args.max_itt

	def read_local_file(self):
		lst = []
		with open(self.file, 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=',')
			next(reader, None)
			for row in reader:
				if len(row) != 4:
					self.logger.critical('FATAL: CSV should contain rows with 4 columns only')
					exit(1)
				# Keep same format a google sheet
				lst.append(dict(zip(self.g_headers, row)))
		return lst

	def setup_wins(self):
		wins = {}
		players = set()

		if args.localdata != None:
			data = self.read_local_file()
		else:
			data = self.SpreadSheet.open_sheet(spreadsheet=self.g_scores_sheet)

		for game in data:
			player1 = game[self.g_headers[0]]
			player2 = game[self.g_headers[1]]
			player1_score = int(game[self.g_headers[2]])
			player2_score = int(game[self.g_headers[3]])

			players.add(player1)
			players.add(player2)
			self.logger.debug("Score Player1: %s, %s  Player2: %s, %s", player1, player1_score, player2, player2_score)

			# Determine who won game
			if player1_score > player2_score:
				self.logger.debug("Player 1 Wins: %s", player1)
				
				if player1 not in wins.keys():
					wins[player1] = {player2: 1}
				elif player2 not in wins[player1].keys():
					wins[player1][player2] = 1
				else:
					wins[player1][player2] += 1

			elif player2_score > player1_score:
				self.logger.debug("Player 2 Wins: %s", player2)

				if player2 not in wins.keys():
					wins[player2] = {player1: 1}
				elif player1 not in wins[player2].keys():
					wins[player2][player1] = 1
				else:
					wins[player2][player1] += 1

			else:
				self.logger.critical("ERROR: No Ties allowed, continuing")

		return wins, list(players)

	def get_games_played(self, wins, player1, player2):
		tot = 0
		if player1 in wins.keys() and player2 in wins[player1].keys():
			tot += wins[player1][player2]
		if player2 in wins.keys() and player1 in wins[player2].keys():
			tot += wins[player2][player1]
		return tot

	def get_vector_diff(self, list1, list2):
		# Lists must be of same length
		diff = 0
		for i in range(0,len(list1)):
			diff += abs(float(list1[i]) - float(list2[i]))
		return diff

	def norm_dict(self, ranks):
		factor = 1.0 / sum(ranks.itervalues())
		return {k: v * factor for k,v in ranks.iteritems()}

	def train_ranking(self):
		wins, players = self.setup_wins()
		total_wins = {player: sum(wins[player].values()) for player in wins}

		# Generate initial rank vector
		rank = self.norm_dict({player: self.init_rank for player in players})
		
		itt = 0
		while itt < self.max_itt:
			itt += 1
			last_rank = rank.copy()
			for player in players:
				if player not in wins.keys():
					rank[player] = 0
				else:
					tot = 0
					for opp in wins[player]:
						tot_games = self.get_games_played(wins=wins, player1=player, player2=opp) 
						tot = tot_games / (last_rank[player] + last_rank[opp])	
					rank[player] = total_wins[player] / tot
			
			# normalize
			rank = self.norm_dict(rank)
			
			diff = self.get_vector_diff(last_rank.values(), rank.values())
			
			if float(diff) < float(self.tol):
				self.logger.info("Converged after %s itterations", itt)
				break
			elif itt % 10 == 0:
				self.logger.info("Working on itteration %s ", itt)

		self.logger.info("Completed ranks: %s", rank)
		return rank

	def upload_sheet(self, ranks):

		if self.ignore_upload:
			self.logger.info("Did not upload to Google Sheets due to ignore_upload flag")
			return

		# SpreadSheet.upload_sheet uploads 2D array to GSheets
		data = []
		for key in ranks:
			data.append([key, int(ranks[key] * 1000)])
		data = sorted(data, key=lambda x: (x[1]), reverse=True)
		data.insert(0,self.g_rank_header)

		self.logger.info("Uploading to Google Sheets")
		self.SpreadSheet.upload_sheet(data=data, spreadsheet=self.g_ranking_sheet)
			

		 
if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('--debug', action='store_true', help='Set logging level to DEBUG')
	parser.add_argument('--localdata', help='Pass in location of local CSV (usually in data/) to ignore GoogleSheets')
	
	# Google Sheet related credentials and options
	parser.add_argument('--g-secrets', help='JSON secrets file supplied by Google API')
	parser.add_argument('--g-url', help='URL of the google sheet with the training data')
	parser.add_argument('--g-ignore-upload', action='store_true', help='Pass parameter to avoid uploading results to Goggle Sheets')
	
	# Bradley-Terry related paramaters

	parser.add_argument('--init-rank', default=0.5, type=float, help='Initial value 0 < x< 1 to set ranks too')
	parser.add_argument('--tol', default=1e-3, type=float, help='Convergence tolerance')
	parser.add_argument('--max-itt', default=1000, type=int, help='Maximum number of itterations of the Bradley Terry model')

	args = parser.parse_args()

	# Initilize ranker
	ranker = BuddyRanker(args)

	# Determine the ranking of all players
	ranks = ranker.train_ranking()

	# Upload the results to GSheets (if flag not set)
	ranker.upload_sheet(ranks=ranks)


