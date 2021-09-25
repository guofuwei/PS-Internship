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
    
    def send_msg(self,username):
        while True:
            send_data=input(username+':')
            if send_data=='EXIT':
                self.theclient_socket.send('EXIT'.encode('utf-8'))
                break
            self.theclient_socket.send(username+':'+send_data.encode('utf-8'))

    def recv_msg(self,username):
        while True:
            try:
                recv_data=self.theclient_socket.recv(1024).decode('utf-8')
                print('\r'+recv_data)
                print(username+':')
            except:
                break

    def login(self):
        servertype=int(input('请选择注册还是登录(登录:1,注册:2):'))
        if servertype==1:
            self.theclient_socket.send('LOGIN'.encode('utf-8'))
            print('现在您正在登录')
            username=input('请输入您的用户名:')
            password=input('请输入您的密码:')
            self.theclient_socket.send(json.dumps({'username':username,'password':password}).encode('utf-8'))
            recv_flag=json.loads(self.theclient_socket.recv(1024).decode('utf-8'))
            if recv_flag.get('code')=='OK':
                print('登录成功!')
                return recv_flag
            else:
                print(recv_flag)
                time.sleep(1)
                os.system('cls')

        elif servertype==2:
            self.theclient_socket.send('REGISTER'.encode('utf-8'))
            print('现在为您注册一个新用户')
            username=input('请输入您的用户名:')
            password1=input('请输入您的密码:')
            password2=input('请再次输入您的密码:')
            self.theclient_socket.send(json.dumps({'username':username,'password1':password1,
            'password2':password2}).encode('utf-8'))
            recv_flag=json.loads(self.theclient_socket.recv(1024).decode('utf-8'))
            if recv_flag.get('code')=='OK':
                print('注册成功!')
                return recv_flag
            else:
                print(recv_flag)
                time.sleep(1)
                os.system('cls')

    def run(self):
        print('*****欢迎来到网络聊天室v1.0*****')
        while True:
            print('您还未登录，请先登录!')
            flag=self.login()
            if flag.get('code')=='OK':
                username=flag.get('msg')
                break
        # print(flag)
        # print(username)
        print('*******您已经进入菜单界面*******')
        print('请选择您要求的服务类型:')
        print('输入1：进入公共聊天室')
        print('输入0:提出程序')

        servernum=int(input('请输入选择的功能:'))
        if servernum==0:exit()
        elif servernum==1:
            self.theclient_socket.send('GROUP_CHAT'.encode('utf-8'))
            os.system('cls')
            print('*****您已成功进入公共聊天室*****')
            print('*****输入EXIT退出*****')
            t1=threading.Thread(target=self.recv_msg,args=(username,))
            t2=threading.Thread(target=self.send_msg,args=(username,))
            t1.start()
            t2.start()



def main():
    client=Client()
    client.run()

if __name__=='__main__':
    main()

