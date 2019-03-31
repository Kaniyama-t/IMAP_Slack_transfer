
from imap_module_wrapper import IMAPConnection
from imap_slackapi import SlackPoster
import requests
import configparser
import os.path
import sys

print('[IMAP_transfar_SlackPost] **************************')
print('                           IMAP MailCheck START')
print('                          **************************')

# = 設定ファイル ロード ========================================================
envConfig = configparser.ConfigParser()
envConfig.read('../slacknotify_envsettings.ini')
addressList = configparser.ConfigParser()
addressList.read('slacknotify_addresslist.ini')
poricyList = configparser.ConfigParser()
poricyList.read('slacknotify_domainlist.ini')
print('                            - Loaded config files.')

# = 新規メールのチェック・Slack転送 =============================================
## 核心的処理
def mailCheckAndProcess(session, mailBoxName):
    ## Flagがついてないメールの番号を取得
    session.selectBox(mailBoxName)
    mails=session.getNoFlaggedMail()
    ## 各メールについて処理
    
    for i in mails[0].split():
        ## メールを取得
        mail=session.getMailDetail(i)
        mailaddressInfo = addressList.items(section=section)
        ## メールアドレスと紐づいた全ての受付チャンネルについて処理
        print('                                     - posting to slack')
        ProceedCnt = 0
        FinishedResponces = []
        for p in mailaddressInfo:
            if('imap_notify' in p[0]):
                ## 受信チャンネルへメール転送
                ProceedCnt = ProceedCnt + 1
                try:
                    print('                                        - ' + p[1] + ' ...',end='')
                    slackpt=SlackPoster()
                    responce=slackpt.IMAPMailPost(
                        channelId = p[1],
                        uid = mail['UID'],
                        succeedState = mail['Succeed'],
                        mailBoxName = mailBoxName,
                        mailFromAdd = mail['From_Address'],
                        mailFromName = mail['From_Name'],
                        mailToAdd = mail['To_Address'],
                        mailToName = mail['To_Name'],
                        mailsub = mail['Subject'],
                        mailbody = mail['Body']
                    )
                    print('succeed(ts:'+responce['ts']+')')
                    session.addFlagToMail(i,'Slack_'+responce['ts'])
                    FinishedResponces.append(responce)
                except Exception as Err_inst:
                    print('failed')
                    print(Err_inst)
                    continue
        if ProceedCnt == len(FinishedResponces):
            print('                                        Transfar Mail Completed of mail '+str(i))
            session.addFlagToMail(i,'POSTED_SLACK_COMPLETED')
        if len(FinishedResponces) != 0:
            print('                                        -Transfar Mail of '+str(i))
            print('                                          - RequirePost:'+str(ProceedCnt))
            print('                                          - CompletedPost:'+str(len(FinishedResponces)))
            session.addFlagToMail(i,'POSTED_SLACK')
        print('                                     - completed')
    session.closeBox()
    

## めんどい色々
print('                            - Start checking all addresses with imap that registrated.')
for sections in addressList.items():
    # [ここから] メールアドレス毎に実行
    section = sections[0]
    if section == "DEFAULT":
        continue
    # IMAPサーバURL/Port ロード
    poricyName = addressList[section]['poricy']
    IMAPserverUrl = poricyList[poricyName]['imap_address']
    IMAPServerPort = poricyList[poricyName]['imap_port']
    print('                            >> ' + addressList[section]['imap_user'])
    # IMAPサーバ接続
    session = IMAPConnection(IMAPserverUrl,IMAPServerPort) # Sock Session作成
    session.login(addressList[section]['imap_user'],addressList[section]['imap_pass']) # Login
    ## 全メールのチェック・転送・マーク処理
    mailCheckAndProcess(session,'INBOX')
    mailCheckAndProcess(session,'INBOX.Sent')
    print('                               - finished all processes with this address')
    ## 後始末
    session.logout()
    # [ここまで] メールアドレス毎に実行

print('                            - Mission completed!')
