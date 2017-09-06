from helpers import call_script, expect_equal_collections
from os import remove
from os.path import abspath, dirname, isdir, isfile, join
from scripts.engine.tools.config import Config
from scripts.engine.tools.sets_collection import SetsCollection

import inspect
import filecmp
import pytest

SCRIPT_PATH = dirname(abspath(inspect.getfile(inspect.currentframe())))

def cleanup(config):
	if isfile(config.get("testset_features_file")):
		remove(config.get("testset_features_file"))
	if isfile(config.get("sets_collection_file")):
		remove(config.get("sets_collection_file"))

def read_collection(file_name):
	result = SetsCollection()
	result.load(file_name)
	return result
	
def test_correct_get_testset_features():
	config_file_name = "test_get_testset_features_config.json"
	config = Config(config_file_name)
	cleanup(config)
	
	args = []
	args.append("python3")
	args.append(join("..", "scripts", "get_testset_features.py"))
	args.append(join("..", "tests", config_file_name))
	call_script(args)
	
	assert filecmp.cmp(join(config.get("testset_base_dir"), "expected_features.csv"),
		config.get("testset_features_file"))
	# Нельзя просто сравнивать два файла, так как иногда в выдаче меняется порядок
	expected_output_collection = read_collection(join(config.get("testset_base_dir"), 
		"expected_sets.dump"))
	output_collection = read_collection(config.get("sets_collection_file"))
	expect_equal_collections(expected_output_collection, output_collection)
	
	cleanup(config)
