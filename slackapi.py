import configparser
import requests
import json

class SlackPoster():

    def __init__(self):
        # Hueee
        config = configparser.ConfigParser()
        config.read('../slacknotify_envsettings.ini')
        self.config = config

    def post(self, channelId, iconURL=None, username=None, ts=None, text=None, attachments=None):
        token = self.config['slack_api']['token']
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+token
            }
        req = {
            "channel":channelId,
            "token": token
            }
        if iconURL != None:
            req["icon_url"] = iconURL
        if username != None:
            req["username"] = username
        if ts != None:
            req["thread_ts"] = ts
        if text != None:
            req["text"] = text
        if attachments != None:
            req["attachments"] = attachments
        res=requests.post("https://slack.com/api/chat.postMessage", data=json.dumps(req), headers=headers)
        print("============================\nPostedToSlack\nurl:https://slack.com/api/chat.postMessage\nreq:\n"+str(req)+"\nres:"+str(res.text)+"\n============================\n")
        

    def defPost(self, channelId, text, ts=None):
        # わーいポストします(ぽーん)
        self.post(channelId=channelId, text=text, ts=ts)

    def IMAPMailPost(self, channelId, uid, mailFromAdd, mailFromName, mailToAdd, mailToName, mailsub, mailbody, msg=None, ts=None):
        self.post(channelId=channelId,ts=ts, text='@channel `メールを受信しました`\n', 
        attachments=[
        {
            "fallback": mailbody,
            "color": "#36a64f",
            "author_name": mailFromName+" ("+mailFromAdd+")",
            "author_link": "mailto:"+mailFromAdd,
            "author_icon": "https://pbs.twimg.com/profile_images/1068841466988920832/wMIpsqCY.jpg",
            "title": mailsub+"#"+uid,
            "title_link": "",
            "text": mailbody,
            "actions": [
                {
                    "name": "btn1Name",
                    "text": "返信",
                    "type": "button",
                    "style": "default",
                    "value": "replyValue"
                },
                {
                    "name": "btn2Name",
                    "text": "別チャンネルへ転送",
                    "type": "button",
                    "style": "primary",
                    "value": "shareValue"
                }
            ],
            "footer": "受取: "+mailToAdd+"<"+mailToName+">",
            "footer_icon": "https://pbs.twimg.com/profile_images/1068841466988920832/wMIpsqCY.jpg"
        }])
        