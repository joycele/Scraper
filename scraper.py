'''
CHECKLIST

Done:
- avoid error html response statuses 
- grab text from html response
- grab urls from html response that have valid domains
- tokenize text and filter out stopwords
- defragment urls
- detect and avoid infinitely appending urls
- detect and avoid crawling very large files
- detect and avoid crawling sets of similar pages
- keep track of: 
	- number of unique pages found
	- longest page in terms of number of words
	- 50 most common words in the entire set of pages
	- number of subdomains found within ics.uci.edu domain (list = [(URL, number), ...]


SET-UP:
- if restarting launcher, delete files if they exist:   ( rm *.pickle *.json ) 
	- unique_pages.pickle
	- longest_page.pickle
	- common_words.json
	- subdomains.json
'''


import re, nltk, os.path, json
#nltk.download('punkt')
from bs4 import BeautifulSoup
from bs4.element import Comment
from urllib.parse import urlparse, urldefrag, urljoin
from simhash import Simhash, SimhashIndex




# set up json files used to keep track of data
if not os.path.isfile("common_words.json"):
    with open("common_words.json", 'w') as common:
        json.dump({}, common)  # { word : frequency }

if not os.path.isfile("subdomains.json"):
    with open("subdomains.json", 'w') as subs:
        json.dump({}, subs)  # { ics url : scraped links on url page }

if not os.path.isfile("unique_pages.json"):
    with open("unique_pages.json", 'w') as unique:
        json.dump({}, unique)  # { new url : page word count }



# global variables: stopwords
with open("stopwords.txt", 'r') as stop:
    stopwords = stop.read()


# code used to update and keep track of report statistics 
def update_report_stats(url, text, next_links):
    # update unique pages
    pages = json.load(open("unique_pages.json"))
    pages[url] = len(text)
    json.dump(pages, open("unique_pages.json", 'w'))
    # update common words
    common_words = json.load(open("common_words.json"))
    for word in text:
        if word in common_words:
            common_words[word] += 1
        else:
            common_words[word] = 1
    json.dump(common_words, open("common_words.json", 'w'))
    # update subdomains
    if ".ics.uci.edu" in urlparse(url).netloc:
        subdomains = json.load(open("subdomains.json"))
        subdomains[url] = len(next_links)
        json.dump(subdomains, open("subdomains.json", 'w'))



# main scraper function called by frontier
def scraper(url, resp):
    if resp.status >= 400:  # return empty list on error response status
        if resp.status >= 600:  # for 600 errors, print error message in resp.error
            print("6XX ERROR:", resp.error)
        return []
    links = extract_next_links(url, resp)
    return links


# simhash implementation for near-duplication detection 
# source = https://leons.im/posts/a-python-implementation-of-simhash-algorithm/ 

# break words into 3-grams
def get_features(s):
    width = 3
    s = s.lower()
    s = re.sub(r'[^\w]+', '', s)
    return [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]


# initialize SimhashIndex
data = {}
def init_index(url, initial_data):
    data[url] = initial_data
    objs = [(str(k), Simhash(get_features(v))) for k, v in data.items()]
    global index 
    index = SimhashIndex(objs, k=3)


# helper function used to get all visible text on a page
# source = https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


# code for parsing html text content
def parse_text(url, soup) -> tuple:
    clean_url = clean_link(url)
    all_text = soup.findAll(text=True)
    visible_text = filter(tag_visible, all_text)  # returns filter object of visible text
    visible_text_str = u" ".join(t.strip().lower() for t in visible_text)  # convert to str
    # check for uniqueness of web page using simhash
    if len(data) == 0:  # very first link, initialize SimhashIndex
        init_index(clean_url, visible_text_str)
        similar = []
    else:
        h = Simhash(get_features(visible_text_str))
        similar = index.get_near_dups(h)
        if len(similar) == 0:  # found a unique webpage with no near duplicate
            index.add(clean_url, h)
    # get tokens that contain alphanumeric characters and are not stopwords
    text = list(filter(lambda w: w not in stopwords and re.search('[a-zA-Z0-9]', w), 
                       nltk.word_tokenize(visible_text_str)))
    return text, similar


# helper function used to defragment url links and convert relative urls to absolute urls
def defragment_and_absolute(current_url, new_url):
    parse_new_url = urlparse(new_url)
    if not bool(parse_new_url.netloc):
        # if new url is a relative link, make it absolute with the current url
        new_url = urljoin(current_url, new_url)
        parse_new_url = urlparse(new_url)
    defrag = urldefrag(new_url)
    return defrag.url


