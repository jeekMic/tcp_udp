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
        self.temm = 1
        self.client_socket_list = list()
        self.client_socket_lists = list()
        self.link = False  # 用于标记是否开启了连接
        self.limit = 0
        self.need_packet_id = 0
        self.pushButton_backup.clicked.connect(self.send_backup)
        self.pushButton_restart_remote.clicked.connect(self.restart)
        # 初始化的时候加载bin文件 存储在这个数组里面

    def restart(self):
        self.tcp_send(init_code=Constant.remote_restart)

    def send_backup(self):
        self.tcp_send(init_code=self.backup())

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
        print("开启服务器...............")
        if len(self.arrs) == 0:
            self.signal_write_msg.emit("【请加载bin文件,以免引起不必要的异常】\n")
            self.signal_write_msg.emit("【请加载bin文件,以免引起不必要的异常】\n")
            return
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
            self.tcp_socket.bind(('', port))  # 监测本地IP地址 和指定的端口号
        except Exception as ret:
            msg = '请检查端口号\n'
            self.signal_write_msg.emit(msg)

        else:
            print("服务器正在监听---------")
            self.link = True
            self.pushButton_unlink.setEnabled(True)
            self.pushButton_link.setEnabled(False)
            self.tcp_socket.listen()
            self.sever_th = threading.Thread(target=self.tcp_server_concurrency)
            self.sever_th.start()
            msg = 'TCP服务端正在监听端口:%s\n' % str(port)
            self.signal_write_msg.emit(msg)

    def tcp_server_concurrency(self):
        while True:
            clientsock, clientaddress = self.tcp_socket.accept()
            print('connect from:', clientaddress)
            msg = "【检测到 客户端 :" + str(clientaddress) + "已经连接】\n"

            self.set_port(clientaddress[1])
            self.signal_write_msg.emit(msg)
            self.client_socket_list.append(clientaddress)
            self.client_socket_lists.append((clientsock, clientaddress))
            self.detect_is_alive()
            # 传输数据都利用clientsock，和s无关
            t = threading.Thread(target=self.tcplink, args=(clientsock, clientaddress))  # t为新创建的线程
            t.start()

    def set_port(self, port):
        """
        :param port: 连接上的端口号
        :return: null
        """
        id = self.combox_port_select.count()
        self.combox_port_select.insertItem(id, str(port))

    def tcplink(self, sock, addr):
        result = []
        index = 0
        while True:
            if self.combox_port_select.currentText() == "all connections":
                index = 5000
            else:
                index = int(self.combox_port_select.currentText())
            if addr[1] == index:
                self.send_socket = sock
            try:
                recvdata = sock.recv(2048)
            except:
                print("socket 出现异常数据")
                sock.close()
                self.send_socket = None
                break
            result = []
            for i in recvdata:
                result.append(hex(i))
            if len(result) < 5:
                return
            self.signal_send_msg.emit(str(result) + "\n")
            self.signal_send_msg.emit("----------------------")

            code, res = Constant.parse_receive(result)
            msg = "收到远程发过来的数据,代号:"+str(code)+"\n"
            self.signal_write_msg.emit(msg)
            self.parse_code(code, res)
            if recvdata == 'exit' or not recvdata:
                break

            # clientsock.send(b' ')
        sock.close()
        self.send_socket = None

    def detect_is_alive(self):
        current = self.combox_port_select.currentText()
        temp = []
        temp_1 = []
        temp_num = []
        self.combox_port_select.clear()
        self.combox_port_select.insertItem(0, "all connections")
        for client, address in self.client_socket_lists:

            try:
                print("连接状态")
                temp.append((client, address))
                temp_1.append(address)
                temp_num.append(address[1])
            except:
                self.combox_port_select.clearEditText()
        self.client_socket_lists = []
        self.client_socket_lists = list(set(temp))
        temp_num = list(set(temp_num))
        for strss in temp_num:
            self.combox_port_select.insertItem(1, str(strss))
        self.combox_port_select.setCurrentText(current)

    def parse_code(self, code, res):
        if code == 12:
            # if self.flag >= self.total:
            #     self.tcp_send(data = str(Constant.finish))
            #     return
            self.tcp_send(data=''.join(self.arrs[self.flag]))
            num_str = "\n【已经发送第" + str(self.flag+1)+"包数据】\n"
            self.signal_write_msg.emit(num_str)
            self.flag += 1
            # if self.flag == self.total:
            #     # 所有的包发送完毕并且成功发送需要发送一条告诉设备已经发送完毕的指令
            #     self.tcp_send(data=str(Constant.finish))
        elif code == 14:
            print("-------------", self.flag, "-------", self.total)
            #self.progressBar.setValue((100 / 35) * self.flag)
            self.signal_progress_msg.emit((100 /(self.total+1)) * self.flag)
            if self.flag >= self.total:
                self.signal_write_msg.emit("【结束包正在发送......】\n")
                print("结束包正在发送---------\n")
                print(''.join(self.finish_all))
                self.tcp_send(data=''.join(self.finish_all))
                self.signal_write_msg.emit("【结束包发送成功---------】\n")
                print("结束包发送成功---------\n")
                return

            self.tcp_send(data=''.join(self.arrs[self.flag]))
            num_str = "\n【已经发送第" + str(self.flag+1)+"包数据】\n"
            self.signal_write_msg.emit(num_str)
            self.flag += 1
            # if self.flag == self.total:
            #     # 所有的包发送完毕并且成功发送需要发送一条告诉设备已经发送完毕的指令
            #     self.tcp_send(data = str(Constant.finish))
        elif code == 13:
            self.signal_write_msg.emit("【第%d包数据发送错误,正在重新发送....】\n" % (res + 1))
            self.tcp_send(data=''.join(self.arrs[res]))
        elif code == 33:
            self.signal_write_msg.emit('【写入错误】\n')
            # self.get_error(self.flag-1)
        elif code == 39:
            if res >= self.total - 1:
                self.signal_write_msg.emit("【远程程序发送命令错误，没有下一包数据可以发送了】")
                return
            if len(self.arrs) == 0:
                self.signal_write_msg.emit("【请先加载文件】")
                return
            self.flag = res + 1
            self.need_packet_id = self.flag

            if self.limit > 5:
                self.limit = 0
                self.signal_write_msg.emit('【我已经尽力了,更新失败】\n')
            else:
                print("发送的包序号", self.flag)
                self.tcp_send(data=''.join(self.arrs[self.flag]))
            self.limit += 1
        elif code == 15:
            self.signal_write_msg.emit('【更新失败】\n')
        elif code == 40:
            self.signal_write_msg.emit('【app源代码损坏,软件更新失败,请重置数据,或者选择恢复方式恢复】\n')
            self.set_visiable()
        elif code == 41:
            self.signal_write_msg.emit('【恢复成功】\n')
            self.set_visiable(is_visiable=1)
        elif code == 35:
            # 返回更新成功后需要初始化一些基本参数
            self.flag = 0
            self.limit = 0
            self.need_packet_id = 0
            self.flag = 0
            self.temm = 1
            self.signal_write_msg.emit(self.show_message_error(code))
            self.signal_progress_msg.emit(100)
        else:
            print("【位置异常,代号{}】".format(code))


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
                msg = '【TCP客户端已连接IP:%s端口:%s】\n' % address
                self.signal_write_msg.emit(msg)

    def get_error(self, error_id):
        if error_id < 100 and error_id > 0:
            return "更新数据第{}包发送有误".format(error_id + 1)
        if error_id == 0:
            return "初始请求更新数据失败"
        if error_id == 102:
            return "结束命令发送有误"
        if error_id >= self.total - 1:
            return "结束包发送有误"

    def tcp_client_concurrency(self, address):
        """
        功能函数，用于TCP客户端创建子线程的方法，阻塞式接收
        :return:
        """
        while True:
            recv_msg = self.tcp_socket.recv(1024)
            if recv_msg:
                msg = recv_msg.decode('utf-8')
                msg = '\n【来自IP:{}端口:{}:】\n'.format(address[0], address[1])
                self.signal_write_msg.emit(msg)
            else:
                self.tcp_socket.close()
                self.reset()
                msg = '【从服务器断开连接】\n'
                self.signal_write_msg.emit(msg)
                break

    # 重置界面上的数据文件,重新加载文件
    def reset_data(self):
        self.arrs = []
        self.finish_all = None
        self.flag = 0
        self.total = None
        self.signal_write_msg.emit("【恭喜您,数据已重置】\n")
        self.progressBar.setValue(0)
        temp = self.combox_port_select.currentText()
        self.combox_port_select.clear()
        self.combox_port_select.insertItem(0, temp)

    def tcp_send(self, data=None, init_code=None):
        arras = ''
        """
        功能函数，用于TCP服务端和TCP客户端发送消息
        :return: None
        """
        send_msg = None

        if self.link is False:
            msg = '【请选择服务，并点击连接网络】\n'
            self.signal_write_msg.emit(msg)
        elif len(self.arrs) == 0:
            self.signal_write_msg.emit("没有加载文件")
            self.show_error_for_loadfile()
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
                    print("--------------------发出的数据-----------------")
                    print(send_msg)
                if self.comboBox_tcp.currentIndex() == 0:
                    # 向所有连接的客户端发送消息
                    # for client, address in self.client_socket_list:
                    # if init_code == None:
                    # update = b'\xFF\xFF\x00\x27\x00\x00\x00\x00\x00\x00\x00\x00\x00\xEE\xEE\x28'
                    if self.flag > 1:
                        print(send_msg)
                    print("正在发送----------", self.flag)
                    self.send_socket.send(send_msg)
                    print("发送完成----------", self.flag)
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
            self.combox_port_select.clear()
            self.combox_port_select.insertItem(0, "all connections")
            try:

                for client, address in self.client_socket_lists:
                    client.close()
                self.tcp_socket.close()
                if self.link is True:
                    msg = '已断开网络\n'
                    self.signal_write_msg.emit(msg)
                self.combox_port_select.clear()
                self.combox_port_select.insertItem(0, "all connections")
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
        self.reset_data()
        length = int(os.path.getsize(filename) / 1024)
        if os.path.getsize(filename)/1024>length:
            length = length+1
        print("一共多少包:", length)
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
            if ssss == '':
                ssss = 'FF'
            arr.append(ssss)
            i += 1

        self.total = m
        print("总共有多少数据:----------")
        print(self.total)
        file.close()

    def get_str(self, arrss):
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
        print("*" * 50)
        return arrss

    def set_visiable(self, is_visiable=0):
        if is_visiable == 0:
            self.combobox_backup.setDisabled(False)
            self.pushButton_backup.setDisabled(False)
            self.pushButton_restart_remote.setDisabled(False)
        else:
            self.combobox_backup.setDisabled(True)
            self.pushButton_backup.setDisabled(True)
            self.pushButton_restart_remote.setDisabled(True)

    # 3A当写入失败的时候开启是从更新区恢复还是从备份区恢复
    def backup(self):
        init_code = None
        if self.combobox_backup.currentIndex() == 0:
            print("从更新区恢复命令已经发送")
            # 从更新区恢复
            init_code = Constant.from_update_recover

        elif self.combobox_backup.currentIndex() == 1:
            print("从备份区恢复命令已经发送")
            # 从备份区恢复
            init_code = Constant.update_from_backup

        else:
            self.signal_write_msg.emit("【调试助手出现异常】")
            return ""
        # self.combobox_backup.setDisabled(False)
        # self.pushButton_backup.setDisabled(False)
        return init_code


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = TcpLogic(1)
    ui.show()
    sys.exit(app.exec_())
