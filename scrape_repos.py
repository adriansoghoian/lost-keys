import urllib2, json, sys, re
from datetime import datetime
from patterns.patterns import patterns
from secrets import git_access_token


def get_repos(username, access_token=git_access_token):
    endpoint = "https://api.github.com/users/" + \
        username + "/repos?access_token=" + access_token
    response = urllib2.urlopen(endpoint)
    data = json.load(response)
    repo_list = []
    for repo in data:
        if(repo['fork']==False):
            repo_list.append(repo['name'])
        else:
            print 'Skipping forked repo'
     #= [repo['name'] for repo in data]
    return repo_list


def get_files(repo, username, access_token=git_access_token):
    endpoint = "https://api.github.com/repos/" + \
        username + "/" + repo + "/git/trees/master?recursive=1&access_token="\
        + access_token
    try:
        response = urllib2.urlopen(endpoint)
        data = json.load(response)
        file_list = [f['path'] for f in data['tree']]
        file_path_list = ['https://raw.githubusercontent.com/'+username+'/'+repo+'/master/'+file_name for file_name in filter_files(file_list)]
        return file_path_list
    except Exception as e:
        return []


def filter_files(files):
    output = []
    # pattern_regex = re.compile(patterns.)
    for each in files:
        try:
            if not any(pattern.encode('utf-8') in str(each).encode('utf-8') for pattern in patterns):
                if '.' in each.split('/')[-1]:
                    output.append(each)
        except UnicodeEncodeError:
            # print "Error:\t", each
            continue
    return output


def get_user_file_list(username):
    repos = get_repos(username=username)
    user_file_list = []
    for repo in repos:
        user_file_list += get_files(repo=repo, username=username)
    return user_file_list


if __name__ == '__main__':
    start = datetime.now()
    username = sys.argv[1]

    user_file_list = get_user_file_list(username=username)
    for f in user_file_list:
        print f

    print 'Task Completed:\t', datetime.now() - start
