#!/usr/bin/python

import gspread
from oauth2client.service_account import ServiceAccountCredentials

class SpreadSheet():

	def __init__(self, gsecrets, url):
		# use creds to create a client to interact with the Google Drive API
		self.scope = ['https://spreadsheets.google.com/feeds']
		self.creds = ServiceAccountCredentials.from_json_keyfile_name(gsecrets, self.scope)
		self.client = gspread.authorize(self.creds)
		self.sheet = self.client.open_by_url(url)
 
	def open_sheet(self, spreadsheet):
		return self.sheet.worksheet(spreadsheet).get_all_records()

	def upload_sheet(self, spreadsheet, data):
		# Multiple ways of doing this with Google API
		# 	My Implementation, import 2D List as CSV into sheet
		#  	Ex: data = [[1,3,5],[2,4,6]]
		self.sheet.worksheet(spreadsheet).clear()
		for y in range(0,len(data)):
			for x in range(0,len(data[y])):
				self.sheet.worksheet(spreadsheet).update_cell(y+1, x+1, data[y][x])
