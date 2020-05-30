import json
import math
from collections import defaultdict

#switch function
def numbers_to_strings(num): 
    switcher = { 
        1: "abcdefghijklmnopqrstuvwxyz",
        2: "0123456789"
    } 
    return switcher.get(num)

if __name__ == "__main__":
    alpha = "abcdefghijklmnopqrstuvwxyz"
    
    for n in range (0, len(alpha)):
        d = defaultdict() 
        startChar = alpha[n]
        for num in range(1,4):
            #open the file
            #add the term frequency if they overlap
            #split into alphabetical
            with open(f"index{num}.json") as f, open("docids.json") as ids:
                data = json.load(f)
                key = json.load(ids)
                for k in data:
                    if k[0] in startChar:
                        if k not in d:
                            d[k] = data[k]
                        else:
                            d[k].update(data[k])
        with(open(f"{startChar}.json", 'w')) as i:
            json.dump(d, i, sort_keys = True)  

    #do the same for nums             
    nums = "0123456789"
    d = defaultdict()
    for num in range(1,4):
            with open(f"index{num}.json") as f, open("docids.json") as ids:
                data = json.load(f)
                key = json.load(ids)
                for k in data:
                    if k[0] in nums:
                        if k not in d:
                            d[k] = data[k]
                        else:
                            d[k].update(data[k])
    with(open(f"{nums}.json", 'w')) as i:
            json.dump(d, i, sort_keys = True)  



    #calculate tfidf
    #tf (token count per document (token_count)/(terms)all terms in document)
    #idf log_e(total docs(total_doc), docs with term(docs_with_term))

    for n in range(0,len(alpha)):
        with open(f"{alpha[n]}.json") as file1, open("docids.json") as docids:
            data = json.load(file1)
            key = json.load(docids)

            total_doc = 37867
            for token in data:

                idf = math.log( ( (float(total_doc)/(float(len(data[token]))) )))
                for docid in data[token]:
                    tf = data[token][docid]["tfidf"]/key[docid]["length"]
                    data[token][docid]["tfidf"] = float(tf)/float(idf)

            with(open(f"{alpha[n]}.json", 'w')) as i:
                json.dump(data, i, sort_keys = True)
    
    with open(f"{nums}.json") as file1, open("docids.json") as docids:
        data = json.load(file1)
        key = json.load(docids)

        total_doc = 37867
        for token in data:

            idf = math.log( ( (float(total_doc)/(float(len(data[token]))) )))
            for docid in data[token]:
                tf = data[token][docid]["tfidf"]/key[docid]["length"]
                data[token][docid]["tfidf"] = float(tf)/float(idf)

        with(open(f"{nums}.json", 'w')) as i:
            json.dump(data, i, sort_keys = True)





