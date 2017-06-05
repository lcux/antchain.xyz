#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 5/6/17 12:14 AM
# @Author  : lcux
# @Site    : https://github.com/lcux
# @File    : functions.py
# @Software: PyCharm

# from . import db
from pymongo import MongoClient, DESCENDING, ASCENDING
import operator, datetime, json, time
from decimal import Decimal as D
from functools import wraps
from urllib.request import Request, urlopen
# from alidayu import api, appinfo

INDEX_PAGE_NUM = 10
db = MongoClient(connect=False).antchain_mainnet


#############
# 测试专用函数
#############


# 用于测试函数运行时间，使用方法：通过装饰器 @fn_timer
def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print("Total time running %s: %s seconds" %
              (function.__name__, str(t1 - t0)))
        return result

    return function_timer


#################
# 区块、交易、地址的内容和数量查询函数
#################

def block_content(sequence=DESCENDING, num=INDEX_PAGE_NUM):
    return db.Block.find().sort("_id", sequence).limit(num)


def block_count():
    # return db.Block.count()
    return db.Block.find({}, {'_id': 1}).sort('_id', DESCENDING)[0]['_id'] + 1


# 有非挖矿交易的区块数量，应该通过tx列表表中交易数量判断
def block_count_gt686():
    return db.Block.count({'size': {'$gt': 686}})
    # return db.Block.find({'size': {'$gt': 686}}, {'_id': 1}).sort('_id', DESCENDING)[0]['_id'] + 1


def transaction_content(sequence=DESCENDING, num=INDEX_PAGE_NUM):
    return db.Transaction.find().sort('timestamp', sequence).limit(num)


# mt即MinerTransaction
def transaction_no_mt_content(sequence=DESCENDING, num=INDEX_PAGE_NUM):
    return db.Transaction.find({'type': {'$ne': 'MinerTransaction'}}).sort('timestamp', sequence).limit(num)


def transaction_count():
    return db.Transaction.count()
    # return db.Transaction.find({}, {'id': 1}).sort('timestamp', DESCENDING)[0]['id'] + 1


def transaction_no_mt_count():
    # return db.Transaction.count({'type': {'$ne': 'MinerTransaction'}})
    return db.Transaction.find({'type': {'$ne': 'MinerTransaction'}}, {'id': 1}).sort('timestamp', DESCENDING)[0][
               'id'] + 1


def address_content(sequence=DESCENDING, num=INDEX_PAGE_NUM):
    return db.Address.find().sort("firsttime", sequence).limit(num)


def address_count():
    # return db.Address.count()
    return db.Address.find({}, {'id': 1}).sort('firsttime', DESCENDING)[0]['id'] + 1


def asset_count1():
    # return db.Transaction.count({'type': 'RegisterTransaction'})
    cur = db.Transaction.find({'type': 'RegisterTransaction'}, {'_id': 1})
    i = 0
    for x in cur:
        i = i + 1
    return i


def asset_count():
    return db.Transaction.count({'type': 'RegisterTransaction'})


def validator_count():
    return db.Transaction.count({'type': 'EnrollmentTransaction'})


def contract_tx_count():
    return db.Transaction.count({'type': 'ContractTransaction'})


def claim_tx_count():
    return db.Transaction.count({'type': 'ClaimTransaction'})


def publish_tx_count():
    return db.Transaction.count({'type': 'PublishTransaction'})


#############
# 资产持有人数查询函数
#############


####
# 一下两个函数的运行速度的结果
# Total time running ans_holding: 0.021109819412231445 seconds
# Total time running ans_holding1: 0.08938765525817871 seconds
# Total time running ans_holding_100_500_1000_5000_10000_100000: 0.0843045711517334 seconds
# Total addresses are 3448

# @fn_timer
def ans_holding():
    return db.Address.count(
        {'balance.c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b': {'$exists': True},
         'balance.c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b.value': {'$ne': '0'}})


# @fn_timer
def ans_holding1():
    zongde = []
    asset = 'c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b'
    ss = 'balance.' + asset
    cur_ad = db.Address.find({ss: {'$exists': True}}, {'balance': 1, 'lasttime': 1})
    for s in cur_ad:
        for x in s['balance'].keys():
            if x == asset and D(s['balance'][x]['value']) != D('0'):
                zongde.append([s['_id'], D(s['balance'][x]['value']), s['lasttime']])
            else:
                continue
    zongde.sort(key=operator.itemgetter(1), reverse=True)
    return len(zongde)


