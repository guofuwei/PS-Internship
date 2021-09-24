import socket
import threading
import pymysql
import settings
import json
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

    def recv_msg(self):
        global clients_list
        while True:
            try:
                recv_data=self.client_socket.recv(1024).decode('utf-8')
                if recv_data:
                    send_data=recv_data
                    for client in clients_list:
                        client.send(send_data.encode('utf-8'))
            except:
                clients_list.pop(self.client_socket)
                self.client_socket.close()
                break

    def run(self):
        is_login=self.client_socket.recv(1024).decode('utf-8')
        if is_login=='LOGIN':
            json_obj=json.loads(self.client_socket.recv(1024))
            username=json_obj.get('username')
            password=json_obj.get('password')
            sql="select * from user_profile where username=%s and password=%s"
            try:
                cursor1.execute(sql,[username,password])
                data=cursor1.fetchone
                if data:
                    self.client_socket.send('OK'.encode('utf-8'))
                else:
                    self.client_socket.send('用户名或密码错误'.encode('utf-8'))
            except:
                pass
        elif is_login=='REGISTER':
            json_obj=json.loads(self.client_socket.recv(1024))
            username=json_obj.get('username')
            password1=json_obj.get('password1')
            password2=json_obj.get('password2')
            if not password1 or not password2 or not username:
                self.client_socket.send('某些字段为空，注册失败'.encode('utf-8'))
            elif password1!=password2:
                self.client_socket.send('两次密码不一致，注册失败'.encode('utf-8'))
            else:
                pass

            





def main():
    server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server_socket.bind(('',7788))
    server_socket.listen(128)
    global client_list



    while True:
        client_socket,client_addrs=server_socket.accept()
        clients_list.append(client_socket)
        client_handle=Client_Handle(client_socket)
    server_socket.close()


if __name__=='__main__':
    main()