#!/usr/bin/env python
#this script creates a graph of tweets of the last 60 seconds. It does not use the cleaned data created
#by tweets_cleaned.py, because saving subresults in a file is unneccesary and would slow down the process.
#Especially if this will be used to directly work on an incoming stream of tweets it needs to be perfomant.

import json
import datetime as dt
import networkx as nx
import re
import matplotlib.pyplot as plt
import itertools

#FIRST get the clean data out, like in tweets_cleaned.py

#this function cleans strings of unicode, replaces a few things, strips strings from spaces at end and beginning,
#and removes multiple spaces.
def clean_string(text):
    text.strip()
    text.replace("\/", "/")
    text.replace("\\", "\ ")
    text.replace("\'", "'")
    text.replace('\"', '"')
    text.replace("\n", " ")
    text.replace("\t", " ")
    text = " ".join(text.split())
    return text

#transform the timestamp strings from tweets to datetime.datetime objects for easy time handling
def timestamp_to_datetime(timestamp):
    yr = int(timestamp[26:])
    #NOW HARDCODED BECAUSE THERE IS ONLY OCT DATA! BUT SHOULD BE FLEXIBLE (TODO)
    m = 10
    d = int(timestamp[8:10])
    hr = int(timestamp[11:13])
    mi = int(timestamp[14:16])
    sec = int(timestamp[17:19])
    datetime_object = dt.datetime(yr,m,d,hr,mi,sec)
    return datetime_object

number_tweets_withouttext = 0

#create empty graph
G = nx.Graph()
#variable to keep track of the oldest entry in the graph. (since it has to <= 60 seconds)
oldestdate = 0
########## TEST BLOCK
tweetfile_handle = open('../tweet_input/tweets.txt','r')
lines = tweetfile_handle.readlines()
oneline = lines[10]

#########

hashtags_1min = {}
hashtags_1min_date = {}
tweetnumber = 0
with open('../tweet_input/tweets.txt','r') as tweetfile_handle:
    for oneline in tweetfile_handle:
        tweetnumber +=1
        print tweetnumber
        oneline_dict = json.loads(oneline)
        
        try:
            G = nx.Graph() # every time build it from scratch.. could be more efficient!
            text_u = oneline_dict['text']
            text_ascii = text_u.encode('ascii','ignore')
            #get timestamp
            timestamp = oneline_dict['created_at']
            timestamp = timestamp.encode('ascii')
            date = timestamp_to_datetime(timestamp)
            #list for the hashtags
            hashtags = ['#']*(len(text_ascii.split('#'))-1)
            for i in range(1,len(text_ascii.split('#'))):
                #get the hashtags with this command:
                #1.: split by hashtags:
                #take everything after a split (=after a hashtag) and then
                #2.: split right after the hashtag (-> .split(' ')[0])
                #save those into graph
                hashtags[i-1] = text_ascii.split('#')[i].split(' ')[0]
                #print hashtags[i-1]

            #update hashtag dictionary and date dictionary
            #if hashtag != []:
            hashtags_1min[tweetnumber] = hashtags
            hashtags_1min_date[tweetnumber] = date
            #remove entries with date that are one minute older than currentdate
            for key, olddate in hashtags_1min_date.items():
                if date - olddate > dt.timedelta(0,60):
                    del hashtags_1min[key]
                    del hashtags_1min_date[key]

                G.add_edges_from(list(itertools.permutations(hashtags_1min[key],2)))

            #print hashtags_1min.keys()

            degrees = G.degree().values()
            if len(degrees) >0:
                avedegree = float(sum(degrees))/len(degrees)
                #one of the 2; second is better, because it ALWAYS has 2 decimal places.
                avedegree = round(avedegree,2)
                with open('../tweet_output/ft2.txt', 'a') as output:
                    result = '%.2f' %avedegree
                    output.write(result)
                    output.write('\n')
            else:
                with open('../tweet_output/ft2.txt', 'a') as output:
                    result = '0'
                    output.write(result)
                    output.write('\n')

        except KeyError:
            number_tweets_withouttext += 1
