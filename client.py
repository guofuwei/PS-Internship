import socket
import threading
import json
import os
import time

class Client():
    def __init__(self):
        theclient_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        theclient_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        server_ip='127.0.0.1'
        server_port=int('7788')
        theclient_socket.connect((server_ip,server_port))
        self.theclient_socket=theclient_socket
    
    def send_msg(self):
        while True:
            send_data=input('')
            if send_data=='EXIT':
                self.theclient_socket.close()
                break
            self.theclient_socket.send(send_data.encode('utf-8'))

    def recv_msg(self):
        while True:
            try:
                recv_data=self.theclient_socket.recv(1024)
                print(recv_data.decode('utf-8'))
            except:
                break

    def login(self):
        servertype=int(input('请选择注册还是登录(登录:1,注册:2):'))
        if servertype==1:
            username='',password=''
            self.theclient_socket.send('LOGIN'.encode('utf-8'))
            print('现在您正在登录')
            print('请输入您的用户名:%s' %username)
            print('请输入您的密码:%s' %password)
            self.theclient_socket.send(json.dumps({'username':username,'password':password}))
            recv_flag=self.theclient_socket.recv(1024).decode('utf-8')
            if recv_flag=='OK':
                print('登录成功!')
                return 'OK'
            else:
                print(recv_flag)
                time.sleep(1)
                os.system('cls')

        elif servertype==2:
            username='',password1='',password2=''
            self.theclient_socket.send('REGISTER'.encode('utf-8'))
            print('现在为您注册一个新用户')
            print('请输入您的用户名:%s' %username)
            print('请输入您的密码:%s' %password1)
            print('请再次输入您的密码:%s' %password2)
            self.theclient_socket.send(json.dumps({'username':username,'password1':password1,
            'password2':password2}))
            recv_flag=self.theclient_socket.recv(1024).decode('utf-8')
            if recv_flag=='OK':
                print('注册成功!')
                return 'OK'
            else:
                print(recv_flag)
                time.sleep(1)
                os.system('cls')

    def run(self):
        while True:
            print('您还未登录，请先登录!')
            flag=self.login()
            if flag=='OK':
                break
        print('*******您已经进入菜单界面*******')
        print('请选择您要求的服务类型:')
        print('输入1：进入公告聊天室')

        servernum=int(input('请输入选择的功能:'))
        if servernum==1:
            os.system('cls')
            print('*****您已成功进入公共聊天室*****')
            print('*****输入EXIT退出*****')
            t1=threading.Thread(target=self.recv_msg)
            t2=threading.Thread(target=self.send_msg)
            t1.start()
            t2.start()



def main():
    client=Client()
    client.run()

if __name__=='__main__':
    main()

