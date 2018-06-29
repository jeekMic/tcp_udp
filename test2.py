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
    # coding:utf-8
    import smtplib
    from email.mime.text import MIMEText  # 引入smtplib和MIMEText

    host = 'smtp.qq.com'  # 设置发件服务器地址
    port = 25  # 设置发件服务器端口号。注意，这里有SSL和非SSL两种形式
    sender = '1915224525@qq.com'  # 设置发件邮箱，一定要自己注册的邮箱
    pwd = '130613Qq'  # 设置发件邮箱的密码，等会登陆会用到
    receiver = '1306133728@qq.com'  # 设置邮件接收人，可以是扣扣邮箱
    body = '<h1>Hi</h1><p>test</p>'  # 设置邮件正文，这里是支持HTML的

    msg = MIMEText(body, 'html')  # 设置正文为符合邮件格式的HTML内容
    msg['subject'] = 'Hello world'  # 设置邮件标题
    msg['from'] = sender  # 设置发送人
    msg['to'] = receiver  # 设置接收人

    try:
        s = smtplib.SMTP(host, port)  # 注意！如果是使用SSL端口，这里就要改为SMTP_SSL
        s.login(sender, pwd)  # 登陆邮箱
        s.sendmail(sender, receiver, msg.as_string())  # 发送邮件！
        print('Done')
    except smtplib.SMTPException:
        print('Error')
