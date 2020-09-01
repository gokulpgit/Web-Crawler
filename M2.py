import csv
import json
from nltk.stem import PorterStemmer
#from sklearn.feature_extraction.text import TfidfVectorizer
from tfidf import TfIdf
from bs4 import BeautifulSoup
import networkx as nx
import re
from lxml import html
from collections import defaultdict

query = input("Enter a term to search: ")

ps = PorterStemmer()

query = [ps.stem(word) for word in query.lower().split()]
list_of_postings = []
important = []
rankDict = defaultdict(int)


for word in query:
    word = ps.stem(word)

    postings = []
    #open file based on first letter
    if word[0].isdigit():
        letterfile = open("num.csv")
    else:
        letterfile = open(word[0] + ".csv", "r")
    #find word in file
    data = (csv.reader(letterfile))
    for row in data:
        if len(row) == 2 and row[0] == word:
            postings.append(eval(row[1]))
    list_of_postings.append([j for i in postings for j in i])


try:
    r = csv.reader(open("important_words.csv"))
    csvLines = list(r)
    for x in csvLines:
        if x[0] in query:
            listOfPages = list(x[1])
            important.extend(listOfPages)
            for page in listOfPages:
                rankDict[page] += 0.5

    results = list_of_postings[0]
except IndexError:
    if(len(results) == 0):
        print("No results were found for this query.")
        exit()
    else:
        pass

for posting in list_of_postings:
    results = set(results).intersection(posting)

if(len(important) > 0):
    for res in results:
        important.append(res)



#vectorizer = TfidfVectorizer()
table = TfIdf()
G = nx.Graph()
#return urls corresponding to numbers
with open("url_files.csv") as f:
    urls = [row for row in csv.reader(f)]

    if len(results) != 0:

        for x in results:
            f = open(urls[x-1][0])
            obj = json.load(f)

            soup = BeautifulSoup(obj["content"], "html.parser", from_encoding="iso-8859-1")
            joinedText = [ps.stem(word) for word in ' '.join([p.get_text() for p in soup.find_all("p", text=True)]).split()]
            line = set(re.sub(r'[^a-zA-Z0-9]', ' ', joinedText.lower()).split())
            #response = vectorizer.fit_transform([])
            table.add_document(obj["url"], joinedText)

            doc = html.fromstring(obj["content"])
            for l in doc.iterlinks():
                G.add_edge(obj["url"],l)

            #print(obj["url"])
        tf_idf = table.similarities(query)
        for x in tf_idf:
            rankDict[x[0]] += x[1]
        #G = nx.barabasi_albert_graph(60, 41)
        pr = nx.pagerank(G, 0.4)
        for key, val in pr.items():
            rankDict[key] += val

        for y in sorted(rankDict.items(), key=lambda x: x[1], reverse=True):
            print(y[0])


    else:
        print("No results were found for this query.")