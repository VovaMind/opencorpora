# -*- coding: utf-8 -*-

import csv
import os

class CsvReader(object):
	def __init__(self, csv_file_path):
		assert os.path.isfile(csv_file_path)
		self.csv_file_path = csv_file_path
	def load_rows(self):
		with open(self.csv_file_path, newline='') as csv_file:
			csv_reader = csv.reader(csv_file)
			column_names = []
			for row in csv_reader:
				if not column_names:
					column_names = row
				else:
					assert len(column_names) == len(row)
					yield dict(zip(column_names, row))
