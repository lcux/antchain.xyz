#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 4/22/17 11:05 PM
# @Author  : lcux
# @Site    : https://github.com/lcux
# @File    : main/views.py
# @Software: PyCharm



from flask import render_template, request, current_app, flash
import antsharesjsonrpc
from app import zhuanhuan
from config import LANGUAGES
from . import main
from .. import db, babel
from ..functions import *
import binascii
import datetime
import json
import operator, random
from decimal import Decimal as D
from exchange import get_exchange_info
# from shiyan import get_exchange_info

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(LANGUAGES.keys())


@main.route('/')
def index():
    # get_exchange_info()
    ans_gai,ans_worth=ans_quota_and_worth()
    return render_template('index.html', block=block_content(), tx=transaction_no_mt_content(),
                           address=address_content(),
                           block_shu=block_count(),
                           block_ne=block_count_gt686() + 1, tx_shu=transaction_count(),
                           tx_ne=transaction_no_mt_count(), address_shu=address_count(),
                           asset_shu=asset_count(), ans=ans_holding(), anc_faxing=anc_criculation(), anc=anc_holding(),
                           pjqksj=block_average_generaetime(),
                           xtyxsj=system_runtime(),addrress_daily_growth=address_growth(),
                           tx_no_mt_daily_growth=tx_no_mt_growth(),ans_gai=ans_gai,ans_worth=ans_worth)


@main.route('/block', methods=['GET', 'POST'])
def block():
    try:
        page = int(request.values['page'])
        counts = block_count()
        if page > counts:
            return render_template('sorry.html', num=str(random.randint(1, 13)))
        q = current_app.config['BLOCK_PRE_PAGE'] * (page - 1)
        cursor_block = db.Block.find({'_id': {'$lte': counts - q}}).sort("_id", DESCENDING).limit(
            current_app.config['BLOCK_PRE_PAGE'])
        return render_template('_block_s.html', block=cursor_block)
    except:
        cursor_block = block_content(num=current_app.config['BLOCK_PRE_PAGE'])
        return render_template('block.html', block=cursor_block)


@main.route('/block_zongshu')
def block_zongshu():
    counts = db.Block.count()
    meiyexianshishu = 50
    if (counts % meiyexianshishu != 0):
        counts = counts / meiyexianshishu + 1
    else:
        counts = counts / meiyexianshishu
    s = str(counts)
    return s


@main.route('/block/height/<int:height>')
def block_height_info(height):
    if height >= block_count():
        return render_template('sorry.html', num=str(random.randint(1, 13)))
    block = db.Block.find_one({'_id': height})
    if not block:
        return render_template('404.html', content='输入的区块高度错误，请重新输入！')
    transaction = []
    for s in block['tx']:
        tx = db.Transaction.find_one({"_id": s})
        transaction.append(tx)
    transaction.reverse()
    return render_template('height.html', block=block, b_tx=transaction)


@main.route('/transaction', methods=['GET', 'POST'])
def transaction():
    meiyexianshishu = 50
    page = 1
    if request.method == 'POST':
        page = int(request.values['page'])
        counts = transaction_no_mt_count()
        # cursor_transaction = db.Transaction.find({'type': {'$ne': 'MinerTransaction'}}).sort("timestamp",
        #                                                                                      DESCENDING).limit(
        #     meiyexianshishu).skip(
        #     meiyexianshishu * (page - 1))
        q = current_app.config['TX_PRE_PAGE'] * (page - 1)
        cursor_transaction = db.Transaction.find({'type': {'$ne': 'MinerTransaction'},'id': {'$lte': counts - q}}).sort("id", DESCENDING).limit(
            current_app.config['TX_PRE_PAGE'])
        return render_template('_tx_s.html', tx=cursor_transaction, not_tx='')

    cursor_transaction = db.Transaction.find({'type': {'$ne': 'MinerTransaction'}}).sort("timestamp", DESCENDING).limit(
        meiyexianshishu).skip(meiyexianshishu * (page - 1))
    return render_template('tx.html', tx=cursor_transaction, not_tx='')


@main.route('/transaction_zongshu')
def transaction_zongshu():
    counts = db.Transaction.count({'type': {'$ne': 'MinerTransaction'}})
    meiyexianshishu = 50
    if (counts % meiyexianshishu != 0):
        counts = counts / meiyexianshishu + 1
    else:
        counts = counts / meiyexianshishu

    s = str(counts)
    return s


