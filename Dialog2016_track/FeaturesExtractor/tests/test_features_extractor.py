# -*- coding: utf-8 -*-
from os.path import join
from scripts.engine.documents_list import *
from scripts.engine.features_extractor import *
from scripts.engine.full_corpus import *
from scripts.engine.tools.id_generator import *
from scripts.engine.tools.sets_collection import *

import filecmp
import os
import pytest

def create_features_extraxtor(base_dir):
	extractror = FeaturesExtractor()
	extractror.load_w2v_data("news_win20.model.bin")
	extractror.load_word_sets(join(base_dir, "word_sets"))
	extractror.set_mystem_file_name("mystem.exe")
	return extractror

def expect_equal_collections(expected, actual):
	assert len(expected.labeled_sets) == len(actual.labeled_sets)
	for key in expected.labeled_sets:
		assert expected.labeled_sets[key] == actual.labeled_sets[key]

def test_markup_data_extractor():
	base_dir = "test_features_extractor_data"
	markup_doc_list = DocumentsList(base_dir, "test_features_extractor_data.csv")
	extractror = create_features_extraxtor(base_dir)
	output_file = "actual_features.csv"
	if os.path.isfile(output_file):
		os.remove(output_file)
	output_collection = SetsCollection()
	
	extractror.exract_markup_data_track1(markup_doc_list, output_file, output_collection)
	
	expected_output_collection = SetsCollection()
	expected_output_collection.load(join(base_dir, "sets_collection.dump"))
	expect_equal_collections(expected_output_collection, output_collection)
	assert filecmp.cmp(output_file, join(base_dir, "expected1.csv"))
	os.remove(output_file)

def test_full_corpora_extractor():
	base_dir = "test_features_extractor_data"
	corpora_doc_list = DocumentsList(base_dir, "test_features_extractor_data2.csv")
	corpora_doc_list2 = DocumentsList(base_dir, "test_features_extractor_data2.csv")
	corpus = FullCorpus(corpora_doc_list, 3, 1, 0, IdGenerator())
	extractror = create_features_extraxtor(base_dir)
	output_file = "actual_features2.csv"
	if os.path.isfile(output_file):
		os.remove(output_file)
	output_collection = SetsCollection()
	output_collection.load(join(base_dir, "sets_collection.dump"))
	
	for doc_ids in corpus.document_chunks():
		extractror.exract_data_track1(corpus, doc_ids, corpora_doc_list2, output_file,
			output_collection)
	
	assert filecmp.cmp(output_file, join(base_dir, "expected2.csv"))
	os.remove(output_file)
