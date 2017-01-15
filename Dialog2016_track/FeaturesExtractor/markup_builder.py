# -*- coding: utf-8 -*-
''' Механизм построения результирующей разметки. '''

from common_config import MARKUP_BUILDER_PARAMS
from string_set import StringSet

import id_generator
import markup_doc
import os
import re
import sys
import time

OUTPUT_CHUNKS_COUNT = 5000

def get_work_dir():
	return os.path.join(MARKUP_BUILDER_PARAMS["work_dir"], sys.argv[1])

def read_token_docs_file(file_name):
	result = {}
	with open(file_name, "r") as input_file:
		for file_line in input_file.readlines():
			line_parts = file_line.replace("\n", "").split(" ")
			if (line_parts[1] not in result):
				result[line_parts[1]] = []
			result[line_parts[1]].append(int(line_parts[0]))
	return result

class TokenOutput:
	def __init__(self, objects, spans):
		self.objects = objects
		self.spans = spans

def read_output_file(file_name):
	result = {}
	token_ids = []
	with open(file_name, "r") as input_file:
		for file_line in input_file.readlines():
			if (file_line.replace("\n", "") == '"","id","objects","spans"'):
				continue
			line_parts = file_line.replace("\n", "").replace('"', "").split(",")
			token_id = int(line_parts[1])
			token_ids.append(token_id)
			token_output = TokenOutput(line_parts[2], line_parts[3])
			result[token_id] = token_output
	# add objects by neighbours (0-st tuple part)
	objects = []
	for i in token_ids:
		current_objects = StringSet()
		current_objects.load_from_string(result[i].objects)
		objects.append(current_objects)
	for (i, j) in zip(objects, range(len(objects))):
		if not i.has_string("LocOrg"):
			continue
		for object_to_add in ["Org", "Location"]:
			if (j > 0 and objects[j - 1].has_string(object_to_add)) or\
			( j < len(objects) - 1 and objects[j + 1].has_string(object_to_add)):
				i.add_string(object_to_add)
	for (i, j) in zip(objects, token_ids):
		result[j].objects = i.get_all()
	return result

def read_tokens_file(doc_name):
	result = {}
	with open(os.path.join(get_work_dir(), doc_name + ".tokens"), "r", encoding="utf-8") as tokens_file:
		for file_line in tokens_file.readlines():
			parts = file_line.replace("\n", "").split(" ")
			if len(parts) < 4:
				continue
			result[int(parts[0])] = (int(parts[1]), int(parts[2]), parts[3])
	return result

def extract_doc_spans(doc_token_ids, token_output):
	result = {}
	token_ids = sorted(doc_token_ids)
	spans_start = {}
	for (token_id, i) in zip(token_ids, range(len(token_ids))):
		token_spans = set(token_output[token_id].spans.split("+"))
		# Спан был в прошлом токене, но нет в текущем спане.
		# Это значит очередной спан завершился.
		prev_token_spans = list(spans_start.keys())
		for prev_token_span in prev_token_spans:
			if prev_token_span not in token_spans:
				new_span = markup_doc.SpanInfo(type = prev_token_span, 
											id = id_generator.IdGenerator.get(),
											token_pos = token_ids[spans_start[prev_token_span]],
											token_length = i - spans_start[prev_token_span],
											text_pos = -1, text_length = -1)
				for j in range(spans_start[prev_token_span], i):
					if token_ids[j] not in result:
						result[token_ids[j]] = set()
					result[token_ids[j]].add(new_span)
				spans_start.pop(prev_token_span)
		# Спан есть в текущем токене, но нет в предыдущем.
		# Это означает начало очередного спана.
		for current_token_span in token_spans:
			if current_token_span == "NONE":
				continue
			if current_token_span not in spans_start:
				spans_start[current_token_span] = i
	for last_token_span in spans_start:
		new_span = markup_doc.SpanInfo(type = last_token_span, 
									id = id_generator.IdGenerator.get(),
									token_pos = token_ids[spans_start[last_token_span]],
									token_length = len(token_ids) - spans_start[last_token_span],
									text_pos = -1, text_length = -1)
		for j in range(spans_start[last_token_span], len(token_ids)):
			if token_ids[j] not in result:
				result[token_ids[j]] = set()
			result[token_ids[j]].add(new_span)
	return result

def get_object_span_ids(class_name, spans):
	result = set()
	class_span_types = {"Org": {"org_name", "org_descr", "geo_adj"},
						"Person": {"surname", "name", "patronymic", "nickname"},
						"LocOrg": {"loc_name", "loc_descr", "org_name", "org_descr", "geo_adj"},
						"Location": {"loc_name", "loc_descr", "geo_adj"},
						"Facility": {"facility_descr", "facility_name"},
						"Project": {"prj_descr", "prj_name"}}
	for span in spans:
		if span.type in class_span_types[class_name]:
			result.add(span.id)
	return result

