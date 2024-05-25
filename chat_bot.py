
from socket import *
import os
from threading import Thread
import threading
address = {}
server_connection_ip = {}
def user_input_first():
    server = Server()
class Server:  
    def __init__(self):
        self.is_server = True
        self.is_client = False
        self.host_exited = False
        self.host = '192.168.99.4'
        self.port = 13026
        self.disconnect = False
        self.is_exiting = False
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        print('Chat running at ', self.host, ' on port ', self.port)
        server_socket.listen(15)
        threading._start_new_thread(self.accept_connections, (server_socket,))
        server_socket.settimeout(30)
        self.user_input()
    def accept_connections(self, server_socket):
        while True:
            try:
                clientSocket = None
                clientSocket, addr = server_socket.accept()
                if clientSocket != None:
                    print('\nAccepted connection with ', addr[0])
                    address[addr[0]] = [clientSocket]
                    threading._start_new_thread(self.receive_message, (clientSocket,))

            except:
                if len(address) > 0:
                    continue
                elif self.is_exiting:
                    server_socket.close()
                    break

    def handle_client(self, connection):
        if connection == "all":
            for key, value in address:
                value[0].send("disconnect exit")
            address.clear()
        else:
            key_list = list(address.keys())
            val_list = list(address.values())
            recievers =  sum([x for x in val_list if connection in x], [])
            index = val_list.index(recievers)
            element = key_list[index]
            elements = address.get(element)
            sockets = elements[0]
            sockets.close()
            address.pop(element)
    def receive_message(self, clientSocket):
        while True:
            if self.disconnect or self.is_exiting or self.host_exited:
                break
            try:
                data = clientSocket.recv(1024)
                data = data.decode()
                message = data[:10]
            except :
                break
            if message == 'disconnect':
                if self.is_server:
                    ip, port = clientSocket.getpeername()
                    ip = address[ip][1]
                elif self.is_client:
                    self.disconnect = True
                    ip, port = clientSocket.getpeername()
                    ip = server_connection_ip[ip][1]
                print("Host at", ip, "disconnected")
                if self.is_server:
                    self.handle_client(ip)
                else:
                    self.handle_server(ip)
                break
            elif data == 'disconnect exit':
                ip, port = clientSocket.getpeername()
                self.host_exited = True
                if self.is_server:
                    ip = server_connection_ip[ip][1]
                    self.handle_client(ip)
                else:
                    ip = address[ip][1]
                    self.handle_server(ip)
                break
            elif data == "":
                return
            elif data[:5] == "name:":
                ip, port = clientSocket.getpeername()
                x = data.split(" ")
                me = x[1]
                if me == "NA":
                    address[ip].append(ip)
                else:
                    address[ip].append(me)
            else:
                if self.is_server:
                    ip, port = clientSocket.getpeername()
                    ip = address[ip][1]
                elif self.is_client:
                    ip, port = clientSocket.getpeername()
                    ip = server_connection_ip[ip][1]
                print("\nMessage \"", data, "\" received from ", ip)
    def send_message(self, reciever, message):
        try: 
            if self.is_client:
                if len(server_connection_ip) == 0:
                    return
                key_list = list(server_connection_ip.keys())
                val_list = list(server_connection_ip.values())
                recievers =  sum([x for x in val_list if reciever in x], [])
                sender = recievers[0]
            else:
                key_list = list(address.keys())
                val_list = list(address.values())
                recievers =  sum([x for x in val_list if reciever in x], [])
                if len(recievers) == 0:
                    return
                index = val_list.index(recievers)
                element = key_list[index]
                element = address.get(element)
                sender = element[0]
            if message == 'disconnect':
                message = message + " " + reciever 
                if self.is_server:
                    var = address[self.clientSocket][0]
                elif self.is_client:
                    var = list(server_connection_ip.keys())[0]
                print("Disconnected from ", var)
            elif message[:5] == "name:":
                print("Your name was added to the system.")
            elif message != "disconnect exit":
                print("Message \"", message, "\" sent", reciever)
            sender.send(message.encode())
        except:
            return
    def connectToServer(self, server_ip, server_port, server_name):
        self.server_ip = server_ip
        self.server_port = server_port
        clientSocket = socket(AF_INET,SOCK_STREAM)
        try:
            clientSocket.connect((self.server_ip, self.server_port))
            server_connection_ip[server_ip] = [clientSocket, server_name]
            threading._start_new_thread(self.receive_message, (clientSocket,))
            print('Successfully connected with ', server_name)
            return True
        except:
            return False
           
    def user_input(self):
        while True:
            if self.is_exiting:
                break
            command = input("Enter command: ")
            if command[:7] == 'connect':
                index = command[8:]
                x = index.split(" ")
                host = x[0]
                serverPort = x[1]
                self.disconnect = False
                serverPort = int(serverPort)
                self.is_server = False
                self.is_client = True
                server_name = input("Enter an nickmane for server or NA: ")
                if server_name == "NA":
                    server_name = host
                if self.connectToServer(host, serverPort, server_name):
                    client_name = input("Enter an nickmane to address you in their system or NA: ")
                    message = "name: " + client_name
                    self.send_message(server_name, message)
                    continue
                else:
                    print("Try agian either IP address or port number is wrong")
            elif command[:4] =='send':
                index = command[5:]
                x = index.split(" ")
                reciever = x[0]
                x.pop(0)
                message = " ".join(x)
                self.send_message(reciever, message)
            elif command[:10] == 'disconnect' and len(command) != 10:
                message = command[:10]
                reciever = command[11:]
                self.send_message(reciever, message)
                if self.is_server:
                    self.handle_client(reciever)
                else:
                    self.disconnect = True
                    self.handle_server(reciever)
                continue
            elif command == 'exit':
                if not self.active_connection_exit():
                    if not self.host_exited:
                        if self.is_client:
                            server = list(server_connection_ip.keys())[0]
                            server_name = server_connection_ip[server][1]
                            self.send_message(server_name, "disconnect exit")
                    if self.is_server:
                        self.handle_client("all")
                    else:
                        self.handle_server(server_name)          
                self.is_exiting = True
                break
    def active_connection_exit(self):
        if  self.is_server:
            if len(address) == 0:
                return True
        else:
            if len(server_connection_ip) == 0:
                return True
        return False  
    def handle_server(self, connection):
        key_list = list(server_connection_ip.keys())
        val_list = list(server_connection_ip.values())
        recievers =  sum([x for x in val_list if connection in x], [])
        index = val_list.index(recievers)
        element = key_list[index]
        elements = server_connection_ip.get(element)
        sockets = elements[0]
        sockets.close()
        server_connection_ip.pop(element)
if __name__ == '__main__':
    user_input_first()
