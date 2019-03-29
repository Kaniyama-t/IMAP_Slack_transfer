class Error(Exception):
    pass

class ConnectionError(Error):
    def __init__(self, url, body, message):
        self.url=url
        self.body=body
        self.message=message

class ConfigParserError(Error):
    def __init__(self, msg="ConfigPerserを実行時にエラーが発生しました"):
        self.message=msg

class IMAPCommandError(Error):
    def __init__(self, causeCommand, message):
        self.command = causeCommand
        self.message = message
        

class SlackPostError(Error):
    def __init__(self, responce, msg="SlackAPIがエラーを返しました"):
        self.responce = responce
        self.message=msg