def extract_doc_objects(doc_token_ids, token_output, token_to_spans, id_to_token):
	result = []
	objects_span_ids = {}
	for token_id in doc_token_ids:
		# Обработка случая org_descr "org_name"
		# Мы не должны разрывать объект в этому случае, несмотря на то
		# что на токене " не висит объект
		# Не разрываем объект по точке: обработка случая "Л.Н. Толстой"
		if id_to_token[token_id][2] == "\"" or id_to_token[token_id][2] == "'" or\
		id_to_token[token_id][2] == "«" or id_to_token[token_id][2] == "<" or\
		id_to_token[token_id][2] == ".":
			continue
		token_objects = set(token_output[token_id].objects.split("+"))
		# Объект был в прошлом токене, но нет в текущем спане.
		# Это значит очередной объект завершился.
		prev_token_classes = list(objects_span_ids.keys())
		for prev_token_class in prev_token_classes:
			if prev_token_class not in token_objects:
				new_object = markup_doc.ObjectInfo(id = id_generator.IdGenerator.get(),
												type = prev_token_class,
												span_ids = sorted(list(objects_span_ids[prev_token_class])))
				# Иногда нет подходящих спанов для объекта (случай LocOrg+Org)
				# В этом случае пропускаем объект
				if new_object.span_ids:
					result.append(new_object)
				objects_span_ids.pop(prev_token_class)
		# Объект есть в текущем токене, но нет в предыдущем.
		# Это означает начало очередного объекта.
		for current_token_class in token_objects:
			if current_token_class == "NONE":
				continue
			if current_token_class not in objects_span_ids:
				objects_span_ids[current_token_class] = set()
			# Добавляем id'ники спанов для объектов
			# Иногда есть токены с объектом, но без спана
			# Не добавляем спаны в этом случае
			if token_id in token_to_spans:
				new_span_ids = get_object_span_ids(current_token_class, token_to_spans[token_id])
				objects_span_ids[current_token_class] = set.union(
					objects_span_ids[current_token_class], new_span_ids)
	for last_token_class in objects_span_ids:
		new_object = markup_doc.ObjectInfo(id = id_generator.IdGenerator.get(),
										type = last_token_class,
										span_ids = sorted(list(objects_span_ids[last_token_class])))
		result.append(new_object)
	return result

def output_document(doc_name, doc_token_ids, token_to_spans, doc_objects):
	document = markup_doc.MarkupDoc(os.path.join(get_work_dir(), doc_name), doc_name, True)
	token_ids = sorted(doc_token_ids)
	all_spans = set()
	for token_id in token_ids:
		if token_id not in token_to_spans:
			continue
		for current_span in token_to_spans[token_id]:
			all_spans.add(current_span)
	all_spans = list(all_spans)
	all_spans.sort(key = lambda x: x.id)
	span_texts = {}
	# Выводим спаны
	with open(os.path.join(get_work_dir(), doc_name + ".spans"), "w") as span_file:
		for span in all_spans:
			debug_text = ""
			for i in range(span.token_pos, span.token_pos + span.token_length):
				if len(debug_text) > 0:
					debug_text += " "
				debug_text += document.tokens[i].text
			debug_text = debug_text.replace("\n", "")
			span_texts[span.id] = debug_text
			# Находим границы в тексте
			text_start_pos = document.tokens[span.token_pos].pos
			end_token_pos = span.token_pos + span.token_length - 1
			text_end_pos = document.tokens[end_token_pos].pos + \
			document.tokens[end_token_pos].length
			# Выводим спан
			span_file.write(str(span.id) + " ")
			span_file.write(span.type + " ")
			span_file.write(str(text_start_pos) + " ")
			span_file.write(str(text_end_pos - text_start_pos) + " ")
			span_file.write(str(span.token_pos) + " ")
			span_file.write(str(span.token_length) + "  # ")
			for i in range(span.token_pos, span.token_pos + span.token_length):
				span_file.write(str(i) + " ")
			for ch in debug_text:
				try:
					span_file.write(ch)
				except:
					# Иногда в тексте встречаются "плохие" символы
					span_file.write("?")
			span_file.write("\n")
	# Выводим объекты
	with open(os.path.join(get_work_dir(), doc_name + ".objects"), "w") as object_file:
		for obj in doc_objects:
			object_file.write(str(obj.id) + " ")
			object_file.write(str(obj.type))
			debug_text = ""
			for id in obj.span_ids:
				object_file.write(" " + str(id))
				if len(debug_text) > 0:
					debug_text += " "
				debug_text += span_texts[id]
			try:
				object_file.write("  # " + debug_text)
			except:
				pass
			object_file.write("\n")

def build_chunk_markup(doc_to_tokens, token_to_output):
	for doc in doc_to_tokens:
		id_to_token = read_tokens_file(doc)
		token_to_spans = extract_doc_spans(doc_to_tokens[doc], token_to_output)
		doc_objects = extract_doc_objects(doc_to_tokens[doc], token_to_output, token_to_spans, id_to_token)
		output_document(doc, doc_to_tokens[doc], token_to_spans, doc_objects)

def build_markup():
	#TODO: id schema update?
	id_generator.IdGenerator.current_id = 1000000000 + int(sys.argv[1])*100000000
	for chunk_id in range(OUTPUT_CHUNKS_COUNT):
		# Читаем файл с парами id токена; имя документа и строим отображение:
		# имя документа -> id токенов
		token_to_doc_file_name = os.path.join(get_work_dir(), 
											"_token_docs_" + str(chunk_id) + ".txt")
		doc_to_tokens = read_token_docs_file(token_to_doc_file_name)
		# Файл с объектами/спанами для токенов. Строим отбражение:
		# id токена -> TokenOutput
		output_file_name = os.path.join(get_work_dir(), 
										"_output_" + str(chunk_id) + ".csv")
		token_to_output = read_output_file(output_file_name)
		build_chunk_markup(doc_to_tokens, token_to_output)

if __name__ == '__main__':
	begin_time = time.time()
	build_markup()
	end_time = time.time()
	print("Working time: " + str(end_time-begin_time))
