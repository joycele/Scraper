import json, sys


f0 = sys.argv[1]
f1 = sys.argv[2]
f2 = sys.argv[3]




# answering #3
t = json.load(open(f0))
h = json.load(open(f1))
e = json.load(open(f2))

combine = t

for word in h:
    if word in combine:
        combine[word] += h[word]
    else:
        combine[word] = h[word]


for token in e:
    if token in combine:
        combine[token] += e[token]
    else:
        combine[token] = e[token]


combine = sorted(combine.items(), key=lambda t: t[1], reverse=True)[:200]


count = 0

for word, frequency in combine:
    if len(word) > 2 and word.islower():
        print(count, "  ", word, '-', frequency)
        count += 1
    if count == 50:
        break
    

