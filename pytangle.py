import json
import logging
import sys
from itertools import islice

from api import *

logging.basicConfig(stream=sys.stdout,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S'
                    )
logger = logging.getLogger('CT')
if __name__ == '__main__':
    with open('config.json') as f:
        config = json.load(f)
    token_ = config['token']
    my_lists = lists({"token" : token_})
    logger.info(my_lists)
    a_list = my_lists[-1]

    param_dict = dict(token=token_)
    param_dict['listId'] = a_list['id']
    param_dict['count'] = 100
    for account in islice(accounts_in_list(**param_dict), 300):
        logger.info(account)

    param_dict = dict(token=token_)
    param_dict['listIds'] = [a_list['id']]
    param_dict['sortBy'] = 'date'
    param_dict['count'] = 100

    for post in islice(posts(**param_dict), 300):
        logger.info(post)
