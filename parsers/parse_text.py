import urllib2
import re
from datetime import datetime


identifiers = [
    "secret",
    "api",
    "key",
    "token",
    "oauth",
    "account",
    "access",
    "facebook",
    "google",
    "twitter",
    "youtube",
    "accu",
    "linkedin",
    "amazon",
    "twilio",
    "pinterest",
    "flickr",
    "foursquare",
    "paypal",
    "stripe",
    "venmo",
    "yahoo",
    "pdx",
    "yelp",
    "digg",
    "soundcloud",
    "spotify",
    "rdio",
    "bitly",
    "azure",
    "salesforce",
    "trello",
    "wordpress"
]

front_watermarks = ["akia", "aiza"]

end_watermarks = [".apps.googleusercontent.com"]

assignment_operators = [
    "=>",
    ": ",
    "\":\"",
    "= ",
    '='
]

exclusion_substr = set([
    "env",
    "config",
    "var",
    "***",
    "secret",
    "api",
    "key",
    "token",
    "oauth"
])

excl_chars = set(["<", ">", "\\", "[", "]", "{", "}", "?", "::", "_", "|", "."])


def get_file(file_path):
    """
    @returns: raw url response given a url path
    """
    try:
        response = urllib2.urlopen(file_path).read()
        return response
    except Exception as e:
        # print e, '\t', file_path
        return ""


def scan_text(text):
    """
    Identifies potential api keys in a text file
    """
    try:
        output = []
        text = text.decode('utf-8')
        if text.find("-----BEGIN RSA PRIVATE KEY-----") == 0 and text.find("-----END RSA PRIVATE KEY-----") > 450:
            output.append(text)
        else:
            text = text.split("\n")
            for t in text:
                found = False
                if 1000 > len(t) >= 20:
                    for wm in end_watermarks:
                        candidates = [m.start() for m in re.finditer(wm, t.lower())]
                        for candidate in candidates:
                            start = 0
                            for a in assignment_operators:
                                tmp = t[:candidate].rfind(a[-1])
                                if tmp > start: start = tmp
                            start += 1
                            span = t[start:candidate+len(wm)]
                            if is_key(span):
                                output.append(t)
                                found = True
                                break
                        if found: break
                    if found: continue
                    for i in identifiers:
                        candidates = [m.start() for m in re.finditer(i, t.lower())]
                        for candidate in candidates:
                            for a in assignment_operators:
                                start = t[candidate:].find(a)
                                if start > -1: 
                                    space_location = t[candidate:].find(' ') 
                                    if space_location != -1 and space_location < start and any(c.isalnum() for c in t[candidate + space_location:candidate + start]): continue
                                    slash_location = t[candidate:].find('/')
                                    if slash_location != -1 and slash_location < start: continue
                                    start += candidate + len(a)
                                    length = min(len(t[start:]), 200)
                                    span = t[start:start + length]
                                    front_bracket_location = span.find('(')
                                    back_bracket_location = span.find(')')
                                    if front_bracket_location != -1 and back_bracket_location != -1 and front_bracket_location < back_bracket_location and span[front_bracket_location:back_bracket_location].find(',') > -1: continue
                                    span = span.split(' ')[0]
                                    if is_key(span):
                                        output.append(t)
                                        found = True
                                        break
                            if found: break
                        if found: break
                    if found: continue
                    for wm in front_watermarks:  
                        candidates = [m.start() for m in re.finditer(wm, t.lower())]
                        for candidate in candidates:
                            start = 0
                            for a in assignment_operators:
                                tmp = t[:candidate].rfind(a[-1])
                                if tmp > start: start = tmp
                            start += 1
                            if any(c.isalnum() for c in t[start:candidate]): continue
                            span = t[candidate:].split(' ')[0]
                            if is_key(span): 
                                output.append(t) 
                                found = True
                                break
                        if found: break
                    if found: continue
        return output
    except:
        return []


def is_key(candidate):
    """
    @returns: boolean to determine whether or not candidate is an api key
    """
    return ((200 > len(candidate) >= 20) and ((not any(substr in candidate.lower() for substr in exclusion_substr) and any(c.isalpha() for c in candidate) and any(c.isdigit() for c in candidate)) and (not any(c in candidate for c in excl_chars) or any(wm in candidate.lower() for wm in end_watermarks) or any(wm in candidate.lower() for wm in front_watermarks))))


def detect_keys_in_file(file_batch):
    """
    Given a batch of files, process them and return deduped candiates
    """
    repo_dict = {}
    for f in file_batch:
        repo_path = f.split('/')[3] + '/' + f.split('/')[4]
        if repo_path not in repo_dict.keys():
            repo_dict[repo_path] = []

        candidates_in_file = scan_text(text=get_file(file_path=f))
        candidates_in_file = [{each: f} for each in candidates_in_file]

        repo_dict[repo_path] += candidates_in_file

    return dedupe_dict(repo_dict)


def dedupe_dict(file_dict):
    """
    dedupes a dictionary
    """
    output_dict = {}
    repos = file_dict.keys()
    for repo in repos:
        list_of_dicts = file_dict[repo]
        for d in list_of_dicts:
            for k, v in d.iteritems():
                output_dict[k] = v
    return output_dict


if __name__ == '__main__':
    start = datetime.now()
