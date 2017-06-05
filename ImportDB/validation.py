#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# author: lcux
# licensed under the MIT License.
# ########function ##########
#对比地址里面的余额信息和utxo信息，计算两者是否相等，若相等，说明信息正确；不相等，则打印两者信息
############################

from pymongo import MongoClient



def contrast():
    cur = db.Address.find({},{'balance':1,'utxo':1})
    print(cur.count())
    for d in cur:
        m=[]
        for u in d['utxo']:
            v=0
            c = db.Transaction.find_one({'_id': u}, {'asset': 1})
            unit = c['asset']['name'][0]['name']
            precision = c['asset']['precision']
            if precision:
                v=0.0
            for l in d['utxo'][u]:
                v += l['value']
                if precision:
                    fs = '%0.8' + 'f'
                    v = float(fs % v)
            m.append({'unit':unit,'value':v})

        d=list(d['balance'].values())
        d.sort(key=lambda x: x['unit'], reverse=True)
        m.sort(key=lambda x: x['unit'], reverse=True)

        if d==m:
            continue
        else:
            print('balance -->',d)
            print('utxo    -->',m)
            print('\n')

if __name__ == '__main__':
    db = MongoClient().antchain_mainnet
    contrast()
