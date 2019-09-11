import requests
import threading
import time
import paho.mqtt.client as mqtt

class Attack(object):

    def __init__(self):
        #start polling thread to simulate normal behaviour
        x = threading.Thread(target=self.poll_heise)
        x.start()

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect("test.mosquitto.org")
        self.client.loop_forever()

    def poll_heise(self):
        while(True):
            time.sleep(2)
            r = requests.get('https://heise.de')

    def on_connect(self):
        print("Connected to MQTT broker at test.mosquitto.org")
        self.client.subscribe("ATTACK")
    
    def on_message(self):
        for i in range(1,80):
            thread = threading.Thread(target=self.write_file,args=(i,))
            thread.start()

    def write_file(self,suffix):
        new_file = open("file{0}".format(suffix),"w")
        new_file.write("testtesttesttest")
        new_file.close()


    

    

