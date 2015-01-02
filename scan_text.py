import urllib2, json, sys, re
from datetime import datetime
from secrets import git_access_token


def get_file(file_path):
    try:
        response = urllib2.urlopen(file_path).read()
        return response
    except:
        return ""


def scan_text(text, band=15):
    """
    Scans an individual file and returns key identifier
    (if found), else, nothing.
    """
    tic = datetime.now()
    text = text.lower()
    identifiers = [
        "secret",
        'api',
        "key",
        "token"
    ]
    assignment_operators = [
        '=',
        ':'
    ]
    chars = set(["\n", "<", ">", "/", "\\", "@", "(", ")", "[", "]", "{", "}", "."])

    output = []

    for i in identifiers:
        candidates = [m.start() for m in re.finditer(i, text)]
        for candidate in candidates:
            span = text[candidate+len(i):candidate+band+len(i)]
            if any(a in assignment_operators for a in span) and not any((c in chars) for c in span):
                words = span.split(" ")
                for w in words:
                    if len(w) > 10:
                        output.append(span)
    toc = datetime.now()
    return dedupe(output), (toc - tic).total_seconds()


def detect_keys_in_file(file_batch):
    tic = datetime.now()
    repo_dict = {}
    scan_text_runtime = None
    for f in file_batch:
        repo_path = f.split('/')[3] + '/' + f.split('/')[4]
        if repo_path not in repo_dict.keys():
            repo_dict[repo_path] = []

        candidates_in_file, scan_text_runtime = scan_text(text=get_file(file_path=f))
        candidates_in_file = [ {each: f} for each in candidates_in_file ]

        repo_dict[repo_path] += candidates_in_file
    toc = datetime.now()
    return dedupe_dict(repo_dict), (toc - tic).total_seconds(), scan_text_runtime


def dedupe_dict(file_dict):
    output_dict = {}
    repos = file_dict.keys()
    for repo in repos: 
        list_of_dicts = file_dict[repo]
        for d in list_of_dicts:
            for k, v in d.iteritems():
                output_dict[k] = v
    return output_dict


def dedupe(seq):
    # http://www.peterbe.com/plog/uniqifiers-benchmark
    keys = {}
    for e in seq:
        keys[e] = 1
    return keys.keys()


if __name__ == '__main__':
    TEST = [
"https://raw.githubusercontent.com/adriansoghoian/DevPolls/master/models/question.rb",
"https://raw.githubusercontent.com/adriansoghoian/Discoveree/master/discoveree/.env"
    ]
    start = datetime.now()

    print detect_keys_in_file(TEST)

    print 'Task Completed:\t', datetime.now() - start
