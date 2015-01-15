from scrape_repos import get_user_file_list
from scan_text import detect_keys_in_file
from datetime import datetime
from threading import Thread
from Queue import Queue


def main(list_of_users):
    q = Queue(maxsize=0)
    num_threads = 0
    for user_file in list_of_users:
        results = []
        with open(user_file.split(".")[0] + "_results.csv", "wb") as r:
            with open(user_file, "rb") as f:
                for line in f.xreadlines():
                    start = datetime.now()
                    q.put(line.rstrip().split(",")[0])
                    num_threads += 1
                for i in range(num_threads):
                    t = Thread(target=threadable, args=(results, q))
                    t.setDaemon(True)
                    t.start()
                q.join()
            for result in results:
                keys = result.keys()
                for key in keys:
                    try:
                        r.write(key + "," + result[key] + "\n")
                    except Exception as e:
                        print e
    return results


def threadable(results, q):
    while True:
        username = q.get()
        user_files = get_user_file_list(username)
        results.append(detect_keys_in_file(user_files))
        q.task_done()


if __name__ == "__main__":
    start = datetime.now()
    file_paths = ["data/test.csv"]
    main(file_paths)
    print "Time took:", str(datetime.now() - start)
