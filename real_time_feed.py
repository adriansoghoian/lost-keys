from scan_text import get_file, scan_text_violently
from secrets import git_access_token
from datetime import datetime
from scrape_repos import filter_files
import urllib2, json, time
import traceback, sys


def monitor_events(cap=5000, type="PushEvent"):
    """
    This monitors GitHub's /events stream,
    looking for a capped number of events of certain type.
    """
    access_token_index = 0
    start = datetime.now()
    results_file_path = "repos/realtime_feed_" + str(start) + ".csv"
    count = 0
    last_checked_event_id = 2565764483 # This is just an arbitrary value I grabbed to initialize this.
    results = []

    with open(results_file_path, "wb") as f:
        while True:
            if count > cap: break
            try:
                data = pulldown_events(git_access_token[access_token_index])
                while int(data[-1]['id']) < last_checked_event_id:
                    time.sleep(10)
                    data = pulldown_events(git_access_token[access_token_index])
                last_checked_event_id = int(data[0]['id'])
                for i, event in enumerate(data):
                    if event['type'] == "PushEvent": 
                        count += 1
                        raw_urls = scrape_event(event, git_access_token[access_token_index])
                        for url in raw_urls:
                            candidates_in_file = scan_text_violently(text=get_file(file_path=url))   
                            candidates_in_file = [ {each: url} for each in candidates_in_file ]   
                            results += candidates_in_file
                        if count > cap: break
                    else:
                        continue
            except Exception as e:
                access_token_index = (1 + access_token_index) % 2
                traceback.print_exc(file=sys.stdout)
                print e

        for result in results:
            keys = result.keys()
            for key in keys:
                try:
                    f.write(key + ", " + result[key] + "\n")
                except Exception as e:
                    print e
    return True


def pulldown_events(access_token, amount_per_page=100):
    """
    Pulls down 100 of the most recent events.
    """
    endpoint = "https://api.github.com/events?per_page=" + str(amount_per_page) + "&access_token=" + access_token
    response = urllib2.urlopen(endpoint)

    return json.load(response)


def scrape_event(event_json, access_token):
    """
    Method takes a json object of the GitHub API's "event" and extracts individual file urls
    for scraping.
    """
    raw_urls = []

    for commit in event_json['payload']['commits']:
        try:
            response = urllib2.urlopen(commit['url'] + "?access_token=" + access_token)
            data = json.load(response)
            for each in data['files']:
                raw_urls.append(each['raw_url'])
        except Exception as e:
            print e

    return filter_files(raw_urls)


if __name__ == "__main__":
    monitor_events()


