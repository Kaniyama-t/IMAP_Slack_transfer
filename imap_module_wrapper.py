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
        # = init Process ====================================
        # = Grobal Attribute ================================
        self.URL = URL
        self.Port = Port
        # ===================================================
        # = SSL IMAP接続確立 =================================
        self.ImapInstance = IMAP4_SSL(host=URL, port=Port) # TODO:SSL確認
        # ===================================================


    def login(self, mUsername, mPassword):
        self.mUsername = mUsername
        self.mPassword = mPassword
        self.ImapInstance.login(mUsername,mPassword)
        print('                               - connected with imap')
        
    def selectBox(self, mailBox):
        self.ImapInstance.select(mailbox=mailBox, readonly=False)
        print('                               - opened' + mailBox)

    def closeBox(self):
        self.ImapInstance.close()
        print('                               - closed')
    
    def logout(self):
        self.ImapInstance.logout()
        print('                               - disconnected')
        
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
        print('                               - searching (UNCHECK _POSTED_SLACK) ... ',end='')

        # == 未送信メール(no-Flagged)を検索
        typ,msgnums = self.ImapInstance.uid('SEARCH',None,'(UNKEYWORD "_POSTED_SLACK")')
        if typ != 'OK':
            print('failed')
            raise IMAPCommandError('search', 'I cannot get no-Flagged Mail.'+'\n responce: '+typ)
        
        # == ログ出力
        if len(msgnums) > 0:
            print('got ' + str(len(msgnums)) + 'mails!')
        else:
            print('no mail.')

        return msgnums

    def getMailDetail(self, mailId):
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

        ### ログ出力
        print('                                  > '+ str(mailId.hex()) +':'+ Subject +' ' + From_Address + '<' + From_Name + '> '+ To_Address + '<' + To_Name + '>')

        ### 本文抽出
        #### 本文取得
        body = ''
        SucceedFlag = False
        try:
            if email_message.is_multipart() == False: # シングルパート
                print('                                     - getting body as single part')
                byt  = bytearray(email_message.get_payload(), 'iso2022_jp')
                body = byt.decode(encoding='iso2022_jp')
            else:   # マルチパート
                print('                                     - getting body as multi part')
                prt  = email_message.get_payload()[0]
                byt  = prt.get_payload(decode=True)
                body = byt.decode(encoding='iso2022_jp')
            print('                                     - body decode succeed!')
            SucceedFlag = True
        except Exception as err_inst:
            body = 'メールを受信しましたが変換できませんでした\n\nエラーログ:\n' + str(err_inst.__class__.__name__) + ":" + str(err_inst)
            print(str(err_inst.__class__.__name__) + str(err_inst))


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
        print('                                     - added flag "'+str(flag)+'"')
        if typ != 'OK':
            raise IMAPCommandError('store', 'I cannot add Flag "' + str(flag) + '" of mail number'+str(mailId)+"."+'\n responce: '+str(d))

    
    def boxlist(self):
        return self.ImapInstance.list()
