import socket
import threading
import sqlite3
import sys


PORT = 9040
BUF_SIZE = 1024
lock = threading.Lock()
clnt_data = []
clnt_cnt = 0


def conn_DB():
    conn = sqlite3.connect('edu.db') # DB 연결
    cur = conn.cursor()
    return (conn, cur)


def handle_clnt(clnt_sock):
    while 1:
        sys.stdout.flush()
        clnt_msg = clnt_sock.recv(BUF_SIZE)

        if not clnt_msg:
            break

        clnt_msg = clnt_msg.decode()
        if clnt_msg.startswith('signup/'):
            clnt_msg = clnt_msg.replace('signup/', '')
            signup(clnt_sock, clnt_msg)
        elif clnt_msg.startswith('login/'):
            clnt_msg = clnt_msg.replace('login/', '')
            login(clnt_sock, clnt_msg)


def signup(clnt_sock, clnt_msg):
    conn, cur = conn_DB()
    user_data = []
    user_id = ''
    member = ''

    while 1:
        overlap = False

        if clnt_msg == "close":
            conn.close()
            return

        if clnt_msg.startswith('teacher/'):
            member = 'teacher'
            user_id = clnt_msg.replace('teacher/', '')
        elif clnt_msg.startswith('student/'):
            member = 'student'
            user_id = clnt_msg.replace('student/', '')
        else:
            print("error")
            conn.close()
            return

        query = "SELECT id FROM %s" % member
        rows = cur.excute(query)

        for row in rows:
            if user_id in row:
                # id 중복
                clnt_sock.send('!NO'.encode())
                overlap = True
                break
            if overlap:
                continue
        
        clnt_sock.send('!OK'.encode())
        info = clnt_sock.recv(BUF_SIZE)
        info = info.decode() # id/pw/name 
        if info == 'close':
            conn.close()
            break

        info = info.split('/')

        for i in range(3):
            user_data.append(info[i])
        
        lock.acquire()
        insert_query = "INSERT INTO %s(id, pw, name) VALUES(?, ?, ?)" % member
        cur.executemany(insert_query, (user_data,))
        conn.commit()
        conn.close()
        lock.release()
        break
    
        

def login(clnt_sock, clnt_msg):
    conn, cur = conn_DB()
    member = ''
    #login/member/id/pw
    if clnt_msg.startswith('teacher/'):
        member = 'teacher'
        input_data = clnt_msg.replace('teacher/', '')
    elif clnt_msg.startswtih('student/'):
        member = 'student'
        input_data = clnt_msg.replace('student/', '')
    else:
        print("error")
        return
    
    input_data = input_data.split('/')
    input_id = input_data[0]
    input_pw = input_data[1]
    
    query = "SELECT pw FROM %s WHERE id =?" % member
    cur.execute(query, (input_id,))
    
    user_pw = cur.fetchone()

    if not user_pw:
        clnt_sock.send("id_error".encode())
        conn.close()
        return

    if (input_pw,) == user_pw:
        print("login sucess")
        
        query = "SELECT * FROM %s WHERE id = ?" % member
        cur.execute(query, (input_id,))
        user_data = cur.fetchone()
        user_data = list(user_data)
        print("user_data " + user_data)
        clnt_data[clnt_cnt-1].append(member)
        clnt_data[clnt_cnt-1] = clnt_data[clnt_cnt-1] + user_data
        print("clnt_data" + clnt_data[clnt_cnt-1])

        #send_user_info()
        
    else :
        print("login fail")
        clnt_sock.send("pw_error".encode())
        conn.close()
        return




if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', PORT))
    sock.listen(5)

    while True:
        clnt_sock, addr = sock.accept()

        lock.acquire()
        clnt_data.insert(clnt_cnt, [clnt_sock])
        print("clnt_data" + clnt_data)
        clnt_cnt += 1
        lock.release()
        thread = threading.Thread(target = handle_clnt, args = (clnt_sock,))
        thread.start()