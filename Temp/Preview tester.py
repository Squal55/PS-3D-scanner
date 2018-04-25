import urllib.request
import time

while True:
    urllib.request.urlretrieve("http://192.168.178.20:8000/stream.mjpg", "Preview_test.mjpg")