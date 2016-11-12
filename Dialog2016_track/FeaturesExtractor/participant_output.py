# -*- coding: utf-8 -*-

from first_track_output import FirstTrackOutput

import os

class ParticipantOutput(object):
	def __init__(self, output_dir, name):
		self.output_dir = output_dir
		self.name = name
		# Участники сдавали в разных форматах. 
		# Часто результаты лежат во внутренних папках.
		while True:
			dir_content = os.listdir(self.output_dir)
			# Если внтури есть файлы (не каталоги), то останавливаемся.
			need_stop = False
			for file_name in dir_content:
				if not os.path.isdir(os.path.join(self.output_dir, file_name)):
					need_stop = True
					break
			if need_stop:
				self.dir_content = set(map(lambda x: os.path.join(self.output_dir, x), 
					dir_content))
				break
			# Если внутри есть каталоги, то только один. 
			# Иначе не знаем куда спускаться.
			# В исходных данных странные исключения, фильтруем их.
			if (len(list(dir_content)) > 1):
				dir_content = list(filter(
					lambda x: x.upper() not in {"__MACOSX", "VIOLET_0.TESTSET"}, 
					dir_content))
			assert len(dir_content) == 1
			self.output_dir = os.path.join(self.output_dir, dir_content[0])
	def get_output_file_name(self, file_name, track_id):
		'''Формируем имя файла с результатами для пары:
		(файл, номер_дорожки).
		'''
		return os.path.join(self.output_dir, file_name) + ".task" + str(track_id)
	def has_output(self, file_name, track_id):
		'''Проверяем наличие результата для пары:
		(файл, номер_дорожки).
		'''
		return self.get_output_file_name(file_name, track_id) in self.dir_content
	def get_track_output(self, file_name, track_id):
		'''Получаем результат участника для пары:
		(файл, номер_дорожки).
		'''
		assert track_id in (1,2,3) # Нам нужны только дорожки 1,2,3
		# Временное ограничение, пока нас интересует только дорожка 1
		assert track_id == 1 
		if (track_id == 1):
			return FirstTrackOutput(self.get_output_file_name(file_name, track_id))
