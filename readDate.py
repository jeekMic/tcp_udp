# coding:utf-8
import time, serial
from struct import *
import binascii

# coding:utf-8
import time, serial
from struct import *
import binascii

# b= hex(eval(a))



def dec2hexstr(n):
    ss = str(hex(n))
    ss = ss[2:]
    if n <= 15:
        ss = '0' + ss
    return ss


def uchar_checksum(data, byteorder='little'):
    '''
    char_checksum 按字节计算校验和。每个字节被翻译为无符号整数
    @param data: 字节串
    @param byteorder: 大/小端
    '''
    length = len(data)
    checksum = 0
    for i in range(0, length):
        checksum += int(data[i], 16)
        checksum &= 0xFF  # 强制截断

    return checksum
def read():
    strss = ""
    file = open('Cloud_ploatform.bin', 'rb')
    i = 0
    arr = []
    m = 0
    while 1:
        if (i >= 1024):

            arr.insert(0, 'aa')
            arr.insert(0, 'aa')
            arr.insert(0, 'aa')
            arr.insert(3, '27')
            arr.insert(4, dec2hexstr(m))
            arr.append('ee')
            arr.append('ee')
            arr.append('ee')
            result = uchar_checksum(arr[4:1029])
            print(arr)
            arr.append(hex(result)[2:4])
            print(arr)
            arr = []
            i = 0
            m = m + 1

        c = file.read(1)
        # 将字节转换成16进制；
        ssss = str(binascii.b2a_hex(c))[2:-1]

        if ssss == '':
            break
        arr.append(ssss)
        i += 1

        # if not c:
        #     break
        # ser = serial.Serial('COM3', 57600, timeout=1)
        # ser.write(bytes().fromhex(ssss))# 将16进制转换为字节
        # if i % 16 == 0:
        #     time.sleep(0.001)
        # #写每一行等待的时间
        #
        i += 1

        # ser.close()

    file.close()
read()


