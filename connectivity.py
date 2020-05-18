import time
import json
import requests
from ratelimit import limits, sleep_and_retry

import logging

# TODO: add config for logger name
logger = logging.getLogger('CT')

ONE_SECOND = 1
ONE_MINUTE = 60
TEN_SECONDS = 10
THIRTY_SECONDS = 30


@sleep_and_retry
@limits(calls=1, period=TEN_SECONDS)
def make_request_1_every_10s(uri, params, max_retries=5):
    return make_request(uri, params, max_retries=5)


@sleep_and_retry
@limits(calls=1, period=THIRTY_SECONDS)
def make_request_1_every_30s(uri, params, max_retries=5):
    return make_request(uri, params, max_retries=5)


# TODO: add config for max_retries
def make_request(uri, params, max_retries=5):
    current_tries = 0
    last_exception = None
    while current_tries < max_retries:
        try:
            response = requests.get(uri, params=params)
            logger.debug(response)
            # TODO: handle errors meaningfully
            assert response.status_code == 200
            return json.loads(response.content.decode('utf-8'))
        except Exception as e:
            logger.debug(e)
            last_exception = e
            # TODO: add config for how long to wait
            time.sleep(1)
            current_tries += 1
    raise last_exception


def iterate_request(param_dict, endpoint, response_field, request_fun):
    next_page = endpoint
    while next_page:
        response = request_fun(next_page, param_dict)
        next_page = None
        yield from response['result'][response_field]
        if 'pagination' in response['result'] and "nextPage" in response["result"]['pagination']:
            next_page = response['result']['pagination']['nextPage']
            param_dict = dict()
