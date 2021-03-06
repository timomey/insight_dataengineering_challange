#!/usr/bin/env python


import json
import datetime as dt
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
    text = text.lower()
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
        text_ascii = clean_string(text_ascii)
        text_ascii = text_ascii.lower()
        #get timestamp
        timestamp = oneline_dict['created_at']
        timestamp = timestamp.encode('ascii')
        date = timestamp_to_datetime(timestamp)

        #instead of loop: map. get the hashtags out.
        hashtags = map(lambda x: x.split(' ')[0], text_ascii.split('#'))
        hashtags = hashtags[1:]
        return (hashtags, date)
    except KeyError:
        notext = 1
        return notext


class graph_connections:
    """
    this class keeps track of the graph.
    it has two dictionaries. degreedict and connectiondict.
    degreedict keeps track of the degree of each node.
        the keys are the names of the nodes and values are the number of connections.
        (example: #test with 5 connections -> degreedict['test'] = 5)
    connectiondict keeps track of all edges in the graph.
        keys are tuple of two connecting hashtags.
        values are the corresponding datetime_object.
        example: if #test and #hashtag have been mentioned in the same tweet:
            connectiondict[('test', 'hashtag')] = datetime_object
            with the corresponding datetime_object.

    methods: self explanatory: add_tweet, remove_old_tweets, get_degrees
    """
    def __init__(self):
        self.degreedict = {}
        self.connectiondict = {}

    def add_tweet(self, hashtags_date_tuple):
        newconnections = itertools.combinations(hashtags_date_tuple[0],2)
        for edge in newconnections:
            if tuple(edge) not in self.connectiondict.keys(): #if edge does not exist yet.
                for vertex in edge: #add the degree counter +1 for each one
                    if vertex in self.degreedict.keys(): #either it already exists:
                        self.degreedict[vertex] +=1
                    else:                           #or not yet.
                        self.degreedict[vertex] = 1
            #in any case, update the time for the edge:
            self.connectiondict[tuple(edge)] = hashtags_date_tuple[1]

    def remove_old_tweets(self, date, time_period):
        #dict comprehension: if the value()/date is older than time_period -> entry stays not in dictionary.
        newdict = { k:v for k,v in self.connectiondict.items() if date - v < dt.timedelta(0,time_period)}
        #print newdict
        #keys that were deleted:
        diff = list(set(self.connectiondict.keys()) - set(newdict.keys()))
        for edge in diff:
            for vertex in edge:
                if vertex in self.degreedict.keys(): #single hashtags could be here, but are not in degreedict.
                    self.degreedict[vertex] -=1
                    if self.degreedict[vertex] <= 0:
                        del self.degreedict[vertex]
        self.connectiondict = newdict

    def get_degrees(self):
        return self.degreedict.values()

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

    tweetnumber = 0
    graphc = graph_connections()
    with open(inputfile,'r') as tweetfile_handle:
        for oneline in tweetfile_handle:
            tweetnumber +=1 #used as a key in the dictionary to save hashtags and dates

            #get hashtags and date from this tweet
            hashtags_date_tuple = tweet_2_hashtags_and_date(oneline)


            #if this was an empty tweet -> go straight to next iteration
            if hashtags_date_tuple == 1:
                number_tweets_withouttext +=1
                continue

            hashtags_date_tuple[0].sort()


            graphc.add_tweet(hashtags_date_tuple)
            graphc.remove_old_tweets(hashtags_date_tuple[1],60)
            degrees = graphc.get_degrees()

            if tweetnumber == 8000:
                print graphc.degreedict.keys()

            #calc average degree and write to outputfile.
            #if: for the case that there are no tweets with hashtags (especially at beginning of inputfile.)
            if len(degrees) >0:
                avedegree = float(sum(degrees))/len(degrees)
                #one of the 2; second is better, because it ALWAYS has 2 decimal places.
                #avedegree = round(avedegree,2)
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
