import subprocess

def call_script(args):
	subprocess.call(args, shell=False)

def read_file_lines(file_name):
	with open(file_name, encoding = "utf-8") as input_file:
		return list(map(lambda x: x.replace("\n", ""), input_file.readlines()))

def expect_equal_collections(expected, actual):
	assert len(expected.labeled_sets) == len(actual.labeled_sets)
	for key in expected.labeled_sets:
		assert expected.labeled_sets[key] == actual.labeled_sets[key]
