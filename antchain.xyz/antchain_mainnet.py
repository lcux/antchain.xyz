#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from pymongo import MongoClient, DESCENDING, ASCENDING
import antsharesjsonrpc
import datetime
import operator
import json
import zhuanhuan
import binascii

######################
# 程序设置部分
######################
app = Flask(__name__)
bootstrap = Bootstrap(app)
monment = Moment(app)

# meiyexianshishu = 50
# page = 1

db = MongoClient(connect=False).antchain_mainnet
# db = MongoClient(connect=False).antchain_testnet


######################
# 视图控制部分
######################

@app.route('/')
def index():
    cursor_block = db.Block.find().sort("height", DESCENDING).limit(10)
    cursor_tx = db.Transaction.find({'type': {'$ne': 'MinerTransaction'}}).sort("_id", DESCENDING).limit(10)
    cursor_address = db.Address.find().sort("$natural", DESCENDING).limit(10)
    # 特定字段查询
    # tx=db.Block.find({'height':{'$lt':8}},{'timestamp':3,'height':1,'version':1}).sort('height',DESCENDING)
    block_shu = db.Block.count()
    block_ne = db.Block.count({'size': {'$gt': 686}})
    tx_shu = db.Transaction.count()
    tx_ne = db.Transaction.count({'type': {'$ne': 'MinerTransaction'}})
    address_shu = db.Address.count()
    asset_shu = db.Transaction.count({'type': 'RegisterTransaction'})
    ans_cur_ad = db.Address.find({'yue': {'$elemMatch': {'danwei': '小蚁股', 'value': {'$ne': 0}}}},
                                 {'address': 1, 'yue': 1, '_id': -1})
    ans_cyr = ans_cur_ad.count()
    anc_faxing = xiaoyibi_fxl(block_shu)
    anc_cur_ad = db.Address.find({'yue': {'$elemMatch': {'danwei': '小蚁币', 'value': {'$ne': 0}}}},
                                 {'address': 1, 'yue': 1, '_id': -1})
    anc_cyr = anc_cur_ad.count()

    pjqksj = (db.Block.find_one({'height': block_shu - 1}, {'timestamp': 1, '_id': -1})['timestamp'] -
              db.Block.find_one({'height': block_shu - 1001}, {'timestamp': 1, '_id': -1})['timestamp']) / 1000
    xtyxsj = (db.Block.find_one({'height': block_shu - 1}, {'timestamp': 1, '_id': -1})['timestamp'] -
              db.Block.find_one({'height': 1}, {'timestamp': 1, '_id': -1})['timestamp'])
    pjqksj = str(pjqksj)[5:11]
    xtyxsj = str(xtyxsj)[0:3] + '天'
    return render_template('index.html', block=cursor_block, tx=cursor_tx, address=cursor_address, block_shu=block_shu,
                           block_ne=block_ne + 1, tx_shu=tx_shu, tx_ne=tx_ne, address_shu=address_shu,
                           asset_shu=asset_shu, ans=ans_cyr, anc_faxing=anc_faxing, anc=anc_cyr, pjqksj=pjqksj,
                           xtyxsj=xtyxsj)


@app.route('/block', methods=['GET', 'POST'])
def block():
    # db = MongoClient().antchain
    meiyexianshishu = 50
    page = 1
    if request.method == 'POST':
        page = int(request.values['page'])
        counts = db.Block.count()
        q = meiyexianshishu * (page - 1)
        cursor_block = db.Block.find({'height': {'$lt': counts - q}}).sort("height", DESCENDING).limit(meiyexianshishu)
        return render_template('block_s.html', block=cursor_block)
    cursor_block = db.Block.find().sort("height", DESCENDING).limit(meiyexianshishu)
    return render_template('block.html', block=cursor_block)


@app.route('/block_zongshu')
def block_zongshu():
    counts = db.Block.count()
    meiyexianshishu = 50
    if (counts % meiyexianshishu != 0):
        counts = counts / meiyexianshishu + 1
    else:
        counts = counts / meiyexianshishu
    s = str(counts)
    return s


