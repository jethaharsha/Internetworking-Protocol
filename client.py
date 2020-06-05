#### reference: https://pythonprogramming.net/client-chatroom-sockets-tutorial-python-3/?completed=/server-chatroom-sockets-tutorial-python-3/
### reference for file transfer: https://www.youtube.com/watch?v=LJTaPaFGmM4

import socket
import threading
import sys
import select
import errno 
import os

  
def ServerResponse(client_socket, connection):
    #receive msg from the server
    while connection:
        msg=client_socket.recv(1024).decode('utf-8')
        print(msg)
        if(msg == "******SERVER SHUTDOWN!******"):
            connection = False
            client_socket.shutdown(socket.SHUT_RDWR) 
            client_socket.close()
            sys.exit(1)
        if(msg =="CREATE_ROOM"):
            room_name = input("Enter name of the room to create: ")
            client_socket.send(room_name.encode('utf-8'))
            msgclient=client_socket.recv(1024).decode('utf-8')
            print(msgclient)
            
        elif(msg == "LIST_ROOMS"):     
            print("List of all the rooms: ")
            msgclient=client_socket.recv(1024).decode('utf-8')
            print(msgclient)
            
        elif(msg =="JOIN_ROOM"):
            room_name = input("Enter name of the room to Join: ")
            client_socket.send(room_name.encode('utf-8'))  
            msgclient=client_socket.recv(1024).decode('utf-8')
            print(msgclient)
            
        elif(msg =="LEAVE_ROOM"):
            room_name = input("Enter name of the room to Leave: ")
            client_socket.send(room_name.encode('utf-8'))  
            msgclient=client_socket.recv(1024).decode('utf-8')
            print(msgclient) 
            
        elif(msg =="MEMBERS_OF_A_ROOM"):
            room_name = input("Enter room name to view its members: ")
            client_socket.send(room_name.encode('utf-8'))     
            
        elif(msg =="BROADCAST_ALL"):
            msg = input("Enter the message to Broadcast: ")
            client_socket.send(msg.encode('utf-8'))  
            msgclient=client_socket.recv(1024).decode('utf-8')
            print(msgclient)
            
        elif(msg =="BROADCAST_ROOM"):
            room = input("Enter the name of the room to broadcast message: ")
            client_socket.send(room.encode('utf-8'))  
            msg = input(f"Enter the message to Broadcast in {room}: ")
            client_socket.send(msg.encode('utf-8'))  
            msgclient=client_socket.recv(1024).decode('utf-8')
            print(msgclient)
        elif(msg =="RETRIEVE_FILE"):
            filename = input("Filename: -> ")
            if filename != 'q':
                filenameEnc = filename.encode('utf-8')
                client_socket.send(filenameEnc)
                data = client_socket.recv(1024).decode('utf-8')
                print(data)
                if data[:6] == "EXISTS":
                    filesize = int(data[6:])
                    message = input("File Exists, "+ str(filesize)+\
                                        "Bytes, download? (Y/N)? ->")
                    if message == 'Y':
                        reply = 'Ok'
                        client_socket.send(reply.encode('utf-8'))
                        f = open('new_'+filename, 'wb')
                        data = client_socket.recv(1024)
                        f.write(data)
                        data = data.decode('utf-8')
                        totalRecv = len(data)
                        while totalRecv < filesize:
                            data = client_socket.recv(1024)                 
                            f.write(data)
                            data = data.decode('utf-8')
                            totalRecv+=len(data)
                            print("{0:.2f}".format((totalRecv/float(filesize))*100) + "% Done")
                        print("Download Complete!")
                        f.close()
                else:
                    print("File does not exist!")
                    
        elif(msg =="QUIT"):
            message = input("Are you sure you want to QUIT? (Y/N)? ->") 
            if message == 'Y':
                reply = 'Ok'
                client_socket.send(reply.encode('utf-8'))            
                msgclient=client_socket.recv(1024).decode('utf-8')
                print(msgclient) 

def Main():
    host = 'localhost'
    port = 5000
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    connection = True
    while connection:
        
        my_username = input("Username: ")
        username = my_username.encode('utf-8')
        client_socket.send(username)
        msg = """CHOOSE YOUR OPTION: 
            Enter 1 : To create a room
            Enter 2 : To list all the rooms
            Enter 3 : To join a room
            Enter 4 : To Leave a room
            Enter 5 : To list members of a room
            Enter 6 : Broadcast message to everyone
            Enter 7 : Broadcast message in a room
            Enter 8 : To transfer a file
            Enter 9 : TO Quit
        """
        print(msg) 
        print("Choose your option:")
        #instantiating the thread with target method client_socket
        t1 = threading.Thread(target = ServerResponse, args = (client_socket, connection))
        t1.start()
        while connection:
            option = input()
            client_socket.send(option.encode('utf-8'))
        break

    
if __name__ == "__main__":   
    try:    
        Main()       
        
    except KeyboardInterrupt:
        print("######## Client exited abruptly! #############")
        
        
    except IOError as e: # types of error messages we can expect when there are no messages to be recieved.
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error occured', str(e))
            sys.exit()

    except Exception as e:
        print('General error',str(e))
        sys.exit()
        pass  

    finally:       
        connection = False
        client_socket.shutdown(socket.SHUT_RDWR) 
        client_socket.close()    #close socket
        sys.exit(1)        
         
                    