# @fn_timer
def ans_holding_100_500_1000_5000_10000_100000():
    zongde = []
    d = {}
    asset = 'c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b'
    ss = 'balance.' + asset
    cur_ad = db.Address.find({ss: {'$exists': True}}, {'balance': 1, 'lasttime': 1})
    for s in cur_ad:
        for x in s['balance'].keys():
            if x == asset and D(s['balance'][x]['value']) != D('0'):
                zongde.append([s['_id'], s['balance'][x]['value'], s['lasttime']])
            else:
                continue
    zongde.sort(key=operator.itemgetter(1), reverse=True)
    # return len(zongde)

    xcount = 0
    for x in range(len(zongde)):
        xcount += zongde[x][1]
        if x == 99:
            d['ans_holding_100'] = str(xcount)
        elif x == 499:
            d['ans_holding_500'] = str(xcount)
        elif x == 999:
            d['ans_holding_1000'] = str(xcount)
        elif x == 4999:
            d['ans_holding_5000'] = str(xcount)
        elif x == 9999:
            d['ans_holding_10000'] = str(xcount)
        elif x == 99999:
            d['ans_holding_100000'] = str(xcount)
    d['ans_holding_' + str(len(zongde))] = str(xcount)
    return d


def anc_holding():
    zongde = []
    asset = '602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7'
    ss = 'balance.' + asset
    cur_ad = db.Address.find({ss: {'$exists': True}}, {'balance': 1, 'lasttime': 1})
    for s in cur_ad:
        for x in s['balance'].keys():
            if x == asset and D(s['balance'][x]['value']) != D('0'):
                zongde.append([s['_id'], D(s['balance'][x]['value']), s['lasttime']])
            else:
                continue
    zongde.sort(key=operator.itemgetter(1), reverse=True)
    return len(zongde)

    # 因为value值存在0.0、0.00、0.000...等的情况，所以不能用以下函数计算
    # return db.Address.count(
    #     {'balance.602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7': {'$exists': True},
    #      'balance.602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7.value': {'$ne': '0'}})


# 返回值为（资产持有人排名list[address，value，lasttime],资产持有人数）的元组
# 需要Mongodb中优化下面的的资产搜索索引
def asset_holding(asset):
    asset_hash = 'balance.' + asset
    # asset_value = 'balance.' + asset + '.value'
    # return db.Address.count({asset_hash:{'$exists':True},asset_value:{'$ne':0}})
    cur_ad = db.Address.find({asset_hash: {'$exists': True}}, {'balance': 1, 'lasttime': 1})
    asset = []
    for s in cur_ad:
        for x in s['balance'].keys():
            if x == asset and D(s['balance'][x]['value']):
                asset.append([s['_id'], s['balance'][x]['value'], s['lasttime']])
            else:
                continue
    asset.sort(key=operator.itemgetter(1), reverse=True)
    holding = len(asset)
    return asset, holding


def asset_holding1(asset, result=1):
    zongde = []
    ss = 'balance.' + asset
    cur_ad = db.Address.find({ss: {'$exists': True}}, {'balance': 1, 'lasttime': 1})
    for s in cur_ad:
        for x in s['balance'].keys():
            if x == asset and D(s['balance'][x]['value']) != D('0'):
                zongde.append([s['_id'], D(s['balance'][x]['value']), s['lasttime']])
            else:
                continue
    zongde.sort(key=operator.itemgetter(1), reverse=True)

    if result == 1:
        return len(zongde)
    else:
        return (zongde, len(zongde))


#############
# 资产发行量查询函数
#############

def ans_criculation():
    return 100000000


def anc_criculation(blocks=None):
    if blocks is None:
        blocks = block_count()
    di = 20000000
    num = 0
    if blocks <= di:
        num = blocks * 8
    elif di < blocks <= di * 2:
        num = di * 8 + (blocks - di) * 7
    elif di * 2 < blocks <= di * 3:
        num = di * (8 + 7) + (blocks - di * 2) * 6
    elif di * 3 < blocks <= di * 4:
        num = di * (8 + 7 + 6) + (blocks - di * 3) * 5
    elif di * 4 < blocks <= di * 5:
        num = di * (8 + 7 + 6 + 5) + (blocks - di * 4) * 4
    elif di * 5 < blocks <= di * 6:
        num = di * (8 + 7 + 6 + 5 + 4) + (blocks - di * 5) * 3
    elif di * 6 < blocks <= di * 7:
        num = di * (8 + 7 + 6 + 5 + 4 + 3) + (blocks - di * 6) * 2
    elif blocks > di * 7:
        num = di * (8 + 7 + 6 + 5 + 4 + 3 + 2) + (blocks - di * 7) * 1
    return num