@app.route('/block/height/<int:height>')
def block_height_info(height):
    # db = MongoClient().antchain
    block = db.Block.find_one({'height': height})
    if not block:
        return render_template('404.html')
    transaction = []
    for s in block['tx']:
        tx = db.Transaction.find_one({"txid": s})
        transaction.append(tx)
    return render_template('height.html', block=block, b_tx=transaction)


@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    # db = MongoClient().antchain
    meiyexianshishu = 50
    page = 1
    if request.method == 'POST':
        page = int(request.values['page'])
        cursor_transaction = db.Transaction.find({'type': {'$ne': 'MinerTransaction'}}).sort("_id",
                                                                                             DESCENDING).limit(
            meiyexianshishu).skip(
            meiyexianshishu * (page - 1))
        return render_template('tx_s.html', tx=cursor_transaction, not_tx='')

    cursor_transaction = db.Transaction.find({'type': {'$ne': 'MinerTransaction'}}).sort("_id", DESCENDING).limit(
        meiyexianshishu).skip(meiyexianshishu * (page - 1))
    return render_template('tx.html', tx=cursor_transaction, not_tx='')


@app.route('/transaction_zongshu')
def transaction_zongshu():
    counts = db.Transaction.count({'type': {'$ne': 'MinerTransaction'}})
    meiyexianshishu = 50
    if (counts % meiyexianshishu != 0):
        counts = counts / meiyexianshishu + 1
    else:
        counts = counts / meiyexianshishu

    s = str(counts)
    return s


@app.route('/tx/hash/<hash>')
def transaction_hash_info(hash):
    # db = MongoClient().antchain
    zongde = []
    tx = db.Transaction.find_one({'txid': hash})
    if tx['attributes']:
        for i in range(len(tx['attributes'])):
            if tx['attributes'][i]['usage']:
                a = binascii.a2b_hex(tx['attributes'][i]['data']).decode('utf8', 'ignore')

                if 'http://' in a:
                    ks = a.find('http://')
                    js = a.find(' ', ks)
                    if js == -1:
                        a = "<a href='" + a[ks:] + "' target='_blank'>" + a[ks:] + '</a>'
                    else:
                        a = "<a href='" + a[ks:js] + "' target='_blank'>" + a[ks:js] + '</a>'
                elif 'https://' in a:
                    ks = a.find('https://')
                    js = a.find(' ', ks)
                    if js == -1:
                        a = "<a href='" + a[ks:] + "' target='_blank'>" + a[ks:] + '</a>'
                    else:
                        a = "<a href='" + a[ks:js] + "' target='_blank'>" + a[ks:js] + '</a>'
                tx['attributes'][i]['data'] = a
            else:
                pass
    if tx['type'] == 'RegisterTransaction':
        danwei = tx['asset']['name'][0]['name']
        fxl = 0
        if danwei == '小蚁币':
            b = db.Block.count()
            fxl = xiaoyibi_fxl(b)
        else:
            duiyingdanweidefaxingzichan = db.Transaction.find(
                {"type": 'IssueTransaction', 'vout': {'$elemMatch': {'danwei': danwei}}})
            for meigefaxingzichan in duiyingdanweidefaxingzichan:
                for y in meigefaxingzichan['vout']:
                    if y['danwei'] == danwei:
                        fxl = fxl + y['value']
        return render_template('tx_hash.html', tx=tx, fxl=fxl)
    elif tx['type'] == 'IssueTransaction':
        dgfxl = 0
        for f in tx['vout']:
            if f['danwei'] == tx['vout'][0]['danwei']:
                dgfxl += f['value']
        return render_template('tx_hash.html', tx=tx, dgfxl=dgfxl)
    elif tx['type'] == 'PublishTransaction':
        heyue_neirong = zhuanhuan.encode(tx['contract']['script'], '  ')
        return render_template('tx_hash.html', tx=tx, heyue_neirong=heyue_neirong)
    else:
        return render_template('tx_hash.html', tx=tx)


