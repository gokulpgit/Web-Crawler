import json
import os
from bs4 import BeautifulSoup
import re
import csv
from string import ascii_lowercase
import pandas
from nltk.stem import PorterStemmer
from simhash import Simhash     #used from https://github.com/leonsim/simhash
from collections import defaultdict


docIDs = {}
importantWords = defaultdict(set)
count = 0
siteCounter = 0
ps = PorterStemmer()
simList = []

letterFile = {}
for letter in ascii_lowercase:
    letterFile[letter] = csv.writer(open(letter + ".csv", "w"))
letterFile["num"] = csv.writer(open("num.csv", "w"))

for site in os.listdir("/Users/gokulg/Downloads/DEV"):
    print(site)
    siteCounter += 1
    if(siteCounter == 7):
        break
    print(siteCounter)
    if(site != ".DS_Store"):    #DO YOU NEED THIS
        for jsonFile in os.listdir("/Users/gokulg/Downloads/DEV/" + site):
            count += 1
            docIDs["/Users/gokulg/Downloads/DEV/" + site + "/" + jsonFile] = count
            with open("/Users/gokulg/Downloads/DEV/" + site + "/" + jsonFile, 'r') as f:
                obj = json.load(f)
                soup = BeautifulSoup(obj["content"], "html.parser", from_encoding="iso-8859-1")
                for script in soup(["script","style"]):
                    script.extract()
                joinedText = soup.get_text().rstrip('\n')
                #joinedText = ' '.join([p.get_text() for p in soup.find_all("p", text=True)])

                set(re.sub(r'[^a-zA-Z0-9]', ' ', joinedText.lower()).split())

                strongText = re.sub(r'[^a-zA-Z0-9]', ' ',' '.join([p.get_text() for p in soup.find_all("strong", text=True)])).split()
                for w in strongText:
                    w = ps.stem(w)
                    if(len(w) > 0):
                        importantWords[w].add(obj["url"])
                titleText = re.sub(r'[^a-zA-Z0-9]', ' ',' '.join([p.get_text() for p in soup.find_all("title", text=True)])).split()
                for w in titleText:
                    w = ps.stem(w)
                    if (len(w) > 0):
                        importantWords[w].add(obj["url"])
                h1Text = re.sub(r'[^a-zA-Z0-9]', ' ',' '.join([p.get_text() for p in soup.find_all("h1", text=True)])).split()
                for w in h1Text:
                    w = ps.stem(w)
                    if (len(w) > 0):
                        importantWords[w].add(obj["url"])
                h2Text = re.sub(r'[^a-zA-Z0-9]', ' ',' '.join([p.get_text() for p in soup.find_all("h2", text=True)])).split()
                for w in h2Text:
                    w = ps.stem(w)
                    if (len(w) > 0):
                        importantWords[w].add(obj["url"])
                h3Text = re.sub(r'[^a-zA-Z0-9]', ' ',' '.join([p.get_text() for p in soup.find_all("h3", text=True)])).split()
                for h3 in h3Text:
                    w = ps.stem(w)
                    if (len(w) > 0):
                        importantWords[w].add(obj["url"])

                line = set(re.sub(r'[^a-zA-Z0-9]', ' ', joinedText.lower()).split())
                simVal = Simhash(line).value
                if simVal not in simList:  # pages with similar content will have the same SimHash value, so this ensures not to crawl similar pages
                    simList.append(simVal)

                    for word in line:
                        word = ps.stem(word)
                        if(len(word) > 0):
                            try:
                                fileName = ""
                                if(word[0].isdigit()):
                                    fileName = "num"
                                else:
                                    fileName = word[0]
                                r = csv.reader(open(fileName + ".csv"))
                                #r = csv.reader(codecs.open(fileName + ".csv", 'rU', 'utf-16'))
                                csvLines = list(r)
                                #csvRow = [x[0] for x in csvLines]   #will this work? will .index take you to the same index?
                                yesWord = False
                                for x in csvLines:
                                    if x[0] == word:
                                        x[1] = x[1][:-1] + ", " + str(docIDs["/Users/gokulg/Downloads/DEV/" + site + "/" + jsonFile]) + "]"
                                        writer = csv.writer(open(fileName + ".csv", 'w'))
                                        writer.writerows(csvLines)
                                        yesWord = True
                                        break
                                if(not yesWord):
                                    with open(fileName + ".csv", 'a+', newline='') as write_obj:
                                        csv_writer = csv.writer(write_obj)
                                        csv_writer.writerow((word, str([docIDs["/Users/gokulg/Downloads/DEV/" + site + "/" + jsonFile]])))
                            except:
                                pass


with open('url_files.csv', 'w', newline="") as csv_file:
    writer = csv.writer(csv_file)
    for key, value in docIDs.items():
       writer.writerow([key, value])

with open('important_words.csv', 'w', newline="") as csv_file:
    writer = csv.writer(csv_file)
    for key, value in importantWords.items():
       writer.writerow([key, value])

print("Num of indexed documents: " + str(count))
dfList = []
colnames = ["Word", "Posting"]
for letter in ascii_lowercase:
    filename = letter + ".csv"
    print(filename)
    df = pandas.read_csv(filename,header = None)
    dfList.append(df)
df = pandas.read_csv("num.csv",header = None)
dfList.append(df)
concatDf = pandas.concat(dfList, axis=0)
concatDf.columns = colnames
concatDf.to_csv("/Users/gokulg/PycharmProjects/Assign3/FINAL_PRODUCT.csv",index=None)

#all_filenames.append("num.csv")

#combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames])
#combined_csv.to_csv("FINAL_PRODUCT.csv", index=False, encoding='utf-8-sig')


                        #with open(word[0] + ".csv", 'a') as fd:
                        #    fd.write([word, [docIDs["/Users/gokulg/Downloads/DEV/" + site + "/" + jsonFile]]])


'''
for file in os.listdir("/Users/gokulg/Downloads/DEV/" + batch[i]):
    count += 1
    docIDs["/Users/gokulg/Downloads/DEV/" + batch[i] + "/" + file] = count
    with open("/Users/gokulg/Downloads/DEV/" + batch[i] + "/" + file, 'r') as f:
        obj = json.load(f)
        soup = BeautifulSoup(obj["content"], "html.parser", from_encoding="iso-8859-1")
        joinedText = ' '.join([p.get_text() for p in soup.find_all("p", text=True)])
        line = set(re.sub(r'[^\w]', ' ', joinedText.lower()).split())
        for word in line:
            partial_index[word].append(docIDs["/Users/gokulg/Downloads/DEV/" + batch[i] + "/" + file])
    print("FILE DONE")

    print("batch done---------------------------------")
    d = csv.writer(open("partial_index" + str(batches) + ".csv", "w"))
    for k in sorted(partial_index.keys()):
        d.writerow([k, partial_index[k]])
'''