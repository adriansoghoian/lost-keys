import itertools

def extract_statistics(file_paths):
    """
    Method to extract statistics from a results.csv file. 
    Assumes that results.csv files are formatted with: URL, KEY_CANDIDATE. 

    Currently tracks: Amazon, Google, Facebook, Twitter. 
    """
    amazon = []
    google = []
    facebook = []
    twitter = []
    num_keys = 0
    for path in file_paths:
        print path
        with open(path, "rb") as f:
            lines = f.readlines()
            for line in lines:
                line_pieces = line.split("\t", 1)
                if "http" not in line_pieces[0][0:5]: continue
                num_keys += 1
                if "akia" in line_pieces[1].lower(): amazon.append(line_pieces[1])
                if "aiza" in line_pieces[1].lower(): google.append(line_pieces[1])
    google = list(set(google))
    amazon = list(set(amazon))

    print "HERE ARE THE RESULTS: \n"
    print "NUMBER OF KEY CANDIDATES: %s \n" % (str(num_keys))
    print "AMAZON KEY CANDIDATES: %s \n" % (str(len(amazon)))
    print amazon
    print "GOOGLE KEY CANDIDATES: %s \n" % (str(len(google)))
    print google



if __name__ == "__main__":
    paths = ["/Users/adrian/workspace/lost-keys/data/realtime_github_repo_results_2015-03-19 13:19:45.390058.csv"]
    extract_statistics(paths)