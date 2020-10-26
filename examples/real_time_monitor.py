# Copyright (C) 2020 Mattia Samory

import json
import logging
import time
from datetime import datetime
import schedule
import optparse
from pytangle.api import API, CONFIG_FILE_LOCATIONS

logger = logging.getLogger()


class PyTangleScraper(object):
    def __init__(self, api_key, config, lists, store_path, quiet, every, timeunit, at):
        self.config = config
        self.api_key = api_key
        self.at = at
        self.timeunit = timeunit
        self.every = every
        self.lists = lists
        self.quiet = quiet
        self.store_path = store_path

        self.timestamp_last_post = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')  # current time
        self.api = API(token=self.api_key, config_file_locations=self.config)
        self.counter = 0
        if not self.quiet:
            logger.setLevel(logging.DEBUG)

    def scrape_once(self):
        most_recent_timestamp = self.timestamp_last_post
        counter = 0
        with open(self.store_path, 'a+') as out_file:

            for post in self.api.posts(listIds=self.lists,
                                       sortBy='date', count=-1, startDate=self.timestamp_last_post,
                                       endDate=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')):
                out_file.write(json.dumps(post) + '\n')
                post_date = post['date']
                if type(post_date) == list: #unpack items if they are nested in a list
                    post_date = post_date[0]
                most_recent_timestamp = max(most_recent_timestamp, post_date)
                counter += 1
        self.timestamp_last_post = most_recent_timestamp
        self.counter += counter
        if not self.quiet:
            logger.debug("returned {} posts ({} up to now)".format(counter, self.counter))
            logger.debug("done at " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def run(self):
        job = schedule.every(self.every).__getattribute__(self.timeunit)
        if self.at:
            job = job.at(self.at)
        job.do(self.scrape_once)
        while True:
            logger.debug('next run at ' + str(schedule.next_run()))
            schedule.run_pending()
            sleep_time = (schedule.next_run() - datetime.now()).total_seconds()
            logger.debug('sleeping for {} seconds'.format(sleep_time))
            time.sleep(sleep_time)


def main():
    usage = "example usage: real_time_monitor.py --every 30 --timeunit minutes --key APIKEY --file log.njson"
    parser = optparse.OptionParser(usage)
    parser.add_option("-f", "--file", dest="filename", default='pytangle_{}.njson'.format(
        time.strftime('%Y%m%d%H%M%S')),
                      help="store to FILE", metavar="FILE")

    def split_list(option, opt, value, parser, *args, **kwargs):
        setattr(parser.values, option.dest, value.split(','))

    parser.add_option("-l", "--lists", dest="lists", default=None, action='callback',
                      callback=split_list, nargs=1, type='string',
                      help="comma-separated ids of the list to scrape, e.g. -l 123,345")

    parser.add_option("-q", "--quiet",
                      action="store_true", dest="quiet", default=False,
                      help="don't print status messages to stdout")

    parser.add_option("-e", "--every", dest="every", default=1, type='int',
                      help="""(int) how many TIMEUNITs to skip.\n
                      Syntax:scrape EVERY TIMEUNIT AT, e.g. every {10} {days} at {10:30}""")

    parser.add_option("-t", "--timeunit", dest="time_unit", default='hour',
                      help="""(str) how often to scrape.\n 
                      Syntax: scrape EVERY TIMEUNIT AT, e.g. every {1} {day} at {10:30}.\n
                      Available values:\n
                            \tsecond\n
                            \tseconds\n
                            \tminute\n
                            \tminutes\n
                            \thour\n
                            \thours\n
                            \tday\n
                            \tdays\n
                            \tweek\n
                            \tweeks\n
                            \tmonday\n
                            \ttuesday\n
                            \twednesday\n
                            \tthursday\n
                            \tfriday\n
                            \tsaturday\n
                            \tsunday""")

    parser.add_option("-a", "--at", dest="at", default=None,
                      help="""(str)  time at which the scraper should be run\n
                      Syntax: scrape EVERY TIMEUNIT AT, e.g. every {1} {day} at {10:30}.\n
                      Available formats (depending on the TIMEUNIT):\n\tHH:MM:SS\n\tHH:MM\n\t`:MM`\n\t:SS 
                      """)

    parser.add_option("-k", "--key", dest="api_key", default=None,
                      help="API key", metavar="CTAPIKEY")
    parser.add_option("-c", "--config", dest="config_path", default=CONFIG_FILE_LOCATIONS,
                      help="pytangle config file location")

    (options, args) = parser.parse_args()

    PyTangleScraper(api_key=options.api_key,
                    config=options.config_path,
                    lists=options.lists,
                    store_path=options.filename,
                    quiet=options.quiet,
                    every=options.every,
                    timeunit=options.time_unit,
                    at=options.at).run()


if __name__ == '__main__':
    main()
