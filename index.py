# index.py

# extra credit implemented:
#  - detect and eliminate exact/near duplicate webpages



import re, os, sys, json
from bs4 import BeautifulSoup
from bs4.element import Comment
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from urllib.parse import urldefrag
from collections import defaultdict
from simhash import Simhash, SimhashIndex


PATH = "DEV"
index = {}  # { token: {docid: {"tfidf": int, "important": bool} }
docids = defaultdict(dict)   # {docid: {"url": str, "length": int} }
urls = {}     # {url: docid}
docid = 0



def tag_visible(element):
    if element.parent.name in ['style', 'script', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


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
    global dup_index 
    dup_index = SimhashIndex(objs, k=3)


# takes in htmlcontent, returns list of words and set of important words
def tokenize(url, soup):
    porter = PorterStemmer()
    # get tokens
    tokenizer = RegexpTokenizer('\w+')
    all_text = soup.findAll(text=True)
    visible_text = filter(tag_visible, all_text)  # returns filter object of visible text
    visible_text_str = u" ".join(t.strip().lower() for t in visible_text)  # convert to str
    # check for uniqueness of web page using simhash
    if len(data) == 0:  # very first link, initialize SimhashIndex
        init_index(docid, visible_text_str)
        similar = []
    else:
        h = Simhash(get_features(visible_text_str))
        similar = dup_index.get_near_dups(h)
        if len(similar) == 0:
            dup_index.add(docid, h)
        else:   # found a near duplicate webpage, return empty list and set
            print("FOUND NEAR DUPLICATES FOR", url, ": DOCIDS", similar)
            return [], set()
    words = tokenizer.tokenize(visible_text_str)
    # get important words
    important_words = set()
    important_tags = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", 'b', "title"])
    for tag in important_tags:
        important_tokens = tokenizer.tokenize(tag.text.lower())
        for token in important_tokens:
            important_words.add(porter.stem(token))
    return words, important_words



# build index with current document
def build_index(tokens, important):
    porter = PorterStemmer()
    for token in tokens:
        stem = porter.stem(token)
        if stem in index:
            if docid in index[stem]:
                index[stem][docid]["tfidf"] += 1
            else:
                index[stem][docid] = {"tfidf": 1, "important": False}
            if stem in important and not index[stem][docid]["important"]:
                index[stem][docid]["important"] = True
        else:
            index[stem] = {docid: {"tfidf": 1, "important": False}}
    # save length of document (needed for tfidf)
    docids[docid]["length"] = len(tokens)
        



if __name__ == "__main__":
    filecount = 1  
    for domain, null, webpages in os.walk(PATH):
        for url in webpages:
            htmlcontent = json.load(open(domain + "/" + url))
            url = urldefrag(htmlcontent["url"]).url
            if url not in urls:
                soup = BeautifulSoup(htmlcontent['content'], 'html.parser') 
                # if there is content
                if soup != None:
                    tokens, important = tokenize(url, soup)
                    if len(tokens) > 0:  # if page contains words
                        docid += 1
                        print("URL:", url, "DOCID:", docid)
                        urls[url] = docid
                        docids[docid]["url"] = url
                        build_index(tokens, important)
            # dump if dict size exceeds 5 megabytes
            if sys.getsizeof(index) / 1048576 >= 5:
                print(f"index dumped {filecount} times")
                with open(f'index{filecount}.json', 'w') as fp:
                    json.dump(index, fp, sort_keys=True)
                index = {}
                filecount += 1
    #dump the remaining files
    print(f"dumped {filecount} times")
    with open(f'index{filecount}.json', 'w') as fp:
        json.dump(index, fp, sort_keys=True)

    print("\n\nPARSED ALL WEB LINKS :", docid, "TOTAL LINKS") 
    # dump url,docid dicts
    with open('docids.json', 'w') as d:
        json.dump(docids, d)
    with open('urls.json', 'w') as u:
        json.dump(urls, u)
            
            
            















        
    
