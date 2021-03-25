import getopt
import sys
import re

class newURL():
    def __init__(self, argv):
        self.url = ''
        self.cleanedURL = ''
        # default max pages to crawl is 10
        self.maxPages = 10
        try:
            # u/url and m/maxpages expect input. h/help as no input.
            opts, args = getopt.getopt(argv,"u:m:h",["url=","maxpages="])
        except getopt.GetoptError:
            print ('\nUSAGE: main.py -u <url> -m <number:default is 10>')
            print ('EXAMPLE: main.py -u https://monzo.com -m 50\n')
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print ('\nUSAGE: main.py -u <url> -m <number:default is 10>')
                print ('EXAMPLE: main.py -u https://monzo.com -m 50\n')
                sys.exit()
            elif opt in ("-u", "--url"):
                # assign input after URL argument to self.url
                self.url = arg
                self.cleanedURL = self.sanitiseURL()
            elif opt in ("-m", "--maxpages"):
                # assign input after max pages argument to self.maxPages
                self.maxPages = arg

    def sanitiseURL(self):
        # this function simply removes any preceding "http(s)://(www.)" and tailing "/" from the provided URL
        reg = re.compile(r"https?://(www\.)?")
        u = reg.sub('', self.url).strip().strip('/')
        return u

