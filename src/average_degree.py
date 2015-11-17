#!/usr/bin/env python


import json
import datetime as dt
import networkx as nx
import itertools
import sys

def clean_string(text):
    """input: string. output is a "clean" string:
            1: spaces at end and beginning are removed:
                                ' input ' -> 'input'
            2: replacements:    "\/" -> "/"
                                "\\" -> "\ "
                                "\'" -> "'"
                                '\"' -> '"'
                                "\n" -> " ")
                                "\t" -> " "
            3: multiple spaces are replaced by one.
                                "input      string" -> "input string"
            """
    text.strip()
    text.replace("\/", "/")
    text.replace("\\", "\ ")
    text.replace("\'", "'")
    text.replace('\"', '"')
    text.replace("\n", " ")
    text.replace("\t", " ")
    text = " ".join(text.split())
    return text

def timestamp_to_datetime(timestamp):
    """
    input: timestamp string from twitter API ('created_at' value example: 'Fri Oct 30 15:29:44 +0000 2015')
    returns the corresponding datetime.datetime object for easy time handling.
    """
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
    """
    input: String: 3 letter abbreviation of month. (example: 'Jan')
            not case sensitive.
    returns: integer corresponding to the month. (example: 'Jan' -> 1)
    """
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    m=0
    for iter in months:
        m+=1
        if m_abbr.lower() == iter:
            return m

def tweet_2_hashtags_and_date(oneline):
    """
    input: tweet in json format as string as received from twitter API
    output: tuple (hashtags, date)
            hashtags is a list of all hashtags that are in the tweet.
            date is the datetime.datetime object corresponding to the timestamp of that tweet.

            (example output:    (hashtags, date) with:
                                hashtags = ['first', 'tweet']
                                date = datetime.datetime(2015, 10, 30, 15, 29, 44)

    """
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


def make_graph_return_degrees(hashtags_1min, hashtags_1min_date, hashtags_date_tuple):
    """
    input:  1: dictionary of hashtags that have timestamps within 1 min. from the current timestamp.
                (keys have to correspond to dates dicitonary!)
            2: dictionary of dates corresponding to the hashtags.
                (keys have to correspond to hashtags dicitonary!)
            3: current hashtags_date_tuple as resulted from function tweet_2_hashtags_and_date.
                only to have the date of the last tweet.
    """
    G = nx.Graph() # every time built from scratch.. could be more efficient!
    #remove entries with date that are one minute older than currentdate
    #NOTE: this assumes that current date is the newest, which is not true for the real
    #twitter stream since tweets do not come in the exact correct order.
    for key, olddate in hashtags_1min_date.items():
        if hashtags_date_tuple[1] - olddate > dt.timedelta(0,60):
            del hashtags_1min[key]
            del hashtags_1min_date[key]
        else:
            #calculate all parmutations of pairs. only have of them are actually needed to add the edges since A-B = B-A
            #->(room for imporvement)
            G.add_edges_from(list(itertools.permutations(hashtags_1min[key],2)))
    #calc degrees and write output
    degrees = G.degree().values()
    return degrees

class tweet_graph:
    """graph of hashtags"""
    def __init__(self):
        self.graph_hashtags = {}
        self.graph_date = {}

    def add_hashtags(self, hashtags_date_tuple):
        self.graph_hashtags

    def clean_old_dates(self):
        pass

    def get_degree(self):
        pass

def tweet_avedegree_60sgraph(inputfile, outputfile):
    """
    input:  1: location of input file
                has to exist and should contain data from the twitter API: 1 json stirngs corresponding to a tweet per line.
            2: location of output file
                if the file already exists, results are saved in new lines below existing content.
                if it does not exist, it is created.

            locations relative to where python is running.

    output: the average degree of nodes of hashtags graph during last 60 seconds.
            this number is generated for every tweet in the input file and is saved to
            a new line in the outputfileselfself.
    """
    number_tweets_withouttext = 0
    hashtags_1min = {}
    hashtags_1min_date = {}
    tweetnumber = 0
    with open(inputfile,'r') as tweetfile_handle:
        for oneline in tweetfile_handle:
            tweetnumber +=1 #used as a key in the dictionary to save hashtags and dates

            #get hashtags and date from this tweet
            hashtags_date_tuple = tweet_2_hashtags_and_date(oneline)

            #if this was an empty tweet -> go straight to next iteration
            if hashtags_date_tuple == 1:
                number_tweets_withouttext +=1
                continue

            #update hashtag dictionary and date dictionary
            hashtags_1min[tweetnumber] = hashtags_date_tuple[0]
            hashtags_1min_date[tweetnumber] = hashtags_date_tuple[1]

            #this function is overkill and can be optimized.
            degrees = make_graph_return_degrees(hashtags_1min, hashtags_1min_date, hashtags_date_tuple)

            #calc average degree and write to outputfile.
            #if: for the case that there are no tweets with hashtags (especially at beginning of inputfile.)
            if len(degrees) >0:
                avedegree = float(sum(degrees))/len(degrees)
                #one of the 2; second is better, because it ALWAYS has 2 decimal places.
#                avedegree = round(avedegree,2)
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
    tweet_avedegree_60sgraph(inputfile, outputfile)
