# -*- coding: utf-8 -*-
""" Тест рассчитан на неразличение начала/середины спанов и объектов. """
from os.path import join
import pytest

from scripts.engine.documents_list import *
from scripts.engine.markup_corpus import *
from scripts.engine.markup_doc import *

def compare_tokens(tokens1, tokens2):
	assert len(tokens1) == len(tokens2)
	for id in tokens1:
		assert tokens1[id].id == tokens2[id].id
		assert tokens1[id].pos == tokens2[id].pos
		assert tokens1[id].length == tokens2[id].length
		assert tokens1[id].text == tokens2[id].text

def compare_spans(spans1, spans2):
	assert len(spans1) == len(spans2)
	for id in spans1:
		assert spans1[id].id == spans2[id].id
		assert spans1[id].type == spans2[id].type
		assert spans1[id].text_pos == spans2[id].text_pos
		assert spans1[id].text_length == spans2[id].text_length
		assert spans1[id].token_pos == spans2[id].token_pos
		assert spans1[id].token_length == spans2[id].token_length

def compare_objects(objects1, objects2):
	assert len(objects1) == len(objects2)
	for id in objects1:
		assert objects1[id].id == objects2[id].id
		assert objects1[id].type == objects2[id].type
		assert objects1[id].span_ids == objects2[id].span_ids

def compare_hanged(hanged, tokens):
	assert len(hanged) == len(tokens)
	for id in hanged:
		assert hanged[id][0] == tokens[id].span_types.get_all()
		assert hanged[id][1] == tokens[id].obj_types.get_all()

def test_correct_markup_corpus():
	base_dir = "test_markup_corpus_data"
	doc_list = DocumentsList(base_dir, "test_markup_corpus_data.csv")
	markup_corpus = MarkupCorpus(doc_list)
	expected_doc_ids = [1,2]
	expected_docs = {
		1: {
			"tokens": {
				100: TokenInfo(100, 0, 1, "a"),
				101: TokenInfo(101, 2, 2, "bc"),
				102: TokenInfo(102, 5, 2, "df"),
				103: TokenInfo(103, 8, 3, "eee")
			},
			"spans": {
				104: SpanInfo("loc_name", 104, 0, 1, 100, 1),
				105: SpanInfo("loc_descr", 105, 2, 2, 101, 1),
				106: SpanInfo("name", 106, 8, 3, 103, 1)
			},
			"objects": {
				107: ObjectInfo(107, "Location", [104, 105]),
				108: ObjectInfo(108, "Person", [106])
			},
			"hanged": {
				100: ["loc_name", "Location"],
				101: ["loc_descr", "Location"],
				102: ["NONE", "NONE"],
				103: ["name", "Person"]
			}
		},
		2: {
			"tokens": {
				110: TokenInfo(110, 0, 4, "zzzz"),
				111: TokenInfo(111, 5, 2, "xy"),
				112: TokenInfo(112, 8, 3, "qqq"),
				113: TokenInfo(113, 12, 4, "pope")
			},
			"spans": {
				114: SpanInfo("surname", 114, 0, 4, 110, 1),
				115: SpanInfo("org_name", 115, 8, 8, 112, 2)
			},
			"objects": {
				116: ObjectInfo(116, "Person", [114]),
				117: ObjectInfo(117, "Org", [115])
			},
			"hanged": {
				110: ["surname", "Person"],
				111: ["NONE", "NONE"],
				112: ["org_name", "Org"],
				113: ["org_name", "Org"]
			}
		}
	}
	doc_id_index = 0
	for doc in markup_corpus.load_documents():
		assert expected_doc_ids[doc_id_index] == doc.document_id
		compare_tokens(expected_docs[doc.document_id]["tokens"], doc.tokens)
		compare_spans(expected_docs[doc.document_id]["spans"], doc.spans)
		compare_objects(expected_docs[doc.document_id]["objects"], doc.objects)
		compare_hanged(expected_docs[doc.document_id]["hanged"], doc.tokens)
		doc_id_index += 1
	assert len(expected_doc_ids) == doc_id_index
