import subprocess

def call_script(args):
	subprocess.call(args, shell=False)

def read_file_lines(file_name):
	with open(file_name, encoding = "utf-8") as input_file:
		return list(map(lambda x: x.replace("\n", ""), input_file.readlines()))
