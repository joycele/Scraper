import glob 
import json
from collections import defaultdict
from collections import Counter
from nltk.stem import PorterStemmer

ps = PorterStemmer()

print("Enter the query you wish to search for")
x = input()
searching = x.lower().split(" and ")

answer_dict = dict()
files = glob.glob('D:\\Documents\\UCI stuff\\CS 121\\Search Engine\\indexers\\*')
for f in files:
    with open(f) as json_file:
        d = json.load(json_file)
        #iterate through phrase 
        #e.g [machine learning, bob]
        for phrase in searching:
            #iterate through word in phrase 
            #e.g [machine, learning]
            for word in phrase.split(" "):
                print(word)
                word = ps.stem(word)
                print(word)
                if word in d:
                    for url in d[word]:
                        if url not in answer_dict:
                            answer_dict[url] = d[word][url]
                        else:
                            answer_dict[url] = answer_dict[url] + d[word][url]
#print(answer_dict)
for result in sorted(answer_dict.items(), key = lambda item: item[1], reverse = True)[:5]:
    print (result)





