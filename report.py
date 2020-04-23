from urllib.parse import urlparse
import re
from collections import defaultdict
#Answering number 1 
#Number of unique urls
def unique(sites):
    file = open("answers.txt","w")
    uniques = list()
    for i in sites:
        if i not in uniques:
            uniques.append(i)
    numUnique = len(uniques)
    file.write("The number of unique urls are", numUnique)
    file.close()

#Answering number 2
#Longest Page with most words
def longest(words):
    file = open("answers.txt", "a")
    longestPage = ""
    maxWords = 0
    #0 is the url 1 is the words 2 is the word count
    for i in range(0, len(words), 3):
        if words[i+2] > maxWords:
            longestPage = words[i]
            maxWords = words[i+2]
    file.write("Url with the most words is: " + longestPage)
    file.close()

#Answering number 3
#50 most common words
def commonWords(words):
    file = open("answers.txt", "a")
    d = dict()
    for word in words[1::3]:
        word = str(word).lower().strip().replace("'", '')
        if word in d:
            d[word] = d[word] + 1
        else:
            d[word] = 1
    ans = []
    for i in range(50):
        wordCounts = d.values()
        maxWord = max(wordCounts)
        ans.append(maxWord)
        del d[maxWord]
    
    file.write("The 50 most common words are: \n")
    for i in ans:
        file.write(i + "\n")
    file.close()

#Answering number 3
#subdomains
def subdomains(sites):
    file = open("answers.txt", "a")
    subdomain = defaultdict(int)
    for url in sites:
        parsed = urlparse(url)
        netloc = parsed.netloc
        if netloc.startswith("www."):
            netloc = netloc.strip("www.")
        words = netloc.split(".")
        ics = ".".join(words[1:])
        if ics == 'ics.uci.edu':
            subdomain[netloc]+=1
    file.write("Number of subdomains are: "+ str(len(subdomains))+"\n")
    subdomain = sorted(subdomain)
    for k, v in subdomain.items():
        file.write(k + ": "+ str(v)+ "\n")
    file.close()


if __name__ == "__main__":
    f1 = open("urls.txt", "r")
    f2 = open("words.txt", "r")
    urls = list()
    words = list()
    for line in f1:
        urls.append(line.rstrip())
    for line in f2:
        words.append(line.rstrip())

    unique(urls)
    longest(words)
    commonWords(words)
    subdomains(urls)
        
