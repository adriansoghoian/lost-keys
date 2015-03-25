import random

from datetime import datetime
from threading import Thread
from Queue import Queue

from scrapers.scrape_repos import Scraper
from parsers.parse_text import Parser


class Survey(object):
    def __init__(self, repo_list_files, num_threads=10, debug=True):
        self.repo_list_files = repo_list_files
        self.debug = debug
        self.num_repos = 0
        self.num_key_rotations = 0
        self.num_urls_processed = 0
        #self.num_events = 0
        self.num_threads = num_threads
        self.num_key_candidates = 0
        self.worker_q = Queue(maxsize=0)
        self.results_q = Queue(maxsize=0)
        #self.url_tasks = Queue(maxsize=0)
        # self.first_event_id = None
        # self.last_event_id = None
        #self.access_token_index = 0
        # self.keep_querying = True
        # self.keep_scraping = True
        # self.trailing_key_window = [] # TODO
        # self.start_time = datetime.now()
        # self.end_time = self.start_time + timedelta(minutes=self.monitor_duration)
        # self.runtime = None
        # self.scantime = None
        # self.results_file_path = "repos/realtime_feed_" + str(self.start_time) + ".csv"


    def run(self):
        """
        main runner for key commit
        """
        #self.worker_q = Queue(maxsize=0)
        #results_q = Queue(maxsize=0)

        #num_threads = 10

        stop = 5

        for repo_list in self.repo_list_files:
            with open(repo_list, "rb") as f:
                for l, line in enumerate(f.xreadlines()):
                    username = line.split(',')[0].split('/')[0].rstrip()
                    repo = line.split(',')[0].split('/')[1].rstrip()
                    self.worker_q.put((username, repo, line))
                    print l, '\t', username, '\t', repo
                    if l > stop:
                        break

                writer_thread = Thread(target=self.writer)#, args=(self.results_q, ))
                writer_thread.setDaemon(True)
                writer_thread.start()

                for i in range(self.num_threads):
                    t = Thread(target=self.worker)#, args=(self.results_q, self.worker_q))
                    t.setDaemon(True)
                    t.start()

                self.worker_q.join()
                self.results_q.join()


    def worker(self):
        while True:
            params = self.worker_q.get()
            username = params[0]
            repo = params[1]
            files = Scraper(username=username, repo=repo).get_files()
            self.results_q.put(Parser.get_keys(files))
            self.worker_q.task_done()


    def writer(self):
        with open("data/github_repo_results_" + str(datetime.now()) + ".csv", "a") as r:
            while True:
                while self.results_q.qsize() > 0:
                    # there are results, so write them to the file
                    results = self.results_q.get()
                    keys = results.keys()
                    if keys:
                        for key in keys:
                            try:
                                r.write(results[key] + "\t" + key + "\n")
                            except Exception as e:
                                print e

                    self.results_q.task_done()


    # def generate_sample_user_list():
    #     """
    #     generate a sampling of the total user body
    #     """
    #     sampling_percentage = 0.0005
    #     filename = "data/user_list_" + str(datetime.now()) + ".csv"
    #     with open(filename, "wb") as r:
    #         with open('data/github_user_list.csv', 'rb') as f:
    #             for index, line in enumerate(f.xreadlines()):
    #                 roll = random.random()
    #                 if roll < sampling_percentage:
    #                     username = line.split(",")[0].rstrip()
    #                     r.write(username + "\n")
    #     return filename


    def summary(self):
        """
        Prints a summary of the run.
        """
        # print "The monitor started at: ", self.start_time
        # print "The monitor ran in total for: %s minutes." % (str(self.runtime))
        # print "The monitor scanned Github events for: %s minutes." % (str(self.scantime))
        print "Rotated keys: %s many times" % (str(self.num_key_rotations))
        print "The number of repos: ", self.num_repos
        # print "The number of events: ", self.num_events
        print "The number of key candidates: ", self.num_key_candidates
        # print "The ID of the first event scanned: ", self.first_event_id
        # print "The ID of the last event scanned: ", self.last_event_id
        print "*"*50


if __name__ == "__main__":
    start = datetime.now()

    survey = Survey(["repos/repo_list_123.csv"], 10, debug=True)
    survey.run()
    survey.summary()
    
    # file_paths = ["repos/repo_list_123.csv"]
    # main(file_paths)
    print "runtime:\t", str(datetime.now() - start)
