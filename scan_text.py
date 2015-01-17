import urllib2, json, sys, re
from datetime import datetime
from secrets import git_access_token


def get_file(file_path):
    try:
        response = urllib2.urlopen(file_path).read()
        return response
    except:
        return ""


def scan_text(text, band=25):
    """
    Scans an individual file and returns key identifier
    (if found), else, nothing.
    """
    text = text.lower()
    identifiers = [
        "secret",
        'api',
        "key",
        "token",
        "oauth",
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
        "aws",
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
    assignment_operators = [
        '=',
        ':',
        '->'
    ]
    exclusion_substr = set([
        "env",
        "token",
        "key",
        "token",
        "secret",
        "config",
        "var"
    ])
    chars = set(["\n", "<", ">", "/", "\\", "@", "[", "]", "{", "}", ".", ","])

    output = []

    for i in identifiers:
        candidates = [m.start() for m in re.finditer(i, text)]
        for candidate in candidates:
            span = text[candidate+len(i):candidate+band+len(i)]
            if any(span.count(a) == 1 for a in assignment_operators):
            # if any(a in assignment_operators for a in span) and span.count(a) == 1 for a in span:
                if not any((c in chars) for c in span):
                    words = span.split(" ")
                    for w in words:
                        if len(w) > 10:
                            if not any(substr in span for substr in exclusion_substr):
                                output.append(text[candidate - 5:candidate + band])
    return dedupe(output)


def scan_text_regex(text):
    try:
        output = []
        text = text.encode('utf-8')
        if text.find("-----BEGIN RSA PRIVATE KEY-----") == 0 and text.find("-----END RSA PRIVATE KEY-----") > 450:
            output.append(text)
        else:
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
            watermarks = ["akia", "aiza", ".apps.googleusercontent.com"]
            assignment_operators = [
                "=>",
                ": ",
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
            excl_chars = set(["<", ">", "/", "\\", "[", "]", "{", "}", "?", ",", "::", "_", "|", "."])

            text = text.split("\n")
            found_key = False
            for t in text:
                line = t.lower()
                if (1000 > len(line) >= 20) and (any(i in line for i in identifiers) or any(wm in line for wm in watermarks)):    
                    for assignment_operator in assignment_operators:
                        if assignment_operator in line:
                            words = line[(line.find(assignment_operator)+len(assignment_operator)):].split(' ')
                            for w in words:
                                if (200 > len(w) >= 20) and (not any(substr in w for substr in exclusion_substr) and any(c.isalpha() for c in w) and any(c.isdigit() for c in w)) and (not any(c in w for c in excl_chars) or any(wm in w for wm in watermarks)):
                                        output.append(t)
                                        found_key = True
                                        break                        
                            if found_key: 
                                found_key = False 
                                break
        return output
    except:
        return []


def scan_text_violently(text):
    try:
        output = []
        text = text.encode('utf-8')
        if text.find("-----BEGIN RSA PRIVATE KEY-----") == 0 and text.find("-----END RSA PRIVATE KEY-----") > 450:
            output.append(text)
        else:
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
            watermarks = ["akia", "aiza", ".apps.googleusercontent.com"]
            assignment_operators = [
                "=>",
                ": ",
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
            excl_chars = set(["<", ">", "/", "\\", "[", "]", "{", "}", "?", ",", "::", "_", "|", "."])

            if (len(text) >= 20):
                possible_keys=[]
                for wm in watermarks:    
                    candidates = [m.start() for m in re.finditer(wm, text.lower())]
                    for candidate in candidates:
                        start = max(text[:candidate].rfind(' '), text[:candidate].rfind('='),text[:candidate].rfind('>')) + 1 
                        length = len(text[start:])
                        if length > 200: length = 200
                        if length < 20: continue
                        span = text[start:start+length].split('\n')[0].split(' ')[0]
                        possible_keys.append(span)
                for i in identifiers:
                    candidates = [m.start() for m in re.finditer(i, text.lower())]
                    for candidate in candidates:
                        start_locations = []
                        for assignment_operator in assignment_operators:
                            start=text[candidate:].find(assignment_operator)
                            if start > -1: 
                                space_location=text[candidate:].find(' ') 
                                if(space_location != -1 and space_location < start and any(c.isalnum() for c in text[candidate+space_location:candidate+start])):
                                    continue
                                start = candidate+start+len(assignment_operator)
                                length = len(text[start:])
                                if length > 200: length = 200
                                if length < 20: continue
                                span = text[start:start+length].split('\n')[0].replace(' ','')
                                possible_keys.append(span)
                for key in possible_keys:
                    if (not any(substr in key.lower() for substr in exclusion_substr) and any(c.isalpha() for c in key) and any(c.isdigit() for c in key)) and (not any(c in key for c in excl_chars) or any(wm in key.lower() for wm in watermarks)):
                        output.append(key)
        return output
    except:
        return []


def detect_keys_in_file(file_batch):
    repo_dict = {}
    for f in file_batch:
        repo_path = f.split('/')[3] + '/' + f.split('/')[4]
        if repo_path not in repo_dict.keys():
            repo_dict[repo_path] = []
        #candidates_in_file = scan_text(text=get_file(file_path=f))
        #candidates_in_file = scan_text_regex(text=get_file(file_path=f))                   
        candidates_in_file = scan_text_violently(text=get_file(file_path=f))
        
        # if (candidates_in_file!=[]):
        #     print candidates_in_file,"\n",f,"\n\n"

        candidates_in_file = [ {each: f} for each in candidates_in_file ]
        repo_dict[repo_path] += candidates_in_file
    return dedupe_dict(repo_dict)


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
