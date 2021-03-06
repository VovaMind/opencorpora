# -*- coding: utf-8 -*-
''' main-файл для извлечения ключевых слов для спанов '''

from engine.tools.config import Config
from engine.markup_corpus import MarkupCorpus
from engine.documents_list import DocumentsList

import collections
import inspect
import os
import re
import sys
import time

SPAN_TYPES = {"prj_descr", "org_descr", "geo_adj", "loc_descr", "job"}
SCRIPT_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


def read_stop_words():
	''' Stop words source: http://www.ranks.nl/stopwords/russian '''
	with open(os.path.join(SCRIPT_PATH, "engine", "data", "stop_word_list.txt"), "r",
			encoding="utf-8") as input_file:
		return set(map(lambda x: x.replace("\n", "").lower(), input_file.readlines()))


def extract_features():
	config = Config(sys.argv[1])
	stop_words = read_stop_words()
	document_list = DocumentsList(config.get("devset_base_dir"),
		config.get("devset_documents_list"))
	corpus = MarkupCorpus(document_list)
	
	span_types_collection = {}
	for doc in corpus.load_documents():
		for token in doc.tokens.values():
			for span_type in token.span_types.objects:
				if span_type not in span_types_collection:
					span_types_collection[span_type] = collections.Counter()
				if re.search(r"\w", token.text) is None or token.text in stop_words:
					continue
				span_types_collection[span_type][token.text.lower()] += 1
	
	if not os.path.exists(config.get("words_set_dir")):
		os.makedirs(config.get("words_set_dir"))
	for span_type in span_types_collection:
		if span_type not in SPAN_TYPES:
			continue
		words = list(filter(lambda x: span_types_collection[span_type][x] >= 2,
			span_types_collection[span_type]))
		if not words:
			continue
		with open(os.path.join(config.get("words_set_dir"), "words_" + span_type + ".txt"), "w",
				encoding = "utf-8" ) as output_file:
			for word in sorted(words):
				print(word, file=output_file)

if __name__ == '__main__':
	begin_time = time.time()
	extract_features()
	end_time = time.time()
	print("Working time: " + str(end_time-begin_time))
