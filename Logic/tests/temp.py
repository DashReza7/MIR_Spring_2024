import json

movies_dict = None
with open("CrawlerResults/IMDB_Crawled.json", "r") as f:
    movies_dict = json.load(f)
    for movie in movies_dict:
        reviews = movie["reviews"]
        for i in range(len(reviews)):
            if reviews[i][1] is None:
                reviews[i][1] = "No rating"
if movies_dict is not None:
    with open("CrawlerResults/IMDB_Crawled.json", "w") as f:
        json.dump(movies_dict, f)

