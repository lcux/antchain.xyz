#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import requests

d = 'http://139.224.226.167:20332'
p = {"jsonrpc": "2.0", "method": "", "params": [], "id": 1}


def chuli(json_params):
    r = requests.post(d, json=json_params)
    result = r.json()
    return result['result']


def getbestblockhash():
    '''获取主链中高度最大的区块的散列'''
    p['method'] = 'getbestblockhash'
    p['params'] = []
    reslut = chuli(p)
    return reslut


def getblock(hash_index=0):
    '''根据指定的散列值或者索引，返回对应的区块信息'''
    p['method'] = 'getblock'
    p['params'] = [hash_index, 1]
    reslut = chuli(p)
    return reslut


def getblockcount():
    '''获取主链中区块的数量'''
    p['method'] = 'getblockcount'
    p['params'] = []
    reslut = chuli(p)
    return reslut


def getblockhash(index=0):
    '''根据指定的索引，返回对应区块的散列值'''
    p['method'] = 'getblockhash'
    p['params'] = [index, 1]
    reslut = chuli(p)
    return reslut


def getconnectioncount():
    '''获取节点当前的连接数'''
    p['method'] = 'getconnectioncount'
    p['params'] = []
    reslut = chuli(p)
    return reslut


def getrawmempool(txid=''):
    '''获取内存中未确认的交易列表'''
    p['method'] = 'getrawmempool'
    if txid:
        p['params'] = [txid, 1]
    else:
        p['params'] = []
    reslut = chuli(p)
    return reslut


def getrawtransaction(txid=''):
    '''根据指定的散列值，返回对应的交易信息'''
    p['method'] = 'getrawtransaction'
    if txid:
        p['params'] = [txid, 1]
    else:
        p['params'] = []
    reslut = chuli(p)
    return reslut

def gettxin(hash_index):
    jiaoyi=getrawtransaction(hash_index)

def gettxout(hash_index):
    '''	<txid> <n>		根据指定的散列和索引，返回对应的零钱信息'''
    p['method'] = 'gettxout'
    p['params'] = [hash_index, 1]
    reslut = chuli(p)
    return reslut

def sendrawtransaction(hash_hex):
    '''广播交易'''
    p['method'] = 'sendrawtransaction'
    p['params'] = hash_hex
    reslut = chuli(p)
    return reslut


def getbalance(asset_id):
    '''根据指定的资产编号，返回钱包中对应资产的余额信息'''
    p['method'] = 'getbalance'
    p['params'] = asset_id
    reslut = chuli(p)
    return reslut


def submitblock(params):
    '''	<hex>提交新的区块'''
    p['method'] = 'submitblock'
    p['params'] = params
    reslut = chuli(p)
    return reslut

if __name__=='__main__':
#    print(getblcok(getbestblockhash()))
#    print(gettxout('cdafe40cf2b712886b08e838e1cfe1f5e258b106741a3be757059027a11ffa29'))
#    print(getrawtransaction('3631f66024ca6f5b033d7e0809eb993443374830025af904fb51b0334f127cda'))
#    print(getblock(0))
#    print(getbalance('c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b'))
    print('Nothing!')