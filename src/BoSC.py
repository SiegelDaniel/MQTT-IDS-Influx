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
#  Contributors: Fraunhofer IEM
# *****************************************************************************


#When contributing, please make sure to stick to PEP8 as much as possible.
#https://www.python.org/dev/peps/pep-0008/

import paho.mqtt.client as mqtt
import sqlite3
import simplejson

class BoSC(object):
    """Implements Bags of SystemCalls as mentioned in the README.md"""
    
    def __init__(self,windowsize,BROKER_IP):
        self.WINDOW_SIZE = windowsize

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_log     = self.on_log

        self.DB_CURSOR     = None
        self.DB_CONNECTION = None
        self.DB_PW         = None
        self.DB_HOST       = None

        self.syscall_LUT   = {}
        self.sliding_window= []

        self.load_lookup_table()
        self.validate_database()
        self.client.connect()
        self.client.loop_forever(BROKER_IP)

    def on_connect(self,client,userdata,flags,rc):
        """Consists of actions to take when the connection is established."""
        print("Subscribing to TRACED")
        self.client.subscribe("TRACED") 

    def on_log(self,client, userdata, level, buf):
        """Uses the built-in logger to output errors and events of interest"""
        print("log: ",buf)

    def connect_database(self,path):
        """Connects to the database and established a cursor and a connection"""
        try:
            self.DB_CONNECTION = sqlite3.connect(path)
            self.DB_CURSOR = self.DB_CONNECTION.cursor()
        except Exception as e:
            print(str(e), "couldn't connect to database at {0}".format(str(path)))

    def load_lookup_table(self):
        """Loads the systemcall LUT from a json file. 
        The file needs to fit the criteria mentioned in the paper which is linked in the README."""
        with open('data.txt') as json_file:
            self.syscall_LUT = simplejson.load(json_file)
        temporary = {}
        counter = 0
        #sorts the unordered dictionary and creates a mapping of syscalls to their indexes
        for key in sorted(self.syscall_LUT, key = self.syscall_LUT.get):
            temporary[key] = counter
            counter += 1
        self.syscall_LUT = temporary

    def validate_database(self):
        """Primarily checks whether the tables needed are present in the database. 
        Constructs them if not."""
        query = "CREATE TABLE IF NOT EXISTS BoSC (BAGS TEXT PRIMARY KEY);"
        try:
            self.DB_CURSOR.execute(query))
            self.DB_CONNECTION.commit()
        except Exception as e:
            print(str(e)," during database validation")

    def on_message(self,client,userdata,msg):
        '''Handles incoming MQTT messages'''

        datadict = simplejson.loads(str(msg.payload,'utf-8'))
        data = datadict['data']
        processname = datadict['processname']

        if len(self.sliding_window) == self.WINDOW_SIZE:
            self.construct_BoSC()
            self.sliding_window = self.sliding_window[1:]
            self.sliding_window.append(data)
            #construct BoSC from window, delete first, append last
        elif len(self.sliding_window) < self.WINDOW_SIZE:
            self.sliding_window.append(data)

    def construct_BoSC(self):
        '''Constructs a Bag of SystemCalls as described in the paper linked in the README.
        Utilizes self.sliding_window in combination with the syscall_LUT.
        Returns a list of integers'''
        bag_size = len(self.syscall_LUT.keys())
        #note bag must contain indexes for all keys and for "other"
        bag = [None] * bag_size+1
        for syscall in self.sliding_window:
            try:
                index = self.syscall_LUT[syscall]
                bag[index] += 1 #unsafe, change to atomic
            except KeyError:
                #key not found, append to "other"
                bag[-1] += 1 #unsafe, change to atomic

        return bag