@app.route('/asset', methods=['GET', 'POST'])
def asset():
    # db = MongoClient().antchain
    meiyexianshishu = 50
    page = 1
    zongde = []
    if request.method == 'POST':
        page = int(request.values['page'])
        cursor_asset = db.Transaction.find({'type': 'RegisterTransaction'}).sort("$natural", ASCENDING).limit(
            meiyexianshishu).skip(
            meiyexianshishu * (page - 1))
        for meigezhucezichan in cursor_asset:
            danwei = meigezhucezichan['asset']['name'][0]['name']
            fxl = 0
            if danwei == '小蚁币':
                b = db.Block.count()
                fxl = xiaoyibi_fxl(b)
            else:
                duiyingdanweidefaxingzicha = db.Transaction.find(
                    {"type": 'IssueTransaction', 'vout': {'$elemMatch': {'danwei': danwei}}})
                for meigefaxingzichan in duiyingdanweidefaxingzicha:
                    for y in meigefaxingzichan['vout']:
                        if y['danwei'] == danwei:
                            fxl = fxl + y['value']
            zongde.append({'neirong': meigezhucezichan, 'fxl': fxl})

        return render_template('asset_s.html', asset=zongde)

    cursor_asset = db.Transaction.find({'type': 'RegisterTransaction'}).sort("$natural", ASCENDING).limit(
        meiyexianshishu).skip(meiyexianshishu * (page - 1))

    for meigezhucezichan in cursor_asset:
        # if meigezhucezichan['asset']['name']:
        #     danwei = meigezhucezichan['asset']['name'][0]['name']
        # else:
        #     danwei = meigezhucezichan['txid']
        danwei = meigezhucezichan['asset']['name'][0]['name']
        fxl = 0
        if danwei == '小蚁币':
            b = db.Block.count()
            fxl = xiaoyibi_fxl(b)
        else:
            duiyingdanweidefaxingzichan = db.Transaction.find(
                {"type": 'IssueTransaction', 'vout': {'$elemMatch': {'danwei': danwei}}})
            for meigefaxingzichan in duiyingdanweidefaxingzichan:
                for y in meigefaxingzichan['vout']:
                    if y['danwei'] == danwei:
                        fxl = fxl + y['value']
        zongde.append({'neirong': meigezhucezichan, 'fxl': fxl})
    return render_template('asset.html', asset=zongde)


@app.route('/asset_zongshu')
def asset_zongshu():
    meiyexianshishu = 50
    counts = db.Transaction.count({'type': 'RegisterTransaction'})
    if (counts % meiyexianshishu != 0):
        counts = counts / meiyexianshishu + 1
    else:
        counts = counts / meiyexianshishu;
    s = str(counts)
    return s


@app.route('/asset/hash/<hash>')
def asset_info(hash):
    # db = MongoClient().antchain
    zongde = []
    faxing_asset = []
    fxcs = 1
    asset = db.Transaction.find_one({'txid': hash})

    danwei = asset['asset']['name'][0]['name']
    fxl = 0
    if danwei == '小蚁币':
        b = db.Block.count()
        fxl = xiaoyibi_fxl(b)
        fxcs = db.Block.count()
    else:
        duiyingdanweidefaxingzichan = db.Transaction.find(
            {"type": 'IssueTransaction', 'vout': {'$elemMatch': {'danwei': danwei}}})
        fxcs = duiyingdanweidefaxingzichan.count()
        for meigefaxingzichan in duiyingdanweidefaxingzichan:
            dgfxl = 0
            for y in meigefaxingzichan['vout']:
                if y['danwei'] == danwei:
                    fxl = fxl + y['value']
                    dgfxl += y['value']
            faxing_asset.append([meigefaxingzichan, dgfxl])
    # 查询地址中有上述资产的余额
    # 下面的方面and中取得是两者的并集
    # cur_ad = db.Address.find({'$and': [{'yue.danwei': {'$in': [danwei]}}, {'yue.value': {'$ne': 0}}]},
    #                          {'address': 1, 'yue': 1, '_id': -1})

    cur_ad = db.Address.find({'yue': {'$elemMatch': {'danwei': danwei, 'value': {'$ne': 0}}}},
                             {'address': 1, 'yue': 1, '_id': -1})
    # = db.Address.find({'yue.danwei': {'$in': [danwei]}},{'address': 1, 'yue': 1, '_id': -1})
    for s in cur_ad:
        for x in range(len(s['yue'])):
            if s['yue'][x]['danwei'] == danwei:
                ad = db.Address.find_one({'address': s['address']}, {'timestamp': 1, '_id': -1})
                zongde.append([s['address'], s['yue'][x]['value'], ad['timestamp']])
            else:
                continue
    zongde.sort(key=operator.itemgetter(1), reverse=True)
    chiyourenshu = len(zongde)
    return render_template('asset_hash.html', asset=asset, tx=asset, issue=faxing_asset, fxl=fxl, fxcs=fxcs,
                           zongde=zongde[:100], cyrs=chiyourenshu)


