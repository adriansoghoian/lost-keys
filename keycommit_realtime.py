from scrapers.scrape_repos import filter_files
from parsers.parse_text import get_file
from parsers.parse_text import scan_text
from secrets import git_access_token
from datetime import datetime, timedelta
from Queue import Queue
from time import sleep
from threading import Thread
import urllib2, json, time
import traceback, sys


class Monitor(object):
    def __init__(self, monitor_duration, num_threads=10, debug=True, use_multiprocess=False):
        self.monitor_duration = monitor_duration # duration in minutes
        self.debug = debug
        self.num_repos = 0
        self.num_key_rotations = 0
        self.num_urls_processed = 0
        self.num_events = 0
        self.num_threads = num_threads
        self.num_key_candidates = 0
        self.results_q = Queue(maxsize=0)
        self.url_tasks = Queue(maxsize=0)
        self.first_event_id = None
        self.last_event_id = None
        self.access_token_index = 0
        self.keep_querying = True
        self.keep_scraping = True
        self.trailing_key_window = [] # TODO
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(minutes=self.monitor_duration)
        self.runtime = None
        self.scantime = None
        self.results_file_path = "repos/realtime_feed_" + str(self.start_time) + ".csv"


    def run(self):
        """
        Main execution method for monitor. Spawns a process to pulldown and convert 
        Github events into raw urls, then spawns several processes to consume the urls and 
        extract keys. 
        Raw urls are managed by a Queue, from which "url tasks" are popped off and processed by 
        the threadable_url_consumer method. 
        """
        event_retriever = Thread(target=self.threadable_retrieve_event_urls, args=())
        event_retriever.setDaemon(True)
        event_retriever.start()

        event_retriever_2 = Thread(target=self.threadable_retrieve_event_urls, args=())
        event_retriever_2.setDaemon(True)
        event_retriever_2.start()

        # writer_thread = Thread(target=self.threadable_writer, args=())
        # writer_thread.setDaemon(True)
        # writer_thread.start()

        # for i in range(1, self.num_threads):
        #     event_processor = Thread(target=self.threadable_url_consumer, args=())
        #     event_processor.setDaemon(True)
        #     event_processor.start()

        while self.keep_querying:
            if (datetime.now() - self.end_time).total_seconds() > 0:
                self.keep_querying = False

                print "STOPPING RETRIEVING EVENTS. \n" 
                print "%s many tasks remaining to be processed." % (str(self.url_tasks.qsize()))

        self.url_tasks.join()
        self.results_q.join()
        self.runtime = (datetime.now() - self.start_time).total_seconds()/60
        self.summary()


    def threadable_writer(self):
        with open("data/realtime_github_repo_results_" + str(datetime.now()) + ".csv", "a") as r:
            while True:
                    try:
                    # there are results, so write them to the file
                        results = self.results_q.get()
                        for result in results:
                            try:
                                r.write(result[1] + "\t" + result[0] + "\n")
                            except Exception as e:
                                print "Error printing: ", e
                        self.results_q.task_done()
                    except Exception as e:
                        pass


    def threadable_url_consumer(self):
        """
        A threadable method to consume and process urls off the task queue.
        """
        while True:
            url = self.url_tasks.get()
            self.url_tasks.task_done()
            if self.url_tasks.qsize() == 0 and not self.keep_querying: break
            if self.debug and not self.keep_querying: print "Remaining tasks in queue: %s \n" % (str(self.url_tasks.qsize()))

            if url == None: continue
            candidates_in_url = scan_text(text=get_file(file_path=url))
            candidates_in_url = [ (each, url) for each in candidates_in_url ]
            candidates_in_url = list(set(candidates_in_url))
            candidates_in_url = [ elem for elem in candidates_in_url if elem not in self.trailing_key_window ]

            if self.debug and len(candidates_in_url) > 0: 
                print "Key candidates: ", candidates_in_url
                print "\n"

            self.results_q.put(candidates_in_url)
            self.trailing_key_window = candidates_in_url
            self.num_key_candidates += len(candidates_in_url)


    def threadable_retrieve_event_urls(self):
        """
        A single process will constantly monitor the Github event stream 
        """
        while self.keep_querying:
            new_events = self.retrieve_events()
            if not self.first_event_id: self.first_event_id = new_events[-1]['id'] 
            self.convert_events_to_urls(new_events)

        self.last_event_id = new_events[0]['id']
        self.scantime = (datetime.now() - self.start_time).total_seconds() / 60


    def convert_events_to_urls(self, new_events):
        """
        Takes in a list of JSON objects representing Github 'events', filters them into 
        raw_urls, and adds them to the Queue for threaded processing.  
        """
        for i, event in enumerate(new_events):
            self.num_events += 1
            urls = []
            if event['type'] == "PushEvent":
                self.num_repos += 1
                print event['actor']['login']
                # for commit in event['payload']['commits']:
                #     try:
                #         response = urllib2.urlopen(commit['url'] + "?access_token=" + git_access_token[self.access_token_index])
                #         data = json.load(response)
                #         for each_file in data['files']:
                #             if "." in each_file['raw_url'].split("/")[-1]:
                #                 urls.append(each_file['raw_url'])
                #         urls = list(set(filter_files(urls)))
                #         self.num_urls_processed += len(urls)
                #         map(self.url_tasks.put, urls)
                #     except Exception as e:
                #         self.rotate_access_token()
                #         self.num_key_rotations += 1
            else:
                continue


    def retrieve_events(self, per_page=100):
        """
        This retrieves a set of events. If those events have already been pulled,
        it halts and then tries again. 
        """
        endpoint = "https://api.github.com/events?per_page=" + str(per_page) + "&access_token=" + git_access_token[self.access_token_index]

        while True:
            try:
                response = urllib2.urlopen(endpoint)
                data = json.load(response)
                if int(data[-1]['id']) < self.last_event_id:
                    sleep(1)
                else:
                    self.last_event_id = int(data[-1]['id'])
                    return data
            except Exception as e:
                self.rotate_access_token()
                self.num_key_rotations += 1


    def rotate_access_token(self):
        """
        Updates Github API access token.
        """
        self.access_token_index = (self.access_token_index + 1) % len(git_access_token)


    def summary(self):
        """
        Prints a summary of the run.
        """
        print "The monitor started at: ", self.start_time
        print "The monitor ran in total for: %s minutes." % (str(self.runtime))
        print "The monitor scanned Github events for: %s minutes." % (str(self.scantime))
        print "Rotated keys: %s many times" % (str(self.num_key_rotations))
        print "The number of repos: ", self.num_repos
        print "The number of events: ", self.num_events
        print "The number of key candidates: ", self.num_key_candidates
        print "The ID of the first event scanned: ", self.first_event_id
        print "The ID of the last event scanned: ", self.last_event_id
        print "*"*50


if __name__ == "__main__":
    monitor = Monitor(10, debug=False)
    monitor.run()
