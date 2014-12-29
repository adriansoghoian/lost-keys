import urllib2, json, sys
from datetime import datetime
from patterns.patterns import patterns
from secrets import git_access_token


def get_repos(username, access_token=git_access_token):
    endpoint = "https://api.github.com/users/" + \
        username + "/repos?access_token=" + access_token
    response = urllib2.urlopen(endpoint)
    data = json.load(response)
    repo_list = [repo['name'] for repo in data]
    return repo_list


def get_files(repo, username, access_token=git_access_token):
    endpoint = "https://api.github.com/repos/" + \
        username + "/" + repo + "/git/trees/master?recursive=1&access_token="\
        + access_token
    response = urllib2.urlopen(endpoint)
    data = json.load(response)
    file_list = [f['path'] for f in data['tree']]
    return filter_files(file_list)


def filter_files(files):
    output = []
    for each in files:
        try:
            if not any(pattern.encode('utf-8') in str(each).encode('utf-8') for pattern in patterns):
                output.append(each)
        except UnicodeEncodeError:
            print "Error:\t", each
            continue
    return output


if __name__ == '__main__':
    start = datetime.now()
    username = sys.argv[1]

    repos = get_repos(username=username)
    master_file = []
    for repo in repos:
        master_file += get_files(repo=repo, username=username)

    print "*"*50
    print master_file
    print "*"*50
    print len(master_file)
    print 'Task Completed:\t', datetime.now() - start