@app.route('/address', methods=['GET', 'POST'])
def address():
    # db = MongoClient().antchain
    meiyexianshishu = 50
    page = 1

    if request.method == 'POST':
        page = int(request.values['page'])
        cursor_address = db.Address.find().sort("$natural", DESCENDING).limit(
            meiyexianshishu).skip(
            meiyexianshishu * (page - 1))
        return render_template('address_s.html', address=cursor_address)

    cursor_address = db.Address.find().sort("$natural", DESCENDING).limit(
        meiyexianshishu).skip(meiyexianshishu * (page - 1))
    # 特定字段查询
    # tx=db.Block.find({'height':{'$lt':8}},{'timestamp':3,'height':1,'version':1}).sort('height',DESCENDING)


    return render_template('address.html', address=cursor_address)


@app.route('/address_zongshu')
def address_zongshu():
    meiyexianshishu = 50
    counts = db.Address.count()
    if (counts % meiyexianshishu != 0):
        counts = counts / meiyexianshishu + 1
    else:
        counts = counts / meiyexianshishu;

    s = str(counts)
    return s


@app.route('/address/<address>')
def address_info(address):
    # db = MongoClient().antchain
    ad = db.Address.find_one({'address': address})
    jiaoyi_huizong = []
    if ad:
        for i in ad['jiaoyi']:
            t = db.Transaction.find_one({'txid': i['txid']})
            jiaoyi_huizong.append(t)
        return render_template('address_address.html', address=ad, tx=jiaoyi_huizong)
    else:
        return render_template('404.html')


@app.route('/address_top')
def address_top():
    # db = MongoClient().antchain
    zongde = []
    cur_ad = db.Address.find({}, {'address': 1, 'jiaoyi': 1, 'timestamp': 1, '_id': -1}).sort('timestamp', DESCENDING)
    for ss in cur_ad:
        zongde.append([ss['address'], len(ss['jiaoyi']), ss['timestamp']])
    zongde.sort(key=operator.itemgetter(1), reverse=True)
    return render_template('address_top.html', zongde=zongde[0:500])


@app.route('/validator', methods=['GET', 'POST'])
def validator():
    # db = MongoClient().antchain
    meiyexianshishu = 50
    page = 1
    neirong = []
    zhuangtai = ''
    if request.method == 'POST':
        page = int(request.values['page'])
        cursor_validator = db.Transaction.find({'type': "EnrollmentTransaction"}).sort("$natural",
                                                                                       DESCENDING).limit(
            meiyexianshishu).skip(
            meiyexianshishu * (page - 1))
        for meigevalidator in cursor_validator:
            neirong.append(meigevalidator)
            r = db.Transaction.find({'vin': {'$elemMatch': {'txid': meigevalidator['vout'][0]['txid']}}})
            if r.count():
                zhuangtai = '无效'
            else:
                zhuangtai = '有效'
        return render_template('validator_s.html', validator=neirong, zhuangtai=zhuangtai)
    cursor_validator = db.Transaction.find({'type': 'EnrollmentTransaction'}).sort("$natural", DESCENDING).limit(
        meiyexianshishu).skip(meiyexianshishu * (page - 1))
    # 检查每个抵押地址里面的抵押金是否被花掉

    for meigevalidator in cursor_validator:
        neirong.append(meigevalidator)
        r = db.Transaction.find({'vin': {'$elemMatch': {'txid': meigevalidator['vout'][0]['txid']}}})
        if r.count():
            zhuangtai = '无效'
        else:
            zhuangtai = '有效'
    # 特定字段查询
    # tx=db.Block.find({'height':{'$lt':8}},{'timestamp':3,'height':1,'version':1}).sort('height',DESCENDING)

    return render_template('validator.html', validator=neirong, zhuangtai=zhuangtai)


