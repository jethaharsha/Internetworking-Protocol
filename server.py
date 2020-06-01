#### reference: https://pythonprogramming.net/client-chatroom-sockets-tutorial-python-3/?completed=/server-chatroom-sockets-tutorial-python-3/
### reference for file transfer: https://www.youtube.com/watch?v=LJTaPaFGmM4


import socket
import threading
import sys
import select
import errno   
import os           

def recieve_message(client_socket):
    try:
        message = client_socket.recv(1024)
        #If a client closes a connection gracefully, 
        #then a socket.close() or socket.shutdown(socket.SHUT_RDWR)will be issued 
        if not len(message):
            return False
        message = message.decode('utf-8')
        return message
        
    except: #Something went wrong like empty message or client exited abruptly by using ctrl+c or just lost the connection.
        return False

'''
Get a list of keys from dictionary which has the given value
'''
def getKeysByValue(dictOfElements, valueToFind):
    listOfKeys = list()
    listOfItems = dictOfElements.items()
    for item  in listOfItems:
        if item[1] == valueToFind:
            listOfKeys.append(item[0])
    return  listOfKeys    


# msg = """CHOOSE YOUR OPTION: 
    # Enter 1 : To create a room
    # Enter 2 : To list all the rooms
    # Enter 3 : To join a room
    # Enter 4 : To Leave a room
    # Enter 5 : To list members of a room
    # Enter 6 : Broadcast message to everyone
    # Enter 7 : Broadcast message in a room
    # Enter 8 : To transfer a file
    # Enter 9 : TO Quit
# """


switcher = {
    1: "CREATE_ROOM",
    2: "LIST_ROOMS",
    3: "JOIN_ROOM",
    4: "LEAVE_ROOM",
    5: "MEMBERS_OF_A_ROOM",
    6: "BROADCAST_ALL",
    7: "BROADCAST_ROOM",
    8: "RETRIEVE_FILE",
    9: "QUIT"
}  

