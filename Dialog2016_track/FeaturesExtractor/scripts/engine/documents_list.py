# -*- coding: utf-8 -*-
''' Список документов с разметкой/результатами участников. В качестве входных данных у нас:
-Путь к базовому каталогу, относительно которого мы указываем пути к файлам.
-csv-файл в котором хранится информация о документах. Строки - документы, столбцы:
	Id документа (info#id)
	Путь к тексту документа (info#text)
	Путь к файлу с токенизацией в формате соревнования (info#contest_tokenization)
	Путь к файлу с токенизацией, где в каждой строке текст одного токена (info#tokenization)
	Путь к файлу со спанами (info#spans)
	Путь к файлу с объектами (info#objects)
	Пути к файлам с ответами участников (answer[номер дорожки]#[имя_участника], например answer1#violet0)
В качестве ответа участника может быть пустая строка, что означает отсутствие ответа.
'''

import csv
import os

import tools.csv_reader

class DocumentsList(object):
	def __init__(self, base_dir, list_file_path):
		assert os.path.isdir(base_dir)
		self.base_dir = base_dir
		self.csv_data = tools.csv_reader.CsvReader(list_file_path)
	def load(self):
		for row in self.csv_data.load_rows():
			DocumentsList.verify_row(row)
			for column_name in row:
				if column_name == 'info#id':
					row[column_name] = int(row[column_name])
					continue
				if row[column_name] == "":
					continue
				data_file_path = os.path.join(self.base_dir, row[column_name])
				assert os.path.isfile(data_file_path)
				row[column_name] = data_file_path
			yield row
	@staticmethod
	def verify_row(row):
		for column_name in row:
			name_parts = column_name.split("#")
			assert len(name_parts) == 2
			assert name_parts[0] in {'info', 'answer1'}
			if name_parts[0]=='info':
				assert name_parts[1] in {'id', 'text', 'contest_tokenization', 'tokenization', 
					'spans', 'objects'}
		assert 'info#id' in row.keys()
		assert 'info#text' in row.keys()
		assert 'info#contest_tokenization' in row.keys() or 'info#tokenization' in row.keys()
		# TODO: тут можно еще другие инварианты проверить
