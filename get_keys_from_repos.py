import urllib2, json, sys, re, os
from datetime import datetime, timedelta
from secrets import git_access_token
from scrape_repos import get_files
from scan_text import detect_keys_in_file
from threading import Thread
from Queue import Queue


def get_recent_repos(interested_days=180):
    current_date = datetime.now()
    filename = "data/repo_list_" + str(interested_days) + "_days_" + str(current_date) + ".csv"

    start = 97037
    count = 0

    with open(filename, "wb") as r, open('data/github_user_list.csv', 'rb') as f:
        for line in f:
            count += 1
            if count >= start:
                username = line.split(",")[0].rstrip()    
                endpoint = "https://api.github.com/users/" + username + "/repos?per_page=100&access_token=" + git_access_token[0]
                try:
                    response = urllib2.urlopen(endpoint)
                    data = json.load(response)
                    for repo in data:
                        repo_update_date = datetime.strptime(repo['updated_at'][:10], '%Y-%m-%d')
                        diff = current_date - repo_update_date
                        if repo['fork'] == False and diff < timedelta(interested_days):
                            r.write(repo['full_name'] + "\n")
                except Exception as e:
                    print e
                    print "User: %s has no repos." % (username)


def get_batch_repos(since_index=0, num_calls=4999, results_directory="data/"):
    git_token_index = 0
    num_called = 0
    last_index = 30052000
    with open(results_directory + "repo_list_" + str(since_index) + ".csv", 'wb') as f:
        while(since_index <= last_index):
            if(num_called < num_calls):
                endpoint = "https://api.github.com/repositories?since=" + str(since_index) + "?per_page=100&access_token=" + git_access_token[git_token_index]
                response = urllib2.urlopen(endpoint)
                repos = json.load(response)
                for repo in repos:
                    f.write(repo['full_name'] + "," + str(repo['id']) + "\n") 

                since_index = repos[-1]['id']
                num_calls += 1
            else:
                num_calls = 0 
                git_token_index = (git_token_index + 1) % 2

    print "Last index: ", since_index



'''
def merge_repo_files(interested_days):
    out_file_name = "data/github_repo_list_"+str(interested_days)+"_days.csv"
    #current_directory = os.getcwd()
    in_files = os.listdir("/data")#current_directory + 
    in_files = ["data/" + csv for csv in in_files if "data/github_repo_list_"+str(interested_days)+"_days_" in csv]
    with open(out_file_name, "wb") as out_file:     
        for in_file_path in in_files:
            with open(in_file_path, "rb") as in_file:
                for line in in_file.xreadlines():
                    out_file.write(line)
'''


def get_keys(lists_of_repos):
    print "Getting Keys"
    git_token_index = 0
    num_calls = 0
    for list_of_repos in lists_of_repos:
        start = datetime.now()
        with open(list_of_repos.split(".")[0] + "_results.csv", "wb") as r:
            with open(list_of_repos, "rb") as f:
                for line in f.xreadlines():
                    username, repo = line.rstrip().split('/')
                    user_files = get_files(repo, username, git_access_token[git_token_index])
                    num_calls += 1
                    if (num_calls >= 5000):
                        num_calls = 0 
                        git_token_index = (git_token_index + 1) % 2
                    result = detect_keys_in_file(user_files)
                    keys = result.keys()
                    for key in keys:
                        try:
                            print 'found key\t', key
                            #r.write(key + "\n" + "\n")
                            r.write(key + "\n" + result[key] + "\n\n")
                        except Exception as e:
                            print e
        print "Time took:", str(datetime.now() - start)


'''
def main(lists_of_repos):
    q = Queue(maxsize=0)
    num_threads = 0
    for list_of_repos in lists_of_repos:
        results = []
        with open(list_of_repos.split(".")[0] + "_results.csv", "wb") as r:
            with open(list_of_repos, "rb") as f:
                for line in f.xreadlines():
                    #start = datetime.now()
                    q.put(line.rstrip())
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
                        #r.write(key + "\n" + "\n")
                        r.write(key + "\n" + result[key] + "\n\n")
                    except Exception as e:
                        print e
    return results


def threadable(results, q):
    while True:
        full_name = q.get()
        username, repo = full_name.split('/')
        user_files = get_files(repo, username)
        results.append(detect_keys_in_file(user_files))
        q.task_done()
'''


if __name__ == "__main__":
    # interested_days = 180
    # if len(sys.argv) == 2: interested_days = sys.argv[1]

    get_batch_repos(23871889)
    #start = datetime.now()
    # in_files = os.listdir(os.getcwd()+"/data") 
    # file_paths = ["data/repo_list_180_days_2015-01-22 20:14:11.237553.csv"] #["data/" + csv for csv in in_files if "data/github_repo_list_"+str(interested_days)+"_days_" in csv]
    # get_keys(file_paths)
    #print "Time took:", str(datetime.now() - start)
    