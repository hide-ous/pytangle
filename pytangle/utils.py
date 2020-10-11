# Copyright (C) 2020 Mattia Samory

import os
import sys
import json
import logging
import logging.config
CONFIG_FILE_LOCATIONS = [os.path.join(os.path.dirname(sys.modules[__name__].__file__), "pytangle_config.json"),
						 os.path.join(os.path.expanduser('~'), "pytangle_config.json"),
						 os.path.join(os.path.abspath('.'), "pytangle_config.json"),
						 ]

logger = logging.getLogger()

def remove_null_values_from_dict(params):
	return dict(filter(lambda x: x[1] is not None, params.items()))



# Why not have entire config read in the utils and transferred to api.py?
def read_config():
	config_ = dict()
	for config_file_location in CONFIG_FILE_LOCATIONS:
		if os.path.exists(config_file_location) and os.path.isfile(config_file_location):
			with open(config_file_location) as f:
				config_ = json.load(f)
	return config_

def read_max_retries(config_):
	if 'max_retries' in config_:
		return config_['max_retries']
	return None

def read_wait_time(config_):
	if 'wait_time' in config_:
		return config_['wait_time']
	return None