# 返回值为（发行数量，发行次数,每次发行的信息表lsit[[每次发行的交易信息,每次发行量],...）的元组
def asset_criculation(asset):
    if asset == '602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7':
        return anc_criculation(block_count()), block_count()
    else:
        it_txs = db.Transaction.find({"type": 'IssueTransaction', 'vout': {'$elemMatch': {'asset': asset}}})
        frequency = it_txs.count()
        criculation = D('0')
        pre_asset = []
        for pre_tx in it_txs:
            pre_criculation = D('0')
            for y in pre_tx['vout']:
                if y['asset'] == asset:
                    criculation += D(y['value'])
                    pre_criculation += D(y['value'])
            pre_asset.append([pre_tx, pre_criculation])
        return criculation, frequency, pre_asset

#
def it_tx_pre_circulation(txid):
    tx = db.Transaction.find_one({'_id': txid})
    circulation = D('0')
    for y in tx['vout']:
        if y['asset'] == tx['vout'][0]['asset']:  # 发行交易的输出vout的第一个，肯定是发行的资产。
            circulation += D(y['value'])
    return circulation





def ans_quota_and_worth():
    cur = db.Exchange.find()
    all_vol = D('0')
    yunbi_price, yunbi_vol = D('0'), D('0')
    yuanbao_price, yuanbao_vol = D('0'), D('0')
    bittrex_price, bittrex_vol = D('0'), D('0')
    e9800_price, e9800_vol = D('0'), D('0')
    jubi_price, jubi_vol = D('0'), D('0')
    szzc51_price, szzc51_vol = D('0'), D('0')
    rate, btc_price = D('0'),D('0')

    for n in cur:
        if n['_id'] == 'yunbi':
            yunbi_price = D(n['yunbi']['last'])
            yunbi_vol = D(n['yunbi']['vol'])
            all_vol += yunbi_vol
        elif n['_id'] == 'yuanbao':
            yuanbao_price = D(n['yuanbao']['last'])
            yuanbao_vol = D(n['yuanbao']['vol'])
            all_vol += yuanbao_vol
        elif n['_id'] == 'bittrex':
            bittrex_price = D(n['bittrex']['last'])
            bittrex_vol = D(n['bittrex']['vol'])
            all_vol += bittrex_vol
        elif n['_id'] == 'e9800':
            e9800_price = D(n['e9800']['last'])
            e9800_vol = D(n['e9800']['vol'])
            all_vol += e9800_vol
        elif n['_id'] == 'jubi':
            jubi_price = D(n['jubi']['last'])
            jubi_vol = D(n['jubi']['vol'])
            all_vol += jubi_vol
        elif n['_id'] == 'szzc51':
            szzc51_price = D(n['szzc51']['last'])
            szzc51_vol = D(n['szzc51']['vol'])
            all_vol += szzc51_vol
        elif n['_id'] == 'bittrex_btc':
            btc_price = D(n['bittrex_btc']['last'])
        elif n['_id'] == 'rate':
            rate = D(n['cnyusd'])
        else:
            pass

    cny_usd_rate = db.Exchange.find_one({'_id': 'rate'})
    if not cny_usd_rate:
        db.Exchange.insert_one({'_id': 'rate', 'cnyusd': get_cny_usd()})
    rate = db.Exchange.find_one({'_id': 'rate'})['cnyusd']

    ans_quota = (yunbi_vol / all_vol * yunbi_price) + (yuanbao_vol / all_vol * yuanbao_price) + (
        bittrex_vol / all_vol * bittrex_price * btc_price * D(rate)) + (e9800_vol / all_vol * e9800_price) + (
                    jubi_vol / all_vol * jubi_price) + (szzc51_vol / all_vol * szzc51_price)
    ans_worth = ans_quota * 100000000
    ans_quota = ans_quota.quantize(D('0.00000000'))
    ans_worth = ans_worth.quantize(D('0.00000000'))

    return str(ans_quota), str(ans_worth)


