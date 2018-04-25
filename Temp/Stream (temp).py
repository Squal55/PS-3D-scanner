import cv2
import urllib
import urllib.request
import numpy as np
import tkinter
from PIL import Image, ImageTk
import threading

root = tkinter.Tk()
image_label = tkinter.Label(root)  
image_label.pack()

def cvloop():    
    #stream=open('C:/Users/Mr T/Downloads/curl-7.59.0-win32-mingw/curl-7.59.0-win32-mingw/bin/test.avi','rb')
    stream=urllib.request.urlopen("http://192.168.178.20:8000/stream.mjpg")
    streamBytes= bytes()
    while True:
        streamBytes+=stream.read(1024)
        a = streamBytes.find(b'\xff\xd8')
        b = streamBytes.find(b'\xff\xd9')
        if a!=-1 and b!=-1:
            jpg = streamBytes[a:b+2]
            streamBytes= streamBytes[b+2:]
            i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)            
            tki = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(i, cv2.COLOR_BGR2RGB)))
            image_label.configure(image=tki)                
            image_label._backbuffer_ = tki  #avoid flicker caused by premature gc
            #cv2.imshow('i',i)
        if cv2.waitKey(1) ==27:
            exit(0)  

thread = threading.Thread(target=cvloop)
thread.start()
root.mainloop()