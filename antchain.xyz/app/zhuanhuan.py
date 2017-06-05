#! /usr/bin/env python
# -*- coding: UTF-8 -*-
import binascii

d = {'00': 'OP_0', '01': 'OP_PUSHBYTES1', '02': 'OP_PUSHBYTES2',
     '03': 'OP_PUSHBYTES3', '04': 'OP_PUSHBYTES4', '05': 'OP_PUSHBYTES5', '06': 'OP_PUSHBYTES6',
     '07': 'OP_PUSHBYTES7', '08': 'OP_PUSHBYTES8', '09': 'OP_PUSHBYTES9', '0a': 'OP_PUSHBYTES10',
     '0b': 'OP_PUSHBYTES11', '0c': 'OP_PUSHBYTES12', '0d': 'OP_PUSHBYTES13', '0e': 'OP_PUSHBYTES14',
     '0f': 'OP_PUSHBYTES15', '10': 'OP_PUSHBYTES16', '11': 'OP_PUSHBYTES17', '12': 'OP_PUSHBYTES18',
     '13': 'OP_PUSHBYTES19', '14': 'OP_PUSHBYTES20', '15': 'OP_PUSHBYTES21', '16': 'OP_PUSHBYTES22',
     '17': 'OP_PUSHBYTES23', '18': 'OP_PUSHBYTES24', '19': 'OP_PUSHBYTES25', '1a': 'OP_PUSHBYTES26',
     '1b': 'OP_PUSHBYTES27', '1c': 'OP_PUSHBYTES28', '1d': 'OP_PUSHBYTES29', '1e': 'OP_PUSHBYTES30',
     '1f': 'OP_PUSHBYTES31', '20': 'OP_PUSHBYTES32', '21': 'OP_PUSHBYTES33', '22': 'OP_PUSHBYTES34',
     '23': 'OP_PUSHBYTES35', '24': 'OP_PUSHBYTES36', '25': 'OP_PUSHBYTES37', '26': 'OP_PUSHBYTES38',
     '27': 'OP_PUSHBYTES39', '28': 'OP_PUSHBYTES40', '29': 'OP_PUSHBYTES41', '2a': 'OP_PUSHBYTES42',
     '2b': 'OP_PUSHBYTES43', '2c': 'OP_PUSHBYTES44', '2d': 'OP_PUSHBYTES45', '2e': 'OP_PUSHBYTES46',
     '2f': 'OP_PUSHBYTES47', '30': 'OP_PUSHBYTES48', '31': 'OP_PUSHBYTES49', '32': 'OP_PUSHBYTES50',
     '33': 'OP_PUSHBYTES51',
     '34': 'OP_PUSHBYTES52', '35': 'OP_PUSHBYTES53', '36': 'OP_PUSHBYTES54', '37': 'OP_PUSHBYTES55',
     '38': 'OP_PUSHBYTES56', '39': 'OP_PUSHBYTES57', '3a': 'OP_PUSHBYTES58', '3b': 'OP_PUSHBYTES59',
     '3c': 'OP_PUSHBYTES60', '3d': 'OP_PUSHBYTES61', '3e': 'OP_PUSHBYTES62', '3f': 'OP_PUSHBYTES63',
     '40': 'OP_PUSHBYTES64', '41': 'OP_PUSHBYTES65', '42': 'OP_PUSHBYTES66', '43': 'OP_PUSHBYTES67',
     '44': 'OP_PUSHBYTES68', '45': 'OP_PUSHBYTES69', '46': 'OP_PUSHBYTES70', '47': 'OP_PUSHBYTES71',
     '48': 'OP_PUSHBYTES72', '49': 'OP_PUSHBYTES73', '4a': 'OP_PUSHBYTES74', '4b': 'OP_PUSHBYTES75',
     '4c': 'OP_PUSHDATA1', '4d': 'OP_PUSHDATA2', '4e': 'OP_PUSHDATA4', '4f': 'OP_1NEGATE',
     '50': '', '51': 'OP_1', '52': 'OP_2', '53': 'OP_3',
     '54': 'OP_4', '55': 'OP_5', '56': 'OP_6', '57': 'OP_7',
     '58': 'OP_8', '59': 'OP_9', '5a': 'OP_10', '5b': 'OP_11',
     '5c': 'OP_12', '5d': 'OP_13', '5e': 'OP_14', '5f': 'OP_15',
     '60': 'OP_16', '61': 'OP_NOP', '62': 'OP_JMP', '63': 'OP_JMPIF',
     '64': 'OP_JMPIFNOT', '65': 'OP_CALL', '66': 'OP_RET', '67': 'OP_APPCALL',
     '68': 'OP_SYSCALL', '69': '', '6a': '', '6b': 'OP_TOALTSTACK',
     '6c': 'OP_FROMMALTSTACK', '6d': 'OP_XDROP', '6e': '', '6f': '',
     '70': '', '71': '', '72': 'OP_XSWAP', '73': 'OP_XTUCK',
     '74': 'OP_DEPTH', '75': 'OP_DROP', '76': 'OP_DUP', '77': 'OP_NIP',
     '78': 'OP_OVER', '79': 'OP_PICK', '7a': 'OP_ROLL', '7b': 'OP_ROT',
     '7c': 'OP_SWAP', '7d': 'OP_TUCK', '7e': 'OP_CAT', '7f': 'OP_SUBSTR',
     '80': 'OP_LEFT', '81': 'OP_RIGHT', '82': 'OP_SIZE', '83': 'OP_INVERT',
     '84': 'OP_AND', '85': 'OP_OR', '86': 'OP_XOR', '87': 'OP_EQUAL',
     '88': 'OP_EQUALVERIFY', '89': 'OP_RESERVED1', '8a': 'OP_RESERVED2', '8b': 'OP_1ADD',
     '8c': 'OP_1SUB', '8d': 'OP_2MUL', '8e': 'OP_2DIV', '8f': 'OP_NEGATE',
     '90': 'OP_ABS', '91': 'OP_NOT', '92': 'OP_0NOTEQUAL', '93': 'OP_ADD',
     '94': 'OP_SUB', '95': 'OP_MUL', '96': 'OP_DIV', '97': 'OP_MOD',
     '98': 'OP_LSHIFT', '99': 'OP_RSHIFT', '9a': 'OP_BOOLAND', '9b': 'OP_BOOLOR',
     '9c': 'OP_NUMEQUAL', '9d': '', '9e': 'OP_UNMNOTEQUAL', '9f': 'OP_LESSTHAN',
     'a0': 'OP_GREATERTHAN', 'a1': 'OP_LESSTHANOREAUAL', 'a2': 'OP_GREATERTHANOREQUAL', 'a3': 'OP_MIN',
     'a4': 'OP_MAX', 'a5': 'OP_WITHIN', 'a6': 'OP_RIPEMD160', 'a7': 'OP_SHA1',
     'a8': 'OP_SHA256', 'a9': 'OP_HASH160', 'aa': 'OP_HASH256', 'ab': '', 'ac': 'OP_CHECKSIG',
     'ae': 'CHECKMULTISIG','c0':'OP_ARRAYSIZE','c1':'OP_PACK','c2':'OP_UNPACK','c3':'OP_PICKITEM'}
