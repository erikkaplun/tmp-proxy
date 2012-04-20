#!/usr/bin/python
# coding: utf-8
import socket
import select
import sys
import os

if sys.version_info > (3, 0, 0):
    #print "This version of python is not supported!\nPlease download python 2.x"
    sys.exit(1)


def console_write(text):
    if os.name == 'nt':
        f = open("dump.txt", "a+")
        f.write(text)
        f.close()
    else:
        print(text)


def handle_client(listener, remote_addr, local_to_server, server_to_local, sockets):
    print ("Something trying to connect...")
    local, address = listener.accept()
    remote = socket.create_connection(remote_addr)
    print ("Client accepted.")
    sockets.append(local)
    sockets.append(remote)
    local_to_server[local] = remote
    server_to_local[remote] = local


def send(connection, data, local_to_server, server_to_local, local_to_server_func, server_to_local_func):
    if connection in local_to_server:
        if local_to_server_func != None:
            data = local_to_server_func(data)
        console_write("Local:\n" + data)
        local_to_server[connection].send(data)
    else:
        if server_to_local_func != None:
            data = server_to_local_func(data)
        console_write("Remote:\n" + data)
        server_to_local[connection].send(data)


def close_socket(connection, local_to_server, sockets):
    #if connection in local_to_server:
        #print ("Local disconnected.")
    #else:
        #print ("Remote disconnected.")
    connection.close()
    sockets.remove(connection)


def proxy(remote_ip, remote_port, local_ip, local_port, size=1024, local_to_server_func=None, server_to_local_func=None):
    local_to_server = {}
    server_to_local = {}
    remote_addr = (remote_ip, remote_port)
    local_addr = (local_ip, local_port)
    sockets = []

    data_to_write = {}

    listener = socket.socket()
    listener.setblocking(0)
    listener.bind(local_addr)
    listener.listen(5)
    sockets.append(listener)

    while True:
        print ("Waiting...")
        ready_to_read, ready_to_write, in_error = select.select(sockets, [], [], 1)
        for connection in ready_to_read:
            if connection == listener:  # Add new socket
                print("accept")
                handle_client(listener, remote_addr, local_to_server, server_to_local, sockets)
            else:  # handle existing socket
                try:  # If socket died
                    print("recv")
                    data = connection.recv(size)
                except socket.error:
                    print ("Connection reset")
                    sockets.remove(connection)
                else:
                    if data:  # Forward data
                        data_to_write[connection] = data
                        print("appending data [" + str(connection) + "] = " + str(data_to_write[connection]))
                    else:  # If socket closed
                        sockets = close_socket(connection, local_to_server, sockets)

        #ready_to_read, ready_to_write, in_error = select.select(sockets, [], [], 1)
        for connection in ready_to_write:
            print("send:")
            send(connection, ''.join(data_to_write[connection]), local_to_server, server_to_local, local_to_server_func, server_to_local_func)

    #print ("Done.")


def to_server(data):
    if len(data) < 2000:
        if data[0:3] == "GET":
            #~ print ("Header detected:")
            #~ print(data)
            #~ firefox = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:11.0) Gecko/20100101 Firefox/11.0"
            #~ data = re.sub("(User-Agent\:.*?\r\n)","User-Agent: "+firefox+"\r\n",data)
            #~ data = data.replace("Accept-Encoding: gzip, deflate\r\n","")
            data = "GET / HTTP/1.1\r\n"
            data += "User-Agent: AutoIt\r\n"
            data += "Host: 127.0.0.1:8000\r\n"
            data += "Cache-Control: no-cache\r\n\r\n"
            print(data)
    return data


def to_client(data):
    return data


if __name__ == '__main__':
    try:
        #~ proxy.proxy('212.95.32.219', 8005, '0.0.0.0', 8005, 8192,to_server, to_client)
        proxy('195.50.209.244', 80, '0.0.0.0', 80, 1024, o_server, to_client)
    except KeyboardInterrupt:
        sys.exit(1)
    else:
        sys.exit(0)
