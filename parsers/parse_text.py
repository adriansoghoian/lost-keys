import urllib2
import re
from datetime import datetime

class Parser(object):
    IDENTIFIERS = [
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

    FRONT_WATERMARKS = ["akia", "aiza"]

    END_WATERMARKS = [".apps.googleusercontent.com"]

    ASSIGNMENT_OPERATORS = ["=>", ": ", "\":\"", "= ", '=']

    EXCL_SUBSTR = set([
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

    EXCL_CHARS = set(["<", ">", "\\", "[", "]", "{", "}", "?", "::", "_", "|", "."])


    @staticmethod
    def get_file(file_path):
        """
        @returns: raw url response given a url path
        """
        try:
            response = urllib2.urlopen(file_path).read()
            return response
        except Exception as e:
            #print e, '\t', file_path
            return ""


    @classmethod
    def scan_text(cls, text):
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
                        for wm in cls.END_WATERMARKS:
                            candidates = [m.start() for m in re.finditer(wm, t.lower())]
                            for candidate in candidates:
                                start = 0
                                for a in cls.ASSIGNMENT_OPERATORS:
                                    tmp = t[:candidate].rfind(a[-1])
                                    if tmp > start: start = tmp
                                start += 1
                                span = t[start:candidate+len(wm)]
                                if cls.is_key(span):
                                    output.append(t)
                                    found = True
                                    break
                            if found: break
                        if found: continue
                        for i in cls.IDENTIFIERS:
                            candidates = [m.start() for m in re.finditer(i, t.lower())]
                            for candidate in candidates:
                                for a in cls.ASSIGNMENT_OPERATORS:
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
                                        if cls.is_key(span):
                                            output.append(t)
                                            found = True
                                            break
                                if found: break
                            if found: break
                        if found: continue
                        for wm in cls.FRONT_WATERMARKS:  
                            candidates = [m.start() for m in re.finditer(wm, t.lower())]
                            for candidate in candidates:
                                start = 0
                                for a in cls.ASSIGNMENT_OPERATORS:
                                    tmp = t[:candidate].rfind(a[-1])
                                    if tmp > start: start = tmp
                                start += 1
                                if any(c.isalnum() for c in t[start:candidate]): continue
                                span = t[candidate:].split(' ')[0]
                                if cls.is_key(span): 
                                    output.append(t) 
                                    found = True
                                    break
                            if found: break
                        if found: continue
            return output
        except:
            return []


    @classmethod
    def is_key(cls, candidate):
        """
        @returns: boolean to determine whether or not candidate is an api key
        """
        return ((200 > len(candidate) >= 20) and ((not any(substr in candidate.lower() for substr in cls.EXCL_SUBSTR) and any(c.isalpha() for c in candidate) and any(c.isdigit() for c in candidate)) and (not any(c in candidate for c in cls.EXCL_CHARS) or any(wm in candidate.lower() for wm in cls.END_WATERMARKS) or any(wm in candidate.lower() for wm in cls.FRONT_WATERMARKS))))


    @staticmethod
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

    @classmethod
    def get_keys(cls, file_batch):
        """
        Given a batch of files, process them and return deduped candiates
        """
        if isinstance(file_batch, list):
            repo_dict = {}
            for f in file_batch:
                repo_path = f.split('/')[3] + '/' + f.split('/')[4]
                if repo_path not in repo_dict.keys():
                    repo_dict[repo_path] = []
                candidates_in_file = cls.scan_text(text=cls.get_file(file_path=f))
                candidates_in_file = [{each: f} for each in candidates_in_file]
                repo_dict[repo_path] += candidates_in_file
            return cls.dedupe_dict(repo_dict)
        elif isinstance(file_batch, basestring):
            candidates_in_file = cls.scan_text(cls.get_file(file_batch))
            candidates_in_file = [(each, file_batch) for each in candidates_in_file]
            candidates_in_file = list(set(candidates_in_file))
            return candidates_in_file

if __name__ == '__main__':
    TEST = [
#"https://raw.githubusercontent.com/adriansoghoian/DevPolls/master/models/question.rb",
"https://raw.githubusercontent.com/adriansoghoian/Discoveree/master/discoveree/.env"
#"https://raw.githubusercontent.com/avatch/keycommit/master/keycommit/keycommit/settings.py"
    ]

    #start = datetime.now()
    #parser = Parser(TEST)
    print Parser.get_keys(TEST)
    #print Parser.detect_keys_in_file(TEST)

    #print scan_text_violently("pubKey = GetScriptFOrMultisig(2, pubkeys);")
    #print 'Task Completed:\t', datetime.now() - start

    # print scan_text_violently("        //String accessKey = \"AKIAIA7HTUW2JJUSU3GQ\"; Mike's\n")
    # print scan_text_violently("\n\"ieOnly\":true,\n\"accessKey\":\"AKIAIA7HTUW2JJUSU3GQ\",\n\"secretKey\":\"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\",\n")

