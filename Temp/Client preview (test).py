import socket
import os
import struct
import fcntl
import sys
import picamera
import time
import shutil
import RPi.GPIO as GPIO
  
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

dir = 'Desktop/photos'

multicast_group = '224.0.0.10'
server_address = ('', 10000)

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to the server address
sock.bind(server_address)

#Init GPIO
ledpin = 7
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(ledpin, GPIO.OUT)
GPIO.output(ledpin, True)

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
        print ('received photo')
        photo_flag = 0
        photo_number = 0
        photo_string = "0"
        if os.path.exists(dir):
            os.system("sudo rm -rf %s" %dir)
        os.makedirs(dir)
        clear()
        
        #Turn on lighting
        GPIO.output(ledpin, False)
        
        #Camera settings
        camera = picamera.PiCamera()
        camera.resolution = (2592, 1944)
        camera.framerate = 30
        camera.brightness = 50
        camera.awb_mode = 'off'
        camera.awb_gains = (1.5,1.5)
        camera.iso = 200
        camera.exposure_mode = 'off'
        camera.shutter_speed = 9000
        cameradelay = 0.55

        
        #Make photos
        for x in range(int(par1)):
            
            while(photo_number > photo_flag):
                photo_string, address = sock.recvfrom(1024)
                photo_flag = int(photo_string)
                
            camera.capture('/home/pi/%s/%s_%d.jpg' % (dir, get_ip_address('eth0'), x+1))
            sock.sendto("Photo: " + str(x+1), address)
            photo_number += 1
            time.sleep(float(par2)-(cameradelay))
        
        #Free-up the camera
        camera.close()
        
    elif command == 'light':
        #Turn off lighting
        GPIO.output(ledpin, True)
            
    elif command == 'download':
        sock.sendto("Acknowledge " + command, address)
        #Send photos
        #for x in range(amount):
    
    elif command == 'reload':
        sock.sendto("Acknowledge " + command, address)
        sock.close()
        os.system("sudo python Reload.py")
        
    elif command == 'kill':
        sock.sendto("Acknowledge " + command, address)
        sys.exit()
        
    elif command == 'connect':
        print("Connect")
        sock.sendto("Acknowledge " + command, address)

#Preview test
    elif command == 'preview':
        
        camera = picamera.PiCamera()
        camera.resolution = (320, 640)
        camera.framerate = 30
        camera.brightness = 50
        camera.awb_mode = 'off'
        camera.awb_gains = (1.5,1.5)
        camera.iso = 200
        camera.exposure_mode = 'off'
        camera.shutter_speed = 9000
        cameradelay = 0.55
        
        if os.path.exists('Desktop/preview'):
            os.system("sudo rm -rf Desktop/preview")
        os.makedirs('Desktop/preview')
        
        while True:
            camera.capture('/home/pi/Desktop/preview/preview.jpg')
    
    else:
        if not command.isdigit():
            sock.sendto("Received wrong command", address)
            print ('Received wrong command')

