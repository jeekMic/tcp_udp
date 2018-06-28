import codecs
import os
from typing import Union

from PyQt5 import QtWidgets
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileDialog

import tcp_udp_web_ui
import socket
import threading
import sys
import stopThreading
from constant import Constant
import binascii
import struct


class TcpLogic(tcp_udp_web_ui.ToolsUi):
    def __init__(self, num):
        super(TcpLogic, self).__init__(num)
        self.finish_all = None
        self.total = None
        self.send_socket = None
        self.tcp_socket = None
        self.sever_th = None
        self.client_th = None
        self.flag = 0
        self.arrs = []
        self.client_socket_list = list()
        self.link = False  # 用于标记是否开启了连接
        # 初始化的时候加载bin文件 存储在这个数组里面

    # 选择bin文件
    def getfiles(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setFilter(QDir.Files)

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            print(filenames)
            f = open(filenames[0], 'r')

            with f:
                data = f.read()
                self.contents.setText(data)

    def tcp_server_start(self):
        print("-----开启服务器-----------")
        """
        功能函数，TCP服务端开启的方法
        :return: None
        """
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # # 取消主动断开连接四次握手后的TIME_WAIT状态
        # self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 50)
        # # 设定套接字为非阻塞式
        # self.tcp_socket.setblocking(False)
        try:
            port = int(self.lineEdit_port.text())
            self.tcp_socket.bind(('', port))
        except Exception as ret:
            msg = '请检查端口号\n'
            self.signal_write_msg.emit(msg)
        else:
            print("服务器正在监听---------")
            self.tcp_socket.listen()
            self.sever_th = threading.Thread(target=self.tcp_server_concurrency)
            self.sever_th.start()
            msg = 'TCP服务端正在监听端口:%s\n' % str(port)
            self.signal_write_msg.emit(msg)

    def tcp_server_concurrency(self):
        while True:
            clientsock, clientaddress = self.tcp_socket.accept()
            print('connect from:', clientaddress)
            msg = "检测到 客户端 :" + str(clientaddress) + "已经连接\n"
            self.signal_write_msg.emit(msg)
            # self.client_socket_list.append((clientsock, clientaddress))
            # 传输数据都利用clientsock，和s无关
            t = threading.Thread(target=self.tcplink, args=(clientsock, clientaddress))  # t为新创建的线程
            t.start()

    def tcplink(self, sock, addr):
        result = []
        while True:
            print("------1")
            if addr[1] == 5000:
                self.send_socket = sock

            recvdata = sock.recv(2048)
            result = []
            for i in recvdata:
                result.append(hex(i))
            if len(result) < 5:
                return
            code, res = Constant.parse_receive(result)
            msg = '来自IP:{}端口:{}:\n{}\n{}'.format(addr[0], addr[1], recvdata, res)
            self.signal_write_msg.emit(msg)
            self.parse_code(code, res)
            if recvdata == 'exit' or not recvdata:
                break

            # clientsock.send(b' ')
        sock.close()
        self.send_socket = None

    def parse_code(self, code, res):
        if code == 12:
            # if self.flag >= self.total:
            #     self.tcp_send(data = str(Constant.finish))
            #     return
            self.tcp_send(data=''.join(self.arrs[self.flag]))
            num_str = "已经发送数据包" + str(self.flag)
            self.signal_write_msg.emit(num_str)
            self.flag += 1
            # if self.flag == self.total:
            #     # 所有的包发送完毕并且成功发送需要发送一条告诉设备已经发送完毕的指令
            #     self.tcp_send(data=str(Constant.finish))
        elif code == 14:
            print("-------------", self.flag, "-------", self.total)
            if self.flag >=self.total:
                self.signal_write_msg.emit("结束包正在发送---------\n")
                print("结束包正在发送---------\n")
                print(''.join(self.finish_all))
                self.tcp_send(data=''.join(self.finish_all))
                self.signal_write_msg.emit("结束包发送成功---------\n")
                print("结束包发送成功---------\n")
                return

            self.tcp_send(data=''.join(self.arrs[self.flag]))
            num_str = "已经发送数据包" + str(self.flag)+"\n"
            self.signal_write_msg.emit(num_str)
            self.flag += 1
            # if self.flag == self.total:
            #     # 所有的包发送完毕并且成功发送需要发送一条告诉设备已经发送完毕的指令
            #     self.tcp_send(data = str(Constant.finish))
        elif code == 13:
            self.signal_write_msg.emit("第%d位数据包发送错误,正在重新发送....\n" % (res + 1))
            self.tcp_send(data=' '.join(self.arrs[res]))
            # 数据包错误，并且第八位为错误的包序号,需要重复的包号
            self.signal_write_msg.emit("数据包已经重新发送\n")
        elif code == 33:
            self.signal_write_msg.emit('write is failed\n')
        elif code == 15:
            self.signal_write_msg.emit('update is failed\n')
        else:
            print("-------------------其他异常")
            print(code)
            self.signal_write_msg.emit(self.show_message_error(code))

    def tcp_client_start(self):
        """
        功能函数，TCP客户端连接其他服务端的方法
        :return:
        """
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            address = (str(self.lineEdit_ip_send.text()), int(self.lineEdit_port.text()))
        except Exception as ret:
            msg = '请检查目标IP，目标端口\n'
            self.signal_write_msg.emit(msg)
        else:
            try:
                msg = '正在连接目标服务器\n'
                self.signal_write_msg.emit(msg)
                self.tcp_socket.connect(address)
            except Exception as ret:
                msg = '无法连接目标服务器\n'
                self.signal_write_msg.emit(msg)
            else:
                self.client_th = threading.Thread(target=self.tcp_client_concurrency, args=(address,))
                self.client_th.start()
                msg = 'TCP客户端已连接IP:%s端口:%s\n' % address
                self.signal_write_msg.emit(msg)

    def tcp_client_concurrency(self, address):
        """
        功能函数，用于TCP客户端创建子线程的方法，阻塞式接收
        :return:
        """
        while True:
            recv_msg = self.tcp_socket.recv(1024)
            if recv_msg:
                msg = recv_msg.decode('utf-8')
                msg = '来自IP:{}端口:{}:\n{}\n'.format(address[0], address[1], msg)
                self.signal_write_msg.emit(msg)
                Constant.parse_receive(msg)
            else:
                self.tcp_socket.close()
                self.reset()
                msg = '从服务器断开连接\n'
                self.signal_write_msg.emit(msg)
                break

    def tcp_send(self, data=None, init_code=None):
        arras = ''
        """
        功能函数，用于TCP服务端和TCP客户端发送消息
        :return: None
        """
        send_msg = None
        if self.link is False:
            msg = '请选择服务，并点击连接网络\n'
            self.signal_write_msg.emit(msg)
        else:
            try:
                if init_code is not None:
                    send_msg = init_code
                    print("-------------------需要的发送格式要求-----------------------")
                    print(send_msg)
                    print(type(send_msg))
                elif data is None:
                    send_msg = (str(self.textEdit_send.toPlainText())).encode('utf-8')
                else:
                    # send_msg = bytes(data, encoding="utf8")
                    # print("--------------2数据的长度为：", len(data))
                    if len(data) == 2065:
                        arras = data[:2064] + '0' + data[-1]
                        send_msg = codecs.decode(arras, 'hex_codec')
                    else:
                        send_msg = codecs.decode(data, 'hex_codec')
                    # temp_send = b""
                    # for i in send_msg:
                    #     temp_send +=i
                    # send_msg = temp_send
                if self.comboBox_tcp.currentIndex() == 0:
                    # 向所有连接的客户端发送消息
                    # for client, address in self.client_socket_list:
                    # if init_code == None:
                    # update = b'\xFF\xFF\x00\x27\x00\x00\x00\x00\x00\x00\x00\x00\x00\xEE\xEE\x28'
                    if self.flag >1:
                        print(send_msg)
                    print("正在发送----------",self.flag)
                    self.send_socket.send(send_msg)
                    print("发送完成----------",self.flag)
                    msg = 'TCP服务端已发送\n'
                    self.signal_write_msg.emit(msg)
                if self.comboBox_tcp.currentIndex() == 1:
                    self.send_socket.send(send_msg)
                    print("-----发送")
                    msg = 'TCP客户端已发送\n'
                    self.signal_write_msg.emit(msg)
            except Exception as ret:
                msg = '发送失败\n'
                self.signal_write_msg.emit(msg)

    def tcp_close(self):
        """
        功能函数，关闭网络连接的方法
        :return:
        """
        if self.comboBox_tcp.currentIndex() == 0:
            try:
                for client, address in self.client_socket_list:
                    client.close()
                self.tcp_socket.close()
                if self.link is True:
                    msg = '已断开网络\n'
                    self.signal_write_msg.emit(msg)
            except Exception as ret:
                pass
        if self.comboBox_tcp.currentIndex() == 1:
            try:
                self.tcp_socket.close()
                if self.link is True:
                    msg = '已断开网络\n'
                    self.signal_write_msg.emit(msg)
            except Exception as ret:
                pass
        try:
            stopThreading.stop_thread(self.sever_th)
        except Exception:
            pass
        try:
            stopThreading.stop_thread(self.client_th)
        except Exception:
            pass

    # ------------------------bin文件解析--------------------
    def dec2hexstr(self, n):
        ss = str(hex(n))
        ss = ss[2:]
        if n <= 15:
            ss = '0' + ss
        return ss

    # crc校验
    def uchar_checksum(self, data, byteorder='little'):
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

    def read_bin(self, filename):
        length = int(os.path.getsize(filename) / 1024 + 0.5)
        file = open(filename, 'rb')
        i = 0
        arr = []
        m = 0
        # 初始结束命令
        zero = Constant.get_finish0('a')
        self.finish_all = self.get_str(zero)
        while 1:

            if i >= 1024:
                print(length)
                print(m)
                arr.insert(0, 'aa')
                arr.insert(0, 'aa')
                arr.insert(0, 'aa')
                arr.insert(3, '27')
                arr.insert(4, self.dec2hexstr(m))
                arr.append('ee')
                arr.append('ee')
                arr.append('ee')
                result = Constant.checkout_custom_long(arr[3:1029])
                arr.append(result[2:4])
                self.arrs.append(arr)
                print(arr)
                arr = []
                m = m + 1
                i = 0
            if m == length:
                self.show_message()
                break

            c = file.read(1)

            ssss = str(binascii.b2a_hex(c))[2:-1]
            if ssss=='':
                ssss = 'FF'
            arr.append(ssss)
            i += 1



        self.total = m
        file.close()
    def get_str(self,arrss):
        arrss.insert(0, 'aa')
        arrss.insert(0, 'aa')
        arrss.insert(0, 'aa')
        arrss.insert(3, '28')
        arrss.insert(4, self.dec2hexstr(0))
        arrss.append('ee')
        arrss.append('ee')
        arrss.append('ee')
        result = Constant.checkout_custom_long(arrss[3:1029])
        arrss.append(result[2:4])
        print(arrss)
        print("*"*50)
        return arrss


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = TcpLogic(1)
    ui.show()
    sys.exit(app.exec_())
