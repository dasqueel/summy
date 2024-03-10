import feedparser
import os 
from pymongo import MongoClient
from groupme import sendComment
import time
import subprocess
from summarizers import *
from transcribers import *
from whisx import transcribe

mongoUrl = os.getenv('battlesqueelMongoUrl')
groupmeId = os.getenv('groupmeId')
groupmeBotId = os.getenv('groupmeBotId')
ngrokDomain = os.getenv("ngrokDomain")

mongoClient = MongoClient(mongoUrl)
mongoDb = mongoClient.bettor
vidsCol = mongoDb['vids']
ytCol = mongoDb['youtubeChannels']

def dbUpdateAndMessage(podcastAbbr, vidId):
    if ytCol.update_one({"abbr": podcastAbbr}, {'$push': {'processedVidIds': vidId}}):
        transcriptUrl = f'{ngrokDomain}/files/{vidId}.txt'
        msg = f"{podcastAbbr} | https://www.youtube.com/watch?v=lbFmceo4D5E | {transcriptUrl}" 
        sendComment(msg, botId=groupmeBotId, groupId=groupmeId)
    else:
        print(f'failed to update datebase | {vidId}')

def downloadPod(pod_title, url):
    output_template = f"./wavs/{pod_title}.wav"
    
    command = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "wav",
        "--postprocessor-args", "-ar 16000",
        "-o", output_template,
        url
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Downloaded and converted audio successfully saved to {output_template}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

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
    channelDoc = ytCol.find_one({"abbr":abbr})
    processed_video_ids = channelDoc["processedVidIds"]
    
    latest_videos_dicts = get_latest_videos(channelDoc['id'])
    latest_videos_ids = [vid['video_id'] for vid in latest_videos_dicts]
    # latest_videos_ids.insert(0, "new1")

    toProcessVids = list(set(latest_videos_ids) - set(processed_video_ids))

    return toProcessVids

def updateChannel(abbr):
    has_new_videos = has_new_video(abbr)
    if len(has_new_videos) > 0:
        for vidId in has_new_videos:
            # transcribe
            # isTranscribed = transcribe(vidId)

            # summarized
            # isSummarized = summarize(vidId)
            if ytCol.update_one({"abbr": abbr}, {'$push': {'processedVidIds': vidId}}):
                # msg = f"{abbr} | https://www.youtube.com/watch?v={str(vidId)}"
                transcriptUrl = f'{ngrokDomain}/files/{vidId}.txt'
                msg = f"{abbr} | https://www.youtube.com/watch?v={str(vidId)} | {transcriptUrl}" 
                # msg = f"{abbr} | {readUrl}" 
                sendComment(msg, botId=groupmeBotId, groupId=groupmeId)
            else:
                print(f'failed to update datebase | {vidId}')
    else:
        print('no new videos')

def checkChannels():
    channelDocs = ytCol.find()

    for channelDoc in channelDocs:
        # print(channelDoc)
        abbr = channelDoc['abbr']

        if channelDoc["toCheck"]: updateChannel(abbr)
        
def updateChannelsSync(podcast):
    try:
        downloadPodResult = downloadPod(podcast)
        transcribeResult = transcribe(podcast)
        print(transcribeResult)
        summaryResult = summarize(podcast)
        print(summaryResult)
        dbUpdateAndMessageResult = dbUpdateAndMessage(podcast)
        print(dbUpdateAndMessageResult)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Cleanup can go here")

async def updateChannelsAsync(podcast):
    try:
        downloadPodResult = await downloadPod(podcast)
        transcribeResult = await transcribe(podcast)
        print(transcribeResult)
        summaryResult = await summarize(podcast)
        print(summaryResult)
        dbUpdateAndMessageResult = await dbUpdateAndMessage(podcast)
        print(dbUpdateAndMessageResult)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Cleanup can go here")

# readTransUrl = f'{ngrokDomain}/files/test.txt'
# msg = f"testChannel | https://www.youtube.com/watch?v=lbFmceo4D5E | {readTransUrl}" 
# sendComment(msg, botId=groupmeBotId, groupId=groupmeId)

