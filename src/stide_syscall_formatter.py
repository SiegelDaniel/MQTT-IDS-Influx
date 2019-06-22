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
import simplejson

class SyscallFormatter(object):
    
    def __init__(self,BROKER_IP="test.mosquitto.org"):
        '''Takes BROKER IP as string as argument'''
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        try:
            self.client.connect(BROKER_IP)
        except Exception:
            raise SystemExit(0)

        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.loop_start()
        

    def on_message(self,client,userdata,msg):
        """MQTT Callback function for handling received messages"""
        datadict = simplejson.loads(msg)

        temp = self.parse(datadict['data'])
        datadict['data'] = temp

        json = simplejson.dumps(datadict)
        self.client.publish('REFINED',json)
    
    
    def on_connect(self,client,userdata,flags,rc):
        self.client.subscribe("TRACED") 

    def parse(self,data):
        split_msg = data.split("(", 1)[0]
        split_msg = split_msg.split(" ",1)[1]
        return split_msg

    def publish(self,topic,data):
        """Using the paho mqtt implementation, publish trace on a certain topic."""
        self.client.publish(topic,data)


if __name__ == "__main__":
     SyscallFormatter =  SyscallFormatter("test.mosquitto.org")
        