


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


def char_checksum(data, byteorder='little'):
    '''
    char_checksum 按字节计算校验和。每个字节被翻译为带符号整数
    @param data: 字节串
    @param byteorder: 大/小端
    '''
    length = len(data)
    checksum = 0
    for i in range(0, length):
        x = int.from_bytes(data[i:i + 1], byteorder, signed=True)
        if x > 0 and checksum > 0:
            checksum += x
            if checksum > 0x7F:  # 上溢出
                checksum = (checksum & 0x7F) - 0x80  # 取补码就是对应的负数值
        elif x < 0 and checksum < 0:
            checksum += x
            if checksum < -0x80:  # 下溢出
                checksum &= 0x7F
        else:
            checksum += x  # 正负相加，不会溢出
        # print(checksum)

    return checksum


def checkout_custom(strss):
    arr = strss.split()
    data = []
    for i in range(len(arr)):
        arr[i] = "0x"+arr[i]
        data.append(eval(arr[i]))
    result = data[0]^data[1]^data[2]^data[3]^data[4]^data[5]^data[6]^data[7]^data[8]^data[9]^data[10]
    result1 = result&0xf0
    result2 = (~result)&0x0f
    # print(hex()&0xf0)
    print(hex(result1+result2))
    return hex(result1+result2)


if __name__ == '__main__':
    print("ajsd")
    # strss = "00 27 00 00 00 00 00 00 00 00 00"
    # result = checkout_custom(strss)
