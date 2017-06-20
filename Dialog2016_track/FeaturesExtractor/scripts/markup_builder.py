# -*- coding: utf-8 -*-
''' Механизм построения результирующей разметки. '''

from engine.documents_list import DocumentsList
from engine.tools.config import Config
from engine.tools.id_generator import IdGenerator
from tools.string_set import StringSet

import engine.markup_doc
import engine.tools.id_generator
import os
import re
import sys
import time

OUTPUT_CHUNKS_COUNT = 5000

class TokenOutput:
	def __init__(self, objects, spans):
		self.objects = objects
		self.spans = spans

class Builder(object):
	def __init__(self, id_generator, part_id, config):
		self.id_generator = id_generator
		self.part_id = part_id
		self.config = config
	
	def get_work_dir(self):
		return os.path.join(self.config.get("output_dir"), str(self.part_id))
	
	@staticmethod
	def read_token_docs_file(file_name):
		result = {}
		with open(file_name, "r") as input_file:
			for file_line in input_file.readlines():
				line_parts = file_line.replace("\n", "").split(" ")
				if (int(line_parts[1]) not in result):
					result[int(line_parts[1])] = []
				result[int(line_parts[1])].append(int(line_parts[0]))
		return result
	
	@staticmethod
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
	
	def read_tokens_file(self, doc_id):
		result = {}
		with open(os.path.join(self.get_work_dir(), str(doc_id) + ".tokens"), "r",
				encoding="utf-8") as tokens_file:
			for file_line in tokens_file.readlines():
				parts = file_line.replace("\n", "").split(" ")
				if len(parts) < 4:
					continue
				result[int(parts[0])] = (int(parts[1]), int(parts[2]), parts[3])
		return result
	
	def read_tokens_list(self, file_name):
		''' Читаем список токенов для определния переводов строки. '''
		# WTF
		with open(file_name, "r", encoding="utf-8") as tokens_file:
			return list(map(lambda x: x.replace("\n", ""), tokens_file.readlines()))
	
	@staticmethod
	def parse_it(str):
		''' TODO: comment? '''
		if str.startswith("begin_"):
			return str[6:], True
		return str, False
	
	def extract_doc_spans(self, distinguish_span_begin, doc_id, doc_token_ids, token_output,
			doc_id_to_token_file):
		tokens_list = self.read_tokens_list(doc_id_to_token_file[doc_id])
		list_index = 0
		result = {}
		token_ids = sorted(doc_token_ids)
		spans_start = {}
		for (token_id, i) in zip(token_ids, range(len(token_ids))):
			is_new_line = False
			if list_index < len(tokens_list) and tokens_list[list_index] == "":
				is_new_line = True
				list_index += 1
			list_index += 1
			token_spans = set(token_output[token_id].spans.split("+"))
			prev_token_spans = list(spans_start.keys())
			for prev_token_span_raw in prev_token_spans:
				prev_token_span, is_begin = Builder.parse_it(prev_token_span_raw)
				should_split = prev_token_span not in token_spans or is_new_line
				if distinguish_span_begin:
					should_split = is_begin or should_split
				if should_split:
					new_span = engine.markup_doc.SpanInfo(type = prev_token_span, 
												id = self.id_generator.get(),
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
			for current_token_span_raw in token_spans:
				current_token_span, is_begin = Builder.parse_it(current_token_span_raw)
				if current_token_span == "NONE":
					continue
				if current_token_span not in spans_start:
					spans_start[current_token_span] = i
		for last_token_span in spans_start:
			new_span = engine.markup_doc.SpanInfo(type = last_token_span, 
										id = self.id_generator.get(),
										token_pos = token_ids[spans_start[last_token_span]],
										token_length = len(token_ids) - spans_start[last_token_span],
										text_pos = -1, text_length = -1)
			for j in range(spans_start[last_token_span], len(token_ids)):
				if token_ids[j] not in result:
					result[token_ids[j]] = set()
				result[token_ids[j]].add(new_span)
		return result
	
	@staticmethod
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
	
	def extract_doc_objects(self, distinguish_span_begin, distinguish_object_begin, doc_id,
			doc_token_ids, token_output, token_to_spans, id_to_token, doc_id_to_token_file):
		doc_info = {
			"info#id": doc_id,
			"info#contest_tokenization": os.path.join(self.get_work_dir(), str(doc_id) + ".tokens")
		}
		document = engine.markup_doc.MarkupDoc(doc_info, True, distinguish_span_begin,
			distinguish_object_begin)
		tokens_list = self.read_tokens_list(doc_id_to_token_file[doc_id])
		list_index = 0
		result = []
		objects_span_ids = {}
		prev_token_id = -1
		is_new_line_skipped = False
		for token_id in doc_token_ids:
			is_new_line = False
			if list_index < len(tokens_list) and tokens_list[list_index] == "":
				is_new_line = True
				list_index += 1
			list_index += 1
			# Обработка случая org_descr "org_name"
			# Мы не должны разрывать объект в этому случае, несмотря на то
			# что на токене " не висит объект
			# Не разрываем объект по точке: обработка случая "Л.Н. Толстой"
			if id_to_token[token_id][2] == "\"" or id_to_token[token_id][2] == "'" or\
					id_to_token[token_id][2] == "«" or id_to_token[token_id][2] == "<":
				prev_token_id = token_id
				is_new_line_skipped = is_new_line
				continue
			if id_to_token[token_id][2] == "." and prev_token_id != -1 and\
					document.tokens[prev_token_id].length <= 2:
				prev_token_id = token_id
				is_new_line_skipped = is_new_line
				continue
			is_new_line = is_new_line or is_new_line_skipped
			is_new_line_skipped = False
			prev_token_id = token_id
			token_objects = set(token_output[token_id].objects.split("+"))
			# Объект был в прошлом токене, но нет в текущем спане.
			# Это значит очередной объект завершился.
			prev_token_classes = list(objects_span_ids.keys())
			for prev_token_class_raw in prev_token_classes:
				prev_token_class, is_begin = Builder.parse_it(prev_token_class_raw)
				if distinguish_object_begin:
					should_split = is_begin or is_new_line
				else:
					should_split = prev_token_class not in token_objects or is_new_line
				if should_split:
					new_object = engine.markup_doc.ObjectInfo(id = self.id_generator.get(),
													type = prev_token_class,
													span_ids = sorted(list(objects_span_ids[prev_token_class])))
					# Иногда нет подходящих спанов для объекта (случай LocOrg+Org)
					# В этом случае пропускаем объект
					if new_object.span_ids:
						result.append(new_object)
					objects_span_ids.pop(prev_token_class)
			# Объект есть в текущем токене, но нет в предыдущем.
			# Это означает начало очередного объекта.
			for current_token_class_raw in token_objects:
				current_token_class, is_begin = Builder.parse_it(current_token_class_raw)
				if current_token_class == "NONE":
					continue
				if current_token_class not in objects_span_ids:
					objects_span_ids[current_token_class] = set()
				# Добавляем id'ники спанов для объектов
				# Иногда есть токены с объектом, но без спана
				# Не добавляем спаны в этом случае
				if token_id in token_to_spans:
					new_span_ids = Builder.get_object_span_ids(current_token_class,
						token_to_spans[token_id])
					objects_span_ids[current_token_class] = set.union(
						objects_span_ids[current_token_class], new_span_ids)
		for last_token_class in objects_span_ids:
			new_object = engine.markup_doc.ObjectInfo(id = self.id_generator.get(),
											type = last_token_class,
											span_ids = sorted(list(objects_span_ids[last_token_class])))
			result.append(new_object)
		return result
	
	def output_document(self, doc_id, doc_token_ids, token_to_spans, doc_objects,
			distinguish_span_begin, distinguish_object_begin):
		doc_info = {
			"info#id": doc_id,
			"info#contest_tokenization": os.path.join(self.get_work_dir(), str(doc_id) + ".tokens")
		}
		document = engine.markup_doc.MarkupDoc(doc_info, True, distinguish_span_begin,
			distinguish_object_begin)
		
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
		with open(os.path.join(self.get_work_dir(), str(doc_id) + ".spans"), "w") as span_file:
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
		with open(os.path.join(self.get_work_dir(), str(doc_id) + ".objects"), "w") as object_file:
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
	
	def build_chunk_markup(self, doc_to_tokens, token_to_output, doc_id_to_token_file):
		distinguish_span_begin = False
		distinguish_object_begin = False
		for doc_id in doc_to_tokens:
			id_to_token = self.read_tokens_file(doc_id)
			token_to_spans = self.extract_doc_spans(distinguish_span_begin, doc_id,
				doc_to_tokens[doc_id], token_to_output, doc_id_to_token_file)
			doc_objects = self.extract_doc_objects(distinguish_span_begin, distinguish_object_begin,
				doc_id, doc_to_tokens[doc_id], token_to_output, token_to_spans, id_to_token, 
				doc_id_to_token_file)
			self.output_document(doc_id, doc_to_tokens[doc_id], token_to_spans, doc_objects,
				distinguish_span_begin, distinguish_object_begin)

def build_markup():
	config = Config(sys.argv[1])
	part_id = int(sys.argv[2])
	builder = Builder(IdGenerator(1000000000 + part_id * 100000000), part_id, config)
	documents_list = DocumentsList(config.get("corpora_base_dir"),
		config.get("corpora_documents_list"))
	doc_id_to_token_file = {}
	for doc_info in documents_list.load():
		doc_id_to_token_file[doc_info["info#id"]] = doc_info["info#tokenization"]
	
	for chunk_id in range(OUTPUT_CHUNKS_COUNT):
		# Читаем файл с парами id токена; имя документа и строим отображение:
		# имя документа -> id токенов
		token_to_doc_file_name = os.path.join(builder.get_work_dir(), 
											"_token_docs_" + str(chunk_id) + ".txt")
		if not os.path.isfile(token_to_doc_file_name):
			break
		doc_to_tokens = Builder.read_token_docs_file(token_to_doc_file_name)
		# Файл с объектами/спанами для токенов. Строим отбражение:
		# id токена -> TokenOutput
		output_file_name = os.path.join(builder.get_work_dir(), 
										"_output_" + str(chunk_id) + ".csv")
		token_to_output = Builder.read_output_file(output_file_name)
		builder.build_chunk_markup(doc_to_tokens, token_to_output, doc_id_to_token_file)

if __name__ == '__main__':
	begin_time = time.time()
	build_markup()
	end_time = time.time()
	print("Working time: " + str(end_time-begin_time))
