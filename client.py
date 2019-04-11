import sys
import socket
import requests
def main():

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1',8000))
    while True:
        # msg = bytes(input(">>:"), encoding="utf8")
        # s.sendall(msg)
        # data = s.recv(1024)
        # print('Received', repr(data))
        proxies = {
            "http":"127.0.0.1:8000"
        }
        r = requests.get("http://job.guet.edu.cn/Home/ArticleDetails?id=fcd7b8f5-a028-4a71-a182-d4444408ea11",proxies = proxies)

        print(r.text)
if __name__ == '__main__':
    try:
        #代理服务器的IP地址和端口号
        ip = "127.0.0.1"
        port = 8000
        main()
    except Exception as e:
        print(e)