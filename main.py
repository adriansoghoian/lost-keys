from scrape_repos import get_user_file_list
from scan_text import detect_keys_in_file
from datetime import datetime


def main(list_of_users):
    for user_file in list_of_users:
        results = []
        with open(user_file.split(".")[0] + "_results.csv", "wb") as r:
            with open(user_file, "rb") as f:
                for line in f.xreadlines():
                    start = datetime.now()
                    try:
                        user_files = get_user_file_list(username=line.rstrip())
                        results.append(detect_keys_in_file(user_files))
                        print "Time it took for %s was %s" % (line, str(datetime.now() - start))
                    except Exception as e:
                        print e
            for result in results:
                keys = result.keys()
                for key in keys: 
                    r.write(key + "," + result[key] + "\n")
    return results


if __name__ == "__main__":
	file_paths = ["data/user_list.csv"]
	main(file_paths)