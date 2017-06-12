from helpers import call_script, read_file_lines
from os.path import isdir, join
from scripts.engine.tools.config import Config

import pytest
import shutil

def test_correct_get_span_keywords():
	config = Config("test_get_span_keywords_config.json")
	if isdir(config.get("words_set_dir")):
		shutil.rmtree(config.get("words_set_dir"))
	
	args = []
	args.append("python")
	args.append(join("..", "scripts", "get_span_keywords.py"))
	args.append(join("..", "tests", "test_get_span_keywords_config.json"))
	call_script(args)
	
	assert {"ab"} == set(read_file_lines(join(config.get("words_set_dir"), "words_loc_descr.txt")))
	assert {"hj"} == set(read_file_lines(join(config.get("words_set_dir"), "words_org_descr.txt")))
	
	shutil.rmtree(config.get("words_set_dir"))
