#Error list:
#E404: Connection not established
#E99 : Parameters out of range
#E2  : Function aborted (user)

#tkmessagebox not working

import socket
import struct
import sys
import os
import datetime
import time
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import *

client_path = r"C:\Users\Public\3dScannerCode\Client.py"

multicast_group = ('224.0.0.10', 10000)

connection_number = -1

# Create the datagram socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set a timeout so the socket does not block indefinitely when trying
# to receive data.
sock.settimeout(3)

connection_list = []

# Set the time-to-live for messages to 1 so they do not go past the
# local network segment.
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

def acknowledge(command):
    global connection_number
    global connection_list
    x = 0
    
    try:
        # Send data to the multicast group
        sent = sock.sendto(str.encode(command), multicast_group)
        
        # Look for responses from all recipients
        while True:
            try:
                data, server = sock.recvfrom(32)
                
                if command[0:5] == "photo" and str(server)[2:16] == connection_list[0]:
                    x += 1
                    tk.Label(window, text="{0} photos done".format(x)).grid(column=1, row=0)
                if command == "connect":
                    connection_number += 1
                    connection_list.append(connection_number)
                    #grabs client IP adresses, depends on input string
                    connection_list[connection_number] = str(server)[2:16]
                    #print(connection_list[n])
                    

            except socket.timeout:
                if not connection_list and command == "connect":
                   print("Connection failed, please repeat connect function")
                   return(1)
                print ('%s finished succesfully!' %command)
                break
            else:
                print (data.decode() + str(server))
                
    finally:
        return (1)
    
def connection_check():
    if not connection_list:
        print("Connection not yet established, please run connect function")
        return (0)
    return (1)

def connect():
    global connection_number
    connection_number = -1
    acknowledge("connect")
    
    if connection_check() == 1:
        return (1)
    return (404)

def photo():
    global connection_list
    
    if connection_check() == 1:
        par1 = amount.get()
        par2 = delay.get()
        if (par1.isdigit() and par2.isdigit()):
            if (int(par1) <= 50 and float(par2) <= 2):
                message = ("photo" + " " + par1 + " " + par2)
                # Send data to the multicast group
                print ('sending "%s"' % message)

                # Look for responses from all recipients
                acknowledge(message)
                return (1)
            print("Parameters out of range, max 50 photos at a 2 second delay.")
            return(99)
        print("Wrong input, please enter numbers only.")
        return(99)
    return (404)

def download():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')
    global connection_number
    global connection_list
    
    if connection_check() == 1:
    
        print("Downloading photos")
        na = folder.get()
        if not os.path.exists("c:\Temp\_pifotos\%s" %na):
            os.system ('mkdir c:\Temp\_pifotos\%s' %na)
        else:
            result = mb.askquestion("Folder already exists", "Are you sure you wish to overwrite an existing folder?", icon='warning')
            if result == "no":
                print("Download aborted")
                return(2)
        for x in range (0, connection_number+1):
            os.system('pscp.exe -pw protoscan1 pi@{0}:/home/pi/Desktop/photos/*.jpg c:\Temp\_pifotos\{1}\\'.format (connection_list[x], na))
        
        print("download complete!")
        return (1)
    return (404)
   
def sync():
    global connection_number
    global connection_list
    
    if connection_check() == 1:
    
        for x in range (0, connection_number+1):
            os.system(r'pscp.exe -pw protoscan1 {0} pi@{1}:/home/pi'.format (client_path, connection_list[x]))
        print("sync complete!")
        return (1)
    return (404)
    
def reboot():
    if connection_check() == 1:
        acknowledge("reboot")
        return (1)
    return (404)
        
def kill():
    if connection_check() == 1:
        acknowledge("kill")
        return (1)
    return (404)

window = tk.Tk()
window.title("3D Scanner")
window.geometry("400x400")

amount = tk.StringVar()
delay = tk.StringVar()
folder = tk.StringVar()

tk.Label(window, text="Amount").grid(column=0, row=1)
tk.Entry(window, width=6, textvariable=amount).grid(column=1, row=1, sticky=W)
tk.Label(window, text="max. 50").grid(column=2, row=1, sticky=W)

tk.Label(window, text="Delay").grid(column=0, row=2)
tk.Entry(window, width=6, textvariable=delay).grid(column=1, row=2, sticky=W)
tk.Label(window, text="max. 3").grid(column=2, row=2, sticky=W)

tk.Label(window, text="Folder").grid(column=0, row=4)
tk.Entry(window, width=10, textvariable=folder).grid(column=1, row=4, sticky=W)


tk.Button(width=8, text="Photos", command=photo).grid(column=0, row=0, sticky=W)
tk.Button(width=8, text="Download", command=download).grid(column=0, row=3, sticky=W)
tk.Button(width=8, text="Sync", command=sync).grid(column=0, row=5, sticky=W)
tk.Button(width=8, text="Reboot", command=reboot).grid(column=0, row=6, sticky=W)
tk.Button(width=8, text="Connect", command=connect).grid(column=0, row=7, sticky=W)
tk.Button(width=8, text="Kill", command=kill).grid(column=0, row=8, sticky=W)

acknowledge("connect")

window.mainloop()