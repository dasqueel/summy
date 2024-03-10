from pymongo import MongoClient
import os

mongoUrl = os.getenv('battlesqueelMongoUrl')
mongoClient = MongoClient(mongoUrl)
mongoDb = mongoClient.bettor
vidsCol = mongoDb['vids']
ytCol = mongoDb['youtubeChannels']
                
def addChannel(abbr, name, id):
    channelDoc = {
        "abbr": abbr,
        "name": name,
        "id": id,
        "processedVidIds": []
    }
    ytCol.insert_one(channelDoc)

# addChannel("g5pod", "groupoffivefocuspodcast4029", "UCwxMyHhwWGOEBrDsBz4A4ZA")