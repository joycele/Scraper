import glob 
import json
from collections import defaultdict
from collections import Counter

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
                if word in d.keys():
                    for url in d[word].keys():
                        if url not in answer_dict.keys():
                            answer_dict[url] = d[word][url]
                        else:
                            answer_dict[url] = answer_dict[url] + d[word][url]
#print(answer_dict)

print (sorted(answer_dict.items(), key = lambda item: item[1], reverse = True)[:5])





