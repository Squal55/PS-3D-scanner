#Error list:
#E404: Connection not established
#E99 : Parameters out of range
#E50 : No data available
#E2  : Function aborted (user)

import threading
import logging
import socket
import struct

import sys
import os
import re

import datetime
import time

import PIL.Image
from PIL import ImageTk
from tkinter import messagebox as mb
from tkinter import *

import tkinter as tk
import cv2

client_path = r"C:\Users\Public\3dScannerCode\Client.py"
reload_path = r"C:\Users\Public\3dScannerCode\Reload.py"

multicast_group = ('224.0.0.10', 10000)

download_flag = 1
connection_number = -1
current_thread = 0

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')

# RE float checker
float_check = re.compile('\d+(\.\d+)?')

# Create the datagram socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set a timeout so the socket does not block indefinitely when trying
# to receive data.
sock.settimeout(1)

connection_list = []

# Set the time-to-live for messages to 1 so they do not go past the
# local network segment.
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

def counter():
    global download_flag
    x = 5
    
    download_message = "Downloading photos"
    
    while not download_flag:

        downloadpro_label.config(text = download_message)
        x = x + 1
        
        if x >= 5:
            download_message = download_message + '.'
            if x == 10:
                x = -5
                
        elif x <= 0:
            download_message = download_message[:-1]
            if x == 0:
                x = 5
            
        time.sleep(.25)
        
    downloadpro_label.config(text = "Download complete!")  
    return(1)

def acknowledge(command):
    global connection_number
    global connection_list
    photo_number = -1
    current_photo = 0
    x = 0
    
    try:
        # Send data to the multicast group
        sock.sendto(str.encode(command), multicast_group)
        data_flag = 0
        
        # Look for responses from all recipients
        while True:
            try:
                data, server = sock.recvfrom(32)
                photo_number += 1
                
                if photo_number == connection_number:
                    current_photo += 1
                    photo_number = -1
                    sock.sendto(str.encode(str(current_photo)), multicast_group)
                    
                data_flag = 1
                
                
                if command[0:5] == "photo" and str(server)[2:16] == connection_list[0]:
                    x += 1
                    tk.Label(window, text="{0} photo(s) done".format(x)).grid(column=1, row=0, sticky=W)
                if command == "connect":
                    connection_number += 1
                    connection_list.append(connection_number)
                    #grabs client IP adresses, depends on input string
                    connection_list[connection_number] = str(server)[2:16]
                    #print(connection_list[n])
                    

            except socket.timeout:
                if not connection_list and command == "connect":
                    print("Connection failed, please repeat connect function")
                    return(404)
                if data_flag == 0:
                    print("No data retrieved, please repeat connect function")
                    return(50)
                print ('%s finished succesfully!' %command)
                if command[0:5] == "photo":
                    sent = sock.sendto(str.encode("light"), multicast_group)
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
    sock.settimeout(1)
    global connection_number
    connection_number = -1
    acknowledge("connect")
    tk.Label(window, text="{0} camera(s) connected".format(connection_number + 1)).grid(column=1, row=7, sticky=W)
    
    if connection_check() == 1:
        return (1)
    return (404)

def photo():
    sock.settimeout(6)
    global connection_list
    
    if connection_check() == 1:
        par1 = amount.get()
        par2 = delay.get()
        if (par1.isdigit() and (par2.isdigit() or float_check.match(par2))):
            if (int(par1) <= 50 and float(par2) <= 5):
                message = ("photo" + " " + par1 + " " + par2)
                # Send data to the multicast group
                print ('sending "%s"' % message)

                # Look for responses from all recipients
                acknowledge(message)
                return (1)
            print("Parameters out of range, max 50 photos at a 5 second delay.")
            return(99)
        print("Wrong input, please enter numbers only.")
        return(99)
    return (404)

def download():
    global ts
    global st
    global connection_number
    global connection_list
    global download_flag
    
    download_flag = 0
    
    counter_thread = threading.Thread(target=counter)
    counter_thread.start()
    
    if connection_check() == 1:
        
        download_message = "Downloading photos"
        print(download_message)
        
        na = folder.get()
        if not os.path.exists("c:\Temp\_pifotos\%s" %na):
            os.system ('mkdir c:\Temp\_pifotos\%s' %na)
        else:
            result = mb.askquestion("Folder already exists", "Are you sure you wish to overwrite an existing folder?", icon='warning')
            if result == "no":
                print("Download aborted")
                download_flag = 1
                return(2)
        for x in range (0, connection_number+1):
            os.system('pscp.exe -pw protoscan1 pi@{0}:/home/pi/Desktop/photos/*.jpg c:\Temp\_pifotos\{1}\\'.format (connection_list[x], na))
        
        print("download complete!")
        download_flag = 1
        return (1)
    return (404)
   
