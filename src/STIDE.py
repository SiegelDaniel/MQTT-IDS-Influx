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
import os
import simplejson
import sys
import config_handler


class STIDE(object):

    def __init__(self):

        self.cfg_handler = config_handler.config_loader("./config.json")
        self.config      = self.cfg_handler.get_config("STIDE")


        #CONFIGURATION RELEVANT
        self.DB_USER       = self.cfg_handler.get_config_point("DB_USER",self.config)
        self.DB_PW         = self.cfg_handler.get_config_point("DB_PW",self.config)
        self.DB_HOST       = self.cfg_handler.get_config_point("DB_HOST",self.config)#"../Traces.sqlite"
        self.BROKER_IP     = self.cfg_handler.get_config_point("BROKER_IP",self.config)
        self.STORAGE_MODE  = self.cfg_handler.get_config_point("STORAGE_MODE",self.config)
        self.WINDOW_SIZE   = self.cfg_handler.get_config_point("WINDOW_SIZE",self.config)

        #NOT CONFIGURATION RELEVANT
        self.DB_CURSOR     = None
        self.DB_CONNECTION = None
        self.call_list =  []

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_log     = self.on_log

        print("Trying to connect to MQTT Broker")
        self.client.connect(self.BROKER_IP)
        print("Connected to MQTT Broker")
        self.client.loop_forever()


    def compare(self,a,b):
        """Compares two lists element-wise, logs mismatches.
        Args:
            a: First list  (should be from the database set)
            b: Second list (should be from the tracing module)
        """
        print("Comparing {0} to {1}".format(str(a),str(b)))
        if len(a) == len(b):
            print("Checking {0} against {1}".format(str(a),str(b)))
            for index in range(len(a)):
                if a[index] != b[index]:
                    print("Mismatch detected at index {0}. \n DB Trace: {1} \n To compare: {2}".format(str(index),str(a),str(b)))
                    self.publish("ANOMALY",str(a))
                else:
                    print("DB Trace:{0} \n Trace:{1} matched".format(str(a),str(b)))

    def publish(self,topic, data):
        """Using the paho mqtt implementation, publish trace on a certain topic."""
        print("Publishing {0}".format(str(data)))
        self.client.publish(topic,data)
    
    def on_connect(self,client, userdata, flags, msg):
        self.connect_to_db()
        self.client.subscribe("REFINED")
        print("Subscribed to MQTT topic REFINED ")

    def STIDE(self,to_compare):
        """sequence time delay embedding:
        Takes an ordered list of system calls. This list is of length WINDOW_SIZE. 
        Gets all fitting datasets from the database and compares accordingly.
        
        Args:
            to_compare: List of length WINDOW_SIZE that contains the ordered systemcalls to compare."""
        print("Starting sTIDE")
        head = to_compare[0]
        SQL = "SELECT * FROM Traces{0} WHERE Trace0 = ?".format(str(self.WINDOW_SIZE))
        try:
            self.DB_CURSOR.execute(SQL,(head,))
            db_results = self.DB_CURSOR.fetchall()
        except Exception as e:
            db_results = []
            print("Exception during STIDE, couldn't retrieve data from DB. See: \n {0}".format(str(e)))
        if db_results == []:
            self.publish("ANOMALY",str(to_compare))
            print("Database is empty.")
            return
        else:
            match_found = False
            for x_tupel in db_results:
                calls = list(x_tupel)
                if to_compare == calls:
                    match_found = True
            if match_found == False:
                self.publish("ANOMALY",str(to_compare))
                print("Database is not empty, but no match for {0} is found.".format(str(to_compare)))

    def insert(self,processinfo,syscalls):
        """
        Takes processinfo (either PID or PNAME as strings) and syscalls as list of strings as arguments
        """
        print("Inserting {0} into database".format(str(syscalls)))
        #build the query depending on window size
        SQL_STATEMENT = self._build_insert_query(self.WINDOW_SIZE)
        try:
            self.DB_CURSOR.execute(SQL_STATEMENT,tuple(syscalls))
            self.DB_CONNECTION.commit()
        except Exception as e:
            if isinstance(e,sqlite3.IntegrityError):
                pass
            else:
                print("Exception during insert {0}".format(str(e)))

    def _build_insert_query(self,windowsize):
        """Used to build the insert query depending on the window size"""
        start = "INSERT INTO TRACES{0}(".format(str(windowsize))
        mid   = ""
        for i in range(0,windowsize-1):
            mid = mid + "Trace{0},".format(str(i))
        mid = mid + "Trace{0})".format(str(windowsize-1))
        mid = mid + " VALUES "
        end = "("
        for j in range(0,windowsize-1):
            end = end + "?,"
        end = end + "?)"

        query = start + mid + end 
        return query

    def _build_creation_query(self,windowsize):
        start = "CREATE TABLE IF NOT EXISTS Traces{0} (".format(str(windowsize))
        columns = ""
        primary_keys = ""
        for i in range(0,windowsize):
            columns = columns + "Trace{0} TEXT NOT NULL,".format(str(i))
            primary_keys = primary_keys + "Trace{0},".format(str(i))
        primary_keys = primary_keys[:-1]
        end = "PRIMARY KEY ({0}))".format(primary_keys)
        return start + columns + end 

    def on_message(self,client, userdata, msg):
        """Callback function for handling received messages"""


        datadict = simplejson.loads(str(msg.payload,'utf-8'))

        data = datadict['data']
        processname = datadict['processname']

        if len(self.call_list) != self.WINDOW_SIZE:
            self.call_list.append(data)
        else:
            if self.DB_CONNECTION is not None:
                if self.STORAGE_MODE == True:
                    self.insert(processname,self.call_list)
                    self.call_list = self.call_list[1:]
                else:
                    self.STIDE(self.call_list)
                    self.call_list = self.call_list[1:]

    def on_log(self,client, userdata, level, buf):
        """Uses the built-in logger to output errors and events of interest"""
        print("log: ",buf)

    def connect_to_db(self):
        """Used to establish a connection to the database using parameters parsed from configuration file"""
        print("Establishing DB connection")
        dir_path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(dir_path, self.DB_HOST)
        path = os.path.normpath(path)
        
        try:
            self.DB_CONNECTION = sqlite3.connect(path)
            self.DB_CURSOR = self.DB_CONNECTION.cursor()
            self.DB_CURSOR.execute(self._build_creation_query(self.WINDOW_SIZE))
            self.DB_CONNECTION.commit()
            print("Established DB connection")
        except sqlite3.Error as e:
            print("Error connecting to DB: {0}".format(str(e)))




if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--learn":
            stide = STIDE()
        else:
            stide = STIDE()
    