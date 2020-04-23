'''
CHECKLIST

Done:
- grabbed text from html response
- grabbed urls from html response that have valid domains
- tokenized text and filtered out stopwords
- defragmented urls

TODO:
- find way to keep track of: 
	- number of unique pages found
	- longest page in terms of number of words
	- 50 most common words in the entire set of pages
	- number of subdomains found within ics.uci.edu domain (list = [(URL, number), ...]
- annoying things to do (have to run crawler and monitor):
	- detect and avoid inifite traps
	- detect and avoid sets of similar pages with no information
	- detect and avoid crawling very large files
'''




import re, nltk
nltk.download('punkt')
from bs4 import BeautifulSoup
from bs4.element import Comment
from urllib.parse import urlparse, urldefrag, urljoin


with open("stopwords.txt", 'r') as stop:
    stopwords = stop.read()



def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


# helper function used to get all visible text on a page
# source = https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


# code for parsing html text content
def parse_text(soup):
    all_text = soup.findAll(text=True)
    visible_text = filter(tag_visible, all_text)  # returns filter object of visible text
    visible_text_str = u" ".join(t.strip().lower() for t in visible_text)  # convert to str
    # get tokens that contain alphanumeric characters and are not stopwords
    text = list(filter(lambda w: w not in stopwords and re.search('[a-zA-Z0-9]', w), 
                       nltk.word_tokenize(visible_text_str)))
    return text


# helper function used to defragment url links and convert relative urls to absolute urls
def defragment_and_absolute(current_url, new_url):
    parse_new_url = urlparse(new_url)
    if not bool(parse_new_url.netloc):
        # if new url is a relative link, make it absolute with the current url
        new_url = urljoin(current_url, new_url)
        parse_new_url = urlparse(new_url)
    defrag = urldefrag(new_url)
    return defrag.url
    

# code for extracting links
def extract_links(url, soup):
    extracted_links = set()
    for link in soup.findAll('a'):
        clean_url = defragment_and_absolute(url, link.get('href'))
        if is_valid(clean_url): 
            # strip extra '/' from the end of some urls to prevent duplicated urls in set
            parse = urlparse(clean_url)
            clean_url = (parse.netloc + parse.path + parse.params + parse.query).strip('/')
            extracted_links.add(clean_url)
    return list(extracted_links)
            

def extract_next_links(url, resp):
    content = resp.raw_response.content # get content from html response
    soup = BeautifulSoup(content, 'html.parser')
    text = parse_text(soup)
    print("TEXT:", text)
    links = extract_links(url, soup)
    print("NEXT LINKS:", links)
    return list()
    # after done debugging, delete return list(), uncomment:
    #return links


# not done
def is_valid(url):
    try:
        valid = False
        valid_domains = ['.*.ics.uci.edu/*',
                         '.*.cs.uci.edu/*',
                         '.*.informatics.uci.edu/*',
                         '.*.stat.uci.edu/*',
                         'today.uci.edu/department/information_computer_sciences/*']
        parsed = urlparse(url)
        # check for valid domains and paths
        for domain in valid_domains:
            if re.match(domain, url):
                valid = True
        if parsed.scheme not in set(["http", "https"]):
            valid = False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()) and valid

    except TypeError:
        print ("TypeError for ", parsed)
        raise
