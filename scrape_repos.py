import urllib2, json, sys
from datetime import datetime
from patterns.patterns import *
from secrets import git_access_token


def get_repos(username, access_token=git_access_token[0]):
    endpoint = "https://api.github.com/users/" + \
        username + "/repos?per_page=100&access_token=" + access_token
    try:
        response = urllib2.urlopen(endpoint)
        data = json.load(response)
        repo_list = []
        for repo in data:
            repo_list.append(repo['name'])
    except:
        print "User: %s has no repos." % (username)
        repo_list = []
    return repo_list


def get_branches(repo, username, access_token=git_access_token[0]):
    endpoint = "https://api.github.com/repos/" + username + \
        "/" + repo + "/branches?access_token=" + access_token
    try:
        response = urllib2.urlopen(endpoint)
        data = json.load(response)
        branch_list = [branch['name'] for branch in data]
        return branch_list
    except Exception as e:
        print e, '\t', endpoint
        return []


def get_files(branch, repo, username, access_token=git_access_token[0]):
    endpoint = "https://api.github.com/repos/" + username + \
        "/" + repo + "/git/trees/" + branch + "?recursive=1&access_token=" + \
        access_token
    try:
        response = urllib2.urlopen(endpoint)
        data = json.load(response)
        file_list = [f['path'] for f in data['tree']]
        file_path_list = ['https://raw.githubusercontent.com/' + username + '/' + repo + '/' + branch + '/' + file_name for file_name in filter_files(file_list)]
        return file_path_list
    except Exception as e:
        print e, '\t', endpoint
        return []


def filter_files(files):
    output = []
    for each in files:
        try:
            if not any(file_type_pattern.encode('utf-8').lower() in str(each).encode('utf-8').lower() for file_type_pattern in file_type_patterns):
               if not any(file_paths_pattern.encode('utf-8').lower() in str(each).encode('utf-8').lower() for file_paths_pattern in file_paths_patterns):
                    extension = "." + each.split('.')[-1].lower()                    
                    if not any((extension == extensions_pattern.encode('utf-8').lower()) for extensions_pattern in extensions_patterns): 
                        output.append(each)
        except UnicodeEncodeError:
            continue
    return output


def get_user_file_list(username):
    repos = get_repos(username=username)
    user_file_list = []
    for repo in repos:
        # branches = get_branches(repo=repo, username=username)
        branches = ['master']
        for branch in branches:
            user_file_list += get_files(
                branch=branch, repo=repo, username=username)
    return user_file_list


def get_repo_file_list(username, repo):
    file_list = []
    branches = get_branches(repo=repo, username=username)
    for branch in branches:
        file_list += get_files(branch=branch, repo=repo, username=username)
    return file_list


if __name__ == '__main__':
    start = datetime.now()
    username = sys.argv[1]

    user_file_list = get_user_file_list(username=username)
    for f in user_file_list:
        print f

    print 'Task Completed:\t', datetime.now() - start
