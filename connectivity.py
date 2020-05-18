import time
import json
import requests
import itertools
from datetime import datetime, timedelta
from ratelimit import limits, sleep_and_retry

import logging
import sys

logger = logging.getLogger('CT')

ONE_SECOND = 1
ONE_MINUTE = 60
TEN_SECONDS = 10
THIRTY_SECONDS = 30


@sleep_and_retry
@limits(calls=1, period=TEN_SECONDS)
def make_request_1_every_10s(uri, params, max_retries=5, logger=logger):
    return make_request(uri, params, max_retries=5, logger=logger)

@sleep_and_retry
@limits(calls=1, period=THIRTY_SECONDS)
def make_request_1_every_30s(uri, params, max_retries=5, logger=logger):
    return make_request(uri, params, max_retries=5, logger=logger)

def make_request(uri, params, max_retries=5, logger=logger):
    current_tries = 0
    last_exception = None
    while current_tries < max_retries:
        try:
            response = requests.get(uri, params=params)
            logger.debug(response)
            assert response.status_code == 200
            return json.loads(response.content.decode('utf-8'))
        except Exception as e:
            logger.debug(e)
            last_exception = e
            time.sleep(1)
            current_tries += 1
    raise last_exception