# helper function used to clean up links for stat purposes
def clean_link(url):
    parse = urlparse(url)
    # remove scheme, strip extra '/' from the end of some urls to prevent duplicacies 
    clean_url = (parse.netloc + parse.path + parse.params + parse.query).strip('/')
    return clean_url
    

# code for extracting links
def extract_links(url, soup):
    extracted_links = set()
    for link in soup.findAll('a'):
        clean_url = defragment_and_absolute(url, link.get('href'))
        if is_valid(clean_url):
            extracted_links.add(clean_url)
    return list(extracted_links)
            

def extract_next_links(url, resp):
    links = []
    content = resp.raw_response.content  # get content from html response
    if content == None:
        print("PAGE HAS NO CONTENT")
        return links
    pages = json.load(open("unique_pages.json"))
    if url in pages:
        print("NOT A UNIQUE PAGE:", url)
        return links
    soup = BeautifulSoup(content, 'html.parser')
    text, similar = parse_text(url, soup)
    if text == None:
        return links
    if len(similar) == 0:   # avoid pages that are near duplicates of previously found pages
        if len(text) > 75:  # avoid pages with low content (<75 tokens) 
            links = extract_links(url, soup)
            update_report_stats(url, text, links)
        else:
            print("FOUND PAGE WITH LOW INFORMATION VALUE:", url)
    else:
        print("FOUND NEAR DUPLICATE FOR:", url, "- duplicate:", similar)
    return links


# helper function used to disect url path string and find infinite loop
def infinite_url(parsed):
    infinite = False
    path = parsed.path.lower().strip('/').split('/')  # list of url path components
    unique = set(path)
    if len(path) - len(unique) >= 2:  # if url path has at least three of the same words, infinite=True
        infinite = True
    return infinite
    

def is_valid(url):
    try:
        valid = False
        url = url.lower()
        valid_domains = ['^https?://([a-z0-9]+[.])*ics.uci.edu*',
                         '^https?://([a-z0-9]+[.])*cs.uci.edu*',
                         '^https?://([a-z0-9]+[.])*informatics.uci.edu*',
                         '^https?://([a-z0-9]+[.])*stat.uci.edu*',
                         '^https?://today.uci.edu/department/information_computer_sciences*']
        parsed = urlparse(url)
        # check for valid domains and paths
        for domain in valid_domains:
            if re.match(domain, url):
                valid = True
        # check for infinitely appending urls
        if infinite_url(parsed):
            valid = False
            print("INFINITELY APPENDING URL:", url)
        # avoid all bad web pages found during crawl: 
        if "files/pdf/" in url or "/download/" in url:
            valid = False
            print("IGNORE PAGE:", url)
        if "wics.ics.uci.edu/events" in url or "/calendar" in url:
            valid = False
            print("CALENDAR TRAP PAGE:", url)  # calendar = infinite trap
        if "archive.ics.uci.edu" in url:
            valid = False
            print("IGNORE PAGE:", url)  # archive.ics.uci.edu - low informational value, 404 statuses"
        if "kay" in url and "wordlist.txt" in url:
            valid = False
            print("IGNORE PAGE:", url)  # Professor Kay's wordlist.txt - large file with low informational value"
        if "eppstein/pix" in url:
            valid = False
            print("IGNORE PAGE:", url)  # Professor Eppstein's picture pages - low informational value"
        if "gallery" in url or ("hack" in parsed.netloc and "img" in url):
            valid = False
            print("IGNORE IMAGE PAGE:", url)  # Page is mostly image - low informational value
        if "evoke.ics.uci.edu/qs-personal-data-landscapes-poster" in url:
            valid = False
            print("IGNORE PAGE:", url)  # evoke landscapes poster - large file with low informational value"
        if "grape.ics.uci.edu/wiki/asterix/wiki" in url:
            valid = False
            print("IGNORE PAGE:", url)  # grape.ics.uci.edu asterix wiki page - low informational value"
        regex =  (r".*\.(css|js|bmp|gif|jpe?g|ico|img"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpe?g|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|db|war|apk"
            + r"|thmx|mso|arff|rtf|jar|csv|Z"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$")
        return not re.match(regex, parsed.path) and valid
    except TypeError:
        print ("TypeError for ", parsed)
        raise




