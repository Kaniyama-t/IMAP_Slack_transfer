import ssl
from imaplib import IMAP4_SSL
import email
from email.header import decode_header, make_header
from email.policy import default
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
        typ,msgnums = self.ImapInstance.uid('SEARCH',None,'(UNKEYWORD "_POSTED_SLACK")')
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
        """
        print('mail['+str(mailId)+']')
        for i in range(len(data)):
            for j in range(len(data[i])):
                if type(data[i][j])==bytes:
                    print("data["+str(i)+"]"+"["+str(j)+"]"+str(data[i][j].decode('iso2022_jp')))
                else:
                    print("data["+str(i)+"]"+"["+str(j)+"]"+str(data[i][j]))
        """
        

        ## emailライブラリに渡す
        email_message = email.message_from_bytes(data[0][1])
        
        ## データ抽出
        ### From
        From_Address = str(make_header(decode_header(email_message['From'])))
        From_Name = ''
        if "<" in From_Address:
            tmp_f = From_Address.split("<")
            From_Name = tmp_f[0]
            From_Address = tmp_f[1].split(">")[0]
        ### To
        To_Address = str(make_header(decode_header(email_message['To'])))
        To_Name = ''
        if "<" in To_Address:
            tmp_t = To_Address.split("<")
            To_Name = tmp_t[0]
            To_Address = tmp_t[1].split(">")[0]
        ### Subject
        Subject = str(make_header(decode_header(email_message['Subject'])))
        ### 本文抽出
        body = ''
        ## TODO ここ↓
        SucceedFlag = False
        try:
            if email_message.is_multipart() == False: # シングルパート
                print("シングルパート")
                byt  = bytearray(email_message.get_payload(), 'iso2022_jp')
                body = byt.decode(encoding='iso2022_jp')
            else:   # マルチパート
                print("マルチパート")
                prt  = email_message.get_payload()[0]
                byt  = prt.get_payload(decode=True)
                body = byt.decode(encoding='iso2022_jp')
            SucceedFlag = True
        except Exception as err_inst:
            body = 'メールを受信しましたが変換できませんでした\n\nエラーログ:\n' + str(err_inst)
            print(str(err_inst))

        #TODO ここ埋めれるように頑張る
        result['Succeed']=SucceedFlag
        result['UID']=mailId.hex()
        result['Subject']=Subject
        result['Body']=body
        result['From_Address']=From_Address
        result['From_Name']=From_Name
        result['To_Address']=To_Address
        result['To_Name']=To_Name
        return result
    
    def addFlagToMail(self,mailId,flag):
        typ,d = self.ImapInstance.uid('store',mailId, '+FLAGS', '\\'+flag+'')
        print('addFragToMail typ:'+str(typ))
        print('addFragToMail d:'+str(d))
        if typ != 'OK':
            raise IMAPCommandError('store', 'I cannot add Flag "' + str(flag) + '" of mail number'+str(mailId)+"."+'\n responce: '+str(d))


    def commitFrags(self):
        typ,d=self.ImapInstance.expunge()
        print('commitFrags typ:'+str(typ))
        print('commitFrags d:'+str(d))
        if typ != 'OK':
            raise IMAPCommandError('expunge', 'I cannot commit Flags of mail.\n responce: '+str(d))
    
    def boxlist(self):
        return self.ImapInstance.list()
