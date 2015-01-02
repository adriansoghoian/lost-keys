import os


def return_files():
    current_directory = os.getcwd()
    files = os.listdir(current_directory + "/data")
    files = [ "data/" + csv for csv in files if "user_list_" in csv ]
    return files


def combine_files(files):
    file_name = "data/github_user_list.csv"
    with open(file_name, "wb") as f: 
        for user_list_path in files:

            with open(user_list_path, "rb") as user_list:
                for line in user_list.xreadlines():
                    f.write(line.split(",")[0].rstrip() + "\n")



if __name__ == "__main__":
    files = return_files()
    print files
    combine_files(files)