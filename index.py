import glob
import re, os.path, json
from bs4 import BeautifulSoup
from bs4.element import Comment
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize,word_tokenize
import sys
from collections import defaultdict

#from sklearn.feature_extraction.text import TfidfVectorizer
#from sklearn.feature_extraction.text import CountVectorizer

#format for dictionary
    #{word: {url: count of word}}

#things to do
#tf-idf score (needed for optimization)
#merge (although i dont see the point of this
#       becuase we are just going to split it up for the searcher anyways)


ps = PorterStemmer()

# global variables: stopwords
with open("stopwords.txt", 'r') as stop:
    stopwords = stop.read()

#used from spacetime_crawerl
# helper function used to get all visible text on a page
# source = https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


#used from spacetime_crawerl without the simHash
def parse_text(soup):
    stemmed_list = list()
    all_text = soup.findAll(text=True)
    visible_text = filter(tag_visible, all_text)  # returns filter object of visible text
    visible_text_str = u" ".join(t.strip().lower() for t in visible_text)  # convert to str
    text = list(filter(lambda w: w not in stopwords and re.search('[a-zA-Z0-9]', w), 
                      nltk.word_tokenize(visible_text_str)))
    #stem the list
    
    for word in text:
        stemmed_list.append(ps.stem(word))
    return stemmed_list

def parse_important(soup):
    stemmed_list = list()
    for important in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", 'b', "title"]):
        text = list(filter(lambda w: w not in stopwords and re.search('[a-zA-Z0-9]', w), 
                      nltk.word_tokenize(important.text.strip())))
        #stem the list
        for word in text:
            stemmed_list.append(ps.stem(word))
    return stemmed_list

#read json files containing html content
#using glob to read from multiple files at the same time
#adjust the file path to whatever you need just keep the dev\\*\\* at the end
files = glob.glob('D:\\Documents\\UCI stuff\\CS 121\\Search Engine\\DEV\\*\\*')
size_of_documents = 0
d = defaultdict()   #entire indexer
filecount = 1       #allows me to write mutiple files 
for f in files:
    with open(f) as json_file:
        data = json.load(json_file)
        soup = BeautifulSoup(data['content'], 'html.parser')

        #if there is content
        if soup != None:
            #first find the text in the headers, titles and bold
            #if inside one of those 3, add 10 to occurance
            for word in parse_important(soup):
                #when word not in the dictionary
                if word not in d.keys():
                    d[word] = dict([(  data['url'], 10)])
                else:
                    #when word and url in dictionnary
                    if data['url'] in d[word].keys():
                        d[word][ data['url']] = d[word][ data['url']] + 10
                    #when word in dictionary but url not in dictionary
                    else:
                        d[word][data['url']] = 10

            #Do the rest of the text
            for word in parse_text(soup):
                #when word not in the dictionary
                if word not in d.keys():
                    d[word] = dict([( data['url'], 1)])
                else:
                    #when word and url in dictionnary
                    if data['url'] in d[word].keys():
                        d[word][ data['url']] = d[word][ data['url']] + 1
                    #when word in dictionary but url not in dictionary
                    else:
                        d[word][data['url']] = 1

            #tf-idf score hardest part


    #dump if dict size exceeds 5 megabytes
    #size is changeable
    if (sys.getsizeof(d) / 1048576) >= 5:
        print(f"indexdumped {filecount} times")
        with open(f'indexers\\index{filecount}.json', 'w') as fp:
            json.dump(d,fp, sort_keys = True)
        d = defaultdict()
        filecount = filecount + 1
        print(size_of_documents)
    
    size_of_documents = 1 + size_of_documents
    print("got here")

#dump the remaining files
print(f"dumped {filecount} times")
with open(f'indexers\\index{filecount}.json', 'w') as fp:
    json.dump(d,fp, sort_keys = True)
filecount = filecount + 1
print(size_of_documents)

