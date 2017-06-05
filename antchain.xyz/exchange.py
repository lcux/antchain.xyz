#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 5/16/17 12:02 AM
# @Author  : lcux
# @Site    : https://github.com/lcux
# @File    : yunbi.py
# @Software: PyCharm


import asyncio
import aiohttp
import async_timeout
from urllib.request import urlopen, Request
import json, ssl, datetime, time
from decimal import Decimal as D
from pymongo import MongoClient
from app import celery
from threading import Thread
from functools import wraps

db = MongoClient(connect=False).antchain_mainnet


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


@asyncio.coroutine
def get_info(url):
    # print('get %s' % url)
    try:
        with async_timeout.timeout(3):
            req = yield from aiohttp.request('GET', url)
            data = yield from req.read()
            change(data)
    except Exception as e:
        pass

def change(data):
    data = json.loads(data.decode('ascii'))
    try:
        if 'ticker' in data:
            yunbi = {}
            yunbi['buy'] = data['ticker']['buy']
            yunbi['sell'] = data['ticker']['sell']
            yunbi['high'] = data['ticker']['high']
            yunbi['low'] = data['ticker']['low']
            yunbi['last'] = data['ticker']['last']
            yunbi['vol'] = data['ticker']['vol']
            yunbi['name'] = 'yunbi'
            yunbi['date'] = datetime.datetime.utcnow()
            if db.Exchange.find_one({'_id': 'yunbi'}):
                result = db.Exchange.update_one({'_id': 'yunbi'}, {'$set': {'yunbi': yunbi}})
                # print(result.matched_count, result.modified_count, 'update yunbi')
            else:
                db.Exchange.insert_one({'_id': 'yunbi', 'yunbi': yunbi})
        if 'name' in data:
            yuanbao = {}
            yuanbao['buy'] = data['buy']
            yuanbao['sell'] = data['sale']
            yuanbao['high'] = data['max']
            yuanbao['low'] = data['min']
            yuanbao['last'] = data['price']
            yuanbao['vol'] = data['volume_24h']
            yuanbao['name'] = 'yuanbao'
            yuanbao['date'] = datetime.datetime.utcnow()
            if db.Exchange.find_one({'_id': 'yuanbao'}):
                result = db.Exchange.update_one({'_id': 'yuanbao'}, {'$set': {'yuanbao': yuanbao}})
                # print(result.matched_count, result.modified_count, 'update yuanbao')
            else:
                db.Exchange.insert_one({'_id': 'yuanbao', 'yuanbao': yuanbao})
        if 'success' in data:
            if data['result'][0]['MarketName'] == 'USDT-BTC':
                bittrex_btc = {}
                bittrex_btc['buy'] = data['result'][0]['Bid']
                bittrex_btc['sell'] = data['result'][0]['Ask']
                bittrex_btc['high'] = data['result'][0]['High']
                bittrex_btc['low'] = data['result'][0]['Low']
                bittrex_btc['last'] = data['result'][0]['Last']
                bittrex_btc['vol'] = data['result'][0]['Volume']
                bittrex_btc['name'] = 'bittrex_btc'
                bittrex_btc['date'] = datetime.datetime.utcnow()
                if db.Exchange.find_one({'_id': 'bittrex_btc'}):
                    result = db.Exchange.update_one({'_id': 'bittrex_btc'}, {'$set': {'bittrex_btc': bittrex_btc}})
                    # print(result.matched_count, result.modified_count, 'update bittrex_btc')
                else:
                    db.Exchange.insert_one({'_id': 'bittrex_btc', 'bittrex_btc': bittrex_btc})
            else:
                bittrex = {}
                bittrex['buy'] = data['result'][0]['Bid']
                bittrex['sell'] = data['result'][0]['Ask']
                bittrex['high'] = data['result'][0]['High']
                bittrex['low'] = data['result'][0]['Low']
                bittrex['last'] = data['result'][0]['Last']
                bittrex['vol'] = data['result'][0]['Volume']
                bittrex['name'] = 'bittrex'
                bittrex['date'] = datetime.datetime.utcnow()
                if db.Exchange.find_one({'_id': 'bittrex'}):
                    result = db.Exchange.update_one({'_id': 'bittrex'}, {'$set': {'bittrex': bittrex}})
                    # print(result.matched_count, result.modified_count, 'update bittrex')
                else:
                    db.Exchange.insert_one({'_id': 'bittrex', 'bittrex': bittrex})
        if 'code' in data:
            e9800 = {}
            e9800['buy'] = data['data']['TopBid']
            e9800['sell'] = data['data']['TopAsk']
            e9800['high'] = data['data']['High']
            e9800['low'] = data['data']['Low']
            e9800['last'] = data['data']['LastPrice']
            e9800['vol'] = data['data']['Volume']
            e9800['name'] = 'e9800'
            e9800['date'] = datetime.datetime.utcnow()
            if db.Exchange.find_one({'_id': 'e9800'}):
                result = db.Exchange.update_one({'_id': 'e9800'}, {'$set': {'e9800': e9800}})
                # print(result.matched_count, result.modified_count, 'update e9800')
            else:
                db.Exchange.insert_one({'_id': 'e9800', 'e9800': e9800})
        if 'volume' in data:
            jubi = {}
            jubi['buy'] = data['buy']
            jubi['sell'] = data['sell']
            jubi['high'] = data['high']
            jubi['low'] = data['low']
            jubi['last'] = data['last']
            jubi['vol'] = data['vol']
            jubi['name'] = 'jubi'
            jubi['date'] = datetime.datetime.utcnow()
            if db.Exchange.find_one({'_id': 'jubi'}):
                result = db.Exchange.update_one({'_id': 'jubi'}, {'$set': {'jubi': jubi}})
                # print(result.matched_count, result.modified_count, 'update jubi')
            else:
                db.Exchange.insert_one({'_id': 'jubi', 'jubi': jubi})
        if isinstance(data, list):
            if 'rank' in data[0]:
                coinmarketcap = {}
                coinmarketcap['rank'] = data[0]['rank']
                if db.Exchange.find_one({'_id': 'coinmarketcap'}):
                    result = db.Exchange.update_one({'_id': 'coinmarketcap'},
                                                    {'$set': {'coinmarketcap': coinmarketcap}})
                    # print(result.matched_count, result.modified_count, 'update coinmarketcap')
                else:
                    db.Exchange.insert_one({'_id': 'coinmarketcap', 'coinmarketcap': coinmarketcap})
    except Exception as e:
        print(e, 'it is here')



def middle():
    url = ['https://yunbi.com//api/v2/tickers/anscny.json', 'https://www.yuanbao.com/api_market/getinfo_cny/coin/ans',
           'https://bittrex.com/api/v1.1/public/getmarketsummary?market=btc-ans',
           'https://19800.com/api/v1/ticker?market=cny_ans&nonce=8', 'https://www.jubi.com/api/v1/ticker?coin=ans',
           'https://bittrex.com/api/v1.1/public/getmarketsummary?market=usdt-btc']

    loop = asyncio.get_event_loop()
    tasks = [get_info(i) for i in url]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close

@celery.task
# @fn_timer
def get_exchange_info():
    thr = Thread(target=middle())
    thr.start()
    # return thr


if __name__ == '__main__':
    print(get_exchange_info())
    # get_cny_usd()
    # get_yunbi_ans_time(1477007960)
