from scan_text import get_file, scan_text_violently
from secrets import git_access_token
from datetime import datetime, timedelta
from scrape_repos import filter_files
from Queue import Queue
from time import sleep
from threading import Thread
import urllib2, json, time
import traceback, sys


class Monitor(object):

    def __init__(self, monitor_duration, num_threads=10):
        self.monitor_duration = monitor_duration # duration in minutes
        self.num_repos = 0 ## TODO
        self.num_key_rotations = 0
        self.num_events = 0 ## TODO
        self.num_threads = 10 
        self.num_key_candidates = 0
        self.key_candidates = []
        self.url_tasks = Queue(maxsize=0)
        self.first_event_id = 0 ## TODO
        self.last_event_id = 0 ## TODO
        self.access_token_index = 0
        self.keep_querying = True
        self.keep_scraping = True
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(minutes=self.monitor_duration)
        self.results_file_path = "repos/realtime_feed_" + str(self.start_time) + ".csv"


    def run(self):
        """
        Main execution method for monitor. Spawns a process to pulldown and convert 
        Github events into raw urls, then spawns several processes to consume the urls and 
        extract keys. 

        Raw urls are managed by a Queue, from which "url tasks" are popped off and processed by 
        the threadable_url_consumer method. 
        """
        results = []
        event_retriever = Thread(target=self.threadable_retrieve_event_urls, args=())
        event_retriever.setDaemon(True)
        event_retriever.start()

        for i in range(1, self.num_threads):
            event_processor = Thread(target=self.threadable_url_consumer, args=())
            event_processor.setDaemon(True)
            event_processor.start()

        while self.keep_querying:
            if (datetime.now() - self.end_time).total_seconds() > 0:
                self.keep_querying = False
                print "STOPPING RETRIEVING EVENTS. \n" 
                print "%s many tasks remaining to be processed." % (str(self.url_tasks.qsize()))

        self.url_tasks.join()
        self.write_results()


    def write_results(self):
        """
        Writes the results to a .csv once everything has been processed. 
        Writes a file in "/repos" in the form defined by self.result_file_path.
        """
        with open(self.results_file_path, "wb") as f:
            for result in self.key_candidates:
                keys = result.keys()
                for key in keys:
                    try: 
                        f.write(result[key] + "\t" + key + "\n")
                    except Exception as e:
                        print e


    def threadable_url_consumer(self):
        """
        A threadable method to consume and process urls off the task queue.
        """
        while self.keep_querying:
            url = self.url_tasks.get()

            candidates_in_url = scan_text_violently(text=get_file(file_path=url))
            candidates_in_url = [ {each: url} for each in candidates_in_url ]

            if len(candidates_in_url) > 0: print candidates_in_url
            self.key_candidates += candidates_in_url
            self.url_tasks.task_done()


    def threadable_retrieve_event_urls(self):
        """
        A single process will constantly monitor the Github event stream 
        """
        while self.keep_querying:
            new_events = self.retrieve_events()  
            self.convert_events_to_urls(new_events)


    def convert_events_to_urls(self, new_events):
        """
        Takes in a list of JSON objects representing Github 'events', filters them into 
        raw_urls, and adds them to the Queue for threaded processing.  
        """
        for i, event in enumerate(new_events):
            urls = []
            if event['type'] != "PushEvent": continue
            for commit in event['payload']['commits']:
                try:
                    response = urllib2.urlopen(commit['url'] + "?access_token=" + git_access_token[self.access_token_index])
                    data = json.load(response)
                    for each_file in data['files']:
                        if "." in each_file['raw_url'].split("/")[-1]:
                            urls.append(each_file['raw_url'])
                    urls = filter_files(urls)
                    map(self.url_tasks.put, urls)
                except Exception as e:
                    self.rotate_access_token()
                    self.num_key_rotations += 1 


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


# def monitor_events(cap=500, type="PushEvent"):
#     """
#     This monitors GitHub's /events stream,
#     looking for a capped number of events of certain type.
#     """
#     access_token_index = 0
#     start = datetime.now()
#     results_file_path = "repos/realtime_feed_" + str(start) + ".csv"
#     count = 0
#     last_checked_event_id = 2565764483 # This is just an arbitrary value I grabbed to initialize this.
#     results = []

#     with open(results_file_path, "wb") as f:
#         while True:
#             if count > cap: break
#             try:
#                 data = pulldown_events(git_access_token[access_token_index])
#                 while int(data[-1]['id']) < last_checked_event_id:
#                     time.sleep(10)
#                     data = pulldown_events(git_access_token[access_token_index])
#                 last_checked_event_id = int(data[0]['id'])
#                 for i, event in enumerate(data):
#                     if event['type'] == "PushEvent": 
#                         count += 1
#                         raw_urls = scrape_event(event, git_access_token[access_token_index])
#                         for url in raw_urls:
#                             candidates_in_file = scan_text_violently(text=get_file(file_path=url))   
#                             candidates_in_file = [ {each: url} for each in candidates_in_file ]
#                             if len(candidates_in_file) > 0: print candidates_in_file   
#                             results += candidates_in_file
#                         if count > cap: break
#                     else:
#                         continue
#             except Exception as e:
#                 access_token_index = (1 + access_token_index) % 2
#                 traceback.print_exc(file=sys.stdout)
#                 print e

#         for result in results:
#             keys = result.keys()
#             for key in keys:
#                 try:
#                     r.write(result[key] + "\t" + key + "\n")
#                 except Exception as e:
#                     print e
#     return True


# def pulldown_events(access_token, amount_per_page=100):
#     """
#     Pulls down 100 of the most recent events.
#     """
#     endpoint = "https://api.github.com/events?per_page=" + str(amount_per_page) + "&access_token=" + access_token
#     response = urllib2.urlopen(endpoint)

#     return json.load(response)


# def scrape_event(event_json, access_token):
#     """
#     Method takes a json object of the GitHub API's "event" and extracts individual file urls
#     for scraping.
#     """
#     raw_urls = []

#     for commit in event_json['payload']['commits']:
#         try:
#             response = urllib2.urlopen(commit['url'] + "?access_token=" + access_token)
#             data = json.load(response)
#             for each in data['files']:
#                 if "." in each['raw_url'].split("/")[-1]: raw_urls.append(each['raw_url'])
#         except Exception as e:
#             print e

#     return filter_files(raw_urls)


if __name__ == "__main__":
    # monitor_events()
    print "Starting at: ", str(datetime.now())
    monitor = Monitor(5)
    monitor.run()
    print "Ending at: ", str(datetime.now())