@app.route('/validator_zongshu')
def validator_zongshu():
    counts = db.Transaction.count({'type': 'EnrollmentTransaction'})
    meiyexianshishu = 50
    if (counts % meiyexianshishu != 0):
        counts = counts / meiyexianshishu + 1
    else:
        counts = counts / meiyexianshishu

    s = str(counts)
    return s


@app.route('/block/<int:hash_index>')
def getbestblockinfo(hash_index):
    #    bestblock = antsharesjsonrpc.getbestblockhash()
    result = antsharesjsonrpc.getblock(hash_index)

    result1 = antsharesjsonrpc.getrawtransaction('c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b')
    #    tup = ''
    #    for i in result.keys():
    #       if i == 'tx' or i == 'script':
    #            continue
    #        else:
    #            tup += i + '  >>  ' + str(result[i]) + ' |-| '
    return render_template('blocks.html', riqi=datetime.datetime.fromtimestamp(result['time']),
                           result=result, res=result1)


@app.route('/bl')
def shuaxin_block():
    # db = MongoClient().antchain
    cursor_block = db.Block.find().sort("$natural", DESCENDING).limit(10)
    # 特定字段查询
    # tx=db.Block.find({'height':{'$lt':8}},{'timestamp':3,'height':1,'version':1}).sort('height',DESCENDING)

    return render_template('block_s.html', block=cursor_block)


@app.route('/tx')
def shuaxin_tx():
    # db = MongoClient().antchain
    cursor_tx = db.Transaction.find({'type': {'$ne': 'MinerTransaction'}}).sort("_id", DESCENDING).limit(10)
    # 特定字段查询
    # tx=db.Block.find({'height':{'$lt':8}},{'timestamp':3,'height':1,'version':1}).sort('height',DESCENDING)
    cursor_NotTransaction = db.NotTransaction.find().sort('$natural', DESCENDING)
    # for s in cursor_NotTransaction:
    #     s
    #     print(s)
    return render_template('tx_s.html', tx=cursor_tx, not_tx='')


@app.route('/xtdd')
def xtdd():
    # db = MongoClient().antchain
    block_shu = db.Block.count()
    block_ne = db.Block.count({'size': {'$gt': 686}})
    tx_shu = db.Transaction.count()
    tx_ne = db.Transaction.count({'type': {'$ne': 'MinerTransaction'}})
    address_shu = db.Address.count()
    asset_shu = db.Transaction.count({'type': 'RegisterTransaction'})
    ans = []
    anc = []
    ans_cur_ad = db.Address.find({'yue': {'$elemMatch': {'danwei': '小蚁股', 'value': {'$ne': 0}}}},
                                 {'address': 1, 'yue': 1, '_id': -1})
    ans_cyr = ans_cur_ad.count()
    anc_faxing = xiaoyibi_fxl(block_shu)
    anc_cur_ad = db.Address.find({'yue': {'$elemMatch': {'danwei': '小蚁币', 'value': {'$ne': 0}}}},
                                 {'address': 1, 'yue': 1, '_id': -1})
    anc_cyr = anc_cur_ad.count()
    pjqksj = (db.Block.find_one({'height': block_shu - 1}, {'timestamp': 1, '_id': -1})['timestamp'] -
              db.Block.find_one({'height': block_shu - 1001}, {'timestamp': 1, '_id': -1})['timestamp']) / 1000
    xtyxsj = (db.Block.find_one({'height': block_shu - 1}, {'timestamp': 1, '_id': -1})['timestamp'] -
              db.Block.find_one({'height': 1}, {'timestamp': 1, '_id': -1})['timestamp'])
    pjqksj = str(pjqksj)[5:11]
    xtyxsj = str(xtyxsj)[0:3] + '天'
    return render_template('xtdd.html', block_shu=block_shu, block_ne=block_ne + 1, tx_shu=tx_shu, tx_ne=tx_ne,
                           address_shu=address_shu,
                           asset_shu=asset_shu, ans=ans_cyr, anc_faxing=anc_faxing, anc=anc_cyr, pjqksj=pjqksj,
                           xtyxsj=xtyxsj)


