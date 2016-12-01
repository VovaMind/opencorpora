# -*- coding: utf-8 -*-
''' main-файл для извлечения признаков '''

from common_config import GET_CORPORA_FEATURES_PARAMS
from shutil import copyfile

import features_extractor
import full_corpus
import id_generator
import os
import sets_collection
import shutil
import sys
import time

current_output_file_id = 0

def get_output_dir_path(part_id):
	return os.path.join(GET_CORPORA_FEATURES_PARAMS["output_dir"], str(part_id))
	
def init_dir(part_id):
	output_dir_path = get_output_dir_path(part_id)
	if not os.path.exists(output_dir_path):
		os.makedirs(output_dir_path)

def get_output_file_names(part_id):
	global current_output_file_id
	print("Current file id: " + str(current_output_file_id))
	if current_output_file_id == 0:
		init_dir(part_id)
	temp = current_output_file_id
	current_output_file_id += 1
	output_dir_path = get_output_dir_path(part_id)
	return (os.path.join(output_dir_path, "_features_" + str(temp) + ".csv"),
			os.path.join(output_dir_path, "_token_docs_" + str(temp) + ".txt"))

def extract_features():
	# TODO: comment
	part_id = int(sys.argv[1])
	id_generator.IdGenerator.current_id = 100000000 * part_id
	corpus = full_corpus.FullCorpus(GET_CORPORA_FEATURES_PARAMS["input_dir"], part_id)
	extractor = features_extractor.FeaturesExtractor()
	extractor.load_w2v_data(GET_CORPORA_FEATURES_PARAMS["w2v_model_file"])
	output_collection = sets_collection.SetsCollection()
	output_collection.load(GET_CORPORA_FEATURES_PARAMS["sets_dump_file"])
	while True:
		docs = corpus.get_documents_chunk()
		if not docs:
			break
		output_file_names = get_output_file_names(part_id)
		# Save tokens and token->doc map.
		is_first_doc = True
		for doc in docs:
			# Сохраняем для документа его исходный текст
			source_doc_path = os.path.join(GET_CORPORA_FEATURES_PARAMS["input_dir"], doc + ".txt")
			target_doc_path = os.path.join(get_output_dir_path(part_id), doc + ".txt")
			copyfile(source_doc_path, target_doc_path)
			try:
				doc_tokens = list(corpus.get_document_info(doc).tokens.values())
			except:
				print("Bad document name: " + doc)
				continue
			doc_tokens.sort(key = lambda x: x.pos)
			with open(os.path.join(get_output_dir_path(part_id), doc + ".tokens"), "w", 
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
			with open(output_file_names[1], file_mode, encoding="utf-8") as token_doc_file:
				for token  in doc_tokens:
					token_doc_file.write(str(token.id) + " ")
					token_doc_file.write(doc + "\n")
		extractor.exract_data_track1(corpus, docs, 
									GET_CORPORA_FEATURES_PARAMS["participants_dir"], 
									output_file_names[0],
									output_collection)
		corpus.clear_documents_cache()

if __name__ == '__main__':
	begin_time = time.time()
	extract_features()
	end_time = time.time()
	print(id_generator.IdGenerator.get())
	print("Working time: " + str(end_time-begin_time))
