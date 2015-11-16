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
