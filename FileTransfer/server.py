import socket
import threading
import os

def RetrFile(name, sock):
    filename = sock.recv(1024)
    filename = filename.decode('utf-8')
    if os.path.isfile(filename):
        sock.send(("EXISTS " +str(os.path.getsize(filename))).encode('utf-8'))
        userResponse = sock.recv(1024)
        userResponse = userResponse.decode('utf-8')
        if(userResponse[:2] == 'Ok'):
            print("sending the file ................")
            with open(filename, 'rb') as f:
                bytesToSend = f.read(1024)
                sock.send(bytesToSend)
                while bytesToSend != "":
                    bytesToSend = f.read(1024)
                    sock.send(bytesToSend)
                    
    else:
        error = 'ERR'
        sock.send(error.encode('utf-8'))
    sock.close()
    
def Main():
    host = 'localhost'
    port = 5000
    
    s = socket.socket()
    s.bind((host,port))
    
    s.listen(5)
    print("Server Started")
    while 1:
        c, addr = s.accept()
        print("Client connected ip:<"+ str(addr) +">")
        t = threading.Thread(target = RetrFile, args = ("retrThread", c)) ## target function is retrfile func and arguments for that funs(fun name, connection_name)
        t.start()
    s.close()
    
if __name__ == "__main__":   
    Main()