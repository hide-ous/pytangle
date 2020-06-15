import json
import logging
import sys
from itertools import islice

from api import *
import logging.config
if __name__ == '__main__':
    with open('config.json') as f:
        config_ = json.load(f)
    token_ = config_['token']

    # Set up proper logging. This one disables the previously configured loggers.
    if "logging" in config_:
        logging.config.dictConfig(config_["logging"])
    else:
        logging.basicConfig(stream=sys.stdout,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S'
                        )
    logger = logging.getLogger()


    my_lists = lists(**{"token" : token_})
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
        break

