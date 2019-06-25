#!/usr/bin/env python3

# *****************************************************************************
#  Copyright (c) 2018 Fraunhofer IEM and others
#
#  This program and the accompanying materials are made available under the
#  terms of the Eclipse Public License 2.0 which is available at
#  http://www.eclipse.org/legal/epl-2.0
#
#  SPDX-License-Identifier: EPL-2.0
#
#  Contributors: Daniel Siegel @ Fraunhofer IEM
# *****************************************************************************



#When contributing, please make sure to stick to PEP8 as much as possible.
#https://www.python.org/dev/peps/pep-0008/

import paho.mqtt.client as mqtt
import time
import json

class SyscallFormatter(object):
    
    def __init__(self,BROKER_IP="test.mosquitto.org"):
        '''Takes BROKER IP as string as argument'''
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        try:
            self.client.connect(BROKER_IP)
            print("Connected to Broker at {0}".format(BROKER_IP))
        except Exception:
            print("BROKER connection failed")
            raise SystemExit(0)
        print("Starting syscall-formatter MQTT client loop.")
        try:
            self.client.loop_forever()
        except Exception as e:
            print(str(e))
            print("Client loop failed to start.")

        

    def on_message(self,client,userdata,msg):
        """MQTT Callback function for handling received messages"""
        decoded_msg = ""
        try:
            #payload is bytes array, decode using utf-8
            decoded_msg  = str(msg.payload,'utf-8')
            datadict = json.loads(decoded_msg)

            temp = self.parse(datadict['data'])
            datadict['data'] = temp

            json_data = json.dumps(datadict)
            self.client.publish("REFINED",json_data)
        except Exception as e:
            print("Couldn't decode message, check error {0}".format(type(e)))
        
    
    
    def on_connect(self,client,userdata,flags,rc):
        print("Subscribing to TRACED")
        self.client.subscribe("TRACED") 

    def parse(self,data):
        print("New message")
        split_msg = data.split("(", 1)[0]
        split_msg = split_msg.split(" ",1)[1]
        return split_msg

    def publish(self,topic,data):
        print("Publishing parsed message")
        """Using the paho mqtt implementation, publish trace on a certain topic."""
        try:
            self.client.publish(topic,data)
        except Exception as e:
            print("Failed to publish message with the following error {0}".format(str(e)))


if __name__ == "__main__":
     SyscallFormatter =  SyscallFormatter("test.mosquitto.org")
        
