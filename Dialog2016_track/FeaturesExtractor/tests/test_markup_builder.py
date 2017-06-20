from helpers import call_script
from os import remove
from os.path import abspath, dirname, isdir, isfile, join
from scripts.engine.tools.config import Config

import filecmp
import pytest

OUTPUT_FILE_LIST = ["33.spans", "33.objects", "55.spans", "55.objects"]

def remove_file(file_name):
	if isfile(file_name):
		remove(file_name)

def cleanup(output_dir):
	for file_name in OUTPUT_FILE_LIST:
		remove_file(join(output_dir, file_name))

def test_correct_markup_building():
	config_file_name = "test_markup_builder_config.json"
	config = Config(config_file_name)
	part_id = "1"
	output_dir = join(config.get("output_dir"), part_id)
	expected_dir = join(config.get("corpora_base_dir"), "expected")

	cleanup(output_dir)
	
	args = []
	args.append("python")
	args.append(join("..", "scripts", "markup_builder.py"))
	args.append(join("..", "tests", config_file_name))
	args.append(part_id)
	call_script(args)
	
	for file_name in OUTPUT_FILE_LIST:
		assert filecmp.cmp(join(expected_dir, file_name), join(output_dir, file_name))
	
	cleanup(output_dir)
