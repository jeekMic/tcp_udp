import sys
import threading
import time

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication
from qtpy import QtWidgets

from constant import Constant
from scan import Ui_Dialog

from socket import *
from time import sleep
class MyDialog(Ui_Dialog):

    def __init__(self):
        super(MyDialog, self).__init__()
        self.setupUi(self)
        self.lineEdit.setText("192.168.1.1")
        self.label.setText("本机IP:")
        self.logic()
        self.changeUi.connect(self.change_str)
        self.udpCliSock = None
    def change_str(self,message):
        self.label_2.setText("设备IP地址: %s" % message)
        print(message)
        self.progressBar.setValue(100)



    def logic(self):
        self.pushButton.clicked.connect(self.close)
        self.pushButton_2.clicked.connect(self.scan)
        self.pushButton_3.clicked.connect(self.cancel)

    def run(self, udpCliSock):
        print("-----1")
        data, address = udpCliSock.recvfrom(1024)
        self.changeUi.emit("数据: "+str(data)+"\n"+str(address[0]))
        self.udpCliSock.close()
        print("-----2")
    def scan(self):
        try:
            print("开始扫描")
            self.label_2.setText("正在搜索.....")
            HOST = '<broadcast>'
            PORT = 5002
            BUFSIZE = 1024
            ADDR = (HOST, PORT)
            self.udpCliSock = socket(AF_INET, SOCK_DGRAM)
            print("==========")
            self.udpCliSock.bind((self.lineEdit.text(), 6000))
            self.udpCliSock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

            print("sending -> %s" % Constant.sea_ip)
            self.progressBar.setValue(50)
            self.udpCliSock.sendto(Constant.sea_ip, ADDR)

            t = threading.Thread(target=self.run, args=(self.udpCliSock,))
            t.start()
        except :
            self.udpCliSock.close()
            print("地址出现错误")

    def cancel(self):
        self.progressBar.setValue(0)

        self.label_2.setText("搜索已取消")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    btnDemo = MyDialog()
    btnDemo.show()
    sys.exit(app.exec_())
