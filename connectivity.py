import time
import json
from collections import defaultdict

import requests
from ratelimit import limits, sleep_and_retry, RateLimitException

import logging

logger = logging.getLogger()

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
            error_details = defaultdict(None, json.loads(errh.response.content))
            error_details['http_status'] = errh.response.status_code
            error_message = error_details['message']
            error_ct_status = error_details['ct_status']
            error_http_status = error_details['http_status']
            error_code = error_details['code']
            error_url = error_details['url']

            logger.debug("error status (HTTP):", error_http_status,
                         "error status (CrowdTangle):", error_ct_status,
                         "error code:", error_code,
                         "error message:", error_message,
                         "error url:", error_url)

            if error_http_status == 429:  # rate limit exceeded
                raise RateLimitException()  # should be handled by ratelimit
            elif error_code == 20:  # Unknown Parameter
                raise errh
            elif error_code == 21:  # Illegal Parameter Value
                raise errh
            elif error_code == 22:  # Missing Parameter
                raise errh
            elif error_code == 30:  # Missing Token
                raise errh
            elif error_code == 31:  # Invalid Token
                raise errh
            elif error_code == 40:  # Does Not Exist
                raise errh
            elif error_code == 41:  # Not Allowed
                raise errh
            elif error_http_status / 100 == 4:  # 4XX error other than 429
                raise errh
            elif error_http_status / 100 == 5:  # 5XX error
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
    # FIXME: poor design, hiding parameters in data
    count = -1
    if "batchSize" in param_dict:
        if "count" in param_dict:
            count = param_dict.pop('count')
        param_dict['count'] = param_dict.pop('batchSize')
    elif "count" in param_dict:
        count = param_dict['count']

    next_page = endpoint
    n_yielded = 0
    while next_page:
        response = request_fun(next_page, param_dict)
        next_page = None
        for result in response['result'][response_field]:
            if (count == -1) or (n_yielded < count):
                yield result
                n_yielded += 1
        if ('pagination' in response['result']) and \
                ("nextPage" in response["result"]['pagination']) and \
                ((count == -1) or (n_yielded < count)):
            next_page = response['result']['pagination']['nextPage']
            param_dict = dict()
