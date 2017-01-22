# -*- coding: utf-8 -*-
''' main-файл для извлечения ключевых слов для спанов '''

from common_config import GET_SPAN_KEYWORDS
from markup_corpus import MarkupCorpus

import collections
import os
import re
import time

SPAN_TYPES = {"prj_descr", "org_descr", "geo_adj", "loc_descr", "job"}

def extract_features():
	corpus = MarkupCorpus(GET_SPAN_KEYWORDS["markup_dir"])
	span_types_collection = {}
	for doc in corpus:
		for token in doc.tokens.values():
			for span_type in token.span_types.objects:
				if span_type not in span_types_collection:
					span_types_collection[span_type] = collections.Counter()
				if re.search(r"\w", token.text) is None:
					continue
				span_types_collection[span_type][token.text.lower()] += 1
	if not os.path.exists(GET_SPAN_KEYWORDS["output_dir"]):
		os.makedirs(GET_SPAN_KEYWORDS["output_dir"])
	for span_type in span_types_collection:
		if span_type not in SPAN_TYPES:
			continue
		words = list(filter(lambda x: span_types_collection[span_type][x] >= 2,
			span_types_collection[span_type]))
		if not words:
			continue
		with open(os.path.join(GET_SPAN_KEYWORDS["output_dir"], "words_" + span_type + ".txt"), "w", 
			encoding = "utf-8" ) as output_file:
			for word in words:
				print(word, file=output_file)

if __name__ == '__main__':
	begin_time = time.time()
	extract_features()
	end_time = time.time()
	print("Working time: " + str(end_time-begin_time))
