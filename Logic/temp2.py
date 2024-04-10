import numpy as np
import random
import json
import os
import re

# 661 real docs

l = 0
r = 20

str_ = "Awesome\nThe movie \u0096 the started out pretty innocently, and for the first 20 minutes, I was wondering where the movie was going. Then it started to happen. The horrible cruelty of concentration camps. Oskar Schindler is an example of a man that no matter what the situation, there are people who won't go along with the cruelty of society. I'm sure it took courage to do what he did, because one wrong move and you'll be dead.Movie brought to life this great man who really shouldn't be forgotten, and thanks to Steven Spielberg, I think he'll be remembered for generations to come. Movie like this should be made once in a while. Not that movie should be used for evangelistic purposes but some story should be told well, and movie is still the best vehicle to do so.I still think that Oskar Shindler's last words in this movie was one of the best dialog in movie history - \"Why did I keep this badge ? I could have saved a person. Why did I keep this car ?, I could have saved five more people.\""

# str_ = re.sub(r"\n", " ", str_)
# str_ = re.sub(r"[^\w\s]", " ", str_)
# pattern = re.compile(r"the", re.IGNORECASE)
# str_ = re.sub(pattern, "foo", str_)

str_ = re.sub(r"[\u0080-\uffff]", " ", str_)

print(str_)
