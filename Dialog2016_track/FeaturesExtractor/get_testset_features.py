# -*- coding: utf-8 -*-
''' main-файл для извлечения признаков '''

import features_extractor
import time
import sets_collection

def extract_features():
	'''Извлекаем признаки.'''
	extractor = features_extractor.FeaturesExtractor()
	extractor.load_w2v_data(
		r"C:\development\OpenCorpora\FactExtAutoAssesst\data\news_win20.model.bin"
	)
	# Путь к ручной разметке
	markup_dir = (
		r"C:\development\OpenCorpora\FactExtAutoAssesst\data"
		r"\factRuEval-2016-master\factRuEval-2016-master\testset"
	)
	# Путь к результатам от участников
	participants_dir = r"C:\development\OpenCorpora\FactExtAutoAssesst\data\factrueval2016"
	# Имя csv-файла, в который будет записан результат
	output_file_name = r"C:\development\OpenCorpora\FactExtAutoAssesst\data\MarkupData.csv"
	output_collection = sets_collection.SetsCollection()
	extractor.exract_markup_data_track1(markup_dir, participants_dir, output_file_name, "test",
										output_collection)
	output_collection.save(r"C:\development\OpenCorpora\FactExtAutoAssesst\data\sets_dump.bin")

if __name__ == '__main__':
	begin_time = time.time()
	extract_features()
	end_time = time.time()
	print("Working time: " + str(end_time-begin_time))
