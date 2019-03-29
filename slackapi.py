import configparser
import requests
import imap_errors
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
        ressrc = requests.post("https://slack.com/api/chat.postMessage", data=json.dumps(req), headers=headers)
        res = ressrc.json()
        print('[IMAP_transfar_SlackPost] Query sended to chat.postMessage')
        print('                           State:'+str(res['ok']))
        print('                           Channel:'+res['channel'])
        print('                           ts:'+res['ts'])
        #print('                           message:'+str(res['message']))
        print('')
        if res['ok'] != True:
            raise imap_errors.SlackPostError(res)
        
        return res

    def defPost(self, channelId, text, ts=None):
        # わーいポストします(ぽーん)
        self.post(channelId=channelId, text=text, ts=ts)

    def IMAPMailPost(self, channelId, uid, succeedState, mailBoxName, mailFromAdd, mailFromName, mailToAdd, mailToName, mailsub, mailbody, msg=None, ts=None):
        ############## genelate common postBody
        postBody = [
        {
            "fallback": mailbody,
            "color": '',
            "author_name": '',
            "author_link": '',
            #"author_icon": "https://pbs.twimg.com/profile_images/1068841466988920832/wMIpsqCY.jpg",
            "title": mailsub+"#"+str(uid),
            "title_link": "",
            "text": mailbody,
            "actions": [
                {
                    "name": "btn2Name",
                    "text": "別チャンネルへ転送",
                    "type": "button",
                    "style": "primary",
                    "value": "shareValue"
                }
            ],
            "footer": ''#,
            #"footer_icon": "https://pbs.twimg.com/profile_images/1068841466988920832/wMIpsqCY.jpg"
        }]
        # リソース作成
        mailFrom_display = mailFromAdd
        mailTo_display = mailToAdd
        if mailFromName != '':
            mailFrom_display = mailFromName+" ("+mailFromAdd+")"
        if mailToName != '':
            mailTo_display = mailToName+" <"+mailToAdd+">"
        # PostMessage時オプションの初期化
        PostUserIcon = ''
        PostUserName = 'メール転送'
        PostStateText = ''

        ###### Edit Body
        # 正しく取得(sock通信/decode/encode)できたデータか判定(以下判定の後)
        # 受信メールなら
        if mailBoxName == 'INBOX':
            # TODO ここに
            PostStateText = '@channel `メールを受信しました'
            PostUserIcon = 'https://takuma-isec.sakura.ne.jp/kaniyama_t/slackapp/src/imaptrans_received.png'
            postBody[0]['color'] = "#36a64f"
            postBody[0]['author_name'] = mailFrom_display
            postBody[0]['author_link'] = 'mailto:'+mailFromAdd
            postBody[0]['footer'] = "受取: " + mailTo_display
            postBody[0]['actions'].append({
                    "name": "btn1Name",
                    "text": "返信",
                    "type": "button",
                    "style": "default",
                    "value": "replyValue"
                })
        elif mailBoxName == 'INBOX.Sent':
            PostStateText = '@channel `メールの送信を検知しました'
            PostUserIcon = 'https://takuma-isec.sakura.ne.jp/kaniyama_t/slackapp/src/imaptrans_sended.png'
            postBody[0]['color'] = "#ffff00"
            postBody[0]['author_name'] = mailTo_display
            postBody[0]['author_link'] = 'mailto:'+mailToAdd
            postBody[0]['footer'] = "送信: " + mailFrom_display

        if succeedState != True:
            PostStateText = PostStateText+"が、正常にメールを読み込めませんでした"
            postBody[0]['color'] = "#ff0000"
            
        
        return self.post(channelId=channelId,ts=ts, text=PostStateText+'`\n', attachments=postBody,username=PostUserName,iconURL=PostUserIcon)
        