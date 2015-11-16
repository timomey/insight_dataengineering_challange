#!/usr/bin/env python

# this program takes tweets from ../tweet_input/tweets.txt and converts the JSON format to what they should look like:
# example:
# <contents of "text" field> (timestamp: <contents of "created_at" field>)
#

#TODO: put everything in functions and make it executable! (monday)

import json
import sys


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



def extract_and_format(inputfile, outputfile):
    """description of function """
    #two variables to count exceptions later on.
    #count the tweets that have unicode that is not ascii
    numberunicodetweets = 0
    #count the tweets that do not have tweet data (actual text in the tweet).
    numberleftout = 0
    #open tweets file; note that "with ... as ..." closes file connection automatically
    with open(inputfile ,'r') as tweetfile_handle:
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
                    numberunicodetweets += 1
                #get timestamp
                timestamp = oneline_dict['created_at']
                timestamp = timestamp.encode('ascii')
                #clean the text string, if it is not clean already.
                cleantext = clean_string(text_ascii)
                #put the result line together
                result = cleantext + ' (timestamp: ' + timestamp + ')'
                #write output to ft1.txt
                with open(outputfile, 'a') as tweet_out:
                    tweet_out.write(result)
                    tweet_out.write('\n')
            except KeyError:
                numberleftout += 1
    #print the counters
    unicodeleftout = str(numberunicodetweets) + ' tweets contained unicode.'
    keyerrorcount = str(numberleftout) + ' tweets left out because of missing data/empty tweet.'
    print unicodeleftout
    print keyerrorcount
    #attach number of unicode tweets to result
    with open(outputfile, 'a') as tweet_out:
        tweet_out.write('\n')
        tweet_out.write(unicodeleftout)

if __name__ == '__main__':
    inputfile = sys.argv[1]
    outputfile = sys.argv[2]
    extract_and_format(inputfile, outputfile)
    print 'tweets extracted from ' + str(inputfile) + ' and saved in ' + str(outputfile)
