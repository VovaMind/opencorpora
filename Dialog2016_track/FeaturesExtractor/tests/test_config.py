from scripts.engine.tools.config import *

import pytest

def test_correct_config_read():
	config = Config("test_config_data.json")
	assert config.get("key1") == 123
	assert config.get("key2") == "doit"
	assert config.get("test_key") == 777
	assert config.get("qwerty") == "what??"
