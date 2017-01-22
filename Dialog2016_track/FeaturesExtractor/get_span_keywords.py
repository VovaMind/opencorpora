# -*- coding: utf-8 -*-
''' main-файл для извлечения ключевых слов для спанов '''

from markup_corpus import MarkupCorpus

import collections
import os
import time

PARAMS = {
	"markup_dir": r"C:\development\OpenCorpora\FactExtAutoAssesst\data"
				r"\factRuEval-2016-master\factRuEval-2016-master\devset",
	"output_dir" : r"C:\development\OpenCorpora\FactExtAutoAssesst\data\word_sets"
}

SPAN_TYPES = {"prj_descr", "org_descr", "geo_adj", "loc_descr", "job"}

def extract_features():
	corpus = MarkupCorpus(PARAMS["markup_dir"])
	span_types_collection = {}
	for doc in corpus:
		for token in doc.tokens.values():
			for span_type in token.span_types.objects:
				if span_type not in span_types_collection:
					span_types_collection[span_type] = collections.Counter()
				span_types_collection[span_type][token.text.lower()] += 1
	if not os.path.exists(PARAMS["output_dir"]):
		os.makedirs(PARAMS["output_dir"])
	for span_type in span_types_collection:
		if span_type not in SPAN_TYPES:
			continue
		words = list(filter(lambda x: span_types_collection[span_type][x] >= 2,
			span_types_collection[span_type]))
		if not words:
			continue
		with open(os.path.join(PARAMS["output_dir"], "words_" + span_type + ".txt"), "w", 
			encoding = "utf-8" ) as output_file:
			for word in words:
				print(word, file=output_file)

if __name__ == '__main__':
	begin_time = time.time()
	extract_features()
	end_time = time.time()
	print("Working time: " + str(end_time-begin_time))