@main.route('/tx/hash/<hash>')
def transaction_hash_info(hash):
    zongde = []
    tx = db.Transaction.find_one({'_id': hash})
    if tx is None:
        return render_template('sorry.html', num=str(random.randint(1, 13)))
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
        unit = ''
        if type(tx['asset']['name']) == type([]):
            unit = tx['asset']['name'][0]['name']
        elif type(tx['asset']['name']) == type(''):
            unit = tx['asset']['name']
            tx['asset']['name'] = [{'name': unit}]
        else:
            print('error asset.name' + str(type(tx['asset']['name'])))
        fxl = D('0')
        if unit == '小蚁币':
            fxl = anc_criculation()
        else:
            duiyingdanweidefaxingzichan = db.Transaction.find(
                {"type": 'IssueTransaction', 'vout': {'$elemMatch': {'unit': unit}}})
            for meigefaxingzichan in duiyingdanweidefaxingzichan:
                for y in meigefaxingzichan['vout']:
                    if y['unit'] == unit:
                        fxl = fxl + D(y['value'])
        return render_template('tx_hash.html', tx=tx, fxl=fxl)
    elif tx['type'] == 'IssueTransaction':
        dgfxl = D('0')
        for f in tx['vout']:
            if f['unit'] == tx['vout'][0]['unit']:
                dgfxl += D(f['value'])
        return render_template('tx_hash.html', tx=tx, dgfxl=dgfxl)
    elif tx['type'] == 'PublishTransaction':
        try:
            heyue_neirong = zhuanhuan.encode(tx['contract']['script'], '  ')
        except:
            heyue_neirong = "转换合约内容失败，出现不可预知的新内容！"
        return render_template('tx_hash.html', tx=tx, heyue_neirong=heyue_neirong)
    elif tx['type'] == 'InvocationTransaction':
        try:
            tiaoyong_neirong = zhuanhuan.encode(tx['script'], '  ')
        except:
            tiaoyong_neirong = tx['script']
        return render_template('tx_hash.html', tx=tx, heyue_neirong=tiaoyong_neirong)
    else:
        return render_template('tx_hash.html', tx=tx)



@main.route('/publish_transaction', methods=['GET', 'POST'])
def publish_transaction():
    return '正在完善中，马上上马。。。'


@main.route('/asset', methods=['GET', 'POST'])
def asset():
    meiyexianshishu = 50
    page = 1
    zongde = []
    if request.method == 'POST':
        page = int(request.values['page'])
        cursor_asset = db.Transaction.find({'type': 'RegisterTransaction'}).sort("timestamp", ASCENDING).limit(
            meiyexianshishu).skip(
            meiyexianshishu * (page - 1))
        for meigezhucezichan in cursor_asset:
            unit = ''
            if type(meigezhucezichan['asset']['name']) == type([]):
                unit = meigezhucezichan['asset']['name'][0]['name']
            elif type(meigezhucezichan['asset']['name']) == type(''):
                unit = meigezhucezichan['asset']['name']
                meigezhucezichan['asset']['name'] = [{'name': unit}]
            else:
                print('error asset.name' + str(type(meigezhucezichan['asset']['name'])))
            # unit = meigezhucezichan['asset']['name'][0]['name']
            fxl = D('0')
            if unit == '小蚁币':
                fxl = ans_criculation()
            else:
                duiyingdanweidefaxingzicha = db.Transaction.find(
                    {"type": 'IssueTransaction', 'vout': {'$elemMatch': {'unit': unit}}})
                for meigefaxingzichan in duiyingdanweidefaxingzicha:
                    for y in meigefaxingzichan['vout']:
                        if y['unit'] == unit:
                            fxl = fxl + D(y['value'])
            zongde.append({'neirong': meigezhucezichan, 'fxl': fxl})

        return render_template('asset_s.html', asset=zongde)

    cursor_asset = db.Transaction.find({'type': 'RegisterTransaction'}).sort("timestamp", ASCENDING).limit(
        meiyexianshishu).skip(meiyexianshishu * (page - 1))

    for meigezhucezichan in cursor_asset:
        unit = ''
        if type(meigezhucezichan['asset']['name']) == type([]):
            unit = meigezhucezichan['asset']['name'][0]['name']
        elif type(meigezhucezichan['asset']['name']) == type(''):
            unit = meigezhucezichan['asset']['name']
            meigezhucezichan['asset']['name'] = [{'name': unit}]
        else:
            print('error asset.name' + str(type(meigezhucezichan['asset']['name'])))
        # unit = meigezhucezichan['asset']['name'][0]['name']
        fxl = D('0')
        if unit == '小蚁币':
            fxl = anc_criculation()
        else:
            duiyingdanweidefaxingzichan = db.Transaction.find(
                {"type": 'IssueTransaction', 'vout': {'$elemMatch': {'unit': unit}}})
            for meigefaxingzichan in duiyingdanweidefaxingzichan:
                for y in meigefaxingzichan['vout']:
                    if y['unit'] == unit:
                        fxl = fxl + D(y['value'])
        zongde.append({'neirong': meigezhucezichan, 'fxl': fxl})
    return render_template('asset.html', asset=zongde)


