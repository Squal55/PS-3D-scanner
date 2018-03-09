import socket
import os
import struct
import fcntl
import sys
import picamera
import time
import shutil
  
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15].encode())
    )[20:24])

def clear():
    data = "0"
    command = "0" 

#camera setup
camera = picamera.PiCamera()
camera.resolution = (2592, 1944)
camera.framerate = 30
camera.brightness = 50
camera.awb_mode = 'off'
camera.awb_gains = (1.5,1.5)
camera.iso = 100
camera.shutter_speed = 10000
cameradelay = 0.55

dir = 'Desktop/photos'

multicast_group = '224.0.0.10'
server_address = ('', 10000)

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to the server address
sock.bind(server_address)

# Tell the operating system to add the socket to the multicast group
# on all interfaces.
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# Receive/respond loop
while True:
    print ('\nwaiting to receive message')
    data, address = sock.recvfrom(1024)
    
    print ('received %s bytes from %s' % (len(data), address))
    print (data)

    print ('sending acknowledgement to', address)
    
    if " " in data:
        command, par1, par2 = data.split(' ',2)
        print(data)
        print('command')
    else:
        command = data.decode()

# Check Message Data


    if command == 'photo':
        print ('Received photo')
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.makedirs(dir)
        clear()

        
        #Make photos
        for x in range(int(par1)):
            camera.capture('/home/pi/%s/%s_%d.jpg' % (dir, get_ip_address('eth0'), x+1))
            millis = int(round(time.time() * 1000))
            print(millis)
            time.sleep(int(par2)-(cameradelay))
            sock.sendto("Photo: " + str(x+1), address)
            
    elif command == 'download':
        sock.sendto("Acknowledge " + command, address)
        #Send photos
        #for x in range(amount):
    
    elif command == 'reboot':
        sock.sendto("Acknowledge " + command, address)
        os.system('sudo shutdown -r now')
        
    elif command == 'kill':
        sock.sendto("Acknowledge " + command, address)
        sys.exit()
        
    elif command == 'status':
        print("test")
        sock.sendto("Acknowledge " + command, address)
    
    else:
        sock.sendto("Received wrong command", address)
        print ('Received wrong command')

