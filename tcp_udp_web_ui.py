from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDialog, QHBoxLayout, QVBoxLayout, QMessageBox
import sys


class ToolsUi(QDialog):
    # 信号槽机制：设置一个信号，用于触发接收区写入动作
    signal_write_msg = QtCore.pyqtSignal(str)
    # 信号槽进制:设置一个信号,用于触发发送区的写入动作
    signal_send_msg = QtCore.pyqtSignal(str)

    # 信号槽进制:设置一个信号,用于触发进度条机制
    signal_progress_msg = QtCore.pyqtSignal(int)

    def __init__(self, num):
        """
        初始化窗口
        :param num: 计数窗口
        """
        super(ToolsUi, self).__init__()
        self.num = num
        self._translate = QtCore.QCoreApplication.translate
        self.setWindowIcon(QIcon("image/b.png"))
        self.setObjectName("TCP-UDP")
        self.resize(640, 480)
        self.setAcceptDrops(False)
        self.setSizeGripEnabled(False)

        # 定义控件
        self.pushButton_get_ip = QtWidgets.QPushButton()
        self.pushButton_link = QtWidgets.QPushButton()
        self.pushButton_unlink = QtWidgets.QPushButton()
        self.pushButton_clear = QtWidgets.QPushButton()
        self.pushButton_exit = QtWidgets.QPushButton()
        self.pushButton_send = QtWidgets.QPushButton()
        self.pushButton_dir = QtWidgets.QPushButton()
        self.pushButton_else = QtWidgets.QPushButton()
        self.pushButton_reset_all = QtWidgets.QPushButton()
        self.label_port = QtWidgets.QLabel()
        self.label_ip = QtWidgets.QLabel()
        self.label_rev = QtWidgets.QLabel()
        self.label_send = QtWidgets.QLabel()
        self.label_sendto = QtWidgets.QLabel()
        self.label_dir = QtWidgets.QLabel()
        self.label_written = QtWidgets.QPushButton()
        self.lineEdit_port = QtWidgets.QLineEdit()
        self.lineEdit_ip_send = QtWidgets.QLineEdit()
        self.lineEdit_ip_local = QtWidgets.QLineEdit()
        self.textEdit_send = QtWidgets.QTextEdit()
        self.textBrowser_recv = QtWidgets.QTextBrowser()
        self.comboBox_tcp = QtWidgets.QComboBox()
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setGeometry(QtCore.QRect())
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        # 从备份区恢复和从更新区恢复
        self.combobox_backup = QtWidgets.QComboBox()
        self.pushButton_backup = QtWidgets.QPushButton()
        self.pushButton_restart_remote = QtWidgets.QPushButton()

        self.label_port_select = QtWidgets.QLabel()
        self.label_port_select.setText("  端口选择:")
        self.combox_port_select = QtWidgets.QComboBox()
        self.combox_port_select.setMaxVisibleItems(5)
        self.combox_port_select.setMaxCount(10)

        # 定义布局
        self.h_box_1 = QHBoxLayout()
        self.h_box_2 = QHBoxLayout()
        self.h_box_3 = QHBoxLayout()
        self.h_box_4 = QHBoxLayout()
        self.h_box_5 = QHBoxLayout()
        self.h_box_6 = QHBoxLayout()
        self.h_box_recv = QHBoxLayout()
        self.h_box_exit = QHBoxLayout()
        self.h_box_all = QHBoxLayout()
        self.v_box_set = QVBoxLayout()
        self.v_box_send = QVBoxLayout()
        self.v_box_web = QVBoxLayout()
        self.v_box_exit = QVBoxLayout()
        self.v_box_bootom_left = QVBoxLayout()
        self.v_box_right = QVBoxLayout()
        self.v_box_left = QVBoxLayout()

        # 向选择功能的下拉菜单添加选项
        self.comboBox_tcp.addItem("")
        self.comboBox_tcp.addItem("")
        self.comboBox_tcp.addItem("")
        self.comboBox_tcp.addItem("")
        self.combobox_backup.addItem("")
        self.combobox_backup.addItem("")
        self.combobox_backup.setDisabled(True)
        self.pushButton_backup.setDisabled(True)
        self.pushButton_restart_remote.setDisabled(False)

        self.combox_port_select.insertItem(0, "all connections")
        # self.comboBox_tcp.addItem("")

        # 设置字体
        font = QtGui.QFont()
        font.setFamily("Yuppy TC")
        font.setPointSize(20)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.label_rev.setFont(font)
        self.label_send.setFont(font)

        # 设置控件的初始属性
        self.label_dir.hide()
        self.label_sendto.hide()
        self.pushButton_dir.hide()
        self.lineEdit_ip_send.hide()
        self.label_dir.setWordWrap(True)  # 让label自动换行
        self.pushButton_unlink.setEnabled(False)
        self.textBrowser_recv.insertPlainText("提示:【请先加载bin文件,以免引起不必要的异常】\n")
        self.textBrowser_recv.insertPlainText("\n")
        self.lineEdit_port.setText(str(6000))
        # 调用布局方法和控件显示文字的方法
        self.layout_ui()
        self.ui_translate()
        self.connect()

    def show_message(self):
        QMessageBox.information(self, "提示", "文件加载成功",
                                QMessageBox.Yes)

    def show_error_for_loadfile(self):
        QMessageBox.information(self, "提示", "大哥,你没有加载文件",
                                QMessageBox.Yes)

    def show_message_error(self, error_id):
        message = "未知异常"
        try:
            if error_id == 32:
                message = "擦除备份区失败"
                pass
            elif error_id == 37:
                message = "备份失败"
                pass
            elif error_id == 30:
                message = "擦除源码区失败"
                pass
            elif error_id == 36:
                message = "更新区代码复制到源码区失败"
            elif error_id == 38:
                message = "恢复失败,错误代码38"
                pass
            elif error_id == 31:
                message = "擦除失败31"
            elif error_id == 35:
                message = "恭喜您! 程序执行完毕！设备更新正常"
                pass
            return message
        except:
            return "储蓄出现异常"

    def layout_ui(self):
        """
        设置控件的布局
        :return:
        """
        # 左侧布局添加
        self.h_box_1.addWidget(self.label_ip)
        self.h_box_1.addWidget(self.lineEdit_ip_local)
        self.h_box_1.addWidget(self.pushButton_get_ip)
        self.h_box_2.addWidget(self.label_port)
        self.h_box_2.addWidget(self.lineEdit_port)
        self.h_box_2.addWidget(self.pushButton_else)
        self.h_box_3.addWidget(self.label_sendto)
        self.h_box_3.addWidget(self.lineEdit_ip_send)
        self.h_box_4.addWidget(self.comboBox_tcp)
        self.h_box_4.addWidget(self.pushButton_link)
        self.h_box_4.addWidget(self.pushButton_unlink)
        self.v_box_set.addLayout(self.h_box_1)
        self.v_box_set.addLayout(self.h_box_2)
        self.v_box_set.addLayout(self.h_box_3)
        self.v_box_set.addLayout(self.h_box_4)
        self.v_box_web.addWidget(self.label_dir)
        self.v_box_web.addWidget(self.pushButton_dir)
        # self.v_box_send.addWidget(self.label_send)
        self.h_box_5.addWidget(self.label_send)

        self.h_box_5.addWidget(self.label_port_select)
        self.h_box_5.addWidget(self.combox_port_select)
        self.h_box_6.addWidget(self.combobox_backup)
        self.h_box_6.addWidget(self.pushButton_backup)
        self.h_box_6.addWidget(self.pushButton_restart_remote)
        self.v_box_send.addLayout(self.h_box_5)
        self.v_box_send.addWidget(self.textEdit_send)
        self.v_box_send.addLayout(self.v_box_web)
        self.v_box_exit.addWidget(self.pushButton_send)
        self.v_box_exit.addWidget(self.pushButton_exit)
        self.v_box_bootom_left.addWidget(self.pushButton_reset_all)
        self.v_box_bootom_left.addWidget(self.label_written)
        self.h_box_exit.addLayout(self.v_box_bootom_left)
        self.h_box_exit.addLayout(self.v_box_exit)
        self.v_box_left.addLayout(self.v_box_set)
        self.v_box_left.addLayout(self.v_box_send)
        self.v_box_left.addLayout(self.h_box_exit)

        # 右侧布局添加
        self.h_box_recv.addWidget(self.label_rev)
        self.h_box_recv.addWidget(self.pushButton_clear)
        self.v_box_right.addLayout(self.h_box_recv)

        self.v_box_right.addWidget(self.textBrowser_recv)
        self.v_box_right.addWidget(self.progressBar)
        self.v_box_right.addLayout(self.h_box_6)

        # 将左右布局添加到窗体布局
        self.h_box_all.addLayout(self.v_box_left)
        self.h_box_all.addLayout(self.v_box_right)

        # 设置窗体布局到窗体
        self.setLayout(self.h_box_all)

    def ui_translate(self):
        """
        控件默认显示文字的设置
        :param : QDialog类创建的对象
        :return: None
        """
        # 设置各个控件显示的文字
        # 也可使用控件的setText()方法设置文字
        self.setWindowTitle(self._translate("TCP-UDP", "TCP/UDP网络测试工具-窗口%s" % self.num))
        self.comboBox_tcp.setItemText(0, self._translate("TCP-UDP", "TCP服务端"))
        self.comboBox_tcp.setItemText(1, self._translate("TCP-UDP", "TCP客户端"))
        self.comboBox_tcp.setItemText(2, self._translate("TCP-UDP", "UDP服务端"))
        self.comboBox_tcp.setItemText(3, self._translate("TCP-UDP", "UDP客户端"))
        self.combobox_backup.setItemText(0, self._translate("TCP-UDP", "从更新区更新"))
        self.combobox_backup.setItemText(1, self._translate("TCP-UDP", "从备份区更新"))
        self.pushButton_restart_remote.setText(self._translate("TCP-UDP", "远程重启"))
        # self.comboBox_tcp.setItemText(4, self._translate("TCP-UDP", "WEB服务端"))
        self.pushButton_link.setText(self._translate("TCP-UDP", "连接网络"))
        self.pushButton_unlink.setText(self._translate("TCP-UDP", "断开网络"))
        self.pushButton_get_ip.setText(self._translate("TCP-UDP", "开始更新"))
        self.pushButton_clear.setText(self._translate("TCP-UDP", "清除消息"))
        self.pushButton_send.setText(self._translate("TCP-UDP", "发送"))
        self.pushButton_exit.setText(self._translate("TCP-UDP", "退出系统"))
        self.pushButton_dir.setText(self._translate("TCP-UDP", "选择路径"))
        self.pushButton_else.setText(self._translate("TCP-UDP", "窗口多开"))
        self.label_ip.setText(self._translate("TCP-UDP", "本机IP:"))
        self.label_port.setText(self._translate("TCP-UDP", "端口号:"))
        self.label_sendto.setText(self._translate("TCP-UDP", "目标IP:"))
        self.label_rev.setText(self._translate("TCP-UDP", "接收区域"))
        self.label_send.setText(self._translate("TCP-UDP", "发送区域"))
        self.label_dir.setText(self._translate("TCP-UDP", "请选择index.html所在的文件夹"))
        self.label_written.setText(self._translate("TCP-UDP", "加载文件"))
        self.pushButton_reset_all.setText(self._translate("TCP-UDP", "重置"))
        self.pushButton_backup.setText(self._translate("TCP-UDP", "恢复"))

    def connect(self):
        """
        控件信号-槽的设置
        :param : QDialog类创建的对象
        :return: None
        """
        self.signal_write_msg.connect(self.write_msg)
        self.signal_send_msg.connect(self.send_msg)
        self.comboBox_tcp.currentIndexChanged.connect(self.combobox_change)
        self.signal_progress_msg.connect(self.change_progress)

    def change_progress(self, int_pro):
        self.progressBar.setValue(int_pro)

    def combobox_change(self):
        # 此函数用于选择不同功能时界面会作出相应变化
        """
        combobox控件内容改变时触发的槽
        :return: None
        """
        self.close_all()
        if self.comboBox_tcp.currentIndex() == 0 or self.comboBox_tcp.currentIndex() == 2:
            self.label_sendto.hide()
            self.label_dir.hide()
            self.pushButton_dir.hide()
            self.pushButton_send.show()
            self.lineEdit_ip_send.hide()
            self.textEdit_send.show()
            self.label_port.setText(self._translate("TCP-UDP", "端口号:"))

        if self.comboBox_tcp.currentIndex() == 1 or self.comboBox_tcp.currentIndex() == 3:
            self.label_sendto.show()
            self.label_dir.hide()
            self.pushButton_dir.hide()
            self.pushButton_send.show()
            self.lineEdit_ip_send.show()
            self.textEdit_send.show()
            self.label_port.setText(self._translate("TCP-UDP", "目标端口:"))

        if self.comboBox_tcp.currentIndex() == 4:
            self.label_sendto.hide()
            self.label_dir.show()
            self.pushButton_dir.show()
            self.pushButton_send.hide()
            self.lineEdit_ip_send.hide()
            self.textEdit_send.hide()
            self.label_port.setText(self._translate("TCP-UDP", "端口号:"))

    def write_msg(self, msg):
        # signal_write_msg信号会触发这个函数
        """
        功能函数，向接收区写入数据的方法
        信号-槽触发
        tip：PyQt程序的子线程中，直接向主线程的界面传输字符是不符合安全原则的
        :return: None
        """
        self.textBrowser_recv.insertPlainText(msg)
        # 滚动条移动到结尾
        self.textBrowser_recv.moveCursor(QtGui.QTextCursor.End)

    def send_msg(self, send_msg):
        '''
        功能函数,上位机在通过网口发送数据的时候将数据呈现在界面上
        :return:
        '''
        self.textEdit_send.insertPlainText(send_msg)

    def closeEvent(self, event):
        """
        重写closeEvent方法，实现dialog窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """
        self.close_all()

    def close_all(self):
        pass


if __name__ == '__main__':
    """
    显示界面
    """
    app = QApplication(sys.argv)
    ui = ToolsUi(1)
    ui.show()
    sys.exit(app.exec_())
