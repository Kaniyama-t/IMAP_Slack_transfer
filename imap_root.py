
from imap_module_wrapper import IMAPConnection
from slackapi import SlackPoster
import configparser
import os.path
import sys


# = 設定ファイル ロード ========================================================
envConfig = configparser.ConfigParser()
envConfig.read('../slacknotify_envsettings.ini')
addressList = configparser.ConfigParser()
addressList.read('slacknotify_addresslist.ini')
poricyList = configparser.ConfigParser()
poricyList.read('slacknotify_domainlist.ini')

# = 新規メールのチェック・Slack転送 =============================================
## 核心的処理
def mailCheckAndProcess(session):
    ## Flagがついてないメールの番号を取得
    mails=session.getNoFlaggedMail()
    ## 各メールについて処理
    
    for i in mails[0].split():
        ## メールを取得
        mail=session.getMailDetail(i)
        mailaddressInfo = addressList.items(section=section)
        ## メールアドレスと紐づいた全ての受付チャンネルについて処理
        for p in mailaddressInfo:
            if('imap_notify' in p[0]):
                ## 受信チャンネルへメール転送
                slackpt=SlackPoster()
                slackpt.IMAPMailPost(
                    channelId = p[1],
                    uid = mail['UID'],
                    mailFromAdd = mail['From_Address'],
                    mailFromName = mail['From_Name'],
                    mailToAdd = mail['To_Address'],
                    mailToName = mail['To_Name'],
                    mailsub = mail['Subject'],
                    mailbody = mail['Body']
                )
    

## めんどい色々
for sections in addressList.items():
    # [ここから] メールアドレス毎に実行
    section = sections[0]
    if section == "DEFAULT":
        continue
    # IMAPサーバURL/Port ロード
    poricyName = addressList[section]['poricy']
    IMAPserverUrl = poricyList[poricyName]['imap_address']
    IMAPServerPort = poricyList[poricyName]['imap_port']
    # IMAPサーバ接続
    session = IMAPConnection(IMAPserverUrl,IMAPServerPort) # Sock Session作成
    session.login(addressList[section]['imap_user'],addressList[section]['imap_pass']) # Login
    ## 全メールのチェック・転送・マーク処理
    session.selectBox('INBOX')
    mailCheckAndProcess(session)
    ## 後始末
    session.closeBox()
    session.logout()
    # [ここまで] メールアドレス毎に実行