# s = '400857d0c654153787af710f4d49cae2b232356d16051e818c2adbb8aaf8896be459570227829573148e946860608fc77'

pushbytes = {'01': 1, '02': 2, '03': 3, '04': 4, '05': 5, '06': 6, '07': 7, '08': 8, '09': 9, '0a': 10, '0b': 11,
             '0c': 12, '0d': 13, '0e': 14, '0f': 15, '10': 16, '11': 17, '12': 18, '13': 19, '14': 20, '15': 21,
             '16': 22, '17': 23, '18': 24, '19': 25, '1a': 26, '1b': 27, '1c': 28, '1d': 29, '1e': 30, '1f': 31,
             '20': 32, '21': 33, '22': 34, '23': 35, '24': 36, '25': 37, '26': 38, '27': 39, '28': 40, '29': 41,
             '2a': 42, 'ab': 43, '2c': 44, '2d': 45, '2e': 46, '2f': 47, '30': 48, '31': 49, '32': 50, '33': 51,
             '34': 52, '35': 53, '36': 54, '37': 55, '38': 56, '39': 57, '3a': 58, '3b': 59, '3c': 60, '3d': 1,
             '3e': 62, '3f': 63, '40': 64, '41': 65, '42': 66, '43': 67, '44': 68, '45': 69, '46': 70, '47': 71,
             '48': 72, '49': 73, '4a': 74, '4b': 75}
two = {'62', '63', '64', '65'}
twenty = {'67'}
budingzijie = {'68'}


def encode(s,zifu='\n'):
    qq = ''
    ll = s[0:2]
    while len(s):
        if ll in pushbytes.keys():
            x=pushbytes[ll]
            y=x*2+2
            qq += d[s[0:2]] + ' ' + s[2:y] + zifu
            s = s[y:]
            ll = s[0:2]
        elif ll in two:
            qq += d[s[0:2]] + ' ' + s[2:6] + zifu
            s = s[6:]
            ll = s[0:2]
        elif ll in twenty:
            ss = str(binascii.a2b_hex(s[2:40]))[2:-1]
            qq += d[s[0:2]] + ' ' + ss + zifu
            s = s[40:]
            ll = s[0:2]
        elif ll in budingzijie:
            c = int(s[2:4], 16) * 2 + 4
            ss = str(binascii.a2b_hex(s[4:c]))[2:-1]
            qq += d[s[0:2]] + ' ' + ss + zifu
            s = s[c:]
            ll = s[0:2]
        else:
            qq += d[s[0:2]] + zifu
            s = s[2:]
            ll = s[0:2]
    return qq



if __name__ == '__main__':
    s='210383cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8aac'
    print(encode(s))