import urllib2
import json
from datetime import datetime
from patterns.patterns import *
from secrets import git_access_token


def get_repos(username, access_token=git_access_token[0]):
    """
    @reference: https://developer.github.com/v3/repos/#get
    @returns: list of public branch names belonging to username
    """
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
    """
    @reference: https://developer.github.com/v3/repos/#list-branches
    @returns: list of public branches in repository
    """
    endpoint = "https://api.github.com/repos/" + username + \
        "/" + repo + "/branches?access_token=" + access_token
    try:
        response = urllib2.urlopen(endpoint)
        data = json.load(response)
        branch_list = [branch['name'] for branch in data]
        return branch_list
    except Exception as e:
        # print e, '\t', endpoint
        return []


def get_files(repo, username, branch='master', access_token=git_access_token[0]):
    """
    @returns: list of file content in a given repository
    """
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
        # print e, '\t', endpoint
        return []


def filter_files(files):
    """
    @returns: list of files filtered through @patterns list
    """
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
    """
    @returns: list of files belonging to a user across all repositories
    """
    repos = get_repos(username=username)
    user_file_list = []
    for repo in repos:
        branches = ['master']
        for branch in branches:
            user_file_list += get_files(repo=repo, username=username)
    return user_file_list


def get_repo_file_list(username, repo, access_token=git_access_token[0]):
    """
    @returns: list of files belonging to a repository across all branches
    """
    file_list = []
    branches = get_branches(repo=repo, username=username, access_token=access_token)
    for branch in branches:
        file_list += get_files(repo=repo, username=username, branch=branch, access_token=access_token)
    return file_list


if __name__ == '__main__':
    print 'runtime:\t', str(datetime.now() - start)
