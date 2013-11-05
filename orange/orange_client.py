import os
import socket, sys
import time
import numpy as np
from exceptions import ZeroDivisionError

teamname="Orange\n"
port=6789
eom="<EOM>\n"
maxlen=4098

print(sys.argv)
if len(sys.argv)>1:
    port = int(sys.argv[1])
  
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', port))

def readsocket(sock,timeout=0):
    inpData=''
    while True:
        chunk = sock.recv(maxlen)
        if not chunk: break
        if chunk == '':
            raise RuntimeError("socket connection broken")
        inpData = inpData + chunk
        if eom in inpData:
            break
    inpData=inpData.strip()[:-len(eom)]
    serversaid(inpData.replace('\n', ' [N] ')[:90])
    return inpData.strip()

def sendsocket(sock,msg):
    msg += eom
    totalsent=0
    MSGLEN = len(msg) 
    while totalsent < MSGLEN:
        sent = sock.send(msg[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent
    isaid(msg)
    
def serversaid(msg):
    print("Server: %s"%msg[:80])
def isaid(msg):
    print("Client: %s"%msg[:80])

if __name__=="__main__":
    # os.system("make")
    try:
        sendsocket(s, teamname)
        input=readsocket(s)

        orange_file = open("orange_input.txt", "w", 0)
        orange_file.write(input)
        os.system("./orange 0");
        # print "GOT NODES N'EDGES\n"

        while True:
            input = readsocket(s)
            # print "GOT FIRST STATE\n"

            if input == "0" or input == "":
                break

            orange_file = open("orange_input.txt", "w", 0)
            orange_file.write(input)
            os.system("./orange 1")
            solution = open("orange_output.txt", "r").read()
            print solution
            sendsocket(s,solution)
            # print "GREAT SUCCESS\n"
            # sendsocket(s,"0\n")

            # for testing, break immediately
            #input = readsocket(s)
            #orange_file = open("orange_input.txt", "w", 0)
            #orange_file.write(input)
            #os.system("./orange 1")
            #break;
  
    finally:
        print "Close socket"
        s.close()

