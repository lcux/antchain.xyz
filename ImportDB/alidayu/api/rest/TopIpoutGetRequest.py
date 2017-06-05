__editor__ = 0x5010
'''
Created by auto_sdk on 2015.09.07
'''
from ..base import RestApi


class TopIpoutGetRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)

    def getapiname(self):
        return 'taobao.top.ipout.get'
