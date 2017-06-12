# -*- coding: utf-8 -*-
''' main-файл для извлечения признаков '''

from engine.documents_list import DocumentsList
from engine.features_extractor import FeaturesExtractor
from engine.markup_corpus import MarkupCorpus
from engine.tools.config import Config
from engine.tools.sets_collection import SetsCollection

import os
import sys
import time

def extract_features():
	config = Config(sys.argv[1])
	documents_list = DocumentsList(config.get("base_dir"), config.get("documents_list"))
	corpus = MarkupCorpus(documents_list)
	
	extractor = FeaturesExtractor()
	extractor.load_w2v_data(config.get("w2v_file_name"))
	extractor.load_word_sets(config.get("words_set_dir"))
	extractor.set_mystem_file_name(config.get("mystem_file_name"))
	
	output_collection = SetsCollection()
	extractor.exract_markup_data_track1(documents_list, config.get("testset_features_file"),
		output_collection)
	output_collection.save(config.get("sets_collection_file"))

if __name__ == '__main__':
	begin_time = time.time()
	extract_features()
	end_time = time.time()
	print("Working time: " + str(end_time-begin_time))
