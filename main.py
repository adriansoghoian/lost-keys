from scrape_repos import get_user_file_list
from scan_text import detect_keys_in_file
from datetime import datetime
from threading import Thread
from Queue import Queue

import numpy

USERNAME_RUN_TIME = []
GET_USER_FILE_LIST_TIME = []
SCAN_TEXT_TIME = []
DETECT_KEYS_IN_FILE_TIME = []


def main(list_of_users, thread_n):
    q = Queue(maxsize=0)
    num_threads = 0

    user_file_iter_times = []

    for user_file in list_of_users:
        user_file_iter_time_start = datetime.now()
        results = []
        with open(user_file.split(".")[0] + "_results.csv", "wb") as r:

            with open(user_file, "rb") as f:

                for line in f.xreadlines():
                    q.put(line.rstrip().split(",")[0])
                    num_threads = thread_n
                for i in range(num_threads):
                    t = Thread(target=threadable, args=(results, q))
                    t.setDaemon(True)
                    t.start()
                q.join()

            print "|"*50

            print "Get User File List: [AVG,STD]\t[" + \
                str(numpy.mean(GET_USER_FILE_LIST_TIME)) + "," + \
                str(numpy.std(GET_USER_FILE_LIST_TIME)) + "]"

            print "Detect Keys: [AVG,STD]\t[" + \
                str(numpy.mean(DETECT_KEYS_IN_FILE_TIME)) + "," + \
                str(numpy.std(DETECT_KEYS_IN_FILE_TIME)) + "]"
            print "\tScan Text: [AVG,STD]\t[" + \
                str(numpy.mean(SCAN_TEXT_TIME)) + "," + \
                str(numpy.std(SCAN_TEXT_TIME)) + "]"

            print "="*50

            print "Username Iteration Loop: [AVG,STD]\t[" + \
                str(numpy.mean(USERNAME_RUN_TIME)) + "," + \
                str(numpy.std(USERNAME_RUN_TIME)) + "]"

            print "*"*50
            print "*"*50
            for result in results:
                keys = result.keys()
                for key in keys:
                    try:
                        r.write(key + "," + result[key] + "\n")
                    except Exception as e:
                        print e

        user_file_iter_times.append(
            (datetime.now() - user_file_iter_time_start).total_seconds())

        print "User File Iteration Loop:\t", user_file_iter_times[-1]
    print "User File Iteration Loop: [AVG, STD]\t[" + \
        str(numpy.mean(user_file_iter_times)) + "," + \
        str(numpy.std(user_file_iter_times)) + "]"
    return results


def threadable(results, q):
    while True:
        tic = datetime.now()
        username = q.get()
        user_files, runtime = get_user_file_list(username)
        GET_USER_FILE_LIST_TIME.append(runtime)
        keys, runtime, scan_text_runtime = detect_keys_in_file(user_files)
        DETECT_KEYS_IN_FILE_TIME.append(runtime)
        if scan_text_runtime is not None:
            SCAN_TEXT_TIME.append(scan_text_runtime)
        results.append(keys)
        toc = datetime.now()
        USERNAME_RUN_TIME.append((toc - tic).total_seconds())
        q.task_done()


if __name__ == "__main__":
    file_paths = ["data/user_list_test.csv"]
    THREAD_RUN_TIME = []
    for i in range(1, 11):
        tic = datetime.now()
        main(file_paths, thread_n=i)
        toc = datetime.now()
        THREAD_RUN_TIME.append((toc - tic).total_seconds())
        print "Thread Count:\t, ", i, "\tTotal Time:", str(THREAD_RUN_TIME[-1])

    import matplotlib.pyplot as plt
    plt.plot(range(1,11), THREAD_RUN_TIME, 'bo')
    plt.plot(range(1,11), THREAD_RUN_TIME, 'b-')
    plt.xlabel("Thread Count")
    plt.ylabel("Time (s)")
    plt.show()
