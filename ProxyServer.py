import select
import socket
import threading
import queue
from concurrent.futures import ThreadPoolExecutor

HEADER_SIZE = 5102
host = '127.0.0.1'
port = 8000

def getinfo(content):
    header = content.decode()
    print(header)
    host_addr = header.split("\r\n")[1].split(":")
    # 如果未指定端口则为默认 80
    if 2 == len(host_addr):
        host_addr.append("80")
    name, host, port = map(lambda x: x.strip(), host_addr)
    return name, host, port

def isNotInLists(host):
    data = []
    f = open("pac.txt")
    while 1:
        lines = f.readlines(10)
        if not lines:
            break
        for line in lines:
            d = line.strip("\n")
            if d:
                data.append(d)
    f.close()

    if host not in data:
        return True
    else:
        return False


def http_socket(client, addr):
    inputs = [client]
    outputs = []
    exceptions = []
    message = {}
    remote_socket = 0
    canAccess = True
    cnt = 0
    host = 0
    port = 0
    while True:
        print("host start wait for receving data...")
        readable, writeable, exceptional = select.select(inputs, outputs, exceptions)
        print("continue")
        for s in readable:
            if s is client:
                content = s.recv(HEADER_SIZE)
                if not content:  # 发送完数据了
                    print("wait for sending data from client ...")
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()
                    del message[s]
                    print(threading.current_thread().getName() + " 退出，准备回收")
                    return
                else:
                    # print("received data\n" + content.decode())

                    if cnt == 0:
                        name, host, port = getinfo(content)
                        cnt = 1
                    # if host != 'job.guet.edu.cn':
                    #     canAccess = False
                    if isNotInLists(host):
                        canAccess = True
                    else:
                        canAccess = False

                    if canAccess:
                        if remote_socket == 0:
                            # 建立socket连接
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.connect((host, int(port)))
                            remote_socket = sock
                        if remote_socket not in inputs:
                            inputs.append(remote_socket)
                            outputs.append(remote_socket)

                        message[s] = queue.Queue()
                        message[remote_socket] = queue.Queue()
                        message[remote_socket].put(content)
                    else:
                        print("拒绝访问...")
                        bcontent = b'''HTTP/1.1 403 Forbidden\r\nServer: none\r\nDate: Thu, 11 Apr 2019 04:17:08 GMT\r\nContent-Type: text/html\r\nTransfer-Encoding: chunked\r\nConnection: keep-alive\r\nContent-Encoding: gzip\r\n<html>
                                                           <head><title>403 Forbidden</title></head>
                                                           <body bgcolor="white">
                                                           <center><h1>403 Forbidden</h1></center>
                                                           <hr><center>none</center>
                                                           </body>
                                                           </html>
                                                            '''
                        # print("发送数据回去")
                        s.sendall(bcontent)
                        inputs.remove(s)
                        s.close()
                        return

                    # if s not in outputs:
                    #     outputs.append(s)

                    # print("Server received \n" + content.decode())
                    # message[s] = queue.Queue()
                    # message[s].put("ack")
                    # if s not in outputs:
                    #     outputs.append(s)
            else:  # 远程服务器发回数据

                data = s.recv(HEADER_SIZE)
                if not data:
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    print("close connection...")
                    s.close()

                else:
                    print("发送数据和回去")
                    # print( data)
                    message[client].put(data)
                    if client not in outputs:  # 添加客户端的连接到outputs
                        outputs.append(client)
                    # client.sendall(data)

        for s in writeable:
            if s is remote_socket:
                try:
                    msg = message[s].get_nowait()
                except queue.Empty:
                    outputs.remove(s)
                else:
                    s.sendall(msg)
                    outputs.remove(s)
            elif s is client:
                try:
                    msg = message[s].get_nowait()
                except queue.Empty:
                    outputs.remove(s)
                else:
                    s.sendall(msg)
                    outputs.remove(s)

                # #byte
                # header = client.recv(HEADER_SIZE)
                # #str
                # request_header = header.decode()


if __name__ == '__main__':
    # 定义一个线程池
    pool = ThreadPoolExecutor(max_workers=10)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    point = (host, port)
    server.bind(point)
    print("Proxy start listen....")
    server.listen(3)

    while True:
        client, addr = server.accept()
        print("click")
        task1 = pool.submit(http_socket, client, addr)

    # http_socket(client,addr)