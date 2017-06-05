__editor__ = 0x5010
'''
Created by auto_sdk on 2014.04.11
'''
from ..base import RestApi


class TopatsResultGetRequest(RestApi):
    def __init__(self, domain='gw.api.taobao.com', port=80):
        RestApi.__init__(self, domain, port)
        self.task_id = None

    def getapiname(self):
        return 'taobao.topats.result.get'
