import feedparser
from bs4 import BeautifulSoup
import os 
from pymongo import MongoClient
from groupme import sendComment
import time

mongoUrl = os.getenv('battlesqueelMongoUrl')
groupmeId = os.getenv('groupmeId')
groupmeBotId = os.getenv('groupmeBotId')

# print(groupmeBotId, groupmeId)

mongoClient = MongoClient(mongoUrl)
mongoDb = mongoClient.bettor
vidsCol = mongoDb['vids']
ytCol = mongoDb['youtubeChannels']

def get_latest_videos(channelId, max_results=2):
    rss_url = f'https://www.youtube.com/feeds/videos.xml?channel_id={channelId}'
    time.sleep(4)
    feed = feedparser.parse(rss_url)
    videos = []

    for entry in feed.entries[:max_results]:
        # print(entry.__dict__)
        video_data = {
            'title': entry.title,
            'publish_date': entry.published,
            'video_id': entry.yt_videoid
        }
        videos.append(video_data)

    return videos

def has_new_video(abbr):
    # check from the store that a new video id isnt in the already processed videos
    channelDoc = ytCol.find_one({"abbr":abbr})
    processed_video_ids = channelDoc["processedVidIds"]
    
    latest_videos_dicts = get_latest_videos(channelDoc['id'])
    latest_videos_ids = [vid['video_id'] for vid in latest_videos_dicts]
    # latest_videos_ids.insert(0, "new1")

    toProcessVids = list(set(latest_videos_ids) - set(processed_video_ids))

    return toProcessVids

def updateChannel(abbr):
    has_new_videos = has_new_video(abbr)
    # print(has_new_video)
    if len(has_new_videos) > 0:
        for vidId in has_new_videos:
            # transcribe
            # isTranscribed = transcribe(vidId)

            # summarized
            # isSummarized = summarize(vidId)
            if ytCol.update_one({"abbr": abbr}, {'$push': {'processedVidIds': vidId}}):
                msg = f"{abbr} | https://www.youtube.com/watch?v={str(vidId)}" 
                sendComment(msg, botId=groupmeBotId, groupId=groupmeId)
            else:
                print(f'failed to update datebase | {vidId}')
    else:
        print('no new videos')

        # send url that with the findinds and transcription
        # https://mysite.heroku.com/trans=<vidId>

def checkChannels():
    channelDocs = ytCol.find()

    for channelDoc in channelDocs:
        # print(channelDoc)
        abbr = channelDoc['abbr']

        if channelDoc["toCheck"]: updateChannel(abbr)

checkChannels()

def addChannel(abbr, name, id):
    channelDoc = {
        "abbr": abbr,
        "name": name,
        "id": id,
        "processedVidIds": []
    }
    ytCol.insert_one(channelDoc)

# addChannel("g5pod", "groupoffivefocuspodcast4029", "UCwxMyHhwWGOEBrDsBz4A4ZA")
'''
def get_latest_processed_pubdate(processed_video_list):

    return sorted(processed_video_list, key=lambda video: datetime.fromisoformat(video['publish_date'].replace('Z', '+00:00')))
'''

