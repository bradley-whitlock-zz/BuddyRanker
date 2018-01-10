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

		self.init_rank = 0.5
		self.tol = 1e-3
		self.max_itt = 50

	def read_file(self):
		lst = []
		with open(self.file, 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=',')
			next(reader, None)
			for row in reader:
				if len(row) != 4:
					self.logger.critical('FATAL: CSV should contain rows with 4 columns only')
					exit(1)
				lst.append(row)
		return lst

	def setup_wins(self):
		wins = {}
		players = set()
		for game in self.read_file():
			player1 = game[0]
			player2 = game[1]
			players.add(player1)
			players.add(player2)
			self.logger.debug("Score Player1: %s, %s  Player2: %s, %s", player1, game[2], player2, game[3])

			# Determine who won game
			if int(game[2]) > int(game[3]):
				self.logger.debug("Player 1 wins: %s", player1)
				# Player 1 Wins
				if player1 not in wins.keys():
					wins[player1] = {player2: 1}
				elif player2 not in wins[player1].keys():
					wins[player1][player2] = 1
				else:
					wins[player1][player2] +=1
			elif int(game[3]) > int(game[2]):
				# Player 2 Wins
				self.logger.debug("Player 2 wins: %s", player2)
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
				self.logger.info("Working on itteration ", itt)

		return rank

		 

if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('--file', required=True, help='CSV file contining the scores of matches')
	parser.add_argument('--debug', action='store_true', help='Set logging level to DEBUG')
	args = parser.parse_args()

	ranker = BuddyRanker(args)

	ranks = ranker.train_ranking()

	print ranks