@main.route('/asset_zongshu')
def asset_zongshu():
    meiyexianshishu = 50
    counts = db.Transaction.count({'type': 'RegisterTransaction'})
    if (counts % meiyexianshishu != 0):
        counts = counts / meiyexianshishu + 1
    else:
        counts = counts / meiyexianshishu;
    s = str(counts)
    return s


@main.route('/asset/hash/<hash>')
def asset_info(hash):
    zongde = []
    faxing_asset = []
    fxcs = 1
    unit = ''
    asset_cur = db.Transaction.find_one({'_id': hash, 'type': 'RegisterTransaction'})
    if asset_cur:
        unit = asset_cur['asset']['name'][0]['name']
        asset = asset_cur['txid']
    else:
        return render_template('404.html', content="输入了错误的资产hash值，请重新校对。")
    fxl = D('0')
    if asset == '602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7':
        fxl = anc_criculation()
        fxcs = db.Block.count()
    else:
        duiyingdanweidefaxingzichan = db.Transaction.find(
            {"type": 'IssueTransaction', 'vout': {'$elemMatch': {'unit': unit}}})
        fxcs = duiyingdanweidefaxingzichan.count()
        for meigefaxingzichan in duiyingdanweidefaxingzichan:
            dgfxl = D('0')
            for y in meigefaxingzichan['vout']:
                if y['unit'] == unit:
                    fxl = fxl + D(y['value'])
                    dgfxl += D(y['value'])
            faxing_asset.append([meigefaxingzichan, dgfxl])
    # 查询地址中有上述资产的余额
    # 下面的方面and中取得是两者的并集
    # cur_ad = db.Address.find({'$and': [{'balance.unit': {'$in': [unit]}}, {'balance.value': {'$ne': 0}}]},
    #                          {'address': 1, 'balance': 1, '_id': -1})

    # cur_ad = db.Address.find({'balance': {'$elemMatch': {'unit': unit, 'value': {'$ne': 0}}}},
    #                          {'address': 1, 'balance': 1, '_id': -1})
    # = db.Address.find({'balance.unit': {'$in': [unit]}},{'address': 1, 'balance': 1, '_id': -1})
    ss = 'balance.' + asset
    cur_ad = db.Address.find({ss: {'$exists': True}}, {'balance': 1, 'lasttime': 1})
    for s in cur_ad:
        for x in s['balance'].keys():
            if x == asset and D(s['balance'][x]['value']) != D('0'):
                zongde.append([s['_id'], D(s['balance'][x]['value']), s['lasttime']])
            else:
                continue
    zongde.sort(key=operator.itemgetter(1), reverse=True)
    chiyourenshu = len(zongde)
    return render_template('asset_hash.html', asset=asset_cur, tx=asset_cur, issue=faxing_asset, fxl=fxl, fxcs=fxcs,
                           zongde=zongde[:5000], cyrs=chiyourenshu)


@main.route('/address', methods=['GET', 'POST'])
def address():
    APG = current_app.config['ADDRESS_PRE_PAGE']
    page = 1

    if request.method == 'POST':
        page = int(request.values['page'])
        cursor_address = db.Address.find().sort("firsttime", DESCENDING).limit(APG).skip(
            APG * (page - 1))
        return render_template('_address_s.html', address=cursor_address)

    cursor_address = db.Address.find().sort("firsttime", DESCENDING).limit(
        APG).skip(APG * (page - 1))
    return render_template('address.html', address=cursor_address)


@main.route('/address_zongshu')
def address_zongshu():
    meiyexianshishu = 50
    counts = db.Address.count()
    if (counts % meiyexianshishu != 0):
        counts = counts / meiyexianshishu + 1
    else:
        counts = counts / meiyexianshishu;
    s = str(counts)
    return s


@main.route('/address/<address>')
def address_info(address):
    ad = db.Address.find_one({'_id': address})
    jiaoyi_huizong = []
    if ad:
        for i in ad['txs']:
            t = db.Transaction.find_one({'_id': i['txid']})
            jiaoyi_huizong.append(t)
        jiaoyi_huizong.reverse()
        return render_template('address_address.html', address=ad, tx=jiaoyi_huizong)
    else:
        return render_template('404.html')


