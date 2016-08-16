# -*- coding: utf-8 -*-

import bisect
import json
import os
import string_set
import subprocess
import sys
from gensim.models import word2vec
from markup_corpus import MarkupCorpus
from pandas import DataFrame, options
from participant_sets import ParticipantSets

WORD2VEC_FEATURES_COUNT = 1000

class FeaturesExtractor(object):
	def load_w2v_data(self, binary_data_path):
		self.w2v_model = word2vec.Word2Vec.load_word2vec_format(binary_data_path, binary=True)
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
		bin_path = "..\\bin"
		with open(os.path.join(bin_path, "input.txt"), "w", encoding='utf8') as input_file:
			for token in doc_tokens:
				input_file.write(token.text + "\n")
		# run mystem
		args = os.path.join(bin_path, "mystem.exe")
		args += (
			" -nid --format json " + os.path.join(bin_path, "input.txt") + " " 
			+ os.path.join(bin_path, "output.txt")
		)
		subprocess.call(args, shell=False)
		# read result
		result = {}
		with open(os.path.join(bin_path, "output.txt"), "r", encoding='utf8') as output_file:
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
						+ part_of_speech, mystem_info)
		# remove files
		os.remove(os.path.join(bin_path, "input.txt"))
		os.remove(os.path.join(bin_path, "output.txt"))
		return result
	def create_init_data_frame(self, doc_tokens, participant_outputs):
		'''Создаем и инициализируем DataFrame. 
		Строки - токены, столбцы - признаки
		'''
		init_data = {
			'token_id' : [], 'token_text' : [], 'token_objects' : [], 'token_type' : [],
			'token_span_types' : [], 'mystem_info' : []
		}
		for i in range(WORD2VEC_FEATURES_COUNT):
			init_data['word2vec_feature_' + str(i)] = []
		# Запускаем mystem для извлечения морфологических признаков.
		# Также используем в word2vec.
		mystem_result = FeaturesExtractor.run_mystem(doc_tokens)
		# Заполняем признаки
		for token in doc_tokens:
			# Добавляем "базовые" признаки
			init_data['token_id'].append(token.id)
			init_data['token_text'].append(token.text)
			init_data['token_objects'].append(token.obj_types.get_all())
			init_data['token_type'].append(token.type)
			init_data['token_span_types'].append(token.span_types.get_all())
			try:
				init_data['mystem_info'].append(mystem_result[token.text][1])
			except:
				# TODO: дублирование константы убрать
				init_data['mystem_info'].append("mystem:none")
			# Добавляем w2v признаки
			w2v_features = self.extract_w2v_features(mystem_result, token.text, token.type)
			assert len(w2v_features) == WORD2VEC_FEATURES_COUNT
			for i in range(WORD2VEC_FEATURES_COUNT):
				init_data['word2vec_feature_' + str(i)].append(w2v_features[i])
		for participant in participant_outputs:
			init_data[FeaturesExtractor.get_participant_col_name(participant.name)] = []
			for i in range(len(doc_tokens)):
				init_data[FeaturesExtractor.get_participant_col_name(participant.name)].append(
					string_set.StringSet())
		return init_data
	@staticmethod
	def prepare_for_output(result_data):
		'''Заменяем объекты StringSet на строковые представления.'''
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
				updated_values.append(value.get_all())
			if updated_values:
				data[col_name] = updated_values
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
	def exract_markup_data_track1(self, markup_dir, participants_dir, output_file_name):
		'''Извлекаем данные для размеченного корпуса (дорожка 1).'''
		# Загружаем результаты участников для размеченного корпуса
		sets = ParticipantSets(participants_dir)
		dev_sets = sets.getTypedSets("dev")
		# Загружаем объекты ParticipantOutput только один раз, 
		# так как работа с файловой системой медленная
		participant_outputs = []
		for devSet in dev_sets:
			participant_outputs.append(devSet)
		# Загружаем сам корпус
		corpus = MarkupCorpus(markup_dir)
		has_header = True # добавляем ли заголовок 
		for doc in corpus:
			print(doc.file_name)
			# Копируем информацию о токенах документа
			doc_tokens = list(doc.tokens.values())
			tokens_start_pos = list(map(lambda x: x.pos, doc_tokens))
			doc_tokens.sort(key = lambda x: x.pos)
			tokens_start_pos.sort()
			# Создаем DataFrame
			result_data = self.create_init_data_frame(doc_tokens, participant_outputs)
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
			output_data = FeaturesExtractor.prepare_for_output(result_data)
			with open(output_file_name, 'a', encoding='utf8') as output_file:
				output_file.write(output_data.to_csv(index = False, header = has_header))
			has_header = False
