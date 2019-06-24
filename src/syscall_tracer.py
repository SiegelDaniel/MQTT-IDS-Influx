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
from subprocess import Popen, PIPE, STDOUT
import lxml
import threading
from datetime import datetime
import rfc3339
import simplejson
import psutil


class SyscallTracer(object):

    def __init__(self,PID,PNAME="",BROKER_IP="test.mosquitto.org"):
        self.PID = PID
        self.PNAME = PNAME
        self.BROKER_IP = BROKER_IP

        self.client = mqtt.Client()
        try:
            self.client.connect(self.BROKER_IP)
        except Exception:
            print("Connection to MQTT broker failed.")
            raise SystemExit(0)

        if self.PID != "" and self.PNAME == "":
            print("Tracing by PID")
            self.trace_by_pid()
            try:
                self.PNAME = self.get_process_name(self.PID)
            except Exception:
                print("PNAME assertion failed.")
        elif self.PID == "" and self.PNAME != "":
            self.trace_by_process()
        else:
            print("No PNAME or PID found")
            raise SystemExit(1)

        self.client.loop_start()

    def find_pids(self):
        import os
        process_ids = []
        try:
            process_ids =  [proc.pid for proc in psutil.process_iter() if proc.name() == self.PNAME]
        except:
            print("Process resolution failed.")
            raise SystemExit(0)
        if len(process_ids) > 0:
            return process_ids[0] 
        else:
            raise ValueError("Could not find a fitting process")

    
    def trace_by_pid(self):

        proc = Popen(['stdbuf', '-oL', 'strace', '-p',str(self.PID), '-tt'],
                    bufsize=1, stdout=PIPE, stderr=STDOUT, close_fds=True)
        for line in iter(proc.stdout.readline, b''):
            trace = str(line,'utf-8')
            self.send_trace(trace)
        proc.stdout.close()
        proc.wait()

    def get_process_name(self,pid):
        process = psutil.Process(int(pid))
        process_name = process.name()
        return process_name

    def trace_by_process(self):
        self.PID = self.find_pids()
        self.trace_by_pid()
        

    def send_trace(self,trace):
        print("Sending trace {0}".format(trace))
        date_string = rfc3339.rfc3339(datetime.now())
        datadict = {
            'timestamp' : date_string,
            'data' : trace,
            'processname': self.PNAME
        }

        self.client.publish('TRACED',simplejson.dumps(datadict))

if __name__ == "__main__":
    Tracer = SyscallTracer("1","","test.mosquitto.org")