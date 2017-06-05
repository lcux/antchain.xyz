__editor__ = 0x5010
'''
Created by auto_sdk on 2016.03.01
'''
from ..base import RestApi


class AlibabaAliqinFcVoiceNumSinglecallRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)
        self.called_num = None
        self.called_show_num = None
        self.extend = None
        self.voice_code = None

    def getapiname(self):
        return 'alibaba.aliqin.fc.voice.num.singlecall'
