__editor__ = 0x5010
'''
Created by auto_sdk on 2014.11.26
'''
from ..base import RestApi


class AppipGetRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)

    def getapiname(self):
        return 'taobao.appip.get'
