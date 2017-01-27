# -*- coding: utf-8 -*-

from common_config import BINARY_PATH, MYSTEM_FILE_NAME, WORD2VEC_FEATURES_COUNT
from gensim.models import word2vec
from itertools import chain
from markup_corpus import MarkupCorpus
from mystem_parser import MystemParser
from pandas import DataFrame, options
from participant_sets import ParticipantSets
from word_sets import WordSets

import bisect
import json
import os
import string_set
import subprocess
import sys

class FeaturesExtractor(object):
	def __init__(self):
		# TODO: proper comment + name
		self.is_cached = False
		self.mystem_parser = MystemParser()
	def load_w2v_data(self, binary_data_path):
		self.w2v_model = word2vec.Word2Vec.load_word2vec_format(binary_data_path, binary=True)
	def load_word_sets(self, input_dir):
		self.word_sets = WordSets(input_dir)
	def extract_w2v_features(self, mystem_result, token_text, token_type):
		'''Извлекаем word2vec признаки для некотрого токена.'''
		stub_result = [-1000] * WORD2VEC_FEATURES_COUNT
		if token_type != "Word":
			return stub_result
		else:
			try:
				query = mystem_result[token_text][0]
			except:
				query = token_text + "_S"
			if query in self.w2v_model:
				return self.w2v_model[query]
			return stub_result
	@staticmethod
	def run_mystem(doc_tokens):
		'''Строим мапу текст токена -> 
		(лексема + часть речи, mystem_info)
		'''
		input_fn = "input_" + str(os.getpid()) + ".txt"
		output_fn = "output_" + str(os.getpid()) + ".txt"

		with open(os.path.join(BINARY_PATH, input_fn), "w", encoding='utf8') as input_file:
			for token in doc_tokens:
				input_file.write(token.text + "\n")
		# run mystem
		args = []
		args.append(os.path.join(BINARY_PATH, MYSTEM_FILE_NAME))
		args.append("-nid")
		args.append("--format")
		args.append("json")
		args.append(os.path.join(BINARY_PATH, input_fn))
		args.append(os.path.join(BINARY_PATH, output_fn))
		subprocess.call(args, shell=False)
		# read result
		result = {}
		with open(os.path.join(BINARY_PATH, output_fn), "r", encoding='utf8') as output_file:
			for line in output_file.readlines():
				mystem_result = json.loads(line)
				text = mystem_result["text"]
				if not mystem_result["analysis"]:
					result[text] = (mystem_result["text"] + "_S", "mystem:none")
					continue
				analysis = mystem_result["analysis"][0]["gr"]
				parts = analysis.split(",")
				if text not in result:
					mystem_info = "mystem:none"
					if "гео" in parts:
						mystem_info = "mystem:geo"
					elif "имя" in parts:
						mystem_info = "mystem:name"
					elif "отч" in parts:
						mystem_info = "mystem:patr"
					elif "фам" in parts:
						mystem_info = "mystem:fam"
					part_of_speech = parts[0]
					if part_of_speech.find("=") != -1:
						part_of_speech = part_of_speech[0:part_of_speech.find("=")]
					result[text] = (mystem_result["analysis"][0]["lex"].lower() + "_" 
						+ part_of_speech, mystem_info, analysis)
		# remove files
		os.remove(os.path.join(BINARY_PATH, input_fn))
		os.remove(os.path.join(BINARY_PATH, output_fn))
		return result
	@staticmethod
	def get_capitalization(token_text):
		if len(token_text) == 0:
			return 'empty'
		elif token_text[0].isupper():
			return 'Capital'
		else:
			return 'lower'
	@staticmethod
	def update_data(is_markup_data, init_data, output_collection):
		data_prefix = "!corrected_data_"
		if is_markup_data:
			output_collection.add_set(data_prefix + "token_type", init_data['token_type'][-1])
			output_collection.add_set(data_prefix + "mystem_info", init_data['mystem_info'][-1])
			output_collection.add_set(data_prefix + "part_of_speech", init_data['part_of_speech'][-1])
		else:
			if not output_collection.has_set(data_prefix + "token_type", init_data['token_type'][-1]):
				init_data['token_type'][-1] = "Punctuator:Unknown"
			if not output_collection.has_set(data_prefix + "mystem_info", init_data['mystem_info'][-1]):
				init_data['mystem_info'][-1] = "mystem:none"
			if not output_collection.has_set(data_prefix + "part_of_speech", init_data['part_of_speech'][-1]):
				init_data['part_of_speech'][-1] = "UNKNOWN"
	def create_init_data_frame(self, doc_tokens, participant_outputs, is_markup_data, output_collection):
		'''Создаем и инициализируем DataFrame. 
		Строки - токены, столбцы - признаки
		'''
		init_data = {
			'token_id' : [], 'token_type' : [], 'mystem_info' : [], 'capitalization' : [],
			'part_of_speech': []
		}
		if (is_markup_data):
			init_data['token_text'] = []
			init_data['token_objects'] = []
			init_data['token_span_types'] = []
		for i in range(WORD2VEC_FEATURES_COUNT):
			init_data['word2vec_feature_' + str(i)] = []
		for i in range(self.word_sets.sets_count()):
			init_data['wordsets_feature_' + str(i)] = []
		for i in self.mystem_parser.features_list:
			init_data['grammar_' + str(i)] = []
		# Запускаем mystem для извлечения морфологических признаков.
		# Также используем в word2vec.
		mystem_result = FeaturesExtractor.run_mystem(doc_tokens)
		# Заполняем признаки
		for token in doc_tokens:
			# Добавляем "базовые" признаки
			init_data['token_id'].append(token.id)
			init_data['token_type'].append(token.type)
			init_data['capitalization'].append(FeaturesExtractor.get_capitalization(token.text))
			if (is_markup_data):
				init_data['token_text'].append(token.text)
				init_data['token_objects'].append(token.obj_types.get_all())
				init_data['token_span_types'].append(token.span_types.get_all())
			try:
				init_data['mystem_info'].append(mystem_result[token.text][1])
				init_data['part_of_speech'].append(mystem_result[token.text][0].split("_")[-1])
				grammar_features = self.mystem_parser.parse(mystem_result[token.text][2])
				for i in grammar_features:
					init_data['grammar_' + (i)].append(grammar_features[i])
			except:
				# TODO: дублирование константы убрать
				init_data['mystem_info'].append("mystem:none")
				init_data['part_of_speech'].append("UNKNOWN")
				for i in self.mystem_parser.features_list:
					init_data['grammar_' + str(i)].append("undefined")
			FeaturesExtractor.update_data(is_markup_data, init_data, output_collection)
			# Добавляем w2v признаки
			w2v_features = self.extract_w2v_features(mystem_result, token.text, token.type)
			assert len(w2v_features) == WORD2VEC_FEATURES_COUNT
			for i in range(WORD2VEC_FEATURES_COUNT):
				init_data['word2vec_feature_' + str(i)].append(w2v_features[i])
			# Добавляем word_sets признаки
			word_sets_features = self.word_sets.get_word_info(token.text)
			assert len(word_sets_features) == self.word_sets.sets_count()
			for i in range(self.word_sets.sets_count()):
				init_data['wordsets_feature_' + str(i)].append(word_sets_features[i])
		for participant in participant_outputs:
			init_data[FeaturesExtractor.get_participant_col_name(participant.name)] = []
			for i in range(len(doc_tokens)):
				init_data[FeaturesExtractor.get_participant_col_name(participant.name)].append(
					string_set.StringSet())
		return init_data
	@staticmethod
	def shift(l, n):
		'''http://stackoverflow.com/questions/2150108/efficient-way-to-shift-a-list-in-python'''
		return l[n:] + l[:n]
	@staticmethod
	def prepare_for_output(result_data, is_markup_data, output_collection):
		'''Заменяем объекты StringSet на строковые представления.
		Перед заменой добавляем контекст для токенов.
		'''
		# Добавляем контекстные признаки без w2v'ка. 
		context_range = 2
		data_with_context = {}
		for i in chain(range(-context_range, 0), range(1, context_range + 1)):
			if i < 0:
				context_col_prefix = "prev_" + str(-i) + "_"
			else:
				context_col_prefix = "next_" + str(i) + "_"
			for col_name in filter(lambda x: x.find("word2vec_feature_") == -1, 
			result_data):
				# Убираем из контекста правильные объекты
				if col_name in {"token_objects", "token_id", "token_text", "token_span_types"}:
					continue
				data_with_context[context_col_prefix + col_name] = result_data[col_name]
				data_with_context[context_col_prefix + col_name] = FeaturesExtractor.shift(
					data_with_context[context_col_prefix + col_name], i)
		result_data.update(data_with_context)
		# Преобразуем в финальный вид.
		data = DataFrame.from_dict(result_data)
		for col_name in data.columns:
			colomn_values = data[col_name]
			is_checked = False
			updated_values = []
			for value in colomn_values:
				if not is_checked:
					if isinstance(value, string_set.StringSet):
						is_checked = True
					else:
						break
				''' Иногда возможные варианты ответа при построении признаков
				для большого корпуса могут не совпадать с вариантами из
				размеченного. R воспринимает признаки как factor-value.
				И мы получим ошибку на неизвестное значение признака.
				Поэтому мы собираем возможные ответы для размеченного корпуса. 
				А для большого корпуса оставляем либо известный ответ, либо
				находим максимально близкий из возможных ответов.
				'''
				str_value = value.get_all()
				if is_markup_data:
					output_collection.add_set(col_name, str_value)
				else:
					if not output_collection.has_set(col_name, str_value):
						# TODO: statistics?
						str_value = output_collection.find_closest_set(col_name, str_value)
				updated_values.append(str_value)
			if updated_values:
				data[col_name] = updated_values
				continue
		return data
	@staticmethod
	def get_participant_col_name(participant_name):
		'''Получаем имя столбца DataFramе 
		для результатов одного из участников.
		'''
		result = str(participant_name)
		dot_pos = participant_name.find('.')
		if dot_pos != -1:
			result = result[0:dot_pos]
		return result + "_result"
	def exract_markup_data_track1(self, markup_dir, participants_dir, output_file_name, data_type, 
								output_collection):
		'''Извлекаем данные для размеченного корпуса (дорожка 1).'''
		# Загружаем результаты участников для размеченного корпуса
		sets = ParticipantSets(participants_dir)
		dev_sets = sets.getTypedSets(data_type)
		# Загружаем объекты ParticipantOutput только один раз, 
		# так как работа с файловой системой медленная
		participant_outputs = []
		for devSet in dev_sets:
			participant_outputs.append(devSet)
		# Загружаем сам корпус
		corpus = MarkupCorpus(markup_dir)
		has_header = True # добавляем ли заголовок 
		for doc in corpus:
			# Копируем информацию о токенах документа
			doc_tokens = list(doc.tokens.values())
			tokens_start_pos = list(map(lambda x: x.pos, doc_tokens))
			doc_tokens.sort(key = lambda x: x.pos)
			tokens_start_pos.sort()
			# Создаем DataFrame
			result_data = self.create_init_data_frame(doc_tokens, participant_outputs, True, output_collection)
			# Итерируем участников и навешиваем объекты на токены
			for participant in participant_outputs:
				column_name = FeaturesExtractor.get_participant_col_name(participant.name)
				if participant.has_output(doc.file_name, track_id = 1):
					found_objects = participant.get_track_output(doc.file_name, 
						track_id = 1).getfound_objects()
					for obj in found_objects:
						token_id = bisect.bisect_left(tokens_start_pos, obj.pos)
						while (
								token_id < len(doc_tokens) and 
								obj.pos + obj.length >= doc_tokens[token_id].pos
							):
							# Проверяем пересечение границ токенов
							if (max(obj.pos, doc_tokens[token_id].pos) < 
								min(obj.pos + obj.length, doc_tokens[token_id].pos 
								+ doc_tokens[token_id].length)):
								result_data[column_name][token_id].add_string(obj.type)
							token_id += 1
				else:
					for value in result_data[column_name]:
						value.add_string('UNKNOWN')
			# Выводим данные
			output_data = FeaturesExtractor.prepare_for_output(result_data, True, output_collection)
			with open(output_file_name, 'a', encoding='utf8') as output_file:
				output_file.write(output_data.to_csv(index = False, header = has_header))
			has_header = False
	def exract_data_track1(self, corpus, doc_names, participants_dir, output_file_name, 
						output_collection):
		'''Извлекаем данные для неразмеченного корпуса (дорожка 1).'''
		# TODO: УБРАТЬ COPY-PAST!!!!!!!!!!!!!
		# Загружаем результаты участников для размеченного корпуса
		if not self.is_cached:
			self.sets = ParticipantSets(participants_dir)
			#self.dev_sets = self.sets.getTypedSets("") # TODO: filter improve
			self.dev_sets = self.sets.getTypedSets("learnset") # TODO: filter improve
			#self.dev_sets = self.sets.getTypedSets("ctrlset") # TODO: filter improve
			# Загружаем объекты ParticipantOutput только один раз, 
			# так как работа с файловой системой медленная
			self.participant_outputs = []
			for devSet in self.dev_sets:
				self.participant_outputs.append(devSet)
			self.is_cached = True
		has_header = True # добавляем ли заголовок 
		for doc in doc_names:
			# Копируем информацию о токенах документа
			try:
				doc_tokens = list(corpus.get_document_info(doc).tokens.values())
			except:
				continue
			tokens_start_pos = list(map(lambda x: x.pos, doc_tokens))
			doc_tokens.sort(key = lambda x: x.pos)
			tokens_start_pos.sort()
			# Создаем DataFrame
			result_data = self.create_init_data_frame(doc_tokens, self.participant_outputs, False, output_collection)
			# Итерируем участников и навешиваем объекты на токены
			for participant in self.participant_outputs:
				column_name = FeaturesExtractor.get_participant_col_name(participant.name)
				if participant.has_output(doc, track_id = 1):
					found_objects = participant.get_track_output(doc, 
						track_id = 1).getfound_objects()
					for obj in found_objects:
						token_id = bisect.bisect_left(tokens_start_pos, obj.pos)
						while (
								token_id < len(doc_tokens) and 
								obj.pos + obj.length >= doc_tokens[token_id].pos
							):
							# Проверяем пересечение границ токенов
							if (max(obj.pos, doc_tokens[token_id].pos) < 
								min(obj.pos + obj.length, doc_tokens[token_id].pos 
								+ doc_tokens[token_id].length)):
								result_data[column_name][token_id].add_string(obj.type)
							token_id += 1
				else:
					for value in result_data[column_name]:
						value.add_string('UNKNOWN')
			# Выводим данные
			output_data = FeaturesExtractor.prepare_for_output(result_data, False, output_collection)
			with open(output_file_name, 'a', encoding='utf8') as output_file:
				output_file.write(output_data.to_csv(index = False, header = has_header))
			has_header = False
