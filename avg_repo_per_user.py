from scrape_repos import get_repos, get_files, filter_files
from scan_text import get_file
import matplotlib.pyplot as plt
import sys
import os
import random
import numpy as np
import datetime
import logging

def logging_config  ():
    program_name = os.path.basename(__file__)
    log_name = "logs/" + program_name + " " + str(datetime.datetime.now()) + ".log"
    logging.basicConfig(filename=log_name, level=logging.INFO)

logging_config()
sampling_percentage = 0.00001

user_count = 0
repos_count = 0
repo_count_list = []

# with open('data/github_user_list.csv', 'rb') as f:
#     for index, line  in enumerate(f.xreadlines()):
#         roll = random.random()

#         if roll < sampling_percentage:
#             username = line.split(",")[0].rstrip()
#             try:
#                 user_count += 1
#                 repos = len(get_repos(username))
#                 repos_count += repos
#                 repo_count_list.append(repos)
#             except Exception as e:
#                 print e

# print "*"*50
# print "Done:\tTotal Users:\t", user_count, "\tAvg Repos/User:\t", repos_count / user_count

# plt.hist(repo_count_list, normed=1, color='pink')
# plt.xlabel('Repo Count')
# plt.ylabel('%')
# plt.title(str(sampling_percentage) + ' of Github User Repo Count')
# plt.grid()
# plt.show()

file_sizes = []
repo_sizes = []
user_sizes = []

num_files_in_repo = []

with open('data/github_user_list.csv', 'rb') as f:
    for index, line  in enumerate(f.xreadlines()):
        roll = random.random()
        if roll < sampling_percentage:
            username = line.split(",")[0].rstrip()
            try:
                print datetime.datetime.now(), "\t", username, "\tUserNumber:\t", user_count
                user_count += 1
                user_size = 0.0
                repos = get_repos(username)
                for r in repos:
                    tic = datetime.datetime.now()
                    files_in_repo = get_files(repo=r, username=username)
                    num_files_in_repo.append(len(files_in_repo))
                    repo_size = 0.0
                    for f in files_in_repo:
                        file_text_size = sys.getsizeof(get_file(f))
                        file_sizes.append(file_text_size)
                        repo_size += file_text_size
                        if file_text_size > 10000:
                            logging.info("[" + str(datetime.datetime.now()) + "]" + " File: " + f + " with size of: " + str(file_text_size))
                    repo_sizes.append(repo_size)
                    user_size += repo_size
                    if (datetime.datetime.now() - tic).total_seconds() > 60:
                        logging.info("[" + str(datetime.datetime.now()) + "]" + " Repo: " + r + " with size of: " + str(repo_size))
                user_sizes.append(user_size)
            except Exception as e:
                print e

print "*"*50
print "Scanned:\t", user_count, "\t Users"
print "Avg File Size:\t", np.mean(file_sizes), "\tStd:\t", np.std(file_sizes), "\tMedian:\t", np.median(file_sizes)
print "Avg Repo Size:\t", np.mean(repo_sizes), "\tStd:\t", np.std(repo_sizes), "\tMedian:\t", np.median(repo_sizes)
print "Avg User Size:\t", np.mean(user_sizes), "\tStd:\t", np.std(user_sizes), "\tMedian:\t", np.median(user_sizes)

print "Avg Number of Files per Repo:\t", np.mean(num_files_in_repo), "\tStd:\t", np.std(num_files_in_repo), "\tMedian:\t", np.median(num_files_in_repo)
