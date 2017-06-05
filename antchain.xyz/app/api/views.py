#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 4/23/17 12:25 AM
# @Author  : lcux
# @Site    : https://github.com/lcux
# @File    : views.py
# @Software: PyCharm

from . import api
from .. import db
import json

@api.route('/api/v1/address/info/<address>')
def api_address_info(address):
    ad = db.Address.find_one({'_id': address}, {'balance': 1, 'txs': 1})
    balance = []
    if ad:
        address = ad['_id']
        for b in ad['balance'].keys():
            balance.append({'balance': ad['balance'][b]['value'], 'unit': ad['balance'][b]['unit'], 'asset': b})
        tx = ad['txs']
        return json.dumps({'address': address, 'balance': balance, 'tx': tx})
    else:
        return json.dumps({'result': 'No Address!'})


@api.route('/api/v1/address/utxo/<address>')
def api_address_utxo(address):
    ad = db.Address.find_one({'_id': address}, {'utxo': 1})
    # utxo = []
    if ad:
        address = ad['_id']
        utxo = ad['utxo']
        return json.dumps({'address': address, 'utxo': utxo, })
    else:
        return json.dumps({'result': 'No Address!'})
