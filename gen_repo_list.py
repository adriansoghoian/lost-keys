from scrape_repos import get_repos, get_files, filter_files
import datetime
import random

sampling_percentage = 1.00

with open('data/github_user_list.csv', 'rb') as f:
    for index, line in enumerate(f.xreadlines()):
        roll = random.random()
        if roll < sampling_percentage:
            username = line.split(",")[0].rstrip()
            try:
                repos = get_repos(username)
                print '*'*50
                print repos
                # for r in repos:
                #     tic = datetime.datetime.now()
                #     files_in_repo = get_files(repo=r, username=username)
                #     num_files_in_repo.append(len(files_in_repo))
                #     repo_size = 0.0
                #     for f in files_in_repo:
                #         file_text_size = sys.getsizeof(get_file(f))
                #         file_sizes.append(file_text_size)
                #         repo_size += file_text_size
                #         if file_text_size > 10000:
                #             logging.info("[" + str(datetime.datetime.now()) + "]" + " File: " + f + " with size of: " + str(file_text_size))
                #     repo_sizes.append(repo_size)
                #     user_size += repo_size
                #     if (datetime.datetime.now() - tic).total_seconds() > 60:
                #         logging.info("[" + str(datetime.datetime.now()) + "]" + " Repo: " + r + " with size of: " + str(repo_size))
                # user_sizes.append(user_size)
            except Exception as e:
                print e
