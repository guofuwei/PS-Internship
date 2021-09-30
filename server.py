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
username_dic={}
private_client=[]

class Client_Handle():
    def __init__(self,client_socket):
        self.client_socket=client_socket

    def recvmsg_group_view(self):
        global group_client
        group_client.append(self.client_socket)
        # print('len is %s' %len(group_client))
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
        # print('***************************')
        global username_dic
        # 拿取参数
        json_obj=json.loads(self.client_socket.recv(1024).decode('utf-8'))
        username=json_obj.get('username')
        password=json_obj.get('password')
        # print(username,password)
        # 校验参数
        if not username or not password:
            self.client_socket.send(json.dumps({'code':10100,'msg':'用户名或密码为空'}).encode('utf-8'))
        elif username_dic.get(username):
            self.client_socket.send(json.dumps({'code':10105,'msg':'该用户已登录'}).encode('utf-8'))
        else:
        # 尝试登录
            # print('-----------------')
            p_m=hashlib.md5()
            p_m.update(password.encode())
            password_m=p_m.hexdigest()
            sql="select * from user_profile where username=%s and password=%s"
            try:
                # ps
                # print(username,password_m) 
                flag=cursor1.execute(sql,[username,password_m])
                if flag:
                    self.username=username
                    username_dic[self.username]=self.client_socket
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

    def group_msg_cat_view(self):
        sql='''select * from group_msg'''
        cursor1.execute(sql)
        data=cursor1.fetchall()
        END='THE MSG IS END'
        for i in range(0,len(data)):
            send_data='内容:{:<10s}     时间:{}'.format(data[i][2],data[i][1].strftime('%Y-%m-%d %H:%M:%S'))
            self.client_socket.send((send_data+'$$##$$').encode('utf-8'))
        self.client_socket.send(END.encode('utf-8'))

    def add_friend_view(self):
        friend_name=self.client_socket.recv(1024).decode('utf-8')
        sql='''select * from user_profile where username=%s'''
        cursor1.execute(sql,[friend_name])
        data=cursor1.fetchone()
        if data:
            self.client_socket.send('OK'.encode('utf-8'))
            is_flag=self.client_socket.recv(1024).decode('utf-8')
            if is_flag=='YES':
                try:
                    # bug
                    sql='''select * from user_profile where username=%s'''
                    cursor1.execute(sql,[self.username])
                    data_now=cursor1.fetchone()
                    # print(data_now)
                    if not data_now[2]:
                        updated_friend_list=friend_name+'++'
                        sql='''update user_profile set friend_list=%s where username=%s'''
                        cursor1.execute(sql,[updated_friend_list,self.username])
                        conn.commit()
                        self.client_socket.send('OK'.encode('utf-8'))
                    elif friend_name in data_now[2]:
                        self.client_socket.send('Already'.encode('utf-8'))
                    else:
                        updated_friend_list=data_now[2]+friend_name+'++'
                        sql='''update user_profile set friend_list=%s where username=%s'''
                        cursor1.execute(sql,[updated_friend_list,self.username])
                        conn.commit()
                        self.client_socket.send('OK'.encode('utf-8'))
                except:
                    self.client_socket.send('FAIL'.encode('utf-8'))




                    
        else:
            self.client_socket.send('FAIL'.encode('utf-8'))

    def cat_friend_view(self):
        sql='''select * from user_profile where username=%s'''
        # print(self.username)
        cursor1.execute(sql,[self.username])
        data=cursor1.fetchone()
        if data[2]:
            self.client_socket.send(data[2].encode('utf-8'))
        else:
            # print('---------------')
            self.client_socket.send('$$##$$'.encode('utf-8'))
            # print('================')


    def private_chat_view(self):
        self.cat_friend_view()
        friend_name=self.client_socket.recv(1024).decode('utf-8')
        sql='''select * from user_profile where username=%s'''
        cursor1.execute(sql,[self.username])
        user_data=cursor1.fetchone()
        # print(user_data)
        # 该用户存在
        if not user_data[2]:
            self.client_socket.send('FAIL'.encode('utf-8'))
        elif friend_name in user_data[2].split('++'):
            self.client_socket.send('OK'.encode('utf-8'))
            # 该用户在线
            if friend_name in private_client:
                self.client_socket.send('OK'.encode('utf-8'))
            # 该用户不在线
            else:
                self.client_socket.send('FAIL'.encode('utf-8'))
            flag=self.client_socket.recv(1024).decode('utf-8')
            if flag=='YES':
                self.private_chat_detail_view(friend_name)
        else:
            self.client_socket.send('FAIL'.encode('utf-8'))


    def private_chat_detail_view(self,friend_name):
        global private_client
        private_client.append(self.username)
        # ps
        # print(private_client)
        global username_dic
        # 判断用户需不需要查看历史消息
        flag=self.client_socket.recv(1024).decode('utf-8')
        if flag=='YES':
            self.get_history_msg_view(friend_name)
        while True:
            try:
                recv_data=self.client_socket.recv(1024).decode('utf-8')
                # print(recv_data)
                if recv_data=='EXIT':
                    # 通知监听线程结束
                    self.client_socket.send('$$##$$EXIT$$##$$'.encode('utf-8'))
                    if friend_name in private_client:
                        send_data='%s已离开聊天室' %self.username
                        username_dic[friend_name].send(send_data.encode('utf-8'))
                    break
                elif recv_data:
                    sql='''insert into private_msg(username1,username2,content) values(%s,%s,%s)'''
                    cursor1.execute(sql,[self.username,friend_name,recv_data])
                    conn.commit()
                    # print('------------------')
                    # print(friend_name)
                    print(username_dic)
                    if friend_name in private_client:
                        username_dic[friend_name].send(recv_data.encode('utf-8'))
            except:
                print('error')
                break
        private_client.remove(self.username)


    def get_history_msg_view(self,friend_name):
        sql1='''select id from private_msg where username1=%s and username2=%s order by id desc limit 1'''
        cursor1.execute(sql1,[self.username,friend_name])
        data=cursor1.fetchone()
        if data:
            last_id=data[0]
        else:
            last_id=0
        # print(last_id)
        sql2='''select * from private_msg where username1=%s and username2=%s and id>%s;'''
        cursor1.execute(sql2,[friend_name,self.username,last_id])
        data=cursor1.fetchall()
        # ps
        # print(data)
        END='THE MSG IS END'
        if data:
            for one_data in data:
                # print(one_data[3])
                self.client_socket.send((one_data[3]+'$$##$$').encode('utf-8'))
            self.client_socket.send(END.encode('utf-8'))

        else:
            self.client_socket.send(END.encode('utf-8'))

    def run(self):
        global username_dic
        # 开始处理需要的业务请求
        while True:
            try:
                view_flag=self.client_socket.recv(1024).decode('utf-8')
                if not view_flag:
                    username_dic.pop(self.username)
                    exit()
                if view_flag=='LOGIN':
                    self.login_view()
                elif view_flag=='REGISTER':
                    self.register_view()
                elif view_flag=='GROUP_CHAT':
                    self.recvmsg_group_view()
                elif view_flag=='GROUP_MSG_CAT':
                    self.group_msg_cat_view()
                elif view_flag=='ADD_FRIEND':
                    self.add_friend_view()
                elif view_flag=='CAT_FRIEND':
                    self.cat_friend_view()
                elif view_flag=='PRIVATE_CHAT':
                    self.private_chat_view()
            except:
                try:
                    username_dic.pop(self.username)
                except:
                    pass
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