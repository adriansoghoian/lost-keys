from patterns.patterns import patterns


def read_log(log_file):
    file_extensions = []
    with open(log_file, "rb") as log:
        for line in log.xreadlines():
	    if line.split(" ")[2] != "Repo":
                file_path = line.split(" ")[3]
                file_extensions.append(file_path.split(".")[-1])

    return file_extensions


def update_patterns(new_patterns):
    file_path = "data/extensions.txt"

    with open(file_path, "a") as f:
        for pattern in new_patterns:
            f.write(pattern)


def main(log_file):
    new_patterns = read_log(log_file)
    update_patterns(new_patterns)


if __name__ == "__main__":
    patterns = read_log("logs/avg_repo_per_user.py 2015-01-09 15:35:43.678890.log")
    dedupe = {}
    for each in patterns:
        dedupe[each] = 1
    print dedupe.keys()
