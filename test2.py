'''
计算645数据域数据长度
@Source 2013-5-10 16:30
'''


def LenCal(s):
    L = ''
    L = hex(len(s) // 2).replace('0x', '')
    if len(L) <= 1:
        L = ('00' + L)[-2:]

    return L


'''
对16进制字符串进行加0x33处理
@Source 2013-5-10 12:00
'''


def Add33(s):
    h = ''
    for i in range(len(s) // 2):
        temper = ''
        temper = hex(int('33', 16) + int(s[2 * i:2 * i + 2], 16)).replace('0x', '')
        if len(temper) <= 1:
            temper = ('00' + temper).upper()[-2:]

        h = h + temper
    ##返回加0x33后的数据
    return h


'''
对16进制字符串进行减0x33处理
@Source 2013-5-10 12:10
'''


def Reduce33(s):
    h = ''
    for i in range(len(s) // 2):
        temper = ''
        temper = hex(int(s[2 * i:2 * i + 2], 16) - int('33', 16)).replace('0x', '')
        ##如果余值为负数，去除'-'
        temper = temper.replace('-', '')

        if len(temper) <= 1:
            temper = ('00' + temper).upper()[-2:]

        h = h + temper
    ##返回减0x33后的数据
    return h


'''
计算16进制字符串的CRC16校验
@Source 2013-5-10 11:00
'''


def CRC16(s):
    h = '0'
    for i in range(len(s) // 2):
        h = hex(int(h, 16) + int(s[2 * i:2 * i + 2], 16))

    h = h.replace('0x', '')
    if len(h) <= 1:
        h = '00' + h

    return h.upper()[-2:]


# 68AAAAAAAAAAAA681300DF16
# print CRC16('68AAAAAAAAAAAA681300')
# print Add33('010101010101')
# print Reduce33('010101010101')

if __name__ == '__main__':
    print(LenCal('2700000000000000000000'))
