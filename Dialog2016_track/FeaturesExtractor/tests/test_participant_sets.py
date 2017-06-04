# -*- coding: utf-8 -*-
from os.path import join
import pytest

from scripts.engine.documents_list import *
from scripts.engine.participant_sets import *

def test_participant_sets_has_output():
	base_dir = "test_participant_sets_data"
	doc_list = DocumentsList(base_dir, "test_participant_sets_data.csv")
	sets = ParticipantSets(doc_list)
	all_names = {"violet_0", "red_22"}
	has_output = { #doc_id -> (name -> yes/no)
		1: {
			"violet_0": False, "red_22": True
		},
		2: {
			"violet_0": True, "red_22": False
		}
	} 
	count = 0
	for doc in doc_list.load():
		for output in sets.participant_outputs(1):
			assert output.name in all_names
			assert has_output[doc["info#id"]][output.name] == output.has_output(doc["info#id"])
			if output.has_output(doc["info#id"]):
				count += 1
	assert count == 2

def compare_first_track_output(expected, actual):
	assert len(expected) == len(actual.found_objects)
	for expected_item,actual_item in zip(expected,actual.found_objects):
		assert expected_item[0] == actual_item.pos
		assert expected_item[1] == actual_item.length
		assert expected_item[2] == actual_item.type

def test_participant_sets_get_track_output():
	expected_output = {
		1: {
			"red_22": [
				(0, 1, "LOCATION"),
				(8, 3, "ORG")
			]
		},
		2: {
			"violet_0": [
				(12, 4, "PERSON")
			]
		}
	}
	base_dir = "test_participant_sets_data"
	doc_list = DocumentsList(base_dir, "test_participant_sets_data.csv")
	sets = ParticipantSets(doc_list)
	for doc in doc_list.load():
		for output in sets.participant_outputs(1):
			if output.has_output(doc["info#id"]):
				compare_first_track_output(expected_output[doc["info#id"]][output.name],
					output.get_track_output(1, doc["info#id"]))
