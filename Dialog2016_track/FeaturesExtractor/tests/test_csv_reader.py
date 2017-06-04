from os.path import join
import pytest

from scripts.engine.tools.csv_reader import *

def test_correct_csv_read():
	csv_data = CsvReader("test_csv_reader_data.csv")
	expected_result = [
		{'info#id': 'a.txt', 'info#text': '44.txt', 'info#objects': '55.txt'},
		{'info#id': '5.ggg', 'info#text': 'a.xx', 'info#objects': 'qdgf.ttt'},
		{'failure': 'failure'} # Если сравниваем с этим элементом, то что-то пошло не так
	]
	index = 0
	for expected_row, csv_row in zip(expected_result, csv_data.load_rows()):
		assert expected_row == csv_row
		index += 1
	# Проверяем, что мы проитерировали все документы
	assert index == len(expected_result) - 1

def test_bad_csv_read():
	csv_data = CsvReader("test_csv_reader_data2.csv")
	with pytest.raises(AssertionError):
		for csv_row in csv_data.load_rows():
			pass
