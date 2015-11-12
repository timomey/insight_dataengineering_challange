#!/usr/bin/env python

# this program takes tweets from ../tweet_input/tweets.txt and converts the JSON format to what they should look like:
# example:
# <contents of "text" field> (timestamp: <contents of "created_at" field>)
#

#TODO: put everything in functions and make it executable! (monday)

import json

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

#two variables to count exceptions later on.
#count the tweets that have unicode that is not ascii
numberunicode = 0
#count the tweets that do not have tweet data (actual text in the tweet).
numberleftout = 0

#open tweets file; note that "with ... as ..." closes file connection automatically
with open('../tweet_input/tweets.txt','r') as tweetfile_handle:
    #only take one line at a time to be able to handle huge data files
    for oneline in tweetfile_handle:
        #use json.loads to turn this line to a dictionary for easy access (alternative would be using reg.exp.)
        oneline_dict = json.loads(oneline)

        #this "try .. except" is to capture the exceptions caused by cases where tweets do not have any texts
        try:
            #from the json, the dictionary 'text' entry has the tweet;
            #if there is no text, excpetion is raised here.
            text_u = oneline_dict['text']

            #this "try.. except" captures tweets that have unicode/ascii only tweets
            try:
                #try encode unicode to ascii. raises error if doesnot work.
                text_ascii = text_u.encode('ascii')
            except UnicodeEncodeError:
                #encode as ascii, ignoring non readable stuff.
                text_ascii = text_u.encode('ascii','ignore')
                #count tweet with unicode
                numberunicode += 1

            #get timestamp
            timestamp = oneline_dict['created_at']
            timestamp = timestamp.encode('ascii')
            #clean the text string, if it is not clean already.
            cleantext = clean_string(text_ascii)
            #put the result line together
            result = cleantext + ' (timestamp: ' + timestamp + ')'

            #write output to ft1.txt
            with open('../tweet_output/ft1.txt', 'a') as tweet_out:
                tweet_out.write(result)
                tweet_out.write('\n')

        except KeyError:
            numberleftout += 1

#print the counters
unicodeleftout = str(numberunicode) + ' tweets contained unicode.'
keyerrorcount = str(numberleftout) + ' tweets left out because of missing data.'
print unicodeleftout
print keyerrorcount

#attach number of unicode tweets to result
with open('../tweet_output/ft1.txt', 'a') as tweet_out:
    tweet_out.write('\n')
    tweet_out.write(unicodeleftout)