@app.route('/ad')
def address_sy():
    # db = MongoClient().antchain
    cursor_address = db.Address.find().sort("$natural", DESCENDING).limit(10)
    # 特定字段查询
    # tx=db.Block.find({'height':{'$lt':8}},{'timestamp':3,'height':1,'version':1}).sort('height',DESCENDING)

    return render_template('address_s.html', address=cursor_address)


def xiaoyibi_fxl(block):
    jianban = 20000000
    anc_faxing = 0
    if block <= jianban:
        anc_faxing = block * 8
    elif block > jianban and block <= jianban * 2:
        anc_faxing = jianban * 8 + (block - jianban) * 7
    elif block > jianban * 2 and block <= jianban * 3:
        anc_faxing = jianban * (8 + 7) + (block - jianban * 2) * 6
    elif block > jianban * 3 and block <= jianban * 4:
        anc_faxing = jianban * (8 + 7 + 6) + (block - jianban * 3) * 5
    elif block > jianban * 4 and block <= jianban * 5:
        anc_faxing = jianban * (8 + 7 + 6 + 5) + (block - jianban * 4) * 4
    elif block > jianban * 5 and block <= jianban * 6:
        anc_faxing = jianban * (8 + 7 + 6 + 5 + 4) + (block - jianban * 5) * 3
    elif block > jianban * 6 and block <= jianban * 7:
        anc_faxing = jianban * (8 + 7 + 6 + 5 + 4 + 3) + (block - jianban * 6) * 2
    elif block > jianban * 7:
        anc_faxing = jianban * (8 + 7 + 6 + 5 + 4 + 3 + 2) + (block - jianban * 7) * 1

    return anc_faxing


@app.route('/hangqing')
def hangqing():
    return render_template('hangqing.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/search')
def search():
    # db = MongoClient().antchain
    if request.method == "GET":
        q = request.args.get('q')
        if q.isdigit():
            q = int(q)
            block = db.Block.find_one({'height': q})
            if block:
                transaction = []
                for s in block['tx']:
                    tx = db.Transaction.find_one({"txid": s})
                    transaction.append(tx)
                return render_template('height.html', block=block, tx=transaction)
            else:
                return render_template('404.html')
        else:
            if db.Block.find_one({'hash': q}):
                block = db.Block.find_one({'hash': q})
                transaction = []
                for s in block['tx']:
                    tx = db.Transaction.find_one({"txid": s})
                    transaction.append(tx)
                return render_template('height.html', block=block, tx=transaction)

            elif db.Transaction.find_one({'txid': q}):
                zongde = []
                tx = db.Transaction.find_one({'txid': q})
                if tx['attributes']:
                    for i in range(len(tx['attributes'])):
                        if tx['attributes'][i]['usage']:
                            a = binascii.a2b_hex(tx['attributes'][i]['data']).decode('utf8', 'ignore')

                            if 'http://' in a:
                                ks = a.find('http://')
                                js = a.find(' ', ks)
                                if js == -1:
                                    a = "<a href='" + a[ks:] + "' target='_blank'>" + a[ks:] + '</a>'
                                else:
                                    a = "<a href='" + a[ks:js] + "' target='_blank'>" + a[ks:js] + '</a>'
                            elif 'https://' in a:
                                ks = a.find('https://')
                                js = a.find(' ', ks)
                                if js == -1:
                                    a = "<a href='" + a[ks:] + "' target='_blank'>" + a[ks:] + '</a>'
                                else:
                                    a = "<a href='" + a[ks:js] + "' target='_blank'>" + a[ks:js] + '</a>'
                            tx['attributes'][i]['data'] = a
                        else:
                            pass
                if tx['type'] == 'RegisterTransaction':
                    danwei = tx['asset']['name'][0]['name']
                    fxl = 0
                    if danwei == '小蚁币':
                        b = db.Block.count()
                        fxl = xiaoyibi_fxl(b)
                    else:
                        duiyingdanweidefaxingzichan = db.Transaction.find(
                            {"type": 'IssueTransaction', 'vout': {'$elemMatch': {'danwei': danwei}}})
                        for meigefaxingzichan in duiyingdanweidefaxingzichan:
                            for y in meigefaxingzichan['vout']:
                                if y['danwei'] == danwei:
                                    fxl = fxl + y['value']
                    return render_template('tx_hash.html', tx=tx, fxl=fxl)
                elif tx['type'] == 'IssueTransaction':
                    dgfxl = 0
                    for f in tx['vout']:
                        if f['danwei'] == tx['vout'][0]['danwei']:
                            dgfxl += f['value']
                    return render_template('tx_hash.html', tx=tx, dgfxl=dgfxl)
                elif tx['type'] == 'PublishTransaction':
                    heyue_neirong = zhuanhuan.encode(tx['contract']['script'], '  ')
                    return render_template('tx_hash.html', tx=tx, heyue_neirong=heyue_neirong)
                else:
                    return render_template('tx_hash.html', tx=tx)
            elif db.Address.find_one({'address': q}):
                ad = db.Address.find_one({'address': q})
                jiaoyi_huizong = []
                if ad:
                    for i in ad['jiaoyi']:
                        t = db.Transaction.find_one({'txid': i['txid']})
                        jiaoyi_huizong.append(t)
                    return render_template('address_address.html', address=ad, tx=jiaoyi_huizong)
                else:
                    return render_template('404.html')
            else:
                return render_template('404.html')


