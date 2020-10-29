# Copyright (C) 2020 Mattia Samory

import time
import json
from collections import defaultdict, deque
from copy import deepcopy
from json import JSONDecodeError
from urllib.parse import urlparse, parse_qs
from sys import exit
from dateutil.parser import parse as date_parse
import requests
from ratelimit import sleep_and_retry, RateLimitException
from pytangle.utils import read_config, read_max_retries, read_wait_time
import itertools
import logging

import sys
from math import floor

logger = logging.getLogger()

# ONE_SECOND = 1
# ONE_MINUTE = 60
# TEN_SECONDS = 10
# THIRTY_SECONDS = 30
MAX_RETRIES = read_max_retries(read_config()) if read_max_retries(read_config()) else 5 



# the following use of ratelimit should be removed
"""
@sleep_and_retry
@limits(calls=1, period=TEN_SECONDS)
def make_request_1_every_10s(uri, params, max_retries=5):
    return make_request(uri, params, max_retries=MAX_RETRIES)


@sleep_and_retry
@limits(calls=1, period=THIRTY_SECONDS)
def make_request_1_every_30s(uri, params, max_retries=5):
    return make_request(uri, params, max_retries=MAX_RETRIES)

"""

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
            logger.error(errh)
            error_details = defaultdict(lambda: None)
            try:
                error_details.update(json.loads(errh.response.content.decode()))
            except AttributeError:
                pass
            except JSONDecodeError as e:
                logger.debug(e)
            error_details['http_status'] = errh.response.status_code
            error_message = error_details['message']
            error_ct_status = error_details['ct_status']
            error_http_status = error_details['http_status']
            error_code = error_details['code']
            error_url = error_details['url']

            logger.debug(("error status (HTTP):{}\n"+
                         "error status (CrowdTangle):{}\n"+
                         "error code:{}\n"+
                         "error message:{}\n"+
                         "error url:{}").format(error_http_status,
                                                error_ct_status,
                                                error_code,
                                                error_message,
                                                error_url))

            if error_http_status == 429:  # rate limit exceeded
                # should be handled by ratelimit
                # it's actually not
                # FIXME: make it so that ratelimit handles this
                # raise
                time.sleep(30)

            elif error_code == 20:  # Unknown Parameter
                logger.error("Crowdtangle error code 20: Unknown Parameter")
                time.sleep(60)
            elif error_code == 21:  # Illegal Parameter Value
                logger.error("Crowdtangle error code 21: Illegal Parameter Value")
                time.sleep(60)
            elif error_code == 22:  # Missing Parameter
                logger.error("Crowdtangle error code 22: Missing Parameter")
                time.sleep(60)
            elif error_code == 30:  # Missing Token
                logger.error("Crowdtangle error code 30: Missing Token")
                time.sleep(60)
            elif error_code == 31:  # Invalid Token
                logger.error("Crowdtangle error code 31: Invalid Token")
                time.sleep(60)
            elif error_code == 40:  # Does Not Exist
                logger.error("Crowdtangle error code 40: Does Not Exist")
                time.sleep(60)
            elif error_code == 41:  # Not Allowed
                logger.error("Crowdtangle error code 41: Not Allowed")
                time.sleep(60)
            elif error_http_status / 100 == 4:  # 4XX other client side error
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
            logger.error("Error Connecting:{}".format(errc) + "\nsleeping")
            last_exception = errc
            time.sleep(60)
            current_tries += 1
        except requests.exceptions.Timeout as errt:
            logger.error("Timeout Error:{}".format(errt) + "\nsleeping")
            last_exception = errt
            time.sleep(60)
            current_tries += 1
        except requests.exceptions.RequestException as err:
            logger.error("Unspecified RequestException".format(err))
            raise err
    # if all retries fail, raise the last exception
    raise last_exception


class Paginator:

    def __init__(self,
                 #endpoint,
                 param_dict,
                 response_item_id_getter,
                 #request_fun,
                 response_field,
                 max_query_offset,
                 endpoint_url,
                 max_cached_ids=100):

        #self.endpoint = endpoint
        self.cached_ids = deque(maxlen=max_cached_ids)

        # self.request_fun = endpoint.request_function()
        # self.response_field = endpoint.get_response_field_name()
        # self.param_dict = deepcopy(endpoint.args)
        # self.max_offset_threshold = endpoint.max_query_offset()
        # self.endpoint_url = endpoint.get_endpoint_url()

        self.response_item_id_getter = response_item_id_getter
        self.response_field = response_field
        self.param_dict = deepcopy(param_dict)
        self.max_offset_threshold = max_query_offset
        self.endpoint_url = endpoint_url


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
        logger.debug("call params " + str(self.next_page_params))
        response = self.request_fun(self.endpoint_url,
                                    self.next_page_params)
        self.response = response

        # update results
        if ('result' not in response) or (self.response_field not in response['result']) or (
                len(response['result'][self.response_field]) == 0):
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
                result_id = self.response_item_id_getter(result) # ??
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
                    end_date = date_parse(self.current_results[-1]['date'])
                    self.next_page_params['endDate'] = end_date.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            self.has_next_page = False
        # make it a regular dictionary
        self.next_page_params = dict(self.next_page_params)
        logger.debug(str(self.next_page_params))

    def __is_spent(self):
        if -1 < self.total_count <= self.returned_count:  # returned all of the items requested
            return True
        elif len(self.current_results) > 0:  # not returned all cached results
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
            # may have fetched no results
            raise StopIteration
        self.returned_count += 1

        return self.current_results.popleft()

    def __iter__(self):
        return self

# create rate limited paginator which inherits paginator and ratelimits it depending on the endpoint
class RateLimitedPaginator(Paginator):
    def __init__(self, 
                 param_dict,
                 response_field,
                 max_query_offset,
                 endpoint_url,
                 max_cached_ids=100,
                 num_calls = 1,
                 time_unit = 10,
                 raise_on_limit = True):
        super().__init__(param_dict, response_field, max_query_offset, endpoint_url, max_cached_ids)
                        # , request_fun, response_field, 
                        #  param_dict, max_offset_threshold, endpoint_url,
                        #  returned_count, next_page, previous_page, response,
                        #  current_results, has_next_page)
                        
        self.request_fun = make_request  # have make request here instead of importing in endpoints.py        
        self.time_unit = time_unit / num_calls
        self.num_calls = 1 #num_calls
        self.clock = time.time()
        self.last_reset = time.time()
        self.clamped_calls = max(1, min(sys.maxsize, floor(self.num_calls)))
        self.num_calls_so_far = 0
        self.raise_on_limit = raise_on_limit
        self.total = 0

    def __period_remaining(self):
        '''
        Return the period remaining for the current rate limit window.
        :return: The remaing period.
        :rtype: float
        '''
        elapsed = time.time() - self.last_reset
        return self.time_unit - elapsed

   
    def __next__(self):
        

        #print(period_remaining, self.clamped_calls)
        if self.__period_remaining() <= 0:
            #print("resetting")
            self.num_calls_so_far = 0
            self.last_reset = time.time()


        # Increase the number of attempts to call the function.
        self.num_calls_so_far += 1
        self.total += 1

        # If the number of attempts to call the function exceeds the
        # maximum then raise an exception.
        if self.num_calls_so_far / 100 >= self.clamped_calls and self.__period_remaining() > 0:
            time.sleep(self.__period_remaining())   # sleep for time remaining        


        #print(self.num_calls / 100, self.total, self.__period_remaining(), self.clamped_calls)
        return super().__next__()

        