def sync():
    global st
    global connection_number
    global connection_list
    
    if connection_check() == 1:
    
        for x in range (0, connection_number+1):
            os.system(r'pscp.exe -pw protoscan1 {0} pi@{1}:/home/pi'.format (client_path, connection_list[x]))
            os.system(r'pscp.exe -pw protoscan1 {0} pi@{1}:/home/pi'.format (reload_path, connection_list[x]))
        print("sync complete!")
        reload()
        tk.Label(window, text="Last synced : {0}".format(st)).grid(column=1, row=5)
        
        return (1)
    return (404)
    
def reload():
    sock.settimeout(1)
    if connection_check() == 1:
        acknowledge("reload")
        return (1)
    return (404)
        
def kill():
    sock.settimeout(1)
    if connection_check() == 1:
        result = mb.askquestion("Kill program", "Are you sure you wish to kill the current script?", icon='warning')
        if result == "no":
            print("Kill aborted")
            return(2)
        else:
            acknowledge("kill")
            return (1)
    return (404)

def preview():
    sock.sendto(str.encode('preview'), multicast_group)
    while True:
        os.system('pscp.exe -pw protoscan1 pi@192.168.178.20:/home/pi/Desktop/preview/preview.jpg c:\Temp\_pifotos\Preview\\')
        img = ImageTk.PhotoImage(PIL.Image.open('c:\Temp\_pifotos\Preview\preview.jpg'))
        panel = tk.Label(root, image = img)
        panel.pack(side = "bottom", fill = "both", expand = "yes")
        

commands = {0 : photo,
            1 : download,
            2 : sync,
            3 : reload,
            4 : connect,
            5 : kill,
            6 : preview,
}

def button(command_number):
    global current_thread
    
    if current_thread.isAlive():
        print("Process still running, please wait")
    else:
        current_thread = threading.Thread(target=commands[command_number])
        current_thread.start()

window = tk.Tk()
window.title("3D Scanner")
window.geometry("400x400")

amount = tk.StringVar()
delay  = tk.StringVar()
folder = tk.StringVar()

photo_label     = tk.Label(window, text="Amount").grid(column=0, row=1)
photo_entry     = tk.Entry(window, width=6, textvariable=amount).grid(column=1, row=1, sticky=W)
max_photo_label = tk.Label(window, text="max. 50").place(x=120, y=25)

delay_label     = tk.Label(window, text="Delay").grid(column=0, row=2)
delay_entry     = tk.Entry(window, width=6, textvariable=delay).grid(column=1, row=2, sticky=W)
max_delay_label = tk.Label(window, text="max. 5s").place(x=120, y=45)

download_label  = tk.Label(window, text="Folder").grid(column=0, row=4)
download_entry  = tk.Entry(window, width=10, textvariable=folder).grid(column=1, row=4, sticky=W)

photos_button   = tk.Button(width=8, text="Photos",   command= lambda: button(0)).grid(column=0, row=0, sticky=W)
download_button = tk.Button(width=8, text="Download", command= lambda: button(1)).grid(column=0, row=3, sticky=W)
sync_button     = tk.Button(width=8, text="Sync",     command= lambda: button(2)).grid(column=0, row=5, sticky=W)
reload_button   = tk.Button(width=8, text="Reload",   command= lambda: button(3)).grid(column=0, row=6, sticky=W)
connect_button  = tk.Button(width=8, text="Connect",  command= lambda: button(4)).grid(column=0, row=7, sticky=W)
kill_button     = tk.Button(width=8, text="Kill",     command= lambda: button(5)).grid(column=0, row=8, sticky=W)
preview_button  = tk.Button(width=8, text="Preview",  command= lambda: button(6)).grid(column=0, row=9, sticky=W)

downloadpro_label = tk.Label(window, text=" ")
downloadpro_label.grid(column=1, row=3, sticky=W)

current_thread = threading.Thread(target=commands[4])
current_thread.start()

window.mainloop()