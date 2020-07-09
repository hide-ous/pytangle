import json
import sys

from api import API
import logging.config

if __name__ == '__main__':
    with open('config.json') as f:
        config_ = json.load(f)

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

    api=API()
    for alist in api.lists():
        print(alist)
    for apost in api.posts(count=5):
        print(apost)
    for aleaderboard in api.leaderboard(count=5):
        print(aleaderboard)
    for alink in api.links(count=5,
        link='https://www.washingtonexaminer.com/news/key-mueller-witness-george-nader-sentenced-to-10-years-in-prison-for-child-sex-charges'):
        print(alink)
    for anaccount in api.accounts_in_list(count=5,listId=alist['id']):
        print(anaccount)
    for apost in api.post(id=apost['id']):
        print(apost)

    for n, apost in enumerate(api.posts(count=10101, sortBy='date')):
        if not n%1000:
            print(n)
    print(n)

