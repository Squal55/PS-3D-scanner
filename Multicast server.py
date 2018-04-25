import socket
import struct
import sys
import os
import datetime
import time
import tkinter as tk

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
                print ('timed out, no more responses')
                break
            else:
                print (data.decode() + str(server))       
    finally:
        print ('closing socket')
        sock.close()
        input("Press Enter to continue...")          
    return (1)

def photo():
    par1 = input("Amount: ")
    par2 = input("Delay: ")
    message = (message + " " + par1 + " " + par2)
        
    # Send data to the multicast group
    print ('sending "%s"' % message)

    # Look for responses from all recipients
    acknowledge(message)

def download():
    na = input("Name folder: ")
    print("Downloading photo's")
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')
    os.system ('mkdir c:\Temp\_pifotos\%s' %na)
    os.system('pscp.exe -pw protoscan1 pi@192.168.178.20:/home/pi/Desktop/photos/*.jpg c:\Temp\_pifotos\%s\\' %na)
    os.system('pscp.exe -pw protoscan1 pi@192.168.178.21:/home/pi/Desktop/photos/*.jpg c:\Temp\_pifotos\%s\\' %na)
    os.system('pscp.exe -pw protoscan1 pi@192.168.178.22:/home/pi/Desktop/photos/*.jpg c:\Temp\_pifotos\%s\\' %na)
    input("Press Enter to continue...")
   
def sync():
    os.system(r'pscp.exe -pw protoscan1 c:\Users\sijme_000\Desktop\Client.py pi@192.168.178.20:/home/pi')
    os.system(r'pscp.exe -pw protoscan1 c:\Users\sijme_000\Desktop\Client.py pi@192.168.178.21:/home/pi')
    os.system(r'pscp.exe -pw protoscan1 c:\Users\sijme_000\Desktop\Client.py pi@192.168.178.22:/home/pi')
    time.sleep(3)
    input("Press Enter to continue...")
    
def message():
    acknowledge(message)

def status():
    acknowledge(message)
        
def kill():
    acknowledge(message)


window = tk.Tk()
window.title("3D Scanner")
window.geometry("400x400")

photo_button = tk.Button(text="Photo")
photo_button.grid(column=0, row=0)

download_button = tk.Button(text="Download")
download_button.grid(column=0, row=1)

window.mainloop()