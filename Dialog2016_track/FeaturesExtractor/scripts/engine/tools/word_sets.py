# -*- coding: utf-8 -*-
''' Набор множеств строк. '''

import os

class WordSets(object):
	def __init__(self, input_dir):
		self.word_sets = []
		if not input_dir:
			return
		all_files = sorted(os.listdir(input_dir))
		for file_name in all_files:
			with open(os.path.join(input_dir, file_name), "r", encoding = "utf-8") as input_file:
				file_lines = set(map(lambda x: x.replace("\n", "").lower(), input_file.readlines()))
				self.word_sets.append(file_lines)
	def sets_count(self):
		return len(self.word_sets)
	def get_word_info(self, word):
		result = []
		for current_set in self.word_sets:
			if word.lower() in current_set:
				result.append(1)
			else:
				result.append(0)
		return result
