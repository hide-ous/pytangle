from abc import ABC
from copy import deepcopy

from connectivity import make_request_1_every_10s, make_request_1_every_30s, make_request


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
    def get_response_item_id(cls, response_item):
        raise NotImplementedError


class Endpoint6CPM(Endpoint, ABC):
    @classmethod
    def request_function(cls):
        return make_request_1_every_10s


class Endpoint2CPM(Endpoint, ABC):
    @classmethod
    def request_function(cls):
        return make_request_1_every_30s


class EndpointOneShotCall(Endpoint, ABC):
    @classmethod
    def request_function(cls):
        return make_request


class ListsEndpoint(EndpointOneShotCall):
    @classmethod
    def get_endpoint_template(cls):
        return 'https://api.crowdtangle.com/lists'

    @classmethod
    def get_response_field_name(cls):
        return 'lists'

    @classmethod
    def get_response_item_id(cls, response_item):
        return response_item['id']


class PostsEndpoint(Endpoint6CPM):
    @classmethod
    def get_endpoint_template(cls):
        return 'https://api.crowdtangle.com/posts'

    @classmethod
    def get_response_field_name(cls):
        return 'posts'

    @classmethod
    def get_response_item_id(cls, response_item):
        return response_item['id']


class LinksEndpoint(Endpoint2CPM):
    @classmethod
    def get_endpoint_template(cls):
        return 'https://api.crowdtangle.com/links'

    @classmethod
    def get_response_field_name(cls):
        return 'posts'

    @classmethod
    def get_response_item_id(cls, response_item):
        return response_item['id']


class LeaderboardEndpoint(Endpoint6CPM):
    @classmethod
    def get_endpoint_template(cls):
        return 'https://api.crowdtangle.com/leaderboard'

    @classmethod
    def get_response_field_name(cls):
        return 'accountStatistics'

    @classmethod
    def get_response_item_id(cls, response_item):
        return response_item['account']['id']


class SearchEndpoint(Endpoint6CPM):
    @classmethod
    def get_endpoint_template(cls):
        return 'https://api.crowdtangle.com/posts/search'

    @classmethod
    def get_response_field_name(cls):
        return 'posts'

    @classmethod
    def get_response_item_id(cls, response_item):
        return response_item['id']


class AccountsEndpoint(Endpoint6CPM):
    @classmethod
    def get_endpoint_template(cls):
        return 'https://api.crowdtangle.com/lists/{}/accounts'

    @classmethod
    def get_endpoint_parameter_name(cls):
        return "listId"

    @classmethod
    def get_response_field_name(cls):
        return 'accounts'

    @classmethod
    def get_response_item_id(cls, response_item):
        return response_item['id']


class PostEndpoint(EndpointOneShotCall):
    def __init__(self, endpoint, args):
        super().__init__(args)
        self.endpoint = endpoint

    def get_endpoint_template(self):
        endpoint_url = None
        if self.endpoint == "platform":
            endpoint_url = "https://api.crowdtangle.com/post/{}"
        elif self.endpoint == "ct":
            endpoint_url = "https://api.crowdtangle.com/ctpost/{}"
        return endpoint_url

    @classmethod
    def get_endpoint_parameter_name(cls):
        return "id"

    @classmethod
    def get_response_field_name(cls):
        return 'posts'

    @classmethod
    def get_response_item_id(cls, response_item):
        return response_item['id']
