import glob, json, time, math
from collections import defaultdict
from collections import Counter
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from operator import itemgetter
import numpy as np
from heapq import heappush, heappushpop
import tkinter as tk


ps = PorterStemmer()
tokenizer = RegexpTokenizer('\w+')
N = 37867  # total number of documents found
docid_map = json.load(open("docids.json"))


def ignore_words(term):
    filter_words = ['a', 'and', 'the', 'of', 'is', 'to']   # words to ignore in query
    return False if term in filter_words else True


def cosine_similarity(query, document):  # dicts: {term: tfidf}
    query = sorted(query.items())
    document = sorted(document.items())
    q_vector = list(map(itemgetter(1), query))
    d_vector = list(map(itemgetter(1), document))
    cos_sim = np.dot(q_vector, d_vector)/np.linalg.norm(q_vector)*np.linalg.norm(d_vector)
    return cos_sim


def search_query(event):
    canvas.delete('result')  # clear results of previous query from interface
    terms = {}  # term index
    docs = []   # list of all matching documents found
    filtered_docs = []  # list of docs to calculate cosine similarity for
    query = list(filter(ignore_words, tokenizer.tokenize(search.get().lower())))
    print(query)
    stemmed_query = []
    if len(query) == 0:  # ignored too many words
        query = tokenizer.tokenize(search.get().lower())
    first = ""
    index = {}  # index loaded in from disk
    start_time = time.time()
    ############################ BEGIN SEARCH CODE HERE ############################
    for term in sorted(query):
        stemmed = ps.stem(term)
        check = stemmed[0]
        # load in proper index files
        if check in "0123456789":
            if check != first:
                with open("0123456789.json") as f:
                    index = json.load(f)
                first = check
        else:
            if check != first:
                with open(f"{check}.json") as f:
                    index = json.load(f)
                first = check
        if stemmed in index:
            terms[stemmed] = index[stemmed]
            stemmed_query.append(stemmed)
        else:
            print("NO MATCH")
            canvas.create_text(75, 325, text="No results found.", font=("TkTextFont", 15),
                               fill='white', tags='result', anchor='w')
            return
    # get list of documents to calculate cosine similarity with
    for term in terms:
        docs.append(list(terms[term].keys()))
    docs.sort(key=len)
    filtered_docs.extend(list(set(docs[0]).intersection(*docs)))
    if len(filtered_docs) < 10:
        for doc in docs:
            for docid in doc:
                if len(filtered_docs) < 10 and docid not in filtered_docs:
                    filtered_docs.append(docid)
    # start scoring and ranking process
    top_ten_heap = []
    query_scores = {}
    query_length = len(stemmed_query)
    for term in stemmed_query:
        # calculate tfidf for query
        frequency = stemmed_query.count(term)
        tf = float(frequency) / query_length
        query_scores[term] = tf *  (1 + math.log(N/len(terms[term])))
    for docid in filtered_docs:
        # compare cosine similarity with each document and query
        document_scores = {}
        important = False
        for term in stemmed_query:
            if docid in terms[term]:
                document_scores[term] = terms[term][docid]["tfidf"]
                important = terms[term][docid]["important"]
            else:
                document_scores[term] = 0
        cos_sim = cosine_similarity(query_scores, document_scores)
        if important:
            cos_sim *= 10  # increase score if term is important
        if len(top_ten_heap) < 10:  # 10 is length of champion list
            heappush(top_ten_heap, (cos_sim, docid))
        else:
            heappushpop(top_ten_heap, (cos_sim, docid))
    ############################# END SEARCH CODE HERE #############################
    end_time = time.time()
    results = sorted(top_ten_heap, reverse=True)
    if len(results) == 0:
        canvas.create_text(75, 325, text="No results found.", font=("TkTextFont", 15),
                           fill='white', tags='result', anchor='w')
    else:
        canvas.create_text(250, 250, text="Query response time: {}s".format(end_time - start_time),
                           fill='white', tags='result', anchor='w')
        canvas.create_text(50, 350, text="Displaying top results:", font=("TkTextFont", 13),
                           fill='white', tags='result', anchor='w')
        for i in range(len(results)):   # display at least top 10
            canvas.create_text(50, 400 + 20 * i, text=docid_map[results[i][1]]["url"], font=("TkTextFont", 10),
                               fill='white', tags='result', anchor='w')
        
    
if __name__ == '__main__':
    root = tk.Tk()
    root.title("CS121 Search Engine")

    canvas = tk.Canvas(root, width=1000, height=700, bg='#222222')
    canvas.pack(fill='both', expand=True)


    canvas.create_text(800, 20, text="Joyce and Jun's Really Rad Search Engine", font=('Courier', 10), fill='white')
    canvas.create_text(500, 150, text="JOOGLE", font=('Courier', 50), fill='white')

    search = tk.Entry(root, width=60, font=('TkTextFont', 13))
    canvas.create_window(500, 225, window=search)
        
    search.bind('<Return>', search_query)
    
    root.mainloop()



































