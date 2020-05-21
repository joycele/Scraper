import glob, json, time
from collections import defaultdict
from collections import Counter
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
import tkinter as tk

ps = PorterStemmer()
tokenizer = RegexpTokenizer('\w+')




def search_query(event):
    canvas.delete('result')  # clear results of previous query from interface
    query = search.get().lower()
    start_time = time.time()
    query = tokenizer.tokenize(search.get().lower())
    print(query)
    ############################ BEGIN SEARCH CODE HERE ############################
    answer_dict = dict()
    files = glob.glob('D:\\Documents\\UCI stuff\\CS 121\\Search Engine\\indexers\\*')
    for f in files:
        with open(f) as json_file:
            d = json.load(json_file)
            for word in query:
                word = ps.stem(word)
                if word in d:
                    for url in d[word]:
                        if url not in answer_dict:
                            answer_dict[url] = d[word][url]
                        else:
                            answer_dict[url] = answer_dict[url] + d[word][url]
    results = sorted(answer_dict.items(), key = lambda item: item[1], reverse = True)
    ############# END CODE HERE, STORE IN RESUTLS IN VARIABLE 'results' ###############
    end_time = time.time()
    canvas.create_text(250, 250, text="Found {} results in {}s".format(len(results), end_time-start_time),
                       fill='white', tags='result', anchor='w')
    canvas.create_text(50, 350, text="Displaying top results:", font=("TkTextFont", 13),
                       fill='white', tags='result', anchor='w')
    for i in range(min(10, len(results))):   # display at least top 10
        canvas.create_text(50, 400 + 20 * i, text=results[i], font=("TkTextFont", 10),
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



































