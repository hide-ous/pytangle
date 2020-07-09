import time
import json
from collections import defaultdict, deque
from copy import deepcopy
from json import JSONDecodeError
from urllib.parse import urlparse, parse_qs
from sys import exit
import dateutil
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
            error_details = defaultdict(lambda: None)
            try:
                error_details.update(json.loads(errh.response.content.decode()))
            except AttributeError as e:
                pass
            except JSONDecodeError as e:
                logger.debug(e)
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
                raise  # should be handled by ratelimit
            elif error_code == 20:  # Unknown Parameter
                exit(-1)
            elif error_code == 21:  # Illegal Parameter Value
                exit(-1)
            elif error_code == 22:  # Missing Parameter
                exit(-1)
            elif error_code == 30:  # Missing Token
                exit(-1)
            elif error_code == 31:  # Invalid Token
                exit(-1)
            elif error_code == 40:  # Does Not Exist
                exit(-1)
            elif error_code == 41:  # Not Allowed
                exit(-1)
            elif error_http_status / 100 == 4:  # 4XX error other than 429
                time.sleep(60)
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


class Paginator:
    def __init__(self, endpoint, max_cached_ids=100):
        self.endpoint = endpoint
        self.cached_ids = deque(maxlen=max_cached_ids)

        self.request_fun = endpoint.request_function()
        self.response_field = endpoint.get_response_field_name()
        self.param_dict = deepcopy(endpoint.args)
        self.max_offset_threshold = endpoint.max_query_offset()
        self.endpoint_url = endpoint.get_endpoint_url()

        self.returned_count = 0

        self.next_page = None
        self.previous_page = None
        self.response = None
        self.current_results = deque()
        self.has_next_page = True

        count = -1
        if "batchSize" in self.param_dict:
            if "count" in self.param_dict:
                count = self.param_dict.pop('count')
            self.param_dict['count'] = self.param_dict.pop('batchSize')
        elif "count" in self.param_dict:
            count = self.param_dict['count']
        self.total_count = count
        self.next_page_params = deepcopy(self.param_dict)

    def __fetch_next_response(self):
        # call CT
        response = self.request_fun(self.endpoint_url,
                                    self.next_page_params)
        self.response = response

        # update results
        if not (response['result'][self.response_field]):
            logger.debug('no results returned')
            self.next_page = None
            self.previous_page = None
            self.has_next_page = False
            self.next_page_params = dict()
            return

        new_ids_to_cache = list()
        for result in response['result'][self.response_field]:
            # check for duplicates
            try:
                result_id = self.endpoint.get_response_item_id(result)
                if result_id not in self.cached_ids:
                    self.current_results.append(result)
                    new_ids_to_cache.append(result_id)
            except NotImplementedError:
                self.current_results.append(result)
        if len(new_ids_to_cache):
            self.cached_ids.extend(new_ids_to_cache)

        # update pagination information
        pagination = defaultdict(lambda: None)
        if 'pagination' in response['result']:
            pagination.update(response["result"]['pagination'])
        self.next_page = pagination['nextPage']
        self.previous_page = pagination['nextPage']

        # update current offset and end date
        logger.debug("next page: {}".format(self.next_page))
        self.next_page_params = defaultdict(lambda: None)
        if self.next_page:
            self.next_page_params.update(parse_qs(urlparse(self.next_page).query))
            # if offset overflows
            if int(self.next_page_params['offset'][0]) > self.max_offset_threshold:
                # if sorting by date, retract endDate, reset offset
                # (does not apply to leaderboard, which can't sortBy date)
                if self.next_page_params['sortBy'] == ["date"]:
                    self.next_page_params['offset'] = 0
                    end_date = dateutil.parser.parse(self.current_results[-1]['date'])
                    self.next_page_params['endDate'] = end_date.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            self.has_next_page = False
        # make it a regular dictionary
        self.next_page_params = dict(self.next_page_params)
        logger.debug(str(self.next_page_params))

    def __is_spent(self):
        if -1 < self.total_count <= self.returned_count:  # returned all of the items requested
            return True
        elif len(self.current_results)>0:  # not returned all cached results
            return False
        elif not self.has_next_page:  # has a next page to fetch
            return True
        return False

    def __next__(self):
        if self.__is_spent():
            raise StopIteration
        if not len(self.current_results):
            self.__fetch_next_response()
        if self.__is_spent():
            #may have fetched no results
            raise StopIteration
        self.returned_count += 1

        return self.current_results.popleft()

    def __iter__(self):
        return self
