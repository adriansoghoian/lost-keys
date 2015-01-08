from scrape_repos import get_repos
import matplotlib.pyplot as plt
import sys
import random

sampling_percentage = 0.0001

user_count = 0
repos_count = 0
repo_count_list = []

with open('data/github_user_list.csv', 'rb') as f:
    for index, line  in enumerate(f.xreadlines()):
        roll = random.random()

        if roll < sampling_percentage:
            username = line.split(",")[0].rstrip()
            try:
                user_count += 1
                repos = len(get_repos(username))
                repos_count += repos
                repo_count_list.append(repos)
            except Exception as e:
                print e

print "*"*50
print "Done:\tTotal Users:\t", user_count, "\tAvg Repos/User:\t", repos_count / user_count

plt.hist(repo_count_list, normed=1, color='pink')
plt.xlabel('Repo Count')
plt.ylabel('%')
plt.title(str(sampling_percentage) + ' of Github User Repo Count')
plt.grid()
plt.show()
