# -*- coding: utf-8 -*-
''' main-файл для извлечения признаков '''

from engine.documents_list import DocumentsList
from engine.features_extractor import FeaturesExtractor
from engine.full_corpus import FullCorpus
from engine.tools.config import Config
from engine.tools.id_generator import IdGenerator
from engine.tools.sets_collection import SetsCollection
from shutil import copyfile

import os
import shutil
import sys
import time

class Helper(object):
	def __init__(self, config):
		self.current_output_file_id = 0
		self.config = config
	
	def get_output_dir_path(self, part_id):
		return os.path.join(self.config.get("output_dir"), str(part_id))
	
	def init_dir(self, part_id):
		output_dir_path = self.get_output_dir_path(part_id)
		if not os.path.exists(output_dir_path):
			os.makedirs(output_dir_path)
	
	def get_output_file_names(self, part_id):
		print("Current file id: " + str(self.current_output_file_id))
		if self.current_output_file_id == 0:
			self.init_dir(part_id)
		temp = self.current_output_file_id
		self.current_output_file_id += 1
		output_dir_path = self.get_output_dir_path(part_id)
		return (os.path.join(output_dir_path, "_features_" + str(temp) + ".csv"),
				os.path.join(output_dir_path, "_token_docs_" + str(temp) + ".txt"))

def saveDocsInfo(part_id, helper, corpus, doc_ids, token_doc_file_name, doc_id_to_text):
	""" Сохраняем токены и отборажение токен->документ. """
	is_first_doc = True
	for doc_id in doc_ids:
		# Сохраняем для документа его исходный текст
		source_doc_path = os.path.join(doc_id_to_text[doc_id])
		target_doc_path = os.path.join(helper.get_output_dir_path(part_id), str(doc_id) + ".txt")
		copyfile(source_doc_path, target_doc_path)
		try:
			doc_tokens = list(corpus.get_document(doc_id).tokens.values())
		except:
			print("Bad document id: " + str(doc_id))
			continue
		doc_tokens.sort(key = lambda x: x.pos)
		with open(os.path.join(helper.get_output_dir_path(part_id), str(doc_id) + ".tokens"), "w",
				encoding="utf-8") as token_file:
			for token  in doc_tokens:
				token_file.write(str(token.id) + " ")
				token_file.write(str(token.pos) + " ")
				token_file.write(str(token.length) + " ")
				token_file.write(str(token.text) + "\n")
		file_mode = "w"
		if is_first_doc:
			is_first_doc = False
		else:
			file_mode = "a"
		with open(token_doc_file_name, file_mode, encoding="utf-8") as token_doc_file:
			for token  in doc_tokens:
				token_doc_file.write(str(token.id) + " ")
				token_doc_file.write(str(doc_id) + "\n")

def extract_features():
	config = Config(sys.argv[1])
	helper = Helper(config)
	part_id = int(sys.argv[2])
	
	documents_list = DocumentsList(config.get("corpora_base_dir"),
		config.get("corpora_documents_list"))
	documents_list2 = DocumentsList(config.get("corpora_base_dir"),
		config.get("corpora_documents_list"))
	
	doc_id_to_text = {}
	for doc_info in documents_list.load():
		doc_id_to_text[doc_info["info#id"]] = doc_info["info#text"]
	
	corpus = FullCorpus(documents_list, config.get("corpora_chunk_size"),
		config.get("corpora_parts_count"), part_id, IdGenerator(100000000 * part_id))
	
	extractor = FeaturesExtractor()
	extractor.load_w2v_data(config.get("w2v_file_name"))
	extractor.load_word_sets(config.get("words_set_dir"))
	extractor.set_mystem_file_name(config.get("mystem_file_name"))
	
	output_collection = SetsCollection()
	output_collection.load(config.get("sets_collection_file"))
	
	for doc_ids in corpus.document_chunks():
		output_file_names = helper.get_output_file_names(part_id)
		saveDocsInfo(part_id, helper, corpus, doc_ids, output_file_names[1], doc_id_to_text)
		extractor.exract_data_track1(corpus, doc_ids, documents_list2, output_file_names[0],
			output_collection)
		corpus.clear_documents_cache()

if __name__ == '__main__':
	print(123)
	begin_time = time.time()
	extract_features()
	end_time = time.time()
	print("Working time: " + str(end_time-begin_time))
