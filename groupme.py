import requests

def sendComment(comment, botId, groupId):

  json = {
    "text": comment,
    "bot_id": botId
  }

  requests.post("https://api.groupme.com/v3/bots/post", json=json)