def system_runtime():
    return ((db.Block.find_one({'_id': block_count() - 1}, {'timestamp': 1, '_id': -1})['timestamp'] -
             db.Block.find_one({'_id': 1}, {'timestamp': 1, '_id': -1})['timestamp']).days + 1)


def block_average_generaetime(num=100):
    return int(((db.Block.find_one({'_id': block_count() - 1}, {'timestamp': 1, '_id': -1})['timestamp'] -
                 db.Block.find_one({'_id': block_count() - (num + 1)}, {'timestamp': 1, '_id': -1})[
                     'timestamp']).seconds) / num)


# 如果year为零，则获取今日的日期，并从0时开始查询截至当前时间的数量;
# 如果year不为零，则从行参数中获取时间，并查询num_days参数时间内的数量;

def address_growth(year=0, month=1, day=1, num_days=1):
    if not year:
        today = datetime.datetime.utcnow()
        year = today.year
        month = today.month
        day = today.day
        c = datetime.datetime(year, month, day)
        return db.Address.count({'firsttime': {'$gte': c}})
    else:
        d = datetime.datetime(year, month, day)
        e = d + datetime.timedelta(days=num_days)
        # c=datetime.datetime(2016,10,18)
        return db.Address.count({'firsttime': {'$gte': d, '$lt': e}})


def tx_no_mt_growth(year=0, month=1, day=1, num_days=1):
    if not year:
        today = datetime.datetime.utcnow()
        year = today.year
        month = today.month
        day = today.day
        c = datetime.datetime(year, month, day)
        # c=datetime.datetime(2016,10,18)
        return db.Transaction.count({'type': {'$ne': 'MinerTransaction'}, 'timestamp': {'$gte': c}})
    else:
        d = datetime.datetime(year, month, day)
        e = d + datetime.timedelta(days=num_days)
        # c=datetime.datetime(2016,10,18)
        return db.Transaction.count({'type': {'$ne': 'MinerTransaction'}, 'timestamp': {'$gte': d, '$lt': e}})


##资产持有人增长率

def asset_holding_daily_growth(asset):
    asset_hash = 'balance.' + asset
    # asset_value = 'balance.' + asset + '.value'
    # return db.Address.count({asset_hash:{'$exists':True},asset_value:{'$ne':0}})
    cur_ad = db.Address.find({asset_hash: {'$exists': True}}, {'balance': 1, 'lasttime': 1})


##资产发行增长率

def asset_criculation_growth(asset):
    pass


##############
#函数
##############

def get_cny_usd():
    host = 'https://ali-waihui.showapi.com'
    path = '/waihui-list'
    method = 'GET'
    appcode = 'XXXXXXXXXXXXXXX'
    querys = 'code=USD'
    bodys = {}
    url = host + path + '?' + querys

    request = Request(url)
    request.add_header('Authorization', 'APPCODE ' + appcode)
    response = urlopen(request)
    content = response.read()
    data = json.loads(content.decode('utf-8'))
    # if (content):
    #     print(content)
    return D(data['showapi_res_body']['list'][0]['zhesuan'])/D('100')


def get_yunbi_ans_time(timestamp=0):
    url='https://yunbi.com/api/v2/k.json?market=anscny&limit=1&period=1440'
    if timestamp:
        url=url+'&timestamp='+str(timestamp)
    request=Request(url)
    response=urlopen(request)
    content=response.read()
    data=json.loads(content.decode('utf-8'))
    if data:
        # print(data,data[0][4])
        # print(type(data[0][4]))
        return str(data[0][4])


def get_coinmarketcap_ans():
    url='https://api.coinmarketcap.com/v1/ticker/antshares/?convert=CNY'
    request=Request(url)
    response=urlopen(request)
    content=response.read()
    data=json.loads(content.decode('utf-8'))
    if data:
        # print(data,data[0][4])
        return data[0]['rank']





if __name__ == '__main__':
    # from pymongo import MongoClient

    # db = MongoClient(connect=False).antchain_mainnet
    # print('ans_quota is %s and ans_worth is %s', ans_quota_and_worth())
    # print(ans_holding(), ans_holding1(), ans_holding_100_500_1000_5000_10000_100000())
    # print('transaction=>', tx_no_mt_growth(year=2016, num_days=4))
    print('address=>', get_cny_usd())
    # print('address=>', get_coinmarketcap_ans())
    # send_message()
