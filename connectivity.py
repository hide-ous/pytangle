import time
import json
import requests
from ratelimit import limits, sleep_and_retry, RateLimitException

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
            response.raise_for_status()
            return json.loads(response.content.decode('utf-8'))
        except requests.exceptions.HTTPError as errh:
            logger.error("Http Error:", errh)
            if errh.response.status_code == 429:
                raise RateLimitException() #should be handled by ratelimit
            elif errh.response.status_code / 100 == 4: #4XX error
                raise errh
            elif errh.response.status_code / 100 == 5:  # 5XX error
                # TODO: add config for how long to wait
                time.sleep(60)
            else:
                time.sleep(1)
            last_exception = errh
            current_tries += 1
        except requests.exceptions.ConnectionError as errc:
            logger.error("Error Connecting:", errc, "\nsleeping")
            last_exception = errc
            time.sleep(60)
            current_tries += 1
        except requests.exceptions.Timeout as errt:
            logger.error("Timeout Error:", errt, "\nsleeping")
            last_exception = errt
            time.sleep(60)
            current_tries += 1
        except requests.exceptions.RequestException as err:
            logger.error("Unspecified RequestException", err)
            raise err
    # if all retries fail, raise the last exception
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
