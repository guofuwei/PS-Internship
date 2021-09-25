import socket
import threading
import pymysql
import settings
import json
import hashlib


conn = pymysql.connect(
    host=settings.MYSQL_CONFIG['HOST'],
    user=settings.MYSQL_CONFIG['USER'],
    password=settings.MYSQL_CONFIG['PASSWORD'],
    database=settings.MYSQL_CONFIG['DATABASE'],)
cursor1=conn.cursor()
clients_list=[]

class Client_Handle():
    def __init__(self,client_socket):
        self.client_socket=client_socket

    def recvmsg_group_view(self):
        global clients_list
        while True:
            try:
                recv_data=self.client_socket.recv(1024).decode('utf-8')
                if recv_data=='EXIT':
                    pass
                elif recv_data:
                    send_data=recv_data
                    for client in clients_list:
                        client.send(send_data.encode('utf-8'))
            except:
                clients_list.pop(self.client_socket)
                self.client_socket.close()
                break

    def login_register_view(self):
        is_login=self.client_socket.recv(1024).decode('utf-8')
        if is_login=='LOGIN':
            json_obj=json.loads(self.client_socket.recv(1024).decode('utf-8'))
            username=json_obj.get('username')
            password=json_obj.get('password')
            p_m=hashlib.md5()
            p_m.update(password.encode())
            password_m=p_m.hexdigest()
            sql="select * from user_profile where username=%s and password=%s"
            try:
                cursor1.execute(sql,[username,password_m])
                data=cursor1.fetchone
                if data:
                    self.client_socket.send(json.dumps({'code':'OK','msg':username}).encode('utf-8'))
                else:
                    self.client_socket.send('用户名或密码错误'.encode('utf-8'))
            except:
                pass
        elif is_login=='REGISTER':
            json_obj=json.loads(self.client_socket.recv(1024).decode('utf-8'))
            username=json_obj.get('username')
            password1=json_obj.get('password1')
            password2=json_obj.get('password2')
            if not password1 or not password2 or not username:
                self.client_socket.send('某些字段为空，注册失败'.encode('utf-8'))
            elif password1!=password2:
                self.client_socket.send('两次密码不一致，注册失败'.encode('utf-8'))
            else:
                p_m=hashlib.md5()
                p_m.update(password1.encode())
                password_m=p_m.hexdigest()
                sql='''insert into user_profile(username,password) values(%s,%s)'''
                cursor1.execute(sql,[username,password_m])
                conn.commit()
                self.client_socket.send(json.dumps({'code':'OK','msg':username}).encode('utf-8'))

    def run(self):
        # 首先接受登录或注册的请求
        self.login_register_view()
        # 开始处理需要的业务请求
        view_flag=self.client_socket.recv(1024).decode('utf-8')
        if view_flag=='GROUP_CHAT':
            self.recvmsg_group_view()



def main():
    server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # 防止意外关闭导致端口被占无法开启
    # server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server_socket.bind(('',7788))
    server_socket.listen(128)
    global client_list



    while True:
        client_socket,client_addrs=server_socket.accept()
        clients_list.append(client_socket)
        client_handle=Client_Handle(client_socket)
        client_handle.run()
    server_socket.close()


if __name__=='__main__':
    main()