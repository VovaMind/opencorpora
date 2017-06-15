from helpers import call_script
from os import remove
from os.path import abspath, dirname, isdir, isfile, join
from scripts.engine.tools.config import Config

import filecmp
import pytest
import shutil

def cleanup(config):
	if isdir(config.get("output_dir")):
		shutil.rmtree(config.get("output_dir"))

def test_correct_get_corpora_features():
	part_id = "1"
	config_file_name = "test_get_corpora_features_config.json"
	config = Config(config_file_name)
	cleanup(config)
	
	args = []
	args.append("python")
	args.append(join("..", "scripts", "get_corpora_features.py"))
	args.append(join("..", "tests", config_file_name))
	args.append(part_id)
	call_script(args)
	
	files_list = ["_features_0.csv", "_features_1.csv", "_token_docs_0.txt", "_token_docs_1.txt",
		"33.tokens", "33.txt", "55.tokens", "55.txt"]
	expected_dir = join(config.get("corpora_base_dir"), "expected")
	result_dir = join(config.get("output_dir"), part_id)
	for file_name in files_list:
		filecmp.cmp(join(expected_dir, file_name), join(result_dir, file_name))
	
	cleanup(config)
