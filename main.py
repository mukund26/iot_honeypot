#! /usr/bin/python

import SocketServer
import sys
import socket
import datetime
import time
import subprocess
import threading
import database
import geoIP
import Gui5
import pdb 

gui_handle=None
opewrt_ip=""

TIMEOUT = 300
PROMPT = "/# "
BUXYBOX = "\x0d\x0a\x0d\x0a\x0d\x0aBusyBox v1.23.2 (2015.07.25 07:32:21 CEST) Built-in shell (ash)\x0d\x0a" \
          "Enter 'help' for a list of built-in commands.\x0d\x0a\x0d\x0a"
OPENWRT = "openwrt"

# known command dictionary
cmd_dict = {}
cmd_dict["test\x0d\x0a"] = "test\x0d\x0a"

class FrontEndResponder(SocketServer.StreamRequestHandler):
# The Handler class as frontend responder

    def __init__(self,request,client_address,server):
        self.attackerIP =""
        self.PORTNUMBER =""
        self.payload =""
        self.date =datetime.datetime.now()
        self.proxySocket = None
        SocketServer.StreamRequestHandler.__init__(self,request,client_address,server)
        SocketServer.TCPServer.allow_reuse_address = True

    def handle(self):
        global gui_handle
        self.receiveQueue = []
        self.attackerIP = self.client_address[0]
        self.serverport = self.server.server_address[1]
        self.serverip=self.server.server_address[0]
        self.attackerport=self.client_address[1]
        self.request.setblocking(0)
	
        print "%s IP %s.%s > %s.%s : try to connect" \
            % (self.date,self.attackerIP,self.client_address[1],\
              self.server.server_address[0],self.PORTNUMBER)
        th = BackEndResponder(self.attackerIP,self.serverport,self.request,self.receiveQueue)
        th.start()
        #create table for telnet in local sqlite db
        now=datetime.datetime.now()
        try:
            country=geoIP.coun(self.attackerIP)
        except :
            country="not found"
        gui_handle.updatePorts(str(self.serverport))
        gui_handle.updateAttackerIPs(self.attackerIP)
        gui_handle.updateUIlogs(str(now)[:10],str(now)[12:],self.attackerIP,str(self.attackerport),"->",self.serverip,str(self.serverport), "TCP", str(sys.getsizeof("")),country,"")
        database.table(str(now)[:10],str(now)[12:],self.attackerIP,self.attackerport,"->",self.serverip,self.serverport,"TCP",sys.getsizeof(""),country,"")       
        # main loop of FrontEndResponder
        while True:
            if (datetime.datetime.today() - self.date).seconds > TIMEOUT:
                break

            # receive response from Attacer
            try:
                self.payload = self.request.recv(8192)
                if len(self.payload) == 0:
                    break
                print "payload : {0}".format(self.payload)
                print "%s %s.%s > %s.%s" \
                % (self.date,self.attackerIP,self.client_address[1], self.request.getsockname()[0],self.request.getsockname()[1])
            
                #save incoming data from attacker in sqlitedb
                now=datetime.datetime.now()
                try:
                    country=geoIP.coun(self.attackerIP)
                except :
                    country="not found"
		
                database.table(str(now)[:10],str(now)[12:],self.attackerIP,self.attackerport,"->",self.serverip,self.serverport, "TCP", sys.getsizeof(self.payload),country,self.payload)  
                gui_handle.updateUIlogs(str(now)[:10],str(now)[12:],self.attackerIP,str(self.attackerport),"->",self.serverip,str(self.serverport),"TCP",str(sys.getsizeof(self.payload)),country,self.payload)
	             
                if len(self.payload) != 0:
                    print self.payload
                    #self.payload =  OPENWRT+"\x0d\x0a"

                    # known command
                    if cmd_dict.has_key(self.payload) == True:
                        self.payload = cmd_dict.get(self.payload)+PROMPT
                        self.request.send(self.payload)

                    # unknown command
                    else:
                        self.receiveQueue.append(self.payload)
                
		
            except socket.error:
                pass

            # check reveice Queue
            if len(th.receiveQueue) != 0:
                sendData = th.receiveQueue.pop(0)
                self.request.send(sendData)
                #save outgoint data from underlying honeypot to attacker in sqlitedb
                now=datetime.datetime.now()
                try:
                    country=geoIP.coun(self.attackerIP)
                except:
                    country="not found"
                database.table(str(now)[:10],str(now)[12:],self.attackerIP,self.attackerport,"<-",self.serverip,self.serverport, "TCP", sys.getsizeof(sendData),country,sendData) 
                gui_handle.updateUIlogs(str(now)[:10],str(now)[12:],self.attackerIP,str(self.attackerport),"<-",self.serverip,str(self.serverport), "TCP",str(sys.getsizeof(sendData)),country,sendData)

        self.request.close()
        #print "%s IP %s.%s > %s.%s : session closed" \
        #    % (self.date,self.attackerIP,self.client_address[1],self.server.server_address[0],self.PORTNUMBER)
        now=datetime.datetime.now()
        try:
            country=ip.country(self.attackerIP)
        except :
            country="not found"
        database.table(str(now)[:10],str(now)[12:],self.attackerIP,self.attackerport,"->",self.serverip,self.serverport,"TCP",sys.getsizeof(self.payload),country,self.payload)
        gui_handle.updateUIlogs(str(now)[:10],str(now)[12:],self.attackerIP,str(self.attackerip),"->",self.serverip,str(self.serverport),"TCP",str(sys.getsizeof(self.payload)),country,self.payload)

class BackEndResponder(threading.Thread):
# The Thread class as backend responder

    def __init__(self,openwrtIP,PORTNUMBER,proxyThreadRequest,proxyThreadQueue):
        self.proxyThreadQueue = proxyThreadQueue
        self.receiveQueue = []
        self.proxyThreadRequest = proxyThreadRequest
        global opewrt_ip
        self.openwrtIP = opewrt_ip
        self.PORTNUMBER = PORTNUMBER
        self.responce = ""
        self.date = datetime.datetime.today()
        self.openwrtSocket = None
        threading.Thread.__init__(self)

        if not self.openwrtSocket:
          self.openwrtSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
          try:
            self.openwrtSocket.connect((self.openwrtIP,int(self.PORTNUMBER)))
          except IndexError:
            print "Error Connection to Openwrt"

    def run(self):
        self.openwrtSocket.setblocking(0)
        while True:
            if ( datetime.datetime.today() - self.date).seconds > TIMEOUT:
                break

            try:
                # receive responce from openwrt
                self.responce = self.openwrtSocket.recv(8192)
                if len(self.responce) != 0:
                    print "Openwrt response data : {0}".format(self.responce)
                    self.receiveQueue.append(self.responce)
            except:
                pass

            # check receive Queue
            if len(self.proxyThreadQueue) != 0:
                sendData = self.proxyThreadQueue.pop(0)
                print "attacker data : {0}".format(sendData)
                self.openwrtSocket.send(sendData)
                self.date = datetime.datetime.today()

        print "%s : BackEndResponder session closed" % self.date


#middleware function
def startmiddleware(ip,port,hand):
    if (ip==None) or (port==None):
    	print "Usage: python main.py [portNum] [openwrtIPaddr] ",sys.exit(-1)
    global opewrt_ip
    global gui_handle
    print ip
    print port
    opewrt_ip = ip
    PORT = int(port)
    gui_handle=hand
    server = SocketServer.ThreadingTCPServer(("",PORT), FrontEndResponder)
    SocketServer.TCPServer.allow_reuse_address = True
    print "============================== Set up IoTPOT ================================"
    server.serve_forever()
