from connectivity import make_request, make_request_1_every_10s, iterate_request, make_request_1_every_30s


def lists(token):
    param_dict = {'token': token}
    response = make_request('https://api.crowdtangle.com/lists', param_dict)
    return response['result']['lists']


def posts(**args):
    return iterate_request(args, 'https://api.crowdtangle.com/posts', 'posts', make_request_1_every_10s)


def links(**args):
    return iterate_request(args, 'https://api.crowdtangle.com/links', 'links', make_request_1_every_30s)


def leaderboard(**args):
    return iterate_request(args, 'https://api.crowdtangle.com/leaderboard', 'leaderboard', make_request_1_every_10s)


def search(**args):
    return iterate_request(args, 'https://api.crowdtangle.com/search', 'leaderboard', make_request_1_every_10s)


def accounts_in_list(**args):
    list_id = args.pop('listId')
    return iterate_request(args, 'https://api.crowdtangle.com/lists/{}/accounts'.format(list_id), 'accounts', make_request_1_every_10s)
