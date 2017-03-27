#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from pymongo import MongoClient, DESCENDING
import antsharesjsonrpc
import antsharesqr
from bson.objectid import ObjectId
import datetime
import time


# 区块模型
class Block():
    def __init__(self, result, cost):
        self.merkleroot = result['merkleroot']
        self.previousblockhash = result['previousblockhash']
        self.nowhash = result['hash']
        try:
            self.nextblockhash = result['nextblockhash']
        except:
            self.nextblockhash = ''
        self.nextminer = result['nextminer']
        self.datetime = datetime.datetime.fromtimestamp(result['time'])
        self.height = result['height']
        self.nonce = result['nonce']
        self.version = result['version']
        self.size = result['size']
        self.txcount = len(result['tx'])
        self.tx = [tx_s['txid'] for tx_s in result['tx']]
        self.script = result['script']
        self.cost = cost

    def new_block(self):
        collection = {
            # '_id': '',
            'merkleroot': self.merkleroot,
            'previousblockhash': self.previousblockhash,
            'hash': self.nowhash,
            'nextblockhash': self.nextblockhash,
            'nextminer': self.nextminer,
            'timestamp': self.datetime,
            'height': self.height,
            'nonce': self.nonce,
            'version': self.version,
            'size': self.size,
            'tx': self.tx,
            'txcount': self.txcount,
            'cost': self.cost,
            'script': self.script
        }
        return collection

    def __repr__(self):
        return '<Block %r' % self.nowhash


# 交易模型
class Transaction():
    def __init__(self, tx, block_hash, block_height, timestamp, tx_vin, tx_vout, cost):
        self.txid = tx['txid']
        self.version = tx['version']
        self.attributes = tx['attributes']
        self.size = tx['size']
        # self.vin = tx['vin']
        # self.vout = tx['vout']
        self.vin = tx_vin
        # [{'address': Azsdddfdssdf, 'value': 1222, 'danwei': '小蚁股',
        # 'jingdu': 0,'txid': 'ajldfjdsidakfdjdi876ds7df9d7f'},...]
        self.vout = tx_vout
        # [{'address': Azsdddfdssdf, 'value': 1222, 'danwei': '小蚁股',
        # 'jingdu': 0,'txid': 'ajldfjdsidakfdjdi876ds7df9d7f'},...]
        self.timestamp = timestamp
        self.scripts = tx['scripts']
        self.type = tx['type']
        self.block_hash = block_hash
        self.block_height = block_height
        self.cost = cost

        if self.type == 'MinerTransaction':
            self.nonce = tx['nonce']
            self.name = "挖矿交易"
        elif self.type == 'ContractTransaction':
            self.name = "合约交易"
        elif self.type == 'IssueTransaction':
            self.name = "资产发行"
        elif self.type == 'ClaimTransaction':
            self.claims = tx['claims']
            self.name = "提取小蚁币"
        elif self.type == 'EnrollmentTransaction':
            self.pubkey = tx['pubkey']
            self.name = "记账人报名"
        elif self.type == 'RegisterTransaction':
            self.asset = tx['asset']
            self.name = "资产登记"
        elif self.type == 'AgencyTransaction':
            self.name = "委托交易"
        elif self.type == 'PublishTransaction':
            self.name = "智能合约发布"
            self.contract=tx['contract']
        else:
            self.name = "无效交易"

    def new_transaction(self):
        collection = {
            # '_id': '',
            'txid': self.txid,
            'version': self.version,
            'attributes': self.attributes,
            'size': self.size,
            'vin': self.vin,
            'vout': self.vout,
            'timestamp': datetime.datetime.fromtimestamp(self.timestamp),
            'scripts': self.scripts,
            'type': self.type,
            'block_hash': self.block_hash,
            'block_height': self.block_height,
            'name': self.name,
            'cost': self.cost
        }

        if self.type == 'MinerTransaction':
            collection['nonce'] = self.nonce
        elif self.type == 'ContractTransaction':
            pass
        elif self.type == 'IssueTransaction':
            pass
        elif self.type == 'ClaimTransaction':
            collection['claims'] = self.claims
        elif self.type == 'EnrollmentTransaction':
            collection['pubkey'] = self.pubkey
        elif self.type == 'RegisterTransaction':
            if self.asset['name']:
                if type(self.asset['name']) == type([]):
                    collection['asset'] = self.asset
                elif type(self.asset['name']) == type(''):
                    self.asset['name'] = [{'name': self.asset['name'], 'lang': 'zh-CN'},
                                          {'name': self.asset['name'], 'lang': 'en'}]
                    collection['asset'] = self.asset
                else:
                    collection['asset'] = self.asset
            else:
                self.asset['name'] = [{'name': '(无名称)', 'lang': 'zh-CN'}, {'name': '(No Name)', 'lang': 'en'}]
                collection['asset'] = self.asset
        elif self.type == 'AgencyTransaction':
            pass
        elif self.type == 'PublishTransaction':
            collection['contract']=self.contract
        else:
            pass

        return collection

    def __repr__(self):
        return '<Transaction %r' % self.name


