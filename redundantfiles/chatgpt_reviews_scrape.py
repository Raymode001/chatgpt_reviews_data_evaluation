import random
import pandas as pd
from google_play_scraper import Sort, reviews_all

s=set()
while len(s)<385:
    s.add(random.randint(1, 22687654))
idx_list=sorted(list(s))

result = reviews_all(
    'com.openai.chatgpt',
    sleep_milliseconds=0, # defaults to 0
    lang='en', # defaults to 'en'
    country='us', # defaults to 'us'
    sort=Sort.NEWEST, 
    filter_score_with=None # defaults to None(means all score)
)

sample = [result[i] for i in idx_list]
print("sample size:", len(sample))
print("samples",sample[:5])