@app.route('/charts')
def charts_info():
    return render_template('charts_base.html')


@app.route('/gonggao')
def gonggao():
    return render_template('gonggao.html')


@app.route('/chart_yaosu')
def yaosu():
    # db = MongoClient().antchain
    block_shu = db.Block.count()
    block_ne = db.Block.count({'size': {'$gt': 686}})
    tx_shu = db.Transaction.count()
    tx_ne = db.Transaction.count({'type': {'$ne': 'MinerTransaction'}})
    address_shu = db.Address.count()
    asset_shu = db.Transaction.count({'type': 'RegisterTransaction'})
    ans = []
    anc = []
    ans_cur_ad = db.Address.find({'yue': {'$elemMatch': {'danwei': '小蚁股', 'value': {'$ne': 0}}}},
                                 {'address': 1, 'yue': 1, '_id': -1})
    ans_cyr = ans_cur_ad.count()
    anc_faxing = xiaoyibi_fxl(block_shu)
    anc_cur_ad = db.Address.find({'yue': {'$elemMatch': {'danwei': '小蚁币', 'value': {'$ne': 0}}}},
                                 {'address': 1, 'yue': 1, '_id': -1})
    anc_cyr = anc_cur_ad.count()
    pjqksj = (db.Block.find_one({'height': block_shu - 1}, {'timestamp': 1, '_id': -1})['timestamp'] -
              db.Block.find_one({'height': block_shu - 1001}, {'timestamp': 1, '_id': -1})['timestamp']) / 1000
    xtyxsj = (db.Block.find_one({'height': block_shu - 1}, {'timestamp': 1, '_id': -1})['timestamp'] -
              db.Block.find_one({'height': 1}, {'timestamp': 1, '_id': -1})['timestamp'])
    pjqksj = str(pjqksj)[5:11]
    xtyxsj = str(xtyxsj)[0:3] + '天'

    return json.dumps({'block_shu': block_shu, 'block_ne': (block_ne + 1), 'tx_shu': tx_shu, 'tx_ne': tx_ne,
                       'address_shu': address_shu,
                       'asset_shu': asset_shu, 'ans': ans_cyr, 'anc_faxing': anc_faxing, 'anc': anc_cyr,
                       'pjqksj': pjqksj,
                       'xtyxsj': xtyxsj})

######################
#  API部分
######################

@app.route('/api/v1/address/info/<address>')
def api_address_info(address):
    # db = MongoClient().antchain
    ad = db.Address.find_one({'address': address})
    jiaoyi_huizong = []
    balances=[]
    if ad:
        address=ad['address']
        for b in ad['yue']:
            adr=db.Transaction.find({'type':'RegisterTransaction'},{'asset':1,'txid':1,'_id':0})
            for z in adr:
                if z['asset']['name'][0]['name']==b['danwei']:
                    balances.append({'balance':b['value'],'asset':z['txid']})
        tx=ad['jiaoyi']
    else:
        return json.dumps({'result':'No Address!'})
    return json.dumps({'address':address,'balances':balances,'tx':tx})

######################
#  程序运行部分
######################

if __name__ == '__main__':
    app.run()
