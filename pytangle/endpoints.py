# Copyright (C) 2020 Mattia Samory

from abc import ABC
from copy import deepcopy
from pytangle.connectivity import RateLimitedPaginator#, make_request_1_every_10s, make_request_1_every_30s, 

"""
Each endpoint has time unit and number of calls properties that are determined by the ratelimits for each 
endpoint as currently specified in https://help.crowdtangle.com/en/articles/3443476-api-cheat-sheet which 
states: "Rate limit defaults: 6 calls/min for all but /links, which is 2 calls/min."
"""

class Endpoint(ABC):
    def __init__(self, args):
        self.args = deepcopy(args)
        if self.has_endpoint_parameter_name():
            endpoint_parameter_name = self.get_endpoint_parameter_name()
            self.endpoint_parameter = self.args.pop(endpoint_parameter_name)

    @classmethod
    def get_endpoint_template(cls):
        raise NotImplementedError

    def get_endpoint_url(self):
        if self.has_endpoint_parameter_name():
            return self.get_endpoint_template().format(self.endpoint_parameter)
        else:
            return self.get_endpoint_template()

    @classmethod
    def has_endpoint_parameter_name(cls):
        try:
            endpoint_parameter_name = cls.get_endpoint_parameter_name()
            return endpoint_parameter_name is not None
        except NotImplementedError:
            return False

    @classmethod
    def get_endpoint_parameter_name(cls):
        raise NotImplementedError

    @classmethod
    def get_response_field_name(cls):
        raise NotImplementedError

    @classmethod
    def max_query_offset(cls):
        return 10000

    @classmethod
    def request_function(cls):
        raise NotImplementedError

    @classmethod
    def response_item_id_getter(cls, response_item):
        raise NotImplementedError

    def __iter__(self):
        return self
    
    def __next__(self):
        return next(self.requester)

    @property
    def requester(self):
        #print("HIIII here")
        #time.sleep(10)
        if not hasattr(self, 'paginator'):
            self.paginator = RateLimitedPaginator(self.args, 
                                        self.response_item_id_getter,
                                        self.get_response_field_name(),
                                        self.max_query_offset(),
                                        self.get_endpoint_url(),
                                        self.get_num_calls(),
                                        self.get_time_unit())
        #print("???")
        #time.sleep(10)
        return self.paginator

# remove
# class Endpoint6CPM(Endpoint, ABC):
#     @classmethod
#     def request_function(cls):
#         return make_request#_1_every_10s


# class Endpoint2CPM(Endpoint, ABC):
#     @classmethod
#     def request_function(cls):
#         return make_request#_1_every_30s



# why do we need this anymore? remove
# class EndpointOneShotCall(Endpoint, ABC):
#     @classmethod # we don't need this anymore
#     def request_function(cls):
#         return make_request

#     @classmethod
#     def call_rate_limited_paginator(cls, args):
#         #print(cls.get_endpoint_template())
#         yield from RateLimitedPaginator(args, 
#                                         cls.request_function(),
#                                         cls.get_response_field_name(),
#                                         cls.max_query_offset(),
#                                         cls.get_endpoint_template())




class ListsEndpoint(Endpoint):
    @classmethod
    def get_endpoint_template(cls):
        return 'https://api.crowdtangle.com/lists'

    @classmethod
    def get_num_calls(cls):
        return 6

    @classmethod
    def get_time_unit(cls):
        return 60         

    @classmethod
    def get_response_field_name(cls):
        return 'lists'

    @classmethod
    def response_item_id_getter(cls, response_item):
        return response_item['id']

    @classmethod
    def response_item_id_getter(cls, response_item):
        return response_item['id']        

class PostsEndpoint(Endpoint):
    @classmethod
    def get_endpoint_template(cls):
        return 'https://api.crowdtangle.com/posts'

    @classmethod
    def get_num_calls(cls):
        return 6

    @classmethod
    def get_time_unit(cls):
        return 60        

    @classmethod
    def get_response_field_name(cls):
        return 'posts'

    @classmethod   
    def response_item_id_getter(cls, response_item):
        return response_item['id']

    # @property
    # def requester(self):        
    #     return Endpoint.requester.fget(self)      


class LinksEndpoint(Endpoint):
    @classmethod
    def get_endpoint_template(cls):
        return 'https://api.crowdtangle.com/links'

    @classmethod
    def get_num_calls(cls):
        return 2

    @classmethod
    def get_time_unit(cls):
        return 60   

    @classmethod
    def get_response_field_name(cls):
        return 'posts'

    @classmethod
    def response_item_id_getter(cls, response_item):
        return response_item['id']


class LeaderboardEndpoint(Endpoint):
    @classmethod
    def get_endpoint_template(cls):
        return 'https://api.crowdtangle.com/leaderboard'

    @classmethod
    def get_num_calls(cls):
        return 6

    @classmethod
    def get_time_unit(cls):
        return 60   

    @classmethod
    def get_response_field_name(cls):
        return 'accountStatistics'

    @classmethod
    def response_item_id_getter(cls, response_item):
        return response_item['account']['id']


class SearchEndpoint(Endpoint):
    @classmethod
    def get_endpoint_template(cls):
        return 'https://api.crowdtangle.com/posts/search'

    
    @classmethod
    def get_num_calls(cls):
        return 6

    @classmethod
    def get_time_unit(cls):
        return 60   

    @classmethod
    def get_response_field_name(cls):
        return 'posts'

    @classmethod
    def response_item_id_getter(cls, response_item):
        return response_item['id']


class AccountsEndpoint(Endpoint):
    @classmethod
    def get_endpoint_template(cls):
        return 'https://api.crowdtangle.com/lists/{}/accounts'

    @classmethod
    def get_num_calls(cls):
        return 6

    @classmethod
    def get_time_unit(cls):
        return 60   

    @classmethod
    def get_endpoint_parameter_name(cls):
        return "listId"

    @classmethod
    def get_response_field_name(cls):
        return 'accounts'

    @classmethod
    def response_item_id_getter(cls, response_item):
        return response_item['id']


class PostEndpoint(Endpoint):
    def __init__(self, endpoint, args):
        super().__init__(args)
        self.endpoint = endpoint

    def get_endpoint_template(self):
        endpoint_url = None
        if self.endpoint == "platform":
            endpoint_url = "https://api.crowdtangle.com/post/{}"
        elif self.endpoint == "ct":
            endpoint_url = "https://api.crowdtangle.com/ctpost/{}"
        else:
            raise AttributeError("endpoint should be one of \"platform\" or \"ct\";"+
                                 " received \"{}\" instead".format(self.endpoint))
        return endpoint_url

    @classmethod
    def get_num_calls(cls):
        return 60

    @classmethod
    def get_time_unit(cls):
        return 60 

    @classmethod
    def get_endpoint_parameter_name(cls):
        return "id"

    @classmethod
    def get_response_field_name(cls):
        return 'posts'

    @classmethod
    def response_item_id_getter(cls, response_item):
        return response_item['id']
