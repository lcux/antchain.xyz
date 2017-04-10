#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# author: lcux
# licensed under the MIT License.

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import antsharesjsonrpc
import antsharesqr
import datetime
import time
import sys
import platform


# 区块模型
class Block:
    def __init__(self, result, cost):
        self.merkleroot = result['merkleroot']
        self.previousblockhash = result['previousblockhash']
        self.presentblockhash = result['hash']
        self.nextblockhash = ''
        try:
            self.nextblockhash = result['nextblockhash']
        except:
            pass
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
            # '_id': self.presentblockhash,
            '_id': self.height,
            'merkleroot': self.merkleroot,
            'previousblockhash': self.previousblockhash,
            'presentblockhash': self.presentblockhash,
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
        return 'Block %r' % self.presentblockhash


# 交易模型
class Transaction:
    def __init__(self, tx, block_hash, block_height, timestamp, tx_vin, tx_vout, cost):
        self.txid = tx['txid']
        self.version = tx['version']
        self.attributes = tx['attributes']
        self.size = tx['size']
        self.vin = []
        for vin in tx_vin:
            i = {'address': vin['address'], 'value': vin['value'], 'unit': vin['unit'], 'precision': vin['precision'],
                 'txid': vin['txid'], 'asset': vin['asset'], 'index': vin['index']}
            self.vin.append(i)
        self.vout = []
        for vout in tx_vout:
            o = {'address': vout['address'], 'value': vout['value'], 'unit': vout['unit'],
                 'precision': vout['precision'], 'txid': vout['txid'], 'asset': vout['asset'], 'to': vout['to']}
            self.vout.append(o)
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
            self.contract = tx['contract']
        else:
            self.name = "无效交易"

    def new_transaction(self):
        collection = {
            '_id': self.txid,
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
                if isinstance(self.asset['name'], list):
                    collection['asset'] = self.asset
                elif isinstance(self.asset['name'], str):
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
            collection['contract'] = self.contract
        else:
            pass

        return collection

    def __repr__(self):
        return 'Transaction %r' % self.name


# 地址模型
class Address:
    def __init__(self, vout, timestamp, index):
        self.addr = vout['address']
        self.txid = vout['txid']
        self.unit = vout['unit']
        self.value = vout['value']
        self.asset = vout['asset']
        self.timestamp = timestamp
        self.utxo = {'txid': self.txid, 'index': index, 'value': self.value, 'unit': self.unit, 'asset': self.asset}

    def new_address(self):
        collection = {
            '_id': self.addr,
            'address': self.addr,
            'balance': [{'value': self.value, 'unit': self.unit}],
            'txs': [{'txid': self.txid}],
            # 'utxo':{self.asset:{self.utxo}},
            'utxo': {self.asset: [self.utxo]},
            'lasttime': datetime.datetime.fromtimestamp(self.timestamp),
            'firsttime': datetime.datetime.fromtimestamp(self.timestamp),
            'qrcode': 'address/' + self.addr + '.png'
        }
        return collection

    def __repr__(self):
        return 'Address %r' % self.addr


def generate_address_qrcode(address):
    plat = platform.system()
    if plat == 'Windows':
        save_path = 'D:\\antchain.me\\static\\address\\' + address + '.png'
        antsharesqr.make_qr(address, save_path)
    elif plat == 'Linux':
        # save_path = '/root/www/antchain_mainnet/static/address/' + address + '.png'
        save_path = '/home/lcux/address/' + address + '.png'
        antsharesqr.make_qr(address, save_path)
    else:
        print('???')


def sync_info():
    while True:
        db_block_count = db.Block.count()
        chain_block_count = antsharesjsonrpc.getblockcount()

        while db_block_count < chain_block_count:
            sync_block(db_block_count)
            db_block_count += 1

        # ###未确认交易的入库
        # weiquerenjiaoyi=antsharesjsonrpc.getrawmempool()
        # # weiquerenjiaoyi.append('c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b')
        # if weiquerenjiaoyi:
        #     db.NotTransaction.drop()
        #     for w in weiquerenjiaoyi:
        #         result=antsharesjsonrpc.getrawtransaction(w)
        #
        #         # 处理交易
        #         # 未完成交易费用的编码,交易的输入输出具体模型设计
        #         transaction = Transaction(result, '', '',int(time.time()),
        #                                       jiaoyi_shuru_neirong_quanbu, jiaoyi_shuchu_neirong_quanbu,
        #                                       tx_feiyong)
        #         tx_collection = transaction.new_transaction()
        #         ss=db.NotTransaction.insert_one(tx_collection)
        #         print('push one NotTransaction!')
        time.sleep(7)


def sync_block(block_height):
    result = antsharesjsonrpc.getblock(block_height)
    block_txs = result['tx']
    block_hash = result['hash']
    block_time = result['time']
    block_cost = 0

    # 处理交易数据,返回交易总费用
    for tx in block_txs:
        block_cost += sync_trasacton(tx, block_hash, block_height, block_time)

    # 处理区块数据
    pre_height = result['height'] - 1
    q = db.Block.find_one({'_id': pre_height}, {'nextblockhash': 1})
    # return None if no matching document is found.
    if q:
        if not q['nextblockhash']:
            q['nextblockhash'] = result['hash']
            db.Block.update({'_id': pre_height}, {'$set': {'nextblockhash': q['nextblockhash']}})
            # print('Block', block_height - 1, 'Done！')
    else:
        print('no block!')
    block = Block(result, block_cost)
    block_collection = block.new_block()
    try:
        db.Block.insert_one(block_collection)
        print("Block", block_height, "in mongodb！")
        # print('Block fee', block_cost, 'Antcoin')
    except DuplicateKeyError:
        print('duplicate block', block_height)


def sync_trasacton(tx, block_hash, block_height, block_time):
    # 格式化交易数据
    txid = tx['txid']
    tx_vin = []
    tx_vout = []
    tx_cost = 0

    # 处理交易输入
    for vin in tx['vin']:
        r = db.Transaction.find_one({'_id': vin['txid']}, {'vout': 1})
        vi = r['vout'][vin['vout']]
        to_s = 'vout.' + str(vin['vout']) + '.to'
        db.Transaction.update_one({'_id': vin['txid']}, {'$set': {to_s: txid}})
        i = {'address': vi['address'], 'value': vi['value'], 'unit': vi['unit'], 'asset': vi['asset'],
             'precision': vi['precision'], 'txid': vi['txid'], 'index': vin['vout']}
        tx_vin.append(i)

    # 处理交易输出
    for vout in tx['vout']:
        value = vout['value']
        asset = vout['asset']
        address = vout['address']
        c = db.Transaction.find_one({'_id': vout['asset']}, {'asset': 1})
        unit = c['asset']['name'][0]['name']
        precision = c['asset']['precision']
        if precision:
            value = float(value)
        else:
            value = int(value)
        to = ''
        v = {'address': address, 'value': value, 'unit': unit, 'asset': asset, 'precision': precision, 'txid': txid,
             'to': to}
        tx_vout.append(v)

    # 处理地址数据,返回交易费用
    if tx_vin or tx_vout:
        if db.Transaction.find_one({'_id': tx['txid']}) is None:
            tx_cost = sync_address(txid, tx_vin[:], tx_vout[:], block_time)
    else:
        tx_cost = 0

    transaction = Transaction(tx, block_hash, block_height, block_time, tx_vin, tx_vout, tx_cost)
    tx_collection = transaction.new_transaction()
    if db.Transaction.find_one({'_id': tx['txid']}) is None:
        try:
            db.Transaction.insert_one(tx_collection)
            # print('Tx fee', tx_cost, 'Antcoin')
        except Exception as e:
            print('duplicate transaction', tx)
            print(e)
    return tx_cost


def sync_address(tx_id, tx_vin, tx_vout, timestamp):
    tx_cost = 0
    r = tx_vin
    c = tx_vout
    vin_anc_count = 0
    vout_anc_count = 0
    vin_address = set()
    vout_address = set()

    for x in range(len(r)):
        if r[x]['unit'] == '小蚁币':
            vin_anc_count += r[x]['value']

        txid = r[x]['txid']
        index = r[x]['index']
        value = r[x]['value']
        unit = r[x]['unit']
        precision = r[x]['precision']
        asset = r[x]['asset']
        addr_cur_vin = db.Address.find_one({'_id': r[x]['address']})
        if addr_cur_vin:
            l = [s['unit'] for s in addr_cur_vin['balance']]
            if unit in l:
                i = l.index(unit)
                addr_cur_vin['balance'][i]['value'] -= value
                if precision:
                    fs = '%0.' + str(precision) + 'f'
                    addr_cur_vin['balance'][i]['value'] = float(fs % addr_cur_vin['balance'][i]['value'])
            else:
                print('impossible error!')
            db.Address.update({'_id': r[x]['address']},
                              {'$set': {'balance': addr_cur_vin['balance']}})
            # print('Change', addr_cur['address'])
            vin_address.add(r[x]['address'])

            # utxo
            # utxo = {'txid': txid, 'index': x, 'value': value, 'unit': unit, 'asset': asset}
            for ux in addr_cur_vin['utxo'][asset]:
                try:
                    if txid == ux['txid'] and index == ux['index']:
                        addr_cur_vin['utxo'][asset].remove(ux)
                        db.Address.update({'_id': r[x]['address']}, {'$set': {'utxo': addr_cur_vin['utxo']}})
                except Exception as e:
                    print(e)
        else:
            print('impossible error！')

    for y in range(len(c)):
        if c[y]['unit'] == '小蚁币':
            vout_anc_count += c[y]['value']

        addr_cur_vout = db.Address.find_one({'_id': c[y]['address']})
        if addr_cur_vout is None:
            addr = Address(c[y], timestamp, y)
            address_collection = addr.new_address()
            try:
                db.Address.insert_one(address_collection)
                generate_address_qrcode(c[y]['address'])
                # print('Add New Address')
            except DuplicateKeyError:
                print('duplicate address', c[y]['address'])
        else:
            txid = c[y]['txid']
            value = c[y]['value']
            unit = c[y]['unit']
            precision = c[y]['precision']
            asset = c[y]['asset']
            l = [zz['unit'] for zz in addr_cur_vout['balance']]
            if unit in l:
                i = l.index(unit)
                addr_cur_vout['balance'][i]['value'] += value
                if precision:
                    fs = '%0.' + str(precision) + 'f'
                    addr_cur_vout['balance'][i]['value'] = float(fs % addr_cur_vout['balance'][i]['value'])
            else:
                addr_cur_vout['balance'].append({'value': value, 'unit': unit})

            db.Address.update({'_id': c[y]['address']}, {'$set': {'balance': addr_cur_vout['balance']}})
            # print('Change', addr_cur['address'])
            vout_address.add(c[y]['address'])

            # utxo
            utxo = {'txid': txid, 'index': y, 'value': value, 'unit': unit, 'asset': asset}
            if asset not in addr_cur_vout['utxo']:
                addr_cur_vout['utxo'][asset] = []
            addr_cur_vout['utxo'][asset].append(utxo)
            db.Address.update({'_id': c[y]['address']}, {'$set': {'utxo': addr_cur_vout['utxo']}})

    # 更新本次交易涉及的地址的交易字段和交易时间字段
    addresses = vin_address | vout_address
    for d in addresses:
        addr_d = db.Address.find_one({'_id': d})
        t={'txid':tx_id}
        if t in addr_d['txs']:
            print('An address has two transactions in a tx and the address is the first use', d)
        else:
            addr_d['lasttime'] = datetime.datetime.fromtimestamp(timestamp)
            addr_d['txs'].append({'txid': tx_id})
            db.Address.update({'_id': d}, {'$set': {'txs': addr_d['txs'], 'lasttime': addr_d['lasttime']}})
            print('Change', d, 'txs and lasttime.')
    #计算交易费用
    if vin_anc_count:
        tx_cost = vin_anc_count - vout_anc_count
        tx_cost = float('%0.8f' % tx_cost)
        if not tx_cost:
            tx_cost = 0
        return tx_cost
    else:
        return tx_cost


if __name__ == '__main__':
    try:
        db = MongoClient().antchain_mainnet
        sync_info()
    except Exception as e:
        print(e)
        sys.exit()
