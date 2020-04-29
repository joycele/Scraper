import json
from urllib.parse import urlparse
import re
from collections import defaultdict

#Answering number 1 and 2
#longest page
#unique pages
with open('unique_pages1.json') as json_file1, open('unique_pages1.json') as json_file2:
    file = open("report.txt", "w")
    data1 = json.load(json_file1)
    data2 = json.load(json_file2)
    numUnique = len(data1) + len(data2)
    tot = 0
    longest = ""
    for k,v in data1.items():
        if v > tot:
            tot = v
            longest = k
    for k,v in data2.items():
        if v > tot:
            tot = v
            longest = k    
    file.write("The number of unique urls are: " + str(numUnique) + "\n")
    file.write("Url with the most words is: \n\t" + longest + "\n\twith " + str(tot) + " words\n")
    file.close()


#Answering number 4
#subdomains
with open('subdomains.json') as json_file:
    file = open("report.txt", "a")
    data = json.load(json_file)
    subdomains = defaultdict()
    for k,v in data.items():
        parsed = urlparse(k)
        netloc = parsed.netloc
        if netloc not in subdomains.keys():
            subdomains[netloc] = v
        else:
            subdomains[netloc] += v

    file.write("Number of subdomains are: "+ str(len(subdomains))+"\n")
    for k, v in sorted(subdomains.items()):
        file.write("    " + k + ": "+ str(v)+ "\n")
    file.close()
