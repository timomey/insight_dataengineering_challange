#!/usr/bin/env python
#this script creates a graph of tweets of the last 60 seconds. It does not use the cleaned data created
#by tweets_cleaned.py, because saving subresults in a file is unneccesary and would slow down the process.
#Especially if this will be used to directly work on an incoming stream of tweets it needs to be perfomant.

import json
import datetime as dt
import networkx as nx
#import re
#import matplotlib.pyplot as plt
import itertools
import sys

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
    yr = int(timestamp.split(' ')[5])
    m = month_abbr2int(timestamp.split(' ')[1])
    d = int(timestamp.split(' ')[2])
    time = timestamp.split(' ')[3]
    hr = int(time.split(':')[0])
    mi = int(time.split(':')[1])
    sec = int(time.split(':')[2])
    datetime_object = dt.datetime(yr,m,d,hr,mi,sec)
    return datetime_object

def month_abbr2int(m_abbr):
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    m=0
    for iter in months:
        m+=1
        if m_abbr.lower() == iter:
            return m

def tweet_2_hashtags_and_date(oneline):
    """input(oneline): tweet in json format as string"""
    oneline_dict = json.loads(oneline)
    try:
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
        return (hashtags, date)
    except KeyError:
        #number_tweets_withouttext += 1
        notext = 1
        return notext



########## TEST BLOCK
#tweetfile_handle = open('./tweet_input/tweets.txt','r')
#lines = tweetfile_handle.readlines()
#oneline = lines[10]

#########
def tweet_60sgraph(inputfile, outputfile):
    number_tweets_withouttext = 0
    #variable to keep track of the oldest entry in the graph. (since it has to <= 60 seconds)
    #oldestdate = 0
    hashtags_1min = {}
    hashtags_1min_date = {}
    tweetnumber = 0
    with open(inputfile,'r') as tweetfile_handle:
        for oneline in tweetfile_handle:
            #just to see progress.
            #tweetnumber +=1
            #print tweetnumber

            #get hashtags and date from this tweet
            hashtags_date_tuple = tweet_2_hashtags_and_date(oneline)

            #if this was an empty tweet -> go straight to next iteration
            if hashtags_date_tuple == 1:
                number_tweets_withouttext +=1
                continue

            #update hashtag dictionary and date dictionary
            hashtags_1min[tweetnumber] = hashtags_date_tuple[0]
            hashtags_1min_date[tweetnumber] = hashtags_date_tuple[1]

            G = nx.Graph() # every time built from scratch.. could be more efficient!
            #remove entries with date that are one minute older than currentdate
            #NOTE: this assumes that current date is the newest, which is not true for the
            #twitter stream since tweets do not come in the exact correct order.
            for key, olddate in hashtags_1min_date.items():
                if hashtags_date_tuple[1] - olddate > dt.timedelta(0,60):
                    del hashtags_1min[key]
                    del hashtags_1min_date[key]
                else:
                    G.add_edges_from(list(itertools.permutations(hashtags_1min[key],2)))

            #calc degrees and write output
            degrees = G.degree().values()
            if len(degrees) >0:
                avedegree = float(sum(degrees))/len(degrees)
                #one of the 2; second is better, because it ALWAYS has 2 decimal places.
                avedegree = round(avedegree,2)
                with open(outputfile, 'a') as output:
                    result = '%.2f' %avedegree
                    output.write(result)
                    output.write('\n')
            else:
                with open(outputfile, 'a') as output:
                    result = '0'
                    output.write(result)
                    output.write('\n')


if __name__ == '__main__':
    inputfile = sys.argv[1]
    outputfile = sys.argv[2]
    tweet_60sgraph(inputfile, outputfile)
    #print str(number_tweets_withouttext) + ' tweets where left out, because they had no text.'
