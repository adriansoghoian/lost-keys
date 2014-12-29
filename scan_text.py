import urllib2, json, sys, re
from datetime import datetime
from secrets import git_access_token


def get_file(file_path):
    response = urllib2.urlopen(file_path).read()
    return response


def scan_text(text, band=15):
    """
    Scans an individual file and returns key identifier
    (if found), else, nothing.
    """
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
    return dedupe(output)


def detect_keys_in_file(file_batch):
    repo_dict = {}
    current_repo = file_batch[0].split('/')[3] + '/' + file_batch[0].split('/')[4]
    repo_dict[current_repo] = {}

    for f in file_batch:
        username = f.split('/')[3]
        repo = f.split('/')[4]
        r = username + '/' + repo

        if 'repo_dict' not in repo_dict[r].keys():
            repo_dict[r]['repo_keys'] = []

        if r in repo_dict.keys():
            candidates_in_file = scan_text(text=get_file(file_path=f))
            repo_dict[r]['repo_keys'] += candidates_in_file
            repo_dict[r][f] = candidates_in_file
        else:
            repo_dict[r]['repo_keys'] = dedupe(repo_dict[r]['repo_keys'])
            repo_dict[r] = {}

        # if r == current_repo:
        #     candidate = scan_text(text=get_file(file_path=f))
        #     current_repo_candidates += candidate
        #     file_paths += f*len(candidate)
        # else:
        #     current_repo = r
        #     current_repo_dict = {}

        # candidate = scan_text(text=get_file(file_path=f)

        # username = f.split('/')[3]
        # repo = f.split('/')[4]
        # candidate = scan_text(text=get_file(file_path=f)
        # if repo in candidates.keys():
        #     for c in candidate:
        #         if c not in candidates[repo]
        #         # candidates[repo] += 
        #     candidates[repo].append(candidate))
        # else:
        #     candidates[repo] = candidate

    return repo_dict


def dedupe(seq):
    # http://www.peterbe.com/plog/uniqifiers-benchmark
    keys = {}
    for e in seq:
        keys[e] = 1
    return keys.keys()


if __name__ == '__main__':
    TEST = [
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/key/__init__.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/key/admin.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/key/found_keys.p',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/key/helpers.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/key/items.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/key/migrations/0001_initial.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/key/migrations/__init__.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/key/models.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/key/patterns.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/key/scanner.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/key/scraper.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/key/tests.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/key/twilio.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/key/twilio_auth_token.p',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/key/twilio_auth_token.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/key/views.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/keycommit/__init__.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/keycommit/settings.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/keycommit/urls.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/keycommit/wsgi.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/manage.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/static/app.js',
'https://raw.githubusercontent.com/AVatch/keycommit/master/keycommit/static/scan.js',
'https://raw.githubusercontent.com/AVatch/keycommit/master/parser/config.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/parser/key_finder.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/scrapscrap/scrapscrap/__init__.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/scrapscrap/scrapscrap/items.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/scrapscrap/scrapscrap/pipelines.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/scrapscrap/scrapscrap/settings.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/scrapscrap/scrapscrap/spiders/__init__.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/scrapscrap/scrapscrap/spiders/github_spider.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/scrapscrap/scrapy.cfg',
'https://raw.githubusercontent.com/AVatch/keycommit/master/scrapscrap/twilio.py',
'https://raw.githubusercontent.com/AVatch/keycommit/master/scrapscrap/urls.p',
    ]
    start = datetime.now()

    print detect_keys_in_file(TEST)

    print 'Task Completed:\t', datetime.now() - start
