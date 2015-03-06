import random

from datetime import datetime
from threading import Thread
from Queue import Queue

from scrapers.scrape_repos import get_repo_file_list
from parsers.parse_text import detect_keys_in_file


def main(repo_list_files):
    """
    main runner for key commit
    """
    worker_q = Queue(maxsize=0)
    results_q = Queue(maxsize=0)

    num_threads = 10

    stop = 5

    for repo_list in repo_list_files:
        with open(repo_list, "rb") as f:
            for l, line in enumerate(f.xreadlines()):
                username = line.split(',')[0].split('/')[0].rstrip()
                repo = line.split(',')[0].split('/')[1].rstrip()
                worker_q.put((username, repo, line))
                print l, '\t', username, '\t', repo
                if l > stop:
                    break

            writer_thread = Thread(target=writer, args=(results_q, ))
            writer_thread.setDaemon(True)
            writer_thread.start()

            for i in range(num_threads):
                t = Thread(target=worker, args=(results_q, worker_q))
                t.setDaemon(True)
                t.start()

            worker_q.join()
            results_q.join()


def worker(results_q, worker_q):
    while True:
        params = worker_q.get()
        username = params[0]
        repo = params[1]
        files = get_repo_file_list(username, repo)
        results_q.put(detect_keys_in_file(files))
        worker_q.task_done()


def writer(results_q):
    with open("data/github_repo_results_" + str(datetime.now()) + ".csv", "a") as r:
        while True:
            while results_q.qsize() > 0:
                # there are results, so write them to the file
                results = results_q.get()
                keys = results.keys()
                if keys:
                    for key in keys:
                        try:
                            r.write(results[key] + "\t" + key + "\n")
                        except Exception as e:
                            print e

                results_q.task_done()


def generate_sample_user_list():
    """
    generate a sampling of the total user body
    """
    sampling_percentage = 0.0005
    filename = "data/user_list_" + str(datetime.now()) + ".csv"
    with open(filename, "wb") as r:
        with open('data/github_user_list.csv', 'rb') as f:
            for index, line in enumerate(f.xreadlines()):
                roll = random.random()
                if roll < sampling_percentage:
                    username = line.split(",")[0].rstrip()
                    r.write(username + "\n")
    return filename


if __name__ == "__main__":
    start = datetime.now()
    file_paths = ["data/github_repo_list.csv"]
    main(file_paths)
    print "runtime:\t", str(datetime.now() - start)
