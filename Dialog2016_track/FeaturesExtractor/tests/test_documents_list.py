# -*- coding: utf-8 -*-
from os.path import join
import pytest

from scripts.engine.documents_list import *

def test_correct_read():
	base_dir = "test_documents_list_data"
	doc_list = DocumentsList(base_dir, "test_documents_list_data.csv")
	expected_result = [
		{
			'info#id': 12, 
			'info#text': join(base_dir, '1.txt'), 
			'info#contest_tokenization': join(base_dir, '22.rtf'),
			'answer1#violet0': join(base_dir, '44.txt')
		},
		{
			'info#id': 15, 
			'info#text': join(base_dir, '22.rtf'), 
			'info#contest_tokenization': "",
			'answer1#violet0': join(base_dir, '1.txt')
		},
		{'failure': 'failure'} # Если сравниваем с этим элементом, то что-то пошло не так
	]

	index = 0
	for expected, doc_info in zip(expected_result, doc_list.load()):
		assert expected == doc_info
		index += 1
	# Проверяем, что мы проитерировали все документы
	assert index == len(expected_result) - 1

def test_incorrect_names():
	base_dir = "test_documents_list_data"
	doc_list = DocumentsList(base_dir, "test_documents_list_data2.csv")
	with pytest.raises(AssertionError):
		for doc_info in doc_list.load():
			pass

def test_incorrect_file_path():
	base_dir = "test_documents_list_data"
	doc_list = DocumentsList(base_dir, "test_documents_list_data3.csv")
	with pytest.raises(AssertionError):
		for doc_info in doc_list.load():
			pass
