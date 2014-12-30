import urllib, urllib2, json, sys
from secrets import git_access_token
from datetime import datetime


def get_batch_users(since_index=0):
    endpoint = "https://api.github.com/users?access_token=" + git_access_token + "&since=" + str(since_index)
    response = urllib2.urlopen(endpoint)
    users = json.load(response)
    users_list = [ (user['login'], user['id']) for user in users ]
    return users_list


def loop_over_github(since_index=0, num_calls=4999, results_directory="data/"):
    i = since_index
    with open(results_directory + "user_list_" + str(since_index) + ".csv", 'wb') as f:
        for call in range(num_calls):
            users_list = get_batch_users(i)
            i = users_list[-1][1]
            for each in users_list:
                f.write(each[0] + "," + str(each[1]) + "\n")


if __name__ == "__main__":
    start = datetime.now()
    try:
        start_index = sys.argv[1]
    except:
        start_index = 0
    loop_over_github(since_index=start_index)
    print "Completed in: ", datetime.now() - start
