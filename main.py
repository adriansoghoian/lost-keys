from scrape_repos import get_user_file_list, get_repo_file_list
from scan_text import detect_keys_in_file
from datetime import datetime
from threading import Thread
from Queue import Queue
import random


def generate_sample_user_list():
    sampling_percentage = 0.0005
    filename = "data/user_list_" + str(datetime.now()) + ".csv"
    with open(filename, "wb") as r:
        with open('data/github_user_list.csv', 'rb') as f:
            for index, line  in enumerate(f.xreadlines()):
                roll = random.random()
                if roll < sampling_percentage:
                    username = line.split(",")[0].rstrip()    
                    r.write(username + "\n")
    return filename


# def main(list_of_users):
#     """Original main() using user list
#     """
#
#     q = Queue(maxsize=0)
#     num_threads = 0
#     for user_file in list_of_users:
#         results = []
#         with open(user_file.split(".")[0] + "_results.csv", "wb") as r:
#             with open(user_file, "rb") as f:
#                 for line in f.xreadlines():
#                     start = datetime.now()
#                     q.put(line.rstrip().split(",")[0])
#                     num_threads += 1
#                 for i in range(num_threads):
#                     t = Thread(target=threadable, args=(results, q))
#                     t.setDaemon(True)
#                     t.start()
#                 q.join()
#             for result in results:
#                 keys = result.keys()
#                 for key in keys:
#                     try:
#                         #r.write(key + "\n" + "\n")
#                         r.write(key + "\n" + result[key] + "\n\n")
#                     except Exception as e:
#                         print e
#     return results


def main(repo_list_files):
    """Uses the repo list need to consolidate
    """
    q = Queue(maxsize=0)
    num_threads = 10

    stop = 10000
    c = 0

    for repo_list in repo_list_files:
        results = []
        with open(repo_list.split(".")[0] + "_results.csv", "wb") as r:
            with open(repo_list, "rb") as f:
                for line in f.xreadlines():
                    c += 1
                    username = line.split(',')[0].split('/')[0].rstrip()
                    repo = line.split(',')[0].split('/')[1].rstrip()
                    q.put((username, repo))
                    # num_threads += 1
                    print c, '\t', username, '\t', repo
                    if c > stop:
                        break
                for i in range(num_threads):
                    t = Thread(target=threadable, args=(results, q))
                    t.setDaemon(True)
                    t.start()
                q.join()


            for result in results:
                keys = result.keys()
                for key in keys:
                    try:
                        #r.write(key + "\n" + "\n")
                        r.write(key + "\n" + result[key] + "\n\n")
                    except Exception as e:
                        print e
    return results


def threadable(results, q):
    while True:
        params = q.get()
        username = params[0]
        repo = params[1]
        # files = get_user_file_list(username)

        files = get_repo_file_list(username, repo)

        results.append(detect_keys_in_file(files))

        q.task_done()


if __name__ == "__main__":
    start = datetime.now()
    # file_paths = ["data/test.csv"]#[generate_sample_user_list()]#
    file_paths = ["repos/repo_list_22489472.csv"]

    main(file_paths)
    print "Time took:", str(datetime.now() - start)
