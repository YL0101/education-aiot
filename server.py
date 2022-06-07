import socket
import threading
import sqlite3

PORT = 9040
BUF_SIZE = 1024
lock = threading.Lock()

def DB():
    conn = sqlite3.connect('db이름.db') # DB 연결
    cur = conn.cursor()
    return (conn, cur)

def handle_clnt(clnt_sock):





if name == 'main':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', PORT))
    sock.listen(5)

    while True:
        clnt_sock, addr = sock.accept()

        thread = threading.Thread(target = handle_clnt, args(clnt_sock,))
        thread.start()