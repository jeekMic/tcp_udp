class Constant(object):
    update = 'FF FF 00 27 00 00 00 00 00 00 00 00 00 EE EE 28'
    finish = 'FF FF 00 28 00 00 00 00 00 00 00 00 00 EE EE 28'

    def __init__(self):
        super(Constant, self).__init__()

    # FF FF 00 27 00 00 00 00 00 00 00 00 00 EE EE
    def parse_hex(self, data):
        arr = data.split()

    def checkout_custom(self, strss):
        arr = strss.split()[2:13]
        data = []
        for i in range(len(arr)):
            arr[i] = "0x" + arr[i]
            data.append(eval(arr[i]))
        result = data[0] ^ data[1] ^ data[2] ^ data[3] ^ data[4] ^ data[5] ^ data[6] ^ data[7] ^ data[8] ^ data[9] ^ \
                 data[10]
        result1 = result & 0xf0
        result2 = (~result) & 0x0f
        # print(hex()&0xf0)
        print(hex(result1 + result2))
        return hex(result1 + result2)

    def checkout_custom_long(strss):
        arr = strss
        data = []
        for i in range(len(arr)):
            arr[i] = "0x" + arr[i]
            data.append(eval(arr[i]))
        result = data[0] ^ data[1] ^ data[2] ^ data[3] ^ data[4] ^ data[5] ^ data[6] ^ data[7] ^ data[8] ^ data[9] ^ \
                 data[10]

        result1 = result & 0xf0
        result2 = (~result) & 0x0f
        # print(hex()&0xf0)
        # print(hex(result1 + result2))
        return hex(result1 + result2)

    # 用于解析来自客户端的命令
    def parse_receive(data):
        try:
            arr = str(data).split()
            arr1 = arr[12]
            arr2 = arr[4]


            if arr1 == '12':
                return 12, "准备更新完毕"
            elif arr1 == '13':
                return 13, int(arr2, 16)
            elif arr1 == '34':
                return 34, "下一包"
            elif arr1 == '15':
                return 15, "程序更新失败"
            elif arr1 == '33':
                return 33, "写入失败"
            else:
                return 77, 77
        except :
            print("出现异常数据")



if __name__ == '__main__':
    con = Constant()
    con.checkout_custom(con.finish)
