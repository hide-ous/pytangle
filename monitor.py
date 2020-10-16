# Copyright (C) 2020 Mattia Samory
import json
import time
import schedule
import optparse

from pytangle.api import API, CONFIG_FILE_LOCATIONS


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
        self.timestamp_last_post = None
        self.api = API(token=self.api_key, config_file_locations=self.config)

    def scrape_once(self):
        with open(self.store_path, 'a+') as out_file:
            most_recent_timestamp = None
            period = None
            if not self.timestamp_last_post:  # first run
                period = PyTangleScraper.__timeunit_to_first_period(self.timeunit, self.every)

            for post in self.api.posts(listIds=self.lists, timeframe=period,
                                       sortBy='date', count=-1, startDate=self.timestamp_last_post,
                                       endDate=time.strftime('%Y-%m-%dT%H:%M:%S')):
                out_file.write(json.dumps(post) + '\n')
                most_recent_timestamp = max(most_recent_timestamp, post['date'])
            self.timestamp_last_post = most_recent_timestamp
        if not self.quiet:
            print("done at ", time.strftime('%Y-%m-%dT%H:%M:%S'))

    def run(self):
        job = schedule.every(self.every).__getattribute__(self.timeunit)
        if self.at:
            job=job.at(self.at)
        job.do(self.scrape_once)
        while True:
            'next run at', schedule.next_run()
            schedule.run_pending()
            time.sleep(1)  # wait one second

    @classmethod
    def __timeunit_to_first_period(cls, timeunit, every):
        to_return = timeunit.upper().rstrip()
        if to_return.endswith('S'):
            to_return = to_return[:-1]
        if to_return not in {"SECOND", "MINUTE", "HOUR", "DAY", "WEEK"}:
            to_return = 'WEEK'  # TODO: crude
        if every:
            to_return = "{} {}".format(every, to_return)
        return to_return


def main():
    usage = "example usage: monitor.py --every 30 --timeunit minutes --key APIKEY --file log.njson"
    parser = optparse.OptionParser(usage)
    parser.add_option("-f", "--file", dest="filename", default='pytangle_{}.njson'.format(
        time.strftime('%Y-%m-%dT%H:%M:%S')),
                      help="store to FILE", metavar="FILE")

    def split_list(option, value):
        setattr(parser.values, option.dest, value.split(','))
    parser.add_option("-l", "--lists", dest="lists", default=None, action='callback',
                      callback=split_list, help="comma-separated ids of the list to scrape, e.g. -l 123,345")

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
