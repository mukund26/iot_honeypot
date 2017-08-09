#!/usr/bin/env python
import sys
from main import *
import threading
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget,QTableWidgetItem,QVBoxLayout,QFrame,QHBoxLayout,QPushButton,QSpacerItem,QSizePolicy,QGridLayout,QGroupBox,QSplitter,QTreeView,QDesktopWidget
from PyQt5.QtGui import QIcon,QStandardItem,QStandardItemModel
from PyQt5.QtCore import pyqtSlot,Qt,QSize

i=0;

class MyThread(threading.Thread):
    def __init__(self,ip,port,handle):
        threading.Thread.__init__(self)
        self.handle = handle
        self.ip = ip
        self.port = port
    def run(self):
        startmiddleware(self.ip,self.port,self.handle)



class App(QWidget):

    def __init__(self):
        super(App,self).__init__()
        self.title = 'IotHoneyPot'
        self.left = 0
        self.top = 0
        desktop = QDesktopWidget()
        self.width = desktop.geometry().width()
        self.height = desktop.geometry().height()
        print "width : %d height %d"%(self.width,self.height)
        self.initUI()
        self.showMaximized()


    def initUI(self):
        self.setWindowTitle(self.title)
	#self.setGeometry(self.left, self.top, self.width, self.height)
	# Add box layout, add table to box layout and add box layout to widget
        self.mainLayout = QVBoxLayout()
   
        #creating the topBar
        self.topBar = QGroupBox()
        self.horizontalLayout = QHBoxLayout()
        startButton = QPushButton("START")
        stopButton = QPushButton("STOP")
        startButton.setFixedSize(100,28)
        stopButton.setFixedSize(100,28)
        self.horizontalLayout.addWidget(startButton,0,Qt.AlignRight)
        self.horizontalLayout.addWidget(stopButton)
        self.topBar.setLayout(self.horizontalLayout)
        startButton.clicked.connect(self.Start)
        stopButton.clicked.connect(self.Stop)
        #topBar ends here

        # create centralWidet
        self.createCentralWidget()

        self.mainLayout.addWidget(self.topBar)
        self.mainLayout.addWidget(self.centralWidget)
        self.setLayout(self.mainLayout)
       
        #self.updatePorts("23")        
        #self.updateAttackerIPs("192.168.8.17")        

        # Show widget
        self.show()

    def Start(self):
	#self.my=thread.start_new_thread(startmiddleware,("192.168.43.152","23",self))
         self.my = MyThread("192.168.1.3","23",self)
         self.my.start()
	 
    def Stop(self):
	self.my.stop()

    def updatePorts(self,port):
        item = QStandardItem(port)
        item.setEditable(False)
        self.ports.appendRow(item)
    
    def updateAttackerIPs(self,ip):
        item = QStandardItem(ip)
        item.setEditable(False)
        self.attackerIP.appendRow(item)

        
    
    def updateUIlogs(self,date,time,attackerip,attackerport,direction,localip,localport,protocol,byte,country,payload):
        global i
	self.tableWidget.insertRow(i+1)
    	self.tableWidget.setItem(i,0,QTableWidgetItem(date))
        self.tableWidget.setItem(i,1,QTableWidgetItem(time))
        self.tableWidget.setItem(i,2,QTableWidgetItem(attackerip))
        self.tableWidget.setItem(i,3,QTableWidgetItem(attackerport))
        self.tableWidget.setItem(i,4,QTableWidgetItem(direction))
        self.tableWidget.setItem(i,5,QTableWidgetItem(localip))
        self.tableWidget.setItem(i,6,QTableWidgetItem(localport))
        self.tableWidget.setItem(i,7,QTableWidgetItem(protocol))
        self.tableWidget.setItem(i,8,QTableWidgetItem(byte))
        self.tableWidget.setItem(i,9,QTableWidgetItem(country))
        self.tableWidget.setItem(i,10,QTableWidgetItem(payload))
        i=(i+1)%1500
        self.tableWidget.show()
        
   
    def createCentralWidget(self):
       # Create table
        self.centralWidget = QSplitter(Qt.Horizontal)
        self.treeView = QTreeView()
        self.treeView.setHeaderHidden(True)
        standardModel = QStandardItemModel()
        rootNode = standardModel.invisibleRootItem()
        self.ports = QStandardItem("Local Ports")
        self.attackerIP = QStandardItem("Attacker IPs")
        self.ports.setEditable(False)
        self.attackerIP.setEditable(False)
        
        rootNode.appendRow(self.ports)
        rootNode.appendRow(self.attackerIP)
   
        self.treeView.setModel(standardModel)

 
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setRowCount(1500) 
        self.tableWidget.setColumnCount(11)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setHorizontalHeaderLabels(['Date', 'Time', 'RemoteIP', 'Remote Port', 'Direction', 'Local IP', 'Local Port', 'Protocol', 'Bytes','Country','Packet Detail'])
        self.tableWidget.setColumnWidth(0,100)
        self.tableWidget.setColumnWidth(2,self.width*0.1)
        self.tableWidget.setColumnWidth(3,self.width*0.07)
        self.tableWidget.setColumnWidth(4,self.width*0.05)
        self.tableWidget.setColumnWidth(5,self.width*0.1)
        self.tableWidget.setColumnWidth(6,self.width*0.06)
        self.tableWidget.setColumnWidth(7,self.width*0.05)
        self.tableWidget.setColumnWidth(8,self.width*0.04)
        self.tableWidget.setColumnWidth(10,self.width*0.095)
#        self.tableWidget.move(30,10)
	

        # table selection change
        self.tableWidget.doubleClicked.connect(self.on_click)
        self.treeView.setMinimumWidth(self.width*0.15)
        self.tableWidget.setMinimumWidth(self.width*0.85) 
        self.centralWidget.addWidget(self.treeView)
        self.centralWidget.addWidget(self.tableWidget)
        self.centralWidget.setMinimumHeight(self.height*0.95) 

    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())

if __name__ == '__main__':
    app = QApplication(sys.argv)

    ex = App()
    exit(app.exec_())
