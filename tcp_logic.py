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
        """
        功能函数，TCP服务端开启的方法
        :return: None
        """
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 取消主动断开连接四次握手后的TIME_WAIT状态
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 设定套接字为非阻塞式
        self.tcp_socket.setblocking(False)
        try:
            port = int(self.lineEdit_port.text())
            self.tcp_socket.bind(('', port))
        except Exception as ret:
            msg = '请检查端口号\n'
            self.signal_write_msg.emit(msg)
        else:
            self.tcp_socket.listen()
            self.sever_th = threading.Thread(target=self.tcp_server_concurrency)
            self.sever_th.start()
            msg = 'TCP服务端正在监听端口:%s\n' % str(port)
            self.signal_write_msg.emit(msg)

    def tcp_server_concurrency(self):
        """
        功能函数，供创建线程的方法；
        使用子线程用于监听并创建连接，使主线程可以继续运行，以免无响应
        使用非阻塞式并发用于接收客户端消息，减少系统资源浪费，使软件轻量化
        :return:None
        """
        while True:
            try:
                client_socket, client_address = self.tcp_socket.accept()
            except Exception as ret:
                pass
            else:
                client_socket.setblocking(False)
                # 将创建的客户端套接字存入列表,client_address为ip和端口的元组
                self.client_socket_list.append((client_socket, client_address))
                msg = 'TCP服务端已连接IP:%s端口:%s\n' % client_address
                self.signal_write_msg.emit(msg)
            # 轮询客户端套接字列表，接收数据
            for client, address in self.client_socket_list:
                try:
                    recv_msg = client.recv(1024)
                except Exception as ret:
                    pass
                else:
                    if recv_msg:
                        if len(recv_msg)<5:
                            return 
                        msg = recv_msg.decode('utf-8')
                        code, res = Constant.parse_receive(msg)
                        msg = '来自IP:{}端口:{}:\n{}\n{}'.format(address[0], address[1], msg, res)
                        print("-----------------")
                        self.signal_write_msg.emit(msg)
                        self.parse_code(code, res)
                    else:
                        client.close()
                        self.client_socket_list.remove((client, address))

    def parse_code(self, code, res):
        if code == 12:
            print(self.arrs[0])
            self.tcp_send(' '.join(self.arrs[self.flag]))
            self.flag += 1
        elif code == 34:
            if self.flag >= 43:
                self.tcp_send(str(Constant.finish))
                return
            print(self.arrs[0])
            self.tcp_send(' '.join(self.arrs[self.flag]))
            self.flag += 1
            if self.flag == 43:
                # 所有的包发送完毕并且成功发送需要发送一条告诉设备已经发送完毕的指令
                self.tcp_send(str(Constant.finish))
        elif code == 13:
            self.signal_write_msg.emit("第%d位数据包发送错误,正在重新发送....\n"%(res+1))
            self.tcp_send(' '.join(self.arrs[res]))
            # 数据包错误，并且第八位为错误的包序号,需要重复的包号
            self.signal_write_msg.emit("数据包已经重新发送\n")
        elif code == 33:
            self.signal_write_msg.emit('write is failed')
        elif code == 15:
            self.signal_write_msg.emit('update is failed')
        else:
            print("其他异常")
            self.show_message_error(code)

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
                Constant.parse_receive(self.msg)
            else:
                self.tcp_socket.close()
                self.reset()
                msg = '从服务器断开连接\n'
                self.signal_write_msg.emit(msg)
                break

    def tcp_send(self, data=None, init_code = None):
        """
        功能函数，用于TCP服务端和TCP客户端发送消息
        :return: None
        """
        send_msg = ""
        if self.link is False:
            msg = '请选择服务，并点击连接网络\n'
            self.signal_write_msg.emit(msg)
        else:
            try:
                if data == None:
                    send_msg = (str(self.textEdit_send.toPlainText())).encode('utf-8')
                else:
                    send_msg = bytes(data, encoding="utf8")
                if self.comboBox_tcp.currentIndex() == 0:
                    # 向所有连接的客户端发送消息
                    for client, address in self.client_socket_list:
                            # if init_code == None:
                            update = b'\xFF\xFF\x00\x27\x00\x00\x00\x00\x00\x00\x00\x00\x00\xEE\xEE\x28'
                            print("===", client)
                            print("===", address)
                            print(update)
                            client.send(update)
                            # binascii.b2a_hex(send_msg)
                            # print("----------", test)
                            # client.send(send_msg)
                    msg = 'TCP服务端已发送\n'
                    self.signal_write_msg.emit(msg)
                if self.comboBox_tcp.currentIndex() == 1:
                    self.tcp_socket.send(send_msg)
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
        file = open(filename, 'rb')
        i = 0
        arr = []
        m = 0
        while 1:
            if (i >= 1024):
                arr.insert(0, 'aa')
                arr.insert(0, 'aa')
                arr.insert(0, 'aa')
                arr.insert(3, '27')
                arr.insert(4, self.dec2hexstr(m))
                arr.append('ee')
                arr.append('ee')
                arr.append('ee')
                result = Constant.checkout_custom_long(arr[4:1029])
                # print("----------",result[2:4])
                arr.append(result[2:4])
                self.arrs.append(arr)
                arr = []
                i = 0
                m = m + 1

            c = file.read(1)
            # 将字节转换成16进制；
            ssss = str(binascii.b2a_hex(c))[2:-1]
            if ssss == '':
                self.show_message()
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


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = TcpLogic(1)
    ui.show()
    sys.exit(app.exec_())
