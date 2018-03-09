#os.system functies werken niet goed, wel als de actie kort genoeg is. Lijkt zichzelf af te kappen na x tijd/data, vooral Sync functie (DL max ~ 26)

import socket
import struct
import sys
import os
import datetime
import time
import tkinter as tk
from tkinter import *

client_path = r"C:\Users\Public\3dScannerCode\Client.py"

multicast_group = ('224.0.0.10', 10000)

# Create the datagram socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set a timeout so the socket does not block indefinitely when trying
# to receive data.
sock.settimeout(3)

# Set the time-to-live for messages to 1 so they do not go past the
# local network segment.
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

def acknowledge(command):
    try:
        # Send data to the multicast group
        sent = sock.sendto(str.encode(command), multicast_group)

        # Look for responses from all recipients
        while True:
            try:
                data, server = sock.recvfrom(32)
            except socket.timeout:
                print ('%s finished!' %command)
                break
            else:
                print (data.decode() + str(server))       
    finally:
        #print ('closing socket')
        #sock.close()
        #input("Press Enter to continue...")          
        return (1)

def photo():
    par1 = aantal.get()
    par2 = delay.get()
    message = ("photo" + " " + par1 + " " + par2)
        
    # Send data to the multicast group
    print ('sending "%s"' % message)

    # Look for responses from all recipients
    acknowledge(message)

def download():
    na = folder.get()
    print("downloading photos")
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')
    os.system ('mkdir c:\Temp\_pifotos\%s' %na)
    os.system('pscp.exe -pw protoscan1 pi@192.168.178.20:/home/pi/Desktop/photos/*.jpg c:\Temp\_pifotos\%s\\' %na)
    os.system('pscp.exe -pw protoscan1 pi@192.168.178.21:/home/pi/Desktop/photos/*.jpg c:\Temp\_pifotos\%s\\' %na)
    os.system('pscp.exe -pw protoscan1 pi@192.168.178.22:/home/pi/Desktop/photos/*.jpg c:\Temp\_pifotos\%s\\' %na)
    print("download complete!")
   
def sync():
    os.system(r'pscp.exe -pw protoscan1 %s pi@192.168.178.20:/home/pi' % client_path)
    os.system(r'pscp.exe -pw protoscan1 %s pi@192.168.178.21:/home/pi' % client_path)
    os.system(r'pscp.exe -pw protoscan1 %s pi@192.168.178.22:/home/pi' % client_path)
    print("sync complete!")
    
def reboot():
    acknowledge("reboot")

def status():
    acknowledge("status")
        
def kill():
    acknowledge("kill")


window = tk.Tk()
window.title("3D Scanner")
window.geometry("400x400")

aantal = tk.StringVar()
delay = tk.StringVar()
folder = tk.StringVar()

tk.Label(window, text="Aantal").grid(column=0, row=1)
tk.Entry(window, width=6, textvariable=aantal).grid(column=1, row=1, sticky=W)

tk.Label(window, text="Delay").grid(column=0, row=2)
tk.Entry(window, width=6, textvariable=delay).grid(column=1, row=2, sticky=W)

tk.Label(window, text="Folder").grid(column=0, row=4)
tk.Entry(window, width=10, textvariable=folder).grid(column=1, row=4, sticky=W)


tk.Button(width=8, text="Photos", command=photo).grid(column=0, row=0, sticky=W)
tk.Button(width=8, text="Download", command=download).grid(column=0, row=3, sticky=W)
tk.Button(width=8, text="Sync", command=sync).grid(column=0, row=5, sticky=W)
tk.Button(width=8, text="Reboot", command=reboot).grid(column=0, row=6, sticky=W)
tk.Button(width=8, text="Status", command=status).grid(column=0, row=7, sticky=W)
tk.Button(width=8, text="Kill", command=kill).grid(column=0, row=8, sticky=W)

window.mainloop()