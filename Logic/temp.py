import numpy as np
import random
import json
import os
import re

# 661 real docs

l = 0
r = 20

# path_to_read = os.getcwd() + "/Logic/tests/CrawlerResults/IMDB_Crawled.json"
# path_to_write = os.getcwd() + "/Logic/tests/CrawlerResults/IMDB_Crawled_Head.json"
path_to_read = os.getcwd() + "/Logic/Data/PreprocessedDocuments.json"
path_to_write = os.getcwd() + "/Logic/Data/PreprocessedDocuments_Head.json"

movies = None
with open(path_to_read, "r") as file:
    movies = json.load(file)
foo = list()
for i in range(l, r + 1):
    foo.append(movies[i])
with open(path_to_write, "w") as file:
    json.dump(foo, file)
print("The end!")
