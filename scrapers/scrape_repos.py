import urllib2
import json
from datetime import datetime
from patterns.patterns import *
from secrets import git_access_token

class Scraper(object):
    def __init__(self, username, repo=None): 
        self.username = username
        self.repo = repo
        self.num_key_rotations = 0
        self.access_token_index = 0


    def get_repos(self):
        """
        @reference: https://developer.github.com/v3/repos/#get
        @returns: list of public branch names belonging to username
        """
        endpoint = "https://api.github.com/users/" + \
            self.username + "/repos?per_page=100&access_token=" + git_access_token[self.access_token_index]
        while True:
            rotated_key = False
            try:
                response = urllib2.urlopen(endpoint)
                data = json.load(response)
                repo_list = []
                for repo in data:
                    repo_list.append(repo['name'])
                return repo_list
            except:
                if not rotated_key:
                    self.rotate_access_token()
                    self.num_key_rotations += 1
                    rotated_key = True
                else:
                    print "User: %s has no repos." % (username)
                    return []
        

    def get_branches(self):
        """
        @reference: https://developer.github.com/v3/repos/#list-branches
        @returns: list of public branches in repository
        """
        endpoint = "https://api.github.com/repos/" + self.username + \
            "/" + self.repo + "/branches?access_token=" + git_access_token[self.access_token_index]
        while True:
            try:
                response = urllib2.urlopen(endpoint)
                data = json.load(response)
                branch_list = [branch['name'] for branch in data]
                return branch_list
            except Exception as e:
                # print e, '\t', endpoint
                self.rotate_access_token()
                self.num_key_rotations += 1
                #return []


    def get_branch_files(self, branch='master'):
        """
        @returns: list of file content in a given repository
        """
        endpoint = "https://api.github.com/repos/" + self.username + \
            "/" + self.repo + "/git/trees/" + branch + "?recursive=1&access_token=" + \
            git_access_token[self.access_token_index]
        while True:
            try:
                response = urllib2.urlopen(endpoint)
                data = json.load(response)
                file_list = [f['path'] for f in data['tree']]
                file_path_list = ['https://raw.githubusercontent.com/' + \
                    self.username + '/' + self.repo + '/' + branch + '/' + \
                    file_name for file_name in self.filter_files(file_list)]
                return file_path_list
            except Exception as e:
                # print e, '\t', endpoint
                self.rotate_access_token()
                self.num_key_rotations += 1
                #return []


    @staticmethod
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


    def rotate_access_token(self):
        """
        Updates Github API access token.
        """
        self.access_token_index = (self.access_token_index + 1) % len(git_access_token)


    def get_files(self):
        """
        @returns: list of files belonging to a user across all repositories 
        or list of files belonging to a repository (across all branches)
        """
        file_list = []
        if(self.username is not None and self.repo is None):
            repos = self.get_repos()
            for repo in repos:
                #branches = ['master']
                #for branch in branches:
                self.repo = repo
                file_list += self.get_branch_files()
        elif(self.username is not None and self.repo is not None):
            #branches = get_branches(repo=repo, username=username, access_token=access_token)
            #for branch in branches:
            file_list += self.get_branch_files()
        return file_list


if __name__ == '__main__':
    print 'runtime:\t', str(datetime.now() - start)


