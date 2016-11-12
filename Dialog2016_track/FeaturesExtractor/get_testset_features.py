# -*- coding: utf-8 -*-
''' main-файл для извлечения признаков '''

from common_config import GET_TESTSET_FEATURES_PARAMS

import features_extractor
import time
import sets_collection

def extract_features():
	'''Извлекаем признаки.'''
	extractor = features_extractor.FeaturesExtractor()
	extractor.load_w2v_data(GET_TESTSET_FEATURES_PARAMS["w2v_model_file"])
	# Имя csv-файла, в который будет записан результат
	output_collection = sets_collection.SetsCollection()
	extractor.exract_markup_data_track1(GET_TESTSET_FEATURES_PARAMS["markup_dir"], 
										GET_TESTSET_FEATURES_PARAMS["participants_dir"], 
										GET_TESTSET_FEATURES_PARAMS["output_file_name"],
										"test", output_collection)
	output_collection.save(GET_TESTSET_FEATURES_PARAMS["sets_dump_file"])

if __name__ == '__main__':
	begin_time = time.time()
	extract_features()
	end_time = time.time()
	print("Working time: " + str(end_time-begin_time))
