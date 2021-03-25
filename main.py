from os import write
import parseArgs as arg
import sys
from bs4 import BeautifulSoup, SoupStrainer
import requests
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, HardwareType
from fp.fp import FreeProxy
import json
from threading import Thread

# initialise crawled_links as a dictionary
crawled_links = dict()

# initialise data with 6 different lists used to sort scraped links and tested links
data = {
    'internal': [],
    'external': [],
    'misc': [],
    '200success': [],
    'XXXother': [],
    'failed': []
}
# global variables for access
# TOTAL_TESTED is equal to 1 to account for the first scrape
TESTED_LINKS = []
TOTAL_TESTED = 1

def first_scrape(u):
    # assign variables from the passed object u (newURL())
    url = u.url
    max_pages = int(u.maxPages)
    base_url = u.cleanedURL
    
    # output the URL selected to crawl, maximum number of pages to crawl and 'sanitised' URL
    print(f'URL: {url}\t|\tMaximum Pages: {max_pages}\t|\tClean URL: {base_url}')

    try:
        # creates the first request using the provided URL, setting headers/proxies if required and disabling redirects
        r = requests.get(url, headers=headers, proxies=proxy, allow_redirects=False)

        # check if the request is successful with 200 OK. If true, then add the link to '200success' within data and then crawl that site further - future i should pass 'r' instead of crawler() carrying another request [this affects max pages! - TBD]
        # print the status of the link and the link itself - as per spec
        if r.status_code == 200:
            print(f'[{r.status_code}]\t{url}')
            data['200success'].append(url)

        # BeautifulSoup is used as the HTML parser and using the feature SoupStrainer to easily pull out <a/> tags from the page source
        for c, link in enumerate(BeautifulSoup(r.text, parse_only=SoupStrainer('a'), features="html.parser")):
            # checks if the <a/> tag found has a 'href=""' attribute, if so it will assign to the variable: l
            if link.has_attr('href'):
                l = link['href']
                if l.startswith("/") or l.startswith("."):
                    # internal, join with the base url
                    internal_link = url+l

                    # if the newly created internal link does not end with '/' then append it
                    if not internal_link.endswith("/"):
                        internal_link = internal_link+"/"
                    
                    # if the newly found internal_link is not already in data['internal'] then append it
                    if internal_link not in data['internal']: data['internal'].append(internal_link)

                    # print list of new internal links found - as per spec
                    # duplicates are printed but not stored in data/json file
                    print(f'\tNew internal link found: {internal_link}')
                elif l.startswith("http") or l.startswith("https") or l.startswith("www"):
                    # external link most likely (does include http(s):// links from provided URL - to be fixed)
                    if l not in data['external']: data['external'].append(l)
                else:
                    # Other misc links such as #, ftp, mailto etc.
                    if l not in data['misc']: data['misc'].append(l)

        # first assignment of crawled_links dict with latest data
        crawled_links[url] = data
    except requests.exceptions.HTTPError as e:
        print(e)

    # Once all links are scraped from the first crawl (not tested), the TestCrawledLinks function is called to start the first active crawl. The provided URL and max pages are provided.
    TestCrawledLinks(url, max_pages)

def crawler(url, max_pages):
    # this function will handle the recursive crawling of internal links found to be 200 OK.
    try:
        # creates the first request using the provided URL, setting headers/proxies if required and disabling redirects
        r = requests.get(url, headers=headers, proxies=proxy, allow_redirects=False)

        # BeautifulSoup is used as the HTML parser and using the feature SoupStrainer to easily pull out <a/> tags from the page source
        for c, link in enumerate(BeautifulSoup(r.text, parse_only=SoupStrainer('a'), features="html.parser")):
            if link.has_attr('href'):
                l = link['href']
                if l.startswith("/") or l.startswith("."):

                    # internal, join with the base url and strip preceding '/' only
                    internal = url+l.lstrip("/")

                    # if the newly found internal_link is not already in data['internal'] then append it
                    if internal not in data['internal']: data['internal'].append(internal)

                    # print list of new internal links found - as per spec
                    # duplicates are printed but not stored in data/json file
                    print(f'\tNew internal link found: {internal}')

                    # call TestURL() back to test the newly found internal url
                    TestURL(url, internal, max_pages)
                elif l.startswith("http") or l.startswith("https") or l.startswith("www"):
                    # external link most likely (does include http(s):// links from provided URL - to be fixed)
                    if l not in data['external']: data['external'].append(l)
                else:
                    # Other misc links such as #, ftp, mailto etc.
                    if l not in data['misc']: data['misc'].append(l)
        
        # refresh crawled_links dict with latest data
        crawled_links[url] = data
    except requests.exceptions.HTTPError as e:
        print(e)

