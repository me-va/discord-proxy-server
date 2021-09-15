from threading import RLock
import requests
import socket
import threading
import time
import pickle
import numpy

#Consts
HOST            = "127.0.0.1"        
PORT            = 8080              
COOLDOWN        = 10                 # Time to server wait for new send for the same ip
DISCORDCOOLDOWN = 3                  # Time to server wait for send new message to discord
AUTHORIZATION   = {"authorization":"..."}# userid
SERVER          = "https://discord.com/api/v9/channels/863844469076918283/messages"# channel to send messages
MAXBUFF         = 8000000 # max binary data buffor (8mb without nitro)
ONATTACKTRIGGER = 10 # messages from the same ip in a row (ddos protection) 


#Global Variable
blacklist = dict()
lock = RLock()
datatosend = numpy.array([])
lastip = dict()
conncounter = 0


def blacklistpresent(ip):
    if ip[0] in blacklist:
        return False



def sendtodiscord():
    global datatosend
    while True:
        time.sleep(DISCORDCOOLDOWN)
        if datatosend.size != 0:
            print(datatosend.size)
            data = datatosend[len(datatosend) -1 ]
            datatosend = numpy.delete(datatosend, -1)
            x = requests.post(SERVER,files=(dict(file=data)),headers=AUTHORIZATION)
            if x.status_code != 200:
                print(f"Sending Erorr {x.status_code}")

def secure(ip):
    global conncounter

    if ip == lastip:
        conncounter += 1
    
    if conncounter == 10:
        blacklist[ip] = 0
    
    if ip != lastip:
        conncounter = 0
    



def cooldown(ip):
    if ip[0] in lastip:
        return True
    with lock:
        lastip.update({ip[0]:ip[1]})
    return False

def cooldowncheck():
    while True:
        time.sleep(COOLDOWN)
        with lock:
            try:
                lastip.popitem()
            except:
                pass
        
def closeserver():
    with open('blacklist.pickle', 'wb') as handle:
        pickle.dump(blacklist, handle, protocol=pickle.HIGHEST_PROTOCOL)

def pushdata(data):
    global datatosend
    datatosend = numpy.append(datatosend,data)
    print(datatosend)


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print("Server Started On " + HOST + str(PORT))
        try: 
            with open('blacklist.pickle', 'rb') as handle:
                print("Blacklist Loaded")
                global blacklist
                blacklist = pickle.load(handle)
        except IOError:
            print("No Blacklist Present")

        threading.Thread(target=cooldowncheck).start()
        threading.Thread(target=sendtodiscord).start()
        try:
            while True:
                conn, addr = s.accept()
                if not blacklistpresent(addr):
                    secure(addr)
                    if cooldown(addr):
                        continue
                    with conn:
                        print('Connected by', addr)
                        while True:
                            data = conn.recv(MAXBUFF)
                            if len(data) > MAXBUFF: break
                            if not data: break
                            pushdata(data)
                else:
                    pass
        except KeyboardInterrupt:
            print("Closing Server")
            closeserver()
            return


if __name__ == "__main__":
    main()
