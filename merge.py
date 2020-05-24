import json
import math
from collections import defaultdict

#switch function
def numbers_to_strings(num): 
    switcher = { 
        1: "abcdef", 
        2: "ghijklmnopq", 
        3: "rstuvwxyz", 
        4: "0123456789"
    } 
    return switcher.get(num)

if __name__ == "__main__":
    
    for n in range(1,5):
        d = defaultdict() 
        startChar = numbers_to_strings(n)
        #switch function

        #open the file
        #add the term frequency if they overlap
        #split into alphabetical
        for num in range(1,4):
            with open(f"index{num}.json") as f, open("docids.json") as ids:
                data = json.load(f)
                key = json.load(ids)
                for k in data:
                    if k[0] in startChar:
                        if k not in d:
                            d[k] = data[k]
                        else:
                            d[k].update(data[k]) 
        with(open(f"ordered index {n}.json", 'w')) as i:
            json.dump(d, i, sort_keys = True)

    #calculate tfidf
    #tf (token count per document (token_count)/(terms)all terms in document)
    #idf log_e(total docs(total_doc), docs with term(docs_with_term))

    for n in range(1,5):
        with open(f"ordered index {n}.json") as file1, open("docids.json") as docids:
            data = json.load(file1)
            key = json.load(docids)

            total_doc = max(key.keys())
            for token in data:

                idf = math.log( ( (float(total_doc)/(float(len(data[token]))) )))
                for docid in data[token]:
                    tf = data[token][docid]["tfidf"]/key[docid]["length"]
                    data[token][docid]["tfidf"] = float(tf)/float(idf)

            with(open(f"ordered index {n}.json", 'w')) as i:
                json.dump(data, i, sort_keys = True)