def TestCrawledLinks(url, max_pages):
    global TOTAL_TESTED, TESTED_LINKS
    # list of threads to handle currently running threads
    #threads = []

    # initialise internal_links variable with all links found to be internal from the initial scrape
    internal_links = crawled_links[url]['internal']

    for c, link in enumerate(internal_links):
        # check if the total tested links is not equal to or more than the maximum pages requested to crawl
        if TOTAL_TESTED >= max_pages:
            break
        # if an internal link is not in TESTED_LINKS and the total of TOTAL_TESTED is still less than maximum pages requested to crawl, then enter
        elif link not in TESTED_LINKS and TOTAL_TESTED <= max_pages:
            # initialise threads
            #thread = Thread(target=CrawlTestURL, args=(url, link, max_pages,))
            #thread.start()
            #threads.append(thread)

            # +1 to the total tested links and call the TestURL() function to check for page status
            TOTAL_TESTED = c+1
            TestURL(url, link, max_pages)
        else:
            continue

    # wait for all threads to finish then continue with X conditions - tbd
    #for t in threads:
        #t.join()

def TestURL(url, link, max_pages):
    global TESTED_LINKS, TOTAL_TESTED
    # check link is not in TESTED_LINKS and the TOTAL_TESTED is not more than maximum pages to crawl
    if link not in TESTED_LINKS and TOTAL_TESTED <= max_pages:
        try:
            r = requests.get(link, headers=headers, proxies=proxy, allow_redirects=False)
            TESTED_LINKS.append(link)
            TOTAL_TESTED += 1
            
            # check if the request is successful with 200 OK. If true, then add the link to '200success' within data and then crawl that site further - future i should pass 'r' instead of crawler() carrying another request [this affects max pages! - TBD]
            # print the status of the link and the link itself - as per spec
            if r.status_code == 200:
                print(f'[{r.status_code}]\t{link}')
                data['200success'].append(link)
                crawler(link, max_pages)
            # if there is a connection but it's not 200 OK, then add the link to 'XXXother' within data. This can include 404, 503, 403 etc.
            # print the status of the link and the link itself - as per spec
            else:
                print(f'[{r.status_code}]\t{link}')
                data['XXXother'].append(link)
        # if there is a connection error, then add the link to 'failed' within data
        except ConnectionError:
            print(f'Cannot connect to {link}')
            data['failed'].append(link)



def writeOut(url):
    # refresh the crawled_links dict with latest data
    crawled_links[url] = data

    # output all data to a JSON file
    with open('links.json', 'w') as out:
        json.dump(crawled_links, out, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    # generate lists of software and hardware names
    software_names = [SoftwareName.CHROME.value]
    hardware_type = [HardwareType.MOBILE__PHONE]

    # rotating for testing, best to actually point out it's a web crawler in the UA when using for real purposes
    user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)

    # proxies from GB only
    proxyObject = FreeProxy(country_id='GB', rand=True)

    # create proxy URL from proxyObject
    proxy = {"http": f"http://{proxyObject.get()}"}

    # generate headers from user_agent_rotator
    headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}

    # create a newURL object named arg_url and start crawl - objects will allow future crawls of multiple provided URLs with their own arguments
    arg_url = arg.newURL(sys.argv[1:])
    first_scrape(arg_url)
    # Once TOTAL_TESTED is equal to or more than maximum pages selected to crawl (crawler stopped), then writeOut() is called
    writeOut(arg_url.url)