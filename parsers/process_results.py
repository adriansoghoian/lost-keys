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

    print "HERE ARE THE RESULTS: \n"
    print "NUMBER OF KEY CANDIDATES: %s \n" % (str(num_keys))
    print "AMAZON KEY CANDIDATES: %s \n" % (str(len(amazon)))
    print amazon
    print "GOOGLE KEY CANDIDATES: %s \n" % (str(len(google)))
    print google



if __name__ == "__main__":
    paths = ["/Users/adrian/desktop/data/github_repo_list_01_results_2015-03-06 21:07:59.399013.csv", 
            "/Users/adrian/desktop/data/github_repo_list_02_results_2015-03-06 21:08:45.492474.csv",
            "/Users/adrian/desktop/data/github_repo_list_03_results_2015-03-06 21:10:56.078463.csv",
            "/Users/adrian/desktop/data/github_repo_list_04_results_2015-03-06 21:11:43.421709.csv",
            "/Users/adrian/desktop/data/github_repo_list_05_results_2015-03-06 21:12:34.892167.csv",
            "/Users/adrian/desktop/data/github_repo_list_06_results_2015-03-06 21:13:36.294829.csv",
            "/Users/adrian/desktop/data/github_repo_list_07_results_2015-03-06 21:14:07.787182.csv",
            "/Users/adrian/desktop/data/github_repo_list_08_results_2015-03-06 21:14:56.007094.csv"
    ]
    extract_statistics(paths)