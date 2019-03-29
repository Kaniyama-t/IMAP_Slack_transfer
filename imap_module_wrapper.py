import ssl
from imaplib import IMAP4_SSL
import email
from email.header import decode_header, make_header
import configparser
import quopri
import base64
import socket
import sys

from imap_errors import Error, IMAPCommandError

class IMAPConnection():

    def __init__(self, URL, Port):
        print("__init__")
        # = init Process ====================================
        # = Grobal Attribute ================================
        self.URL = URL
        self.Port = Port
        # ===================================================
        # = SSL IMAP接続確立 =================================
        self.ImapInstance = IMAP4_SSL(host=URL, port=Port) # TODO:SSL確認
        # ===================================================


    def login(self, mUsername, mPassword):
        print("logined")
        self.mUsername = mUsername
        self.mPassword = mPassword
        self.ImapInstance.login(mUsername,mPassword)
        
    def selectBox(self, mailBox):
        print("selectBox")
        self.ImapInstance.select(mailbox=mailBox, readonly=False)
        
    def closeBox(self):
        print("closeBox")
        self.ImapInstance.close()
    
    def logout(self):
        print("logouted")
        self.ImapInstance.logout()
        
    def getNoFlaggedMail(self):
        """
        Flaggedメッセージを取得します

        Returns
        -------
        aaa : List<>
            対象の果物の値段。
        """
        # = SSL IMAP受信メール確認 ===========================
        # == メールボックス選択
        print("getNoFlaggedMail")

        # == 未送信メール(no-Flagged)を検索
        typ,msgnums = self.ImapInstance.uid('SEARCH',None,'(UNKEYWORD "POSTED_Slack")')
        if typ != 'OK':
            raise IMAPCommandError('search', 'I cannot get no-Flagged Mail.'+'\n responce: '+typ)
        
        return msgnums

    def getMailDetail(self, mailId):
        print("postSlack")
        # == 未送信メールを処理
        result={}
        ## メッセージ取得(ヘッダ・本文)
        typ, data = self.ImapInstance.uid('fetch',mailId, '(RFC822)')
        if typ != 'OK':
            raise IMAPCommandError('search', 'I cannot get Mail data of number'+mailId+"."+'\n responce: '+typ)
    
        ## ログ出力ぅ
        print('mail['+str(mailId)+']')
        for i in range(len(data)):
            for j in range(len(data[i])):
                if type(data[i][j])==bytes:
                    print("data["+str(i)+"]"+"["+str(j)+"]"+str(data[i][j].decode('iso2022_jp')))
                else:
                    print("data["+str(i)+"]"+"["+str(j)+"]"+str(data[i][j]))

        ## emailライブラリに渡す
        email_message = email.message_from_bytes(data[0][1])

        ## 本文抽出
        body = ''
        if email_message.is_multipart() == False: # シングルパート
            byt  = bytearray(email_message.get_payload(), 'iso2022_jp')
            body = byt.decode(encoding='iso2022_jp')
        else:   # マルチパート
            prt  = email_message.get_payload()[0]
            byt  = prt.get_payload(decode=True)
            body = byt.decode(encoding='iso2022_jp')

        #TODO ここ埋めれるように頑張る
        result['UID']=str(mailId)
        result['Subject']=str(make_header(decode_header(email_message['Subject'])))
        result['Body']=body
        result['From_Address']=str(make_header(decode_header(email_message['From'])))
        result['From_Name']=""
        result['To_Address']=str(make_header(decode_header(email_message['To'])))
        result['To_Name']=""
        return result
    
    def addFlagToMail(self,mailId,flag):
        self.ImapInstance.store(mailId, '+FLAGS', '\\'+flag)
    
    def boxlist(self):
        return self.ImapInstance.list()