@main.route('/address_top')
def address_top():
    zongde = []
    cur_ad = db.Address.find({}, {'_id': 1, 'txs': 1, 'lasttime': 1}).sort('ladb.sttime', DESCENDING)
    for ss in cur_ad:
        zongde.append([ss['_id'], len(ss['txs']), ss['lasttime']])
    zongde.sort(key=operator.itemgetter(1), reverse=True)
    return render_template('address_top.html', zongde=zongde[0:500])


@main.route('/validator', methods=['GET', 'POST'])
def validator():
    meiyexianshishu = 50
    page = 1
    neirong = []
    zhuangtai = ''
    if request.method == 'POST':
        page = int(request.values['page'])
        cursor_validator = db.Transaction.find({'type': "EnrollmentTransaction"}).sort("timestamp",
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
    cursor_validator = db.Transaction.find({'type': 'EnrollmentTransaction'}).sort("timestamp", DESCENDING).limit(
        meiyexianshishu).skip(meiyexianshishu * (page - 1))
    # 检查每个抵押地址里面的抵押金是否被花掉

    for meigevalidator in cursor_validator:
        neirong.append(meigevalidator)
        r = db.Transaction.find({'vin': {'$elemMatch': {'txid': meigevalidator['vout'][0]['txid']}}})
        if r.count():
            zhuangtai = '无效'
        else:
            zhuangtai = '有效'
    return render_template('validator.html', validator=neirong, zhuangtai=zhuangtai)


@main.route('/validator_zongshu')
def validator_zongshu():
    counts = db.Transaction.count({'type': 'EnrollmentTransaction'})
    meiyexianshishu = 50
    if (counts % meiyexianshishu != 0):
        counts = counts / meiyexianshishu + 1
    else:
        counts = counts / meiyexianshishu

    s = str(counts)
    return s


################
## 首页异步调用
################
@main.route('/xtdd')
def xtdd():
    get_exchange_info.delay()
    ans_gai,ans_worth=ans_quota_and_worth()
    return render_template('xtdd.html', block_shu=block_count(), block_ne=block_count_gt686() + 1,
                           tx_shu=transaction_count(), tx_ne=transaction_no_mt_count(),
                           address_shu=address_count(),
                           asset_shu=asset_count(), ans=ans_holding(), anc_faxing=anc_criculation(), anc=anc_holding(),
                           pjqksj=block_average_generaetime(),
                           xtyxsj=system_runtime(),addrress_daily_growth=address_growth(),
                           tx_no_mt_daily_growth=tx_no_mt_growth(),ans_gai=ans_gai,ans_worth=ans_worth)


@main.route('/bl')
def shuaxin_block():
    return render_template('block_s.html', block=block_content())


@main.route('/tx')
def shuaxin_tx():
    return render_template('tx_s.html', tx=transaction_no_mt_content(), not_tx='')


@main.route('/ad')
def address_sy():
    return render_template('address_s.html', address=address_content())


@main.route('/hangqing')
def hangqing():
    return render_template('hangqing.html')


@main.route('/search')
def search():
    if request.method == "GET":
        q = request.args.get('q')
        if q.isdigit():
            q = int(q)
            block = db.Block.find_one({'_id': q})
            if block:
                transaction = []
                for s in block['tx']:
                    tx = db.Transaction.find_one({"_id": s})
                    transaction.append(tx)
                transaction.reverse()
                return render_template('height.html', block=block, b_tx=transaction)
            else:
                return render_template('404.html')
        else:
            if db.Address.find_one({'_id': q}):
                ad = db.Address.find_one({'_id': q})
                jiaoyi_huizong = []
                if ad:
                    for i in ad['txs']:
                        t = db.Transaction.find_one({'_id': i['txid']})
                        jiaoyi_huizong.append(t)
                    jiaoyi_huizong.reverse()
                    return render_template('address_address.html', address=ad, tx=jiaoyi_huizong)
                else:
                    return render_template('404.html')
            elif db.Transaction.find_one({'_id': q}):
                zongde = []
                tx = db.Transaction.find_one({'_id': q})
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
                    unit = tx['asset']['name'][0]['name']
                    fxl = D('0')
                    if unit == '小蚁币':
                        fxl = anc_criculation()
                    else:
                        duiyingdanweidefaxingzichan = db.Transaction.find(
                            {"type": 'IssueTransaction', 'vout': {'$elemMatch': {'unit': unit}}})
                        for meigefaxingzichan in duiyingdanweidefaxingzichan:
                            for y in meigefaxingzichan['vout']:
                                if y['unit'] == unit:
                                    fxl = fxl + D(y['value'])
                    return render_template('tx_hash.html', tx=tx, fxl=fxl)
                elif tx['type'] == 'IssueTransaction':
                    dgfxl = D('0')
                    for f in tx['vout']:
                        if f['unit'] == tx['vout'][0]['unit']:
                            dgfxl += D(f['value'])
                    return render_template('tx_hash.html', tx=tx, dgfxl=dgfxl)
                elif tx['type'] == 'PublishTransaction':
                    heyue_neirong = zhuanhuan.encode(tx['contract']['script'], '  ')
                    return render_template('tx_hash.html', tx=tx, heyue_neirong=heyue_neirong)
                else:
                    return render_template('tx_hash.html', tx=tx)
            elif db.Block.find_one({'presentblockhash': q}):
                block = db.Block.find_one({'presentblockhash': q})
                transaction = []
                for s in block['tx']:
                    tx = db.Transaction.find_one({"_id": s})
                    transaction.append(tx)
                transaction.reverse()
                return render_template('height.html', block=block, b_tx=transaction)

            else:
                return render_template('404.html')


@main.route('/charts')
def charts_info():
    return render_template('charts_base.html')


@main.route('/chart_yaosu')
def yaosu():
    # db = MongoClient().antchain
    # block_shu = db.Block.count()
    # block_ne = db.Block.count({'size': {'$gt': 686}})
    # tx_shu = db.Transaction.count()
    # tx_ne = db.Transaction.count({'type': {'$ne': 'MinerTransaction'}})
    # address_shu = db.Address.count()
    # asset_shu = db.Transaction.count({'type': 'RegisterTransaction'})
    # ans = []
    # anc = []
    # ans_cur_ad = db.Address.find({'balance': {'$elemMatch': {'unit': '小蚁股', 'value': {'$ne': 0}}}},
    #                              {'address': 1, 'balance': 1, '_id': -1})
    # ans_cyr = ans_cur_ad.count()
    # anc_faxing = anc_criculation()
    # anc_cur_ad = db.Address.find({'balance': {'$elemMatch': {'unit': '小蚁币', 'value': {'$ne': 0}}}},
    #                              {'address': 1, 'balance': 1, '_id': -1})
    # anc_cyr = anc_cur_ad.count()
    # pjqksj = (db.Block.find_one({'_id': block_shu - 1}, {'timestamp': 1, '_id': -1})['timestamp'] -
    #           db.Block.find_one({'_id': block_shu - 101}, {'timestamp': 1, '_id': -1})['timestamp']) / 100
    # xtyxsj = (db.Block.find_one({'_id': block_shu - 1}, {'timestamp': 1, '_id': -1})['timestamp'] -
    #           db.Block.find_one({'_id': 1}, {'timestamp': 1, '_id': -1})['timestamp'])
    # pjqksj = str(pjqksj)[5:11]
    # xtyxsj = str(xtyxsj)[0:3] + '天'

    return json.dumps({'block_shu': block_count(), 'block_ne': block_count_gt686() + 1, 'tx_shu': transaction_count(),
                       'tx_ne': transaction_no_mt_count(),
                       'address_shu': address_count(),
                       'asset_shu': asset_count(), 'ans': ans_holding(), 'anc_faxing': anc_criculation(),
                       'anc': anc_holding(),
                       'pjqksj': block_average_generaetime(),
                       'xtyxsj': system_runtime()})


@main.route('/gonggao')
def gonggao():
    return render_template('gonggao.html')


@main.route('/shiyan')
def shiyan():
    return '0'


@main.route('/block/<int:hash_index>')
def getbestblockinfo(hash_index):
    #    bestblock = antsharesjsonrpc.getbestblockhash()
    result = antsharesjsonrpc.getblock(hash_index)
    result1 = antsharesjsonrpc.getrawtransaction('3e7997bdecc55e70610ebfeb3539f652a0bc4e9ef05488cd8f22a34980c1d045', 1)
    result0 = antsharesjsonrpc.getrawtransaction('3e7997bdecc55e70610ebfeb3539f652a0bc4e9ef05488cd8f22a34980c1d045', 0)
    # result1 = antsharesjsonrpc.getrawtransaction('c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b')
    #    tup = ''
    #    for i in result.keys():
    #       if i == 'tx' or i == 'script':
    #            continue
    #        else:
    #            tup += i + '  >>  ' + str(result[i]) + ' |-| '
    return render_template('blocks.html', riqi=datetime.datetime.fromtimestamp(result['time']),
                           result=result, res=result1)


@main.route('/address_daily_growth')
def address_daily_growth():
    return '今日地址增长数为（从每天8点开始）:' + str(address_growth())
