# -*- coding: utf-8 -*-
''' Механизм построения результирующей разметки. '''

from common_config import GET_CONTEST_FORMAT_PARAMS

import collections
import os
import sys
import time

def get_work_dir():
	return os.path.join(GET_CONTEST_FORMAT_PARAMS["work_dir"], sys.argv[1])

def get_document_names():
	# TODO: code duplication remove
	# Оставляем только файлы, имя которых начинается с "book_".
	dir_file_names = filter(lambda x: x.find("book_") == 0, os.listdir(get_work_dir()))
	
	# Убираем расширения файлов.
	doc_names = map(lambda x: x[0:x.find(".")], dir_file_names)
	
	# оставляем только документы с полной информацией, 
	# то есть для каждого документа book_id есть:
	# tokens-файл, spans-файл, objects-файл и txt-файл (всего 4 штуки)
	cnt = collections.Counter(doc_names)
	return list(filter(lambda x: cnt[x] == 4, cnt))

def read_spans(doc_name):
	result = {}
	with open(os.path.join(get_work_dir(), doc_name + ".spans"), "r") as span_file:
		for file_line in span_file.readlines():
			parts = file_line.replace("\n", "").split(" ")
			span_id = int(parts[1])
			text_start = int(parts[4])
			text_length = int(parts[5])
			result[span_id] = (text_start, text_length)
	return result

def process_objects(doc_name, spans):
	with open(os.path.join(get_work_dir(), doc_name + ".objects"), "r") as object_file:
		with open(os.path.join(get_work_dir(), doc_name + ".task1"), "w", 
		encoding='utf8') as output_file:
			for file_line in object_file.readlines():
				temp = file_line[0:file_line.index("  #")]
				parts = temp.split(" ")
				obj_type = parts[1]
				parts = map(lambda x: int(x), parts[2:])
				min_pos = 2**32
				max_pos = -min_pos
				for span_id in parts:
					min_pos = min(min_pos, spans[span_id][0])
					max_pos = max(max_pos, spans[span_id][0] + spans[span_id][1])
				output_file.write(obj_type + " " + str(min_pos) + " " + str(max_pos - min_pos) + "\n")

def get_contest_format():
	documents = get_document_names()
	for doc in documents:
		spans = read_spans(doc)
		process_objects(doc, spans)

if __name__ == '__main__':
	begin_time = time.time()
	get_contest_format()
	end_time = time.time()
	print("Working time: " + str(end_time-begin_time))
