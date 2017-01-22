# -*- coding: utf-8 -*-
''' main-файл для извлечения ключевых слов для спанов '''

from markup_corpus import MarkupCorpus

import collections
import time

PARAMS = {
	"markup_dir": r"C:\development\OpenCorpora\FactExtAutoAssesst\data"
				r"\factRuEval-2016-master\factRuEval-2016-master\devset",
	"output_file_name" : r"span_types_keywords_devset.txt"
}

def extract_features():
	corpus = MarkupCorpus(PARAMS["markup_dir"])
	span_types_collection = {}
	for doc in corpus:
		print(doc.doc_name)
		for token in doc.tokens.values():
			for span_type in token.span_types.objects:
				if span_type not in span_types_collection:
					span_types_collection[span_type] = collections.Counter()
				span_types_collection[span_type][token.text.lower()] += 1
	with open(PARAMS["output_file_name"], "w", encoding = "utf-8") as output_file:
		for span_type in span_types_collection:
			print(span_type, file=output_file)
			print(span_types_collection[span_type].most_common(20), file=output_file)

if __name__ == '__main__':
	begin_time = time.time()
	extract_features()
	end_time = time.time()
	print("Working time: " + str(end_time-begin_time))