# 地址模型
class Address():
    def __init__(self, vout, timestamp):
        self.addr = vout['address']
        self.txid = vout['txid']
        self.danwei = vout['danwei']
        self.value = vout['value']
        self.timestamp = timestamp
        # if vout['precision']:
        #     self.value = float(vout['value'])
        # else:
        #     self.value = int(vout['value'])

    def new_address(self):
        collection = {
            # '_id': '',
            'address': self.addr,
            'yue': [{'value': self.value, 'danwei': self.danwei}],
            'jiaoyi': [{'txid': self.txid}],
            'timestamp': datetime.datetime.fromtimestamp(self.timestamp),
            'dzcssj': datetime.datetime.fromtimestamp(self.timestamp),
            'erweima': 'address/' + self.addr + '.png'
        }
        return collection

    def __repr__(self):
        return 'Address %r' % self.addr


def jieshou_block():
    db = MongoClient().antchain_mainnet

    while 1:
        db_block_count = db.Block.count()
        chain_block_count = antsharesjsonrpc.getblockcount()

        while db_block_count < chain_block_count:
            result = antsharesjsonrpc.getblock(db_block_count)
            db_tx_count = db.Transaction.count()

            block_txs = result['tx']
            block_txs_count = len(block_txs)
            block_feiyong = 0

            while block_txs_count:
                # 处理交易输入输出
                tx_vin = block_txs[len(block_txs) - block_txs_count]['vin']
                tx_vout = block_txs[len(block_txs) - block_txs_count]['vout']
                tx_id = block_txs[len(block_txs) - block_txs_count]['txid']
                tx_vin_count = len(tx_vin)
                tx_vout_count = len(tx_vout)
                jiaoyi_shuru_neirong_quanbu = []
                jiaoyi_shuchu_neirong_quanbu = []
                db_address_count = db.Address.count()
                tx_feiyong = 0

                if not db.Transaction.find_one({'txid':tx_id},{'_id':1}):

                    while tx_vin_count:
                        #处理交易输入
                        r = db.Transaction.find_one({'txid': tx_vin[len(tx_vin) - tx_vin_count]['txid']}, {'vout': 1})
                        shuru_value = r['vout'][tx_vin[len(tx_vin) - tx_vin_count]['vout']]['value']
                        shuru_address = r['vout'][tx_vin[len(tx_vin) - tx_vin_count]['vout']]['address']
                        shuru_danwei = r['vout'][tx_vin[len(tx_vin) - tx_vin_count]['vout']]['danwei']
                        shuru_jingdu = r['vout'][tx_vin[len(tx_vin) - tx_vin_count]['vout']]['jingdu']
                        ssss = 'vout.' + str(tx_vin[len(tx_vin) - tx_vin_count]['vout']) + '.to'
                        n = db.Transaction.update_one({'txid': tx_vin[len(tx_vin) - tx_vin_count]['txid']},
                                                      {'$set': {ssss: tx_id}})

                        jiaoyi_shuru_neirong = {'address': shuru_address, 'value': shuru_value, 'danwei': shuru_danwei,
                                                'jingdu': shuru_jingdu,
                                                'txid': tx_vin[len(tx_vin) - tx_vin_count]['txid']}
                        jiaoyi_shuru_neirong_quanbu.append(jiaoyi_shuru_neirong)
                        tx_vin_count = tx_vin_count - 1

                    while tx_vout_count:
                        #处理交易输出
                        shuchu_value = tx_vout[len(tx_vout) - tx_vout_count]['value']
                        shuchu_asset = tx_vout[len(tx_vout) - tx_vout_count]['asset']
                        shuchu_address = tx_vout[len(tx_vout) - tx_vout_count]['address']
                        c = db.Transaction.find_one({'txid': shuchu_asset}, {'asset': 1})
                        shuchu_danwei = c['asset']['name'][0]['name']
                        shuchu_jingdu = c['asset']['precision']
                        if shuchu_jingdu:
                            shuchu_value = float(shuchu_value)
                        else:
                            shuchu_value = int(shuchu_value)

                        jiaoyi_shuchu_neirong = {'address': shuchu_address, 'value': shuchu_value, 'danwei': shuchu_danwei,
                                                 'jingdu': shuchu_jingdu,
                                                 'txid': tx_id, 'to': ''}
                        jiaoyi_shuchu_neirong_quanbu.append(jiaoyi_shuchu_neirong)
                        tx_vout_count = tx_vout_count - 1

                    # 计算交易费用
                    # [{'value':20,'danwei':'bi','jingdu':8,'txid':ulasdfja,'address':addjFITljflsd},{'value':30,'danwei':'gu','jingdu':0,'txid':ulasdfjadlsjdfl}]
                    # [{'value':20,'danwei':'bi','jingdu':8,'txid':ulasdfja,'address':addjFITljflsd},{'value':30,'danwei':'gu','jingdu':0,'txid':ulasdfjadlsjdfl}]

                    if len(jiaoyi_shuru_neirong_quanbu) or len(jiaoyi_shuchu_neirong_quanbu):
                        if not len(jiaoyi_shuru_neirong_quanbu):
                            # 输入为零，输出不为零,资产发行，把相关资产加入地址账户
                            for s in jiaoyi_shuchu_neirong_quanbu:
                                addr_cur = db.Address.find_one({'address': s['address']})
                                if not addr_cur:
                                    #产生了新地址
                                    addr = Address(s, result['time'])
                                    address_collection = addr.new_address()
                                    db.Address.insert_one(address_collection)
                                    # save_path = 'D:\\antchain.me\\static\\address\\' + s['address'] + '.png'
                                    # antsharesqr.make_qr(s['address'], save_path)
                                    save_path = '/root/www/antchain_mainnet/static/address/' + s['address'] + '.png'
                                    antsharesqr.make_qr(s['address'],save_path)
                                    print('Add New Address')
                                else:
                                    #更新地址内容
                                    value = s['value']
                                    danwei = s['danwei']
                                    jingdu = s['jingdu']
                                    l = [z['danwei'] for z in addr_cur['yue']]
                                    if danwei in l:
                                        i = l.index(danwei)
                                        addr_cur['yue'][i]['value'] = addr_cur['yue'][i]['value'] + value
                                        if jingdu:
                                            fs='%0.'+str(jingdu)+'f'
                                            addr_cur['yue'][i]['value'] = float(fs % addr_cur['yue'][i]['value'])
                                    else:
                                        addr_cur['yue'].append({'value': value, 'danwei': danwei})

                                    addr_cur['jiaoyi'].append({'txid': s['txid']})
                                    addr_cur['timestamp'] = datetime.datetime.fromtimestamp(result['time'])
                                    db.Address.update({'address': s['address']},
                                                      {'$set': {'yue': addr_cur['yue'], 'jiaoyi': addr_cur['jiaoyi'],
                                                                'timestamp': addr_cur['timestamp']}})
                                    print('Change', addr_cur['address'])

                            print('ClaimTransaction or IssueTransaction')
                            tx_feiyong = 0
                        elif not len(jiaoyi_shuchu_neirong_quanbu):
                            # 输入不为零，输出为零，均为交易费用，并从相关账户中减掉相应资产
                            # for s in jiaoyi_shuru_neirong_quanbu:
                            #     addr_cur = db.Address.find_one({'address': s['address']})
                            #     value = s['value']
                            #     danwei = s['danwei']
                            #     l = [s['danwei'] for s in addr_cur['yue']]
                            #     if danwei in l:
                            #         i = l.index(danwei)
                            #         addr_cur['yue'][i]['value'] = addr_cur['yue'][i]['value'] - value
                            #
                            #     else:
                            #         print('程序出现错误')
                            #     addr_cur['jiaoyi'].append(s)
                            #     addr_cur['jiaoyi_cishu'] = addr_cur['jiaoyi_cishu'] + 1
                            #     db.Address.update({'address': s['address']},
                            #                       {'$set': {'yue': addr_cur['yue'], 'jiaoyi': addr_cur['jiaoyi'],
                            #                                 'jiaoyi_cishu': addr_cur['jiaoyi_cishu']}})
                            #     print('已对', addr_cur['address'], s['address'], '地址完成跟新。')
                            #
                            #     feiyong.append({s['value'],s['danewi']})
                            #
                            #     ll=[s['danwei'] for s in feiyong]
                            #
                            #
                            #     for s in feiyong:
                            #         for s
                            #         s['danwei']
                            print('impossible error 0!')
                        else:
                            # 输入输出均不为零，计算输入输出的小蚁币的差值即为交易费用
                            r = jiaoyi_shuru_neirong_quanbu
                            c = jiaoyi_shuchu_neirong_quanbu
                            shuru_xiaoyibi_zonghe = 0
                            shuchu_xiaoyibi_zonghe = 0
                            shuru_dizhi = set()
                            shuchu_dizhi = set()
                            for x in range(len(r)):
                                if r[x]['danwei'] == '小蚁币':
                                    shuru_xiaoyibi_zonghe = shuru_xiaoyibi_zonghe + r[x]['value']
                                addr_cur = db.Address.find_one({'address': r[x]['address']})
                                if addr_cur:
                                    value = r[x]['value']
                                    danwei = r[x]['danwei']
                                    jingdu = r[x]['jingdu']
                                    l = [s['danwei'] for s in addr_cur['yue']]
                                    if danwei in l:
                                        i = l.index(danwei)
                                        addr_cur['yue'][i]['value'] = addr_cur['yue'][i]['value'] - value
                                        if jingdu:
                                            fs = '%0.' + str(jingdu) + 'f'
                                            addr_cur['yue'][i]['value'] = float(fs % addr_cur['yue'][i]['value'])
                                    else:
                                        print('impossible error 1!')
                                    addr_cur['timestamp'] = datetime.datetime.fromtimestamp(result['time'])
                                    db.Address.update({'address': r[x]['address']},
                                                      {'$set': {'yue': addr_cur['yue']}})
                                    print('Change', addr_cur['address'])
                                    shuru_dizhi.add(r[x]['address'])
                                else:
                                    print('impossible error 2！')

                            for y in range(len(c)):
                                if c[y]['danwei'] == '小蚁币':
                                    shuchu_xiaoyibi_zonghe = shuchu_xiaoyibi_zonghe + c[y]['value']
                                addr_cur = db.Address.find_one({'address': c[y]['address']})
                                if not addr_cur:
                                    addr = Address(c[y], result['time'])
                                    address_collection = addr.new_address()
                                    db.Address.insert_one(address_collection)
                                    # save_path = 'D:\\antchain.me\\static\\address\\' + c[y]['address'] + '.png'
                                    # antsharesqr.make_qr(c[y]['address'], save_path)
                                    save_path = '/root/www/antchain_mainnet/static/address/' + c[y]['address'] + '.png'
                                    antsharesqr.make_qr(c[y]['address'],save_path)
                                    print('Add New Address')
                                else:
                                    value = c[y]['value']
                                    danwei = c[y]['danwei']
                                    jingdu = c[y]['jingdu']
                                    l = [zz['danwei'] for zz in addr_cur['yue']]
                                    if danwei in l:
                                        i = l.index(danwei)
                                        addr_cur['yue'][i]['value'] = addr_cur['yue'][i]['value'] + value
                                        if jingdu:
                                            fs = '%0.' + str(jingdu) + 'f'
                                            addr_cur['yue'][i]['value'] = float(fs % addr_cur['yue'][i]['value'])
                                    else:
                                        addr_cur['yue'].append({'value': value, 'danwei': danwei})
                                    db.Address.update({'address': c[y]['address']},
                                                      {'$set': {'yue': addr_cur['yue']}})
                                    print('Change', addr_cur['address'])
                                    shuchu_dizhi.add(c[y]['address'])
                            #更新本次交易涉及的地址的交易字段和交易时间字段
                            #计算本次交易的费用
                            dizhi = shuchu_dizhi | shuru_dizhi
                            for d in dizhi:
                                addr_d = db.Address.find_one({'address': d})
                                addr_d['jiaoyi'].append({'txid': tx_id})
                                addr_d['timestamp'] = datetime.datetime.fromtimestamp(result['time'])
                                db.Address.update({'address': d},
                                                  {'$set': {'jiaoyi': addr_d['jiaoyi'], 'timestamp': addr_d['timestamp']}})
                                print('Change', d, 'Transaction.')

                            tx_feiyong = shuru_xiaoyibi_zonghe - shuchu_xiaoyibi_zonghe
                            tx_feiyong = float('%0.8f' % tx_feiyong)
                            if not tx_feiyong:
                                tx_feiyong = 0
                    else:
                        # 输入输出均为零
                        tx_feiyong = 0

                    # 处理交易
                    # 完成交易费用的编码,交易的输入输出具体模型设计

                    transaction = Transaction(block_txs[len(block_txs) - block_txs_count], result['hash'], result['height'],
                                              result['time'],
                                              jiaoyi_shuru_neirong_quanbu, jiaoyi_shuchu_neirong_quanbu,
                                              tx_feiyong)
                    tx_collection = transaction.new_transaction()
                    db.Transaction.insert_one(tx_collection)
                    print('sum', len(block_txs), 'tx，Done', len(block_txs) - block_txs_count + 1)
                    print('Tx fee', tx_feiyong, 'Antcoin')
                    db_tx_count = db_tx_count + 1
                    print('Transaction sum', db_tx_count)
                    block_txs_count = block_txs_count - 1
                else:
                    block_txs_count = block_txs_count - 1
                    continue

                block_feiyong = block_feiyong + tx_feiyong
            # time.sleep(0.1)
            # 处理区块
            q = db.Block.find_one({'hash': result['previousblockhash']}, {'nextblockhash': 1})
            if q:
                if not q['nextblockhash']:
                    q['nextblockhash'] = result['hash']
                    db.Block.update({'hash': result['previousblockhash']},
                                    {'$set': {'nextblockhash': q['nextblockhash']}})
                    print('Block', db_block_count - 1, 'Done！')
            block = Block(result, block_feiyong)
            db.Block.insert_one(block.new_block())
            print("Block", db_block_count, "in mongodb！")
            print('Block fee', block_feiyong, 'Antcoin')
            db_block_count = db_block_count + 1

        ###未确认交易的入库
        weiquerenjiaoyi=antsharesjsonrpc.getrawmempool()
        # weiquerenjiaoyi.append('c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b')
        if weiquerenjiaoyi:
            db.NotTransaction.drop()
            for w in weiquerenjiaoyi:
                result=antsharesjsonrpc.getrawtransaction(w)
                # 处理交易输入输出问题
                tx_vin = result['vin']
                tx_vin_count = len(tx_vin)
                jiaoyi_shuru_neirong_quanbu = []
                tx_vout = result['vout']
                tx_vout_count = len(tx_vout)
                jiaoyi_shuchu_neirong_quanbu = []
                tx_id = result['txid']
                tx_feiyong = 0

                while tx_vin_count:
                    r = db.Transaction.find_one({'txid': tx_vin[len(tx_vin) - tx_vin_count]['txid']},
                                                {'vout': 1})
                    shuru_value = r['vout'][tx_vin[len(tx_vin) - tx_vin_count]['vout']]['value']
                    shuru_address = r['vout'][tx_vin[len(tx_vin) - tx_vin_count]['vout']]['address']
                    shuru_danwei = r['vout'][tx_vin[len(tx_vin) - tx_vin_count]['vout']]['danwei']
                    shuru_jingdu = r['vout'][tx_vin[len(tx_vin) - tx_vin_count]['vout']]['jingdu']
                    jiaoyi_shuru_neirong = {'address': shuru_address, 'value': shuru_value,
                                            'danwei': shuru_danwei,
                                            'jingdu': shuru_jingdu,
                                            'txid': tx_vin[len(tx_vin) - tx_vin_count]['txid']}
                    jiaoyi_shuru_neirong_quanbu.append(jiaoyi_shuru_neirong)
                    tx_vin_count = tx_vin_count - 1

                while tx_vout_count:
                    shuchu_value = tx_vout[len(tx_vout) - tx_vout_count]['value']
                    shuchu_asset = tx_vout[len(tx_vout) - tx_vout_count]['asset']
                    shuchu_address = tx_vout[len(tx_vout) - tx_vout_count]['address']
                    c = db.Transaction.find_one({'txid': shuchu_asset}, {'asset': 1})
                    shuchu_danwei = c['asset']['name'][0]['name']
                    shuchu_jingdu = c['asset']['precision']
                    if shuchu_jingdu:
                        shuchu_value = float(shuchu_value)
                    else:
                        shuchu_value = int(shuchu_value)

                    jiaoyi_shuchu_neirong = {'address': shuchu_address, 'value': shuchu_value,
                                             'danwei': shuchu_danwei,
                                             'jingdu': shuchu_jingdu,
                                             'txid': tx_id, 'to': ''}
                    jiaoyi_shuchu_neirong_quanbu.append(jiaoyi_shuchu_neirong)
                    tx_vout_count = tx_vout_count - 1

                    # 计算交易费用
                    # [{'value':20,'danwei':'bi','jingdu':8,'txid':ulasdfja,'address':addjFITljflsd},{'value':30,'danwei':'gu','jingdu':0,'txid':ulasdfjadlsjdfl}]
                    # [{'value':20,'danwei':'bi','jingdu':8,'txid':ulasdfja,'address':addjFITljflsd},{'value':30,'danwei':'gu','jingdu':0,'txid':ulasdfjadlsjdfl}]

                if len(jiaoyi_shuru_neirong_quanbu) or len(jiaoyi_shuchu_neirong_quanbu):
                    if not len(jiaoyi_shuru_neirong_quanbu):
                        # 输入为零，输出不为零,资产发行，把相关资产加入地址账户
                        print('ClaimTransaction or IssueTransaction')
                        tx_feiyong = 0
                    else:
                        # 输入输出均不为零，计算输入输出的小蚁币的差值即为交易费用
                        wr = jiaoyi_shuru_neirong_quanbu
                        wc = jiaoyi_shuchu_neirong_quanbu
                        shuru_xiaoyibi_zonghe = 0
                        shuchu_xiaoyibi_zonghe = 0
                        shuru_dizhi = set()
                        shuchu_dizhi = set()
                        for x in range(len(wr)):
                            if wr[x]['danwei'] == '小蚁币':
                                shuru_xiaoyibi_zonghe = shuru_xiaoyibi_zonghe + wr[x]['value']
                            shuru_dizhi.add(wr[x]['address'])

                        for y in range(len(wc)):
                            if wc[y]['danwei'] == '小蚁币':
                                shuchu_xiaoyibi_zonghe = shuchu_xiaoyibi_zonghe + wc[y]['value']
                            shuchu_dizhi.add(wc[y]['address'])
                        # 计算本次交易的费用
                        tx_feiyong = shuru_xiaoyibi_zonghe - shuchu_xiaoyibi_zonghe
                        tx_feiyong = float('%0.8f' % tx_feiyong)
                        if not tx_feiyong:
                            tx_feiyong = 0
                else:
                    # 输入输出均为零
                    tx_feiyong = 0

                # 处理交易
                # 未完成交易费用的编码,交易的输入输出具体模型设计
                transaction = Transaction(result, '', '',int(time.time()),
                                              jiaoyi_shuru_neirong_quanbu, jiaoyi_shuchu_neirong_quanbu,
                                              tx_feiyong)
                tx_collection = transaction.new_transaction()
                ss=db.NotTransaction.insert_one(tx_collection)
                print('push one NotTransaction!')
        time.sleep(7)


if __name__ == '__main__':
    jieshou_block()
