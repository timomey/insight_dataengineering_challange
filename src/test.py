inputfile = '../tweet_input/tweets_10min.txt'
outputfile = '../tweet_output/tweets_10min_degree_3.txt'
with open(inputfile,'r') as tweetfile_handle:
    for oneline in tweetfile_handle:
        tweetnumber +=1 #used as a key in the dictionary to save hashtags and dates
        if tweetnumber >1000:
            print 'break'
            break

        #get hashtags and date from this tweet
        hashtags_date_tuple = tweet_2_hashtags_and_date(oneline)

        #if this was an empty tweet -> go straight to next iteration
        if hashtags_date_tuple == 1:
            number_tweets_withouttext +=1
            continue

        #update hashtag dictionary and date dictionary
        #hashtags_1min[tweetnumber] = hashtags_date_tuple[0]
        #hashtags_1min_date[tweetnumber] = hashtags_date_tuple[1]

        #hashtag_date[tweetnumber] = hashtags_date_tuple

        graphc.add_tweet(hashtags_date_tuple)
        graphc.remove_old_tweets(hashtags_date_tuple[1],60)
        degrees = graphc.get_degrees()

        #this function is overkill and can be optimized.
        #degrees = make_graph_return_degrees(hashtags_1min, hashtags_1min_date, hashtags_date_tuple)

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
