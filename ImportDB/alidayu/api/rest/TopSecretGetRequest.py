__editor__ = 0x5010
'''
Created by auto_sdk on 2016.04.06
'''
from ..base import RestApi


class TopSecretGetRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)
        self.random_num = None
        self.secret_version = None

    def getapiname(self):
        return 'taobao.top.secret.get'
