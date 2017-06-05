#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# author: lcux
# licensed under the MIT License.

from pymongo.errors import DuplicateKeyError
import antsharesjsonrpc
import antsharesqr
import sys
import platform
from functions import *


# 区块模型
class Block:
    def __init__(self, result, cost):
        self.merkleroot = result['merkleroot']
        self.previousblockhash = result['previousblockhash']
        self.presentblockhash = result['hash']
        try:
            self.nextblockhash = result['nextblockhash']
        except:
            self.nextblockhash = ''
        self.nextminer = result['nextconsensus']
        self.datetime = datetime.datetime.utcfromtimestamp(result['time'])
        self.height = result['index']
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
    def __init__(self, tx, block_hash, block_height, timestamp, tx_vin, tx_vout, id):
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
        self.net_fee = tx['net_fee']
        self.sys_fee = tx['sys_fee']
        self.id = id  # 主要用于方面检索，快速翻页使用，快速查询数量,挖矿交易时该字段为空字符串

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
            self.description = ''
        elif self.type == 'AgencyTransaction':
            self.name = "委托交易"
        elif self.type == 'PublishTransaction':
            self.name = "合约发布交易"
            self.contract = tx['contract']
        elif self.type == 'InvocationTransaction':
            self.name = "合约调用交易"
            self.script = tx['script']
        else:
            self.name = "未知属性交易"

    def new_transaction(self):
        collection = {
            '_id': self.txid,
            'txid': self.txid,
            'version': self.version,
            'attributes': self.attributes,
            'size': self.size,
            'vin': self.vin,
            'vout': self.vout,
            'timestamp': datetime.datetime.utcfromtimestamp(self.timestamp),
            'scripts': self.scripts,
            'type': self.type,
            'block_hash': self.block_hash,
            'block_height': self.block_height,
            'name': self.name,
            'net_fee': self.net_fee,
            'sys_fee': self.sys_fee,
            'id': self.id
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
            collection['description'] = self.description
        elif self.type == 'AgencyTransaction':
            pass
        elif self.type == 'PublishTransaction':
            collection['contract'] = self.contract
        elif self.type == 'InvocationTransaction':
            collection['script'] = self.script
        else:
            pass

        return collection

    def __repr__(self):
        return 'Transaction %r' % self.name


# 地址模型
class Address:
    def __init__(self, vout, timestamp, index, id):
        self.addr = vout['address']
        self.txid = vout['txid']
        self.unit = vout['unit']
        self.value = vout['value']
        self.asset = vout['asset']
        self.tag = []
        self.timestamp = datetime.datetime.utcfromtimestamp(timestamp)
        self.utxo = {'txid': self.txid, 'index': index, 'value': self.value, 'unit': self.unit, 'asset': self.asset}
        self.id = id  # 用于查询地址数量，快速检查地址总数

    def new_address(self):
        collection = {
            '_id': self.addr,
            'address': self.addr,
            'balance': {self.asset: {'value': self.value, 'unit': self.unit}},
            'txs': [{'txid': self.txid}],
            'utxo': {self.asset: [self.utxo]},
            'lasttime': self.timestamp,
            'firsttime': self.timestamp,
            'qrcode': 'address/' + self.addr + '.png',
            'tag': self.tag,
            'id': self.id
        }
        return collection

    def __repr__(self):
        return 'Address %r' % self.addr


# 统计数据模型
class Daily_Count:
    def __init__(self, date, tx_num_growth, address_num_growth, ans_hold, anc_hold, ans_quota, ans_worth, txs,
                 addresses,ans_holding_num):
        self.date = date
        self.tx_count = tx_num_growth
        self.address_count = address_num_growth
        self.ans_hold = ans_hold
        self.anc_hold = anc_hold
        self.ans_quota = ans_quota
        self.ans_worth = ans_worth
        self.txs = txs
        self.addresses = addresses
        self.ans_holding_num=ans_holding_num

    def new_daily_count(self):
        collection = {
            '_id': self.date,
            'tx_count_growth': self.tx_count,
            'address_count_growth': self.address_count,
            'ans_holding': self.ans_hold,
            'anc_holding': self.anc_hold,
            'ans_quota': self.ans_quota,
            'ans_worth': self.ans_worth,
            'txs': self.txs,
            'addresses': self.addresses,
            'ans_holding_num':self.ans_holding_num
        }
        return collection


##########
## 功能函数
#########
# @fn_timer
def daily_counts(block_height, block_time):
    asset_hold = []
    try:
        if block_height != 0:
            pre_tx_utc = db.Block.find_one({'_id': block_height - 1}, {'timestamp': 1})['timestamp']
            present_tx_utc = datetime.datetime.utcfromtimestamp(block_time)
            if pre_tx_utc.day < present_tx_utc.day:
                previous_daily_address_count = address_growth(year=pre_tx_utc.year, month=pre_tx_utc.month,
                                                              day=pre_tx_utc.day,
                                                              num_days=1)
                previous_daily_no_mt_tx_count = tx_no_mt_growth(year=pre_tx_utc.year, month=pre_tx_utc.month,
                                                                day=pre_tx_utc.day, num_days=1)
                # asset_cur=db.Transaction.find({'type': 'RegisterTransaction'})
                # for asset in asset_cur:
                #     asset_id=asset['_id']
                #     counts=asset_holding(asset_id)
                #     asset_hold.append({asset_id:counts})
                if datetime.datetime.utcnow() - present_tx_utc < datetime.timedelta(seconds=30):
                    ans_quota, ans_worth = ans_quota_and_worth()
                else:
                    ans_quota =get_yunbi_ans_time(pre_tx_utc)
                    ans_worth = str(D(ans_quota)*100000000)

                ans_holding_num=ans_holding_100_500_1000_5000_10000_100000()

                daily_count = Daily_Count(pre_tx_utc, previous_daily_no_mt_tx_count, previous_daily_address_count,
                                          ans_holding(), anc_holding(), ans_quota, ans_worth, transaction_no_mt_count(),
                                          address_count(),ans_holding_num)
                daily_count_collection = daily_count.new_daily_count()
                db.Daily_Count.insert_one(daily_count_collection)
                print('insert daily_count')
    except Exception as e:
        print(e, 'daily_count')


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


##########
## 处理过程
##########

def sync_address(tx_id, tx_vin, tx_vout, timestamp):
    r = tx_vin
    c = tx_vout
    vin_address = set()
    vout_address = set()

    for x in range(len(r)):
        txid = r[x]['txid']
        index = r[x]['index']
        value = r[x]['value']
        # unit = r[x]['unit']
        # precision = r[x]['precision']
        asset = r[x]['asset']
        addr_cur_vin = db.Address.find_one({'_id': r[x]['address']})
        if addr_cur_vin:
            # utxo and balance
            for ux in addr_cur_vin['utxo'][asset]:
                try:
                    if txid == ux['txid'] and index == ux['index']:
                        addr_cur_vin['utxo'][asset].remove(ux)
                        addr_cur_vin['balance'][asset]['value'] = str(
                            D(addr_cur_vin['balance'][asset]['value']) - D(value))
                        db.Address.update({'_id': r[x]['address']},
                                          {'$set': {'balance': addr_cur_vin['balance'], 'utxo': addr_cur_vin['utxo']}})
                except Exception as e:
                    print(e, 'update_vin_address')
            vin_address.add(r[x]['address'])
        else:
            print('impossible error ，address！')

    for y in range(len(c)):
        addr_cur_vout = db.Address.find_one({'_id': c[y]['address']})
        if addr_cur_vout is None:
            # iid = db.Address.count()
            # iid = db.Address.find({}, {'id': 1}).sort('firsttime', DESCENDING)[0]['id'] + 1
            id = ''
            try:
                cur = db.Address.find({}, {'id': 1}).sort('id', DESCENDING)

                id = cur[0]['id'] + 1
            except Exception as e:
                print(e, 'sync_address')
                id = 0
            addr = Address(c[y], timestamp, y, id)
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
            # precision = c[y]['precision']
            asset = c[y]['asset']
            utxo = {'txid': txid, 'index': y, 'value': value, 'unit': unit, 'asset': asset}
            if asset not in addr_cur_vout['utxo']:
                addr_cur_vout['utxo'][asset] = []
                addr_cur_vout['utxo'][asset].append(utxo)
                addr_cur_vout['balance'][asset] = {'value': value, 'unit': unit}
            if utxo not in addr_cur_vout['utxo'][asset]:
                addr_cur_vout['utxo'][asset].append(utxo)
                addr_cur_vout['balance'][asset]['value'] = str(D(addr_cur_vout['balance'][asset]['value']) + D(value))
            try:
                db.Address.update({'_id': c[y]['address']},
                                  {'$set': {'balance': addr_cur_vout['balance'], 'utxo': addr_cur_vout['utxo']}})
            except Exception as e:
                print(e, 'update_vout_address')
            vout_address.add(c[y]['address'])
    # 更新本次交易涉及的地址的交易字段和交易时间字段
    addresses = vin_address | vout_address
    for d in addresses:
        addr_d = db.Address.find_one({'_id': d})
        t = {'txid': tx_id}
        if t in addr_d['txs']:
            print('An address has two transactions in a tx and the address is the first use', d)
        else:
            addr_d['lasttime'] = datetime.datetime.utcfromtimestamp(timestamp)
            addr_d['txs'].append({'txid': tx_id})
            db.Address.update({'_id': d}, {'$set': {'txs': addr_d['txs'], 'lasttime': addr_d['lasttime']}})
            print('Change', d, 'txs and lasttime.')


def sync_trasacton(tx, block_hash, block_height, block_time):
    # 格式化交易数据
    txid = tx['txid']
    tx_vin = []
    tx_vout = []
    id = 0

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
        to = ''
        v = {'address': address, 'value': value, 'unit': unit, 'asset': asset, 'precision': precision, 'txid': txid,
             'to': to}
        tx_vout.append(v)

    # 处理地址数据
    if tx_vin or tx_vout:
        sync_address(txid, tx_vin[:], tx_vout[:], block_time)

    # id = db.Transaction.count()
    # id = db.Transaction.find({}, {'id': 1}).sort('timestamp', DESCENDING)[0]['id'] + 1
    if tx['type']=='MinerTransaction':
        id=0
    else:
        try:
            cur = db.Transaction.find({'type': {'$ne': 'MinerTransaction'}}, {'id': 1}).sort('id', DESCENDING)
            id = cur[0]['id'] + 1
        except Exception as e:
            print(e, 'sync_transaction')
            id = 0

    transaction = Transaction(tx, block_hash, block_height, block_time, tx_vin, tx_vout, id)
    tx_collection = transaction.new_transaction()
    try:
        db.Transaction.insert_one(tx_collection)
        # print('Tx fee', tx_cost, 'Antcoin')
    except Exception as e:
        print('duplicate transaction', tx)
        print(e)
    tx_cost = str(D(tx['net_fee']) + D(tx['sys_fee']))
    return tx_cost


def sync_block(block_height):
    result = antsharesjsonrpc.getblock(block_height)
    block_txs = result['tx']
    block_hash = result['hash']
    block_time = result['time']
    block_cost = D('0')

    # 处理交易数据,返回交易总费用
    for tx in block_txs:
        if db.Transaction.find_one({'_id': tx['txid']}) is None:
            block_cost = block_cost + D(sync_trasacton(tx, block_hash, block_height, block_time))
        else:
            block_cost = D(tx['net_fee']) + D(tx['sys_fee'])
    # 处理区块数据
    pre_height = result['index'] - 1
    q = db.Block.find_one({'_id': pre_height}, {'nextblockhash': 1})
    # return None if no matching document is found.
    if q:
        if not q['nextblockhash']:
            q['nextblockhash'] = result['hash']
            db.Block.update({'_id': pre_height}, {'$set': {'nextblockhash': q['nextblockhash']}})
            # print('Block', block_height - 1, 'Done！')
    else:
        print('no block!')
    block = Block(result, str(block_cost))
    block_collection = block.new_block()

    ##处理每日更新数据
    daily_counts(block_height, block_time)

    try:
        db.Block.insert_one(block_collection)
        if block_height % 1000 == 0:
            print("Block", block_height, "in mongodb！")
            # print('Block fee', block_cost, 'Antcoin')
    except DuplicateKeyError:
        print('duplicate block', block_height)


def sync_info():
    while True:
        # db_block_count = db.Block.count()
        try:
            cur = db.Block.find({}, {'_id': 1}).sort('_id', DESCENDING)
            db_block_count = cur[0]['_id'] + 1
        except Exception as e:
            print(e, 'sync_info')
            db_block_count = 0
        chain_block_count = antsharesjsonrpc.getblockcount()

        while db_block_count < chain_block_count:
            sync_block(db_block_count)
            db_block_count += 1
        time.sleep(7)


if __name__ == '__main__':
    try:
        db = MongoClient().antchain_mainnet
        sync_info()
    except Exception as e:
        print(e, )
        sys.exit()