def IRC_chat(client_socket, client_address, clients, rooms, sockets_list):
    try:
        flag1 = True
        while flag1:
            # FIRST-----GET the username from the client
            username = recieve_message(client_socket)
            if username is False: ######client closed before sending a name
                continue
            #append this new client_socket to our sockets_list
            sockets_list.append(client_socket) 
            clients[client_socket] = username #After this, we'd like to save this client's username, which we'll save as the value to the key that is the socket object:
                
            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, username))       
            # while the client remains connected and sends various options
            flag =  True
            while flag:
                ### recieve the option from the client
                choice=client_socket.recv(1024)
                choice = choice.decode('utf-8')
                print("Printing choice from client: ",choice)
                if(choice == '1'):
                    client_socket.send("CREATE_ROOM".encode('utf-8'))
                    room_name = client_socket.recv(1024).decode('utf-8')
                    if room_name in rooms.keys():
                        client_socket.send("Room already exist, try again!".encode('utf-8'))
                    else:
                        rooms.setdefault(room_name, []).append(username)
                        print(rooms)
                        client_socket.send("Room Created".encode('utf-8'))            
                elif(choice == '2'): 
                    client_socket.send("LIST_ROOMS".encode('utf-8'))
                    keys = ", ".join(list(rooms.keys()))
                    print(keys)
                    if not keys:
                        client_socket.send("There are NO rooms available!".encode('utf-8'))
                    else:
                        client_socket.send(keys.encode('utf-8'))      
                    
                elif(choice == '3'): 
                    client_socket.send("JOIN_ROOM".encode('utf-8'))
                    room_name = client_socket.recv(1024).decode('utf-8')
                    #check if the room exists
                    if room_name in rooms.keys():
                        if username in rooms[room_name]:
                            client_socket.send(("Client is already added to the room").encode('utf-8'))
                        else:
                            rooms[room_name].append(username)
                            client_socket.send(("Client is added to " + room_name).encode('utf-8'))
                    else:
                        client_socket.send("ROOM DO NOT EXIST!".encode('utf-8'))
                    print(rooms)    
                elif(choice == '4'):
                    client_socket.send("LEAVE_ROOM".encode('utf-8'))
                    room_name = client_socket.recv(1024).decode('utf-8')
                    if room_name in rooms.keys():
                        if username in rooms[room_name]:
                            rooms[room_name].remove(username)
                            print(rooms)
                            client_socket.send(("Client is removed from the room " + room_name).encode('utf-8'))
                        else:
                            client_socket.send("USER IS NOT IN THIS ROOM".encode('utf-8'))
                    else:
                        client_socket.send("ROOM DO NOT EXIST!".encode('utf-8'))
                elif(choice == '5'):
                    client_socket.send("MEMBERS_OF_A_ROOM".encode('utf-8'))
                    room_name = client_socket.recv(1024).decode('utf-8')
                    all_members = ", ".join(list(rooms[room_name]))
                    print(all_members)
                    if not all_members:
                        client_socket.send("ROOM IS EMPTY!".encode('utf-8'))
                    else:
                        client_socket.send(all_members.encode('utf-8'))
                elif(choice == '6'):
                    client_socket.send("BROADCAST_ALL".encode('utf-8'))
                    msg = client_socket.recv(1024).decode('utf-8')
                    print(msg)
                    count = 0
                    for key, value in clients.items():
                        if value == username:
                            print("INSIDE IF")
                            continue
                        else:
                            count +=1
                            # key.send(value.encode('utf-8'))
                            # key.send(msg.encode('utf-8'))
                            key.send(("You recieved a new message from {} \n".format(username)).encode('utf-8'))
                            key.send(msg.encode('utf-8')) 
                            
                    if count == 0:
                        client_socket.send("No client available to broadcast message".encode('utf-8'))
                    else:
                        client_socket.send("Message succesfully broadcasted to all the clients".encode('utf-8'))
                
                elif(choice == '7'):
                    client_socket.send("BROADCAST_ROOM".encode('utf-8'))
                    roomname = client_socket.recv(1024).decode('utf-8')
                    count = 0
                    all_members = list(rooms[roomname])
                    print(all_members)
                    if roomname in rooms.keys():
                        msg = client_socket.recv(1024).decode('utf-8')
                        for user in all_members:
                            print(user)
                            if user == username:
                                continue
                            else:
                                count+=1
                                value = getKeysByValue(clients, user)
                                client_socket_value = value[-1]
                                client_socket_value.send(f"{username} > {msg}".encode('utf-8'))          
                    if count == 0:
                        client_socket.send("No client available to broadcast message".encode('utf-8'))
                    else:
                        client_socket.send("Message succesfully broadcasted to all the clients in the room".encode('utf-8'))            
                                
                elif(choice == '8'):
                    client_socket.send("RETRIEVE_FILE".encode('utf-8'))
                    filename = client_socket.recv(1024).decode('utf-8')
                    print(filename)
                    if os.path.isfile(filename):
                        client_socket.send(("EXISTS " +str(os.path.getsize(filename))).encode('utf-8'))
                        userResponse = client_socket.recv(1024)
                        userResponse = userResponse.decode('utf-8')
                        if(userResponse[:2] == 'Ok'):
                            print("sending the file ................")
                            with open(filename, 'rb') as f:
                                bytesToSend = f.read(1024)
                                client_socket.send(bytesToSend)
                                while bytesToSend != "":
                                    bytesToSend = f.read(1024)
                                    client_socket.send(bytesToSend)
                elif(choice == '9'):
                    client_socket.send("QUIT".encode('utf-8'))
                    userResponse = client_socket.recv(1024)
                    userResponse = userResponse.decode('utf-8')
                    if(userResponse[:2] == 'Ok'):
                    
                        # clients.remove(client_socket)
                        #check if the user is present in any room
                        
                        for key in rooms.keys():
                            if username in rooms[key]:
                                #remove the user from the room
                                rooms[key].remove(username)
                        client_socket.send("You are logged out".encode('utf-8'))
                        print(username + " has been logged out")
                        del clients[client_socket]
                        #print(clients.keys())
                        
                        flag = False 
                        flag1=False
                    
                else:
                    client_socket.send("Enter a Valid option".encode('utf-8'))                    
    except:
        del clients[client_socket]
        for key in rooms.keys():
            if username in rooms[key]:
                #remove the user from the room
                rooms[key].remove(username)
        print(username + " has been logged out")
        # print(clients.keys())
        flag = False 
        flag1=False     
                
            
def Main():
    host = 'localhost'
    port = 5000
    global server_socket, client_socket, connection
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server_socket.bind((host, port))
    print(f'Listening for connections on {host}:{port}')
    sockets_list =[server_socket]
    global clients
    clients = {} ########client dictionary where sockets will be the 'KEY' and user message will be the 'values'
    rooms = {}    
    server_socket.listen(10)
    print("Server Started")
    connection = True
    while connection:
        client_socket, client_address = server_socket.accept()
        print("Client connected ip:<"+ str(client_address) +">")
        t = threading.Thread(target = IRC_chat, args = (client_socket, client_address, clients, rooms, sockets_list)) ## target function is IRC_chat func and arguments for that funs(fun name, connection_name)
        t.start()

    
if __name__ == "__main__":   
    try:
        Main()
    except KeyboardInterrupt:
        print("Server closed with KeyboardInterrupt!")
        ## server closes the connection
        connection = False
        for client_socket in clients:
            client_socket.send("******SERVER SHUTDOWN!******".encode('utf-8'))
            # client_socket.shutdown(socket.SHUT_RDWR) 
            client_socket.close()    #close socket
            # sys.exit(1)

    finally:  
        # server_socket.shutdown(socket.SHUT_RDWR)
        
        server_socket.close()
        sys.exit(1)         
 

# except KeyboardInterrupt:
    # try:
        # if connection:
            # connection.close()
    # except: pass
    # break
# sock.shutdown
# sock.close() 