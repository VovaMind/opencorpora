# -*- coding: utf-8 -*-
from os.path import join
import pytest

from scripts.engine.documents_list import *
from scripts.engine.full_corpus import *
from scripts.engine.markup_doc import *
from scripts.engine.tools.id_generator import *

def test_correct_full_corpus():
	IdGenerator.current_id = 0
	base_dir = "test_full_corpus_data"
	doc_list = DocumentsList(base_dir, "test_full_corpus_data.csv")
	corpus = FullCorpus(doc_list, 2, 1, 0, IdGenerator())
	expected_docs = [[11, 22], [33]]
	expected_info = [
		{
			"info#id": 11,
			"info#text": join(base_dir, "doc1.txt"),
			"info#tokenization": join(base_dir, "doc1.tokens")
		},
		{
			"info#id": 22,
			"info#text": join(base_dir, "doc2.txt"),
			"info#tokenization": join(base_dir, "doc2.tokens")
		},
		{
			"info#id": 33,
			"info#text": join(base_dir, "doc3.txt"),
			"info#tokenization": join(base_dir, "doc3.tokens")
		}
	]
	expected_info_id = 0
	expected_doc_tokens = [
		{
			1: TokenInfo(1, 0, 4, "abba"),
			2: TokenInfo(2, 5, 2, "ba"),
			3: TokenInfo(3, 8, 1, "a")
		},
		{
			4: TokenInfo(4, 0, 6, "qwerty")
		},
		{
			5: TokenInfo(5, 0, 1, "a"),
			6: TokenInfo(6, 2, 1, "b"),
			7: TokenInfo(7, 4, 2, "cc")
		},
	]
	expected_doc_tokens_id = 0
	for expected, docs in zip(expected_docs, corpus.document_chunks()):
		assert expected == docs
		for doc in docs:
			info = corpus.get_document_info(doc)
			assert expected_info[expected_info_id] == info
			expected_info_id += 1
			document = corpus.get_document(doc)
			assert len(expected_doc_tokens[expected_doc_tokens_id]) == len(document.tokens)
			for id in document.tokens:
				assert expected_doc_tokens[expected_doc_tokens_id][id].id == document.tokens[id].id
				assert expected_doc_tokens[expected_doc_tokens_id][id].pos == document.tokens[id].pos
				assert expected_doc_tokens[expected_doc_tokens_id][id].length == document.tokens[id].length
				assert expected_doc_tokens[expected_doc_tokens_id][id].text == document.tokens[id].text
			expected_doc_tokens_id += 1
		corpus.clear_documents_cache()
