import socket

def Main():
    host = 'localhost'
    port = 5000
    
    s = socket.socket()
    s.connect((host,port))
    
    filename = input("Filename: -> ")
    if filename != 'q':
        filenameEnc = filename.encode('utf-8')
        s.send(filenameEnc)
        data = s.recv(1024)
        data = data.decode('utf-8')
        if data[:6] == "EXISTS":
            filesize = int(data[6:])
            message = input("File Exists, "+ str(filesize)+\
                                "Bytes, download? (Y/N)? ->")
            if message == 'Y':
                reply = 'Ok'
                s.send(reply.encode('utf-8'))
                f = open('new_'+filename, 'wb')
                data = s.recv(1024)
                f.write(data)
                data = data.decode('utf-8')
                totalRecv = len(data)
                while totalRecv < filesize:
                    data = s.recv(1024)                 
                    f.write(data)
                    data = data.decode('utf-8')
                    totalRecv+=len(data)
                    print("{0:.2f}".format((totalRecv/float(filesize))*100) + "% Done")
                print("Download Complete!")
        else:
            print("File does not exist!")
    s.close()
    
if __name__ == "__main__":   
    Main()
                
            
        