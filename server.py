import socket
import threading
import pymysql
import settings
import json
import hashlib
import datetime


conn = pymysql.connect(
    host=settings.MYSQL_CONFIG['HOST'],
    user=settings.MYSQL_CONFIG['USER'],
    password=settings.MYSQL_CONFIG['PASSWORD'],
    database=settings.MYSQL_CONFIG['DATABASE'],)
cursor1=conn.cursor()
group_client=[]
username_list=[]

class Client_Handle():
    def __init__(self,client_socket):
        self.client_socket=client_socket

    def recvmsg_group_view(self):
        global group_client
        group_client.append(self.client_socket)
        print('len is %s' %len(group_client))
        while True:
            try:
                recv_data=self.client_socket.recv(1024).decode('utf-8')
                if recv_data=='EXIT':
                    send_data=self.username+'已退出群聊聊天室'
                    for client in group_client:
                        client.send(send_data.encode('utf-8'))
                    group_client.remove(self.client_socket)
                    print('len is %s' %len(group_client))
                    break
                elif recv_data:
                    # 群聊记录的存储
                    nowtime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    sql='''insert into group_msg(create_time,content) values(%s,%s)'''
                    cursor1.execute(sql,[nowtime,recv_data])
                    conn.commit()
                    # 群发消息
                    send_data=recv_data
                    for client in group_client:
                        if client!=self.client_socket:
                            client.send(send_data.encode('utf-8'))
            except:
                group_client.remove(self.client_socket)
                print('len is %s' %len(group_client))
                break

    def login_view(self):
        global username_list
        # 拿取参数
        json_obj=json.loads(self.client_socket.recv(1024).decode('utf-8'))
        username=json_obj.get('username')
        password=json_obj.get('password')
        # print(username,password)
        # 校验参数
        if not username or not password:
            self.client_socket.send(json.dumps({'code':10100,'msg':'用户名或密码为空'}).encode('utf-8'))
        elif username_list.count(username):
            self.client_socket.send(json.dumps({'code':10105,'msg':'该用户已登录'}).encode('utf-8'))
        else:
        # 尝试登录
            p_m=hashlib.md5()
            p_m.update(password.encode())
            password_m=p_m.hexdigest()
            sql="select * from user_profile where username=%s and password=%s"
            try:
                # print(username,password_m)
                flag=cursor1.execute(sql,[username,password_m])
                if flag:
                    self.username=username
                    username_list.append(username)
                    self.client_socket.send(json.dumps({'code':'OK','msg':username}).encode('utf-8'))
                else:
                    self.client_socket.send(json.dumps({'code':10101,'msg':'用户名或密码错误'}).encode('utf-8'))
            except:
                pass


    def register_view(self):
        json_obj=json.loads(self.client_socket.recv(1024).decode('utf-8'))
        username=json_obj.get('username')
        password1=json_obj.get('password1')
        password2=json_obj.get('password2')
        if not password1 or not password2 or not username:
            self.client_socket.send(json.dumps({'code':10102,'msg':'某些字段为空，注册失败'}).encode('utf-8'))
        elif password1!=password2:
            self.client_socket.send(json.dumps({'code':10103,'msg':'两次密码不一致，注册失败'}).encode('utf-8'))
        else:
            p_m=hashlib.md5()
            p_m.update(password1.encode())
            password_m=p_m.hexdigest()
            sql='''insert into user_profile(username,password) values(%s,%s)'''
            cursor1.execute(sql,[username,password_m])
            conn.commit()
            self.client_socket.send(json.dumps({'code':'OK','msg':username}).encode('utf-8'))

    
    def run(self):
        global username_list
        # 开始处理需要的业务请求
        while True:
            try:
                view_flag=self.client_socket.recv(1024).decode('utf-8')
                if not view_flag:
                    username_list.remove(self.username)
                    exit()
                if view_flag=='LOGIN':
                    self.login_view()
                elif view_flag=='REGISTER':
                    self.register_view()
                elif view_flag=='GROUP_CHAT':
                    self.recvmsg_group_view()
            except:
                break


def main():
    server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # 防止意外关闭导致端口被占无法开启
    # server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server_socket.bind(('',7788))
    server_socket.listen(128)
    global group_client



    while True:
        client_socket,client_addrs=server_socket.accept()
        client_handle=Client_Handle(client_socket)
        threading.Thread(target=client_handle.run).start()
    server_socket.close()


if __name__=='__main__':
    main()