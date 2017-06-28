#!/APSshare/anaconda3/x86_64/bin/python

""" Example of json-rpc usage with Wergzeug and requests.

NOTE: there are no Werkzeug and requests in dependencies of json-rpc.
NOTE: server handles all url paths the same way (there are no different urls).

"""

from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

from jsonrpc import JSONRPCResponseManager, dispatcher
import json

import epics
import time

import queue
import threading

from sys import stdout

monitored_pvs = {}

logfile = "monitors.txt"

#
exitFlag = False
queueLock = None
workQueue = None

class pvMon():
  def __init__(self, pv_name="", notify_comparison=None, notify_value=None, email=None):
    self.pv_name = pv_name
    self.pv_obj = None
    self.last_val = None
    self.val = None
    self.notify_comparison = notify_comparison
    self.notify_value = float(notify_value)
    self.email = email
    self.monCallbackInit = False
    self.connCallbackInit = False
    self.state = None

    # Create the comparision function
    if self.notify_comparison == "==":
      self.compare = lambda a, b: a == b
    elif self.notify_comparison == "!=":
      self.compare = lambda a, b: a != b
    elif self.notify_comparison == "<":
      self.compare = lambda a, b: a < b
    elif self.notify_comparison == "<=":
      self.compare = lambda a, b: a <= b
    elif self.notify_comparison == ">":
      self.compare = lambda a, b: a > b
    elif self.notify_comparison == ">=":
      self.compare = lambda a, b: a >= b
    else:
      self.compare = lambda a, b: False

  def createMon(self):
    # Create the PV opject with monitors
    self.pv_obj = epics.PV(self.pv_name, callback=self.monCallback, connection_callback=self.connCallback)
    
      
  def monCallback(self, **kw):
    if self.monCallbackInit == False:
      self.val = kw['value']
      print("self.last_val =", self.last_val, "; self.val =", self.val)
      self.monCallbackInit = True
    else:
      self.last_val = self.val
      self.val = kw['value']
      print("self.last_val =", self.last_val, "; self.val =", self.val)
      print("callback!")
      stdout.write("stdout write!\n")
      stdout.flush()
      # Check to see if notify conidition is satisfied
      if self.compare(self.val, self.notify_value):
        # Check to see if a notification needs to be sent
        if not self.compare(self.last_val, self.notify_value):
          # Add the job of sending the email notification to the work queue
          stdout.write("NOTIFICATION CONDITION!\n")
          stdout.flush()

  def connCallback(self, **kw):
    if self.connCallbackInit == False:
      # Ignore the first callback, which happens when the PV first connects
      self.connCallbackInit = True
    else:
      print("connection change:\n", "  ", kw['pvname'], kw['conn'])


class epicsThread (threading.Thread):
  def __init__(self, threadID, name, q):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.q = q

  def run(self):
      print ("Starting " + self.name)
      process_data(self.name, self.q)
      print ("Exiting " + self.name)


def process_data(threadName, q):
  while not exitFlag:
    queueLock.acquire()
    if not workQueue.empty():
      print("work queue isn't empty!")
      function, kw = q.get()
      ### This will send the emails
      print(kw, "!!!!!!! Hi Kevin")
      
      function(kw["pv_name"], kw["comparison"], kw["value"], kw["email"])
      
      queueLock.release()
      print ("%s processing %s" % (threadName, kw))
    else:
      queueLock.release()
      
      # Spend approximately one second waiting for channel-access monitors
      for i in range(100):
        epics.poll(evt=1.e-2, iot=0.1)


def createMonitor(pv_name, comparison, value, email):
  ###
  key=pv_name+";"+comparison+";"+value
  monitored_pvs[key] = pvMon(pv_name, comparison, value, email)
  monitored_pvs[key].createMon()


def monitorCheck(kw):
  #
  key = kw['pv_name']+';'+kw['comparison']+';'+kw['value']
  #!print(key)
  #!print(monitored_pvs.keys())
  
  while not workQueue.empty():
    time.sleep(0.2)
  
  if key in monitored_pvs.keys():
    #!print("This monitor is a DUPE!")
    retval = True
  else:
    #!print("This monitor doesn't exist yet.")
    retval = False
    
  return retval
  

# json payloads will contain the following arguments
#  method
#  params
#  jsonrpc
#  id


# addNotification requires the following parameters:
#   pv_name
#   comparison
#   value
#   email
#   expiration

@dispatcher.add_method
def addNotification(**kw):
    # Add an email notification

    monitorExists = monitorCheck(kw)

    if not monitorExists:
      # let the EPICS thread create the monitors
      workQueue.put((createMonitor, kw))
    
      # append the monitor request to the log file
      fh = open(logfile, 'a')
      fh.write(json.dumps(kw, sort_keys=True))
      fh.write('\n')
      fh.close()
      
      retval = True
    else:
      retval = False
    
    # This should evenutally return an error if the workQueue is full
    # It should return a warning if the notification already exists
    return retval

@dispatcher.add_method
def listNotifications(**kw):
    # Return a list of all of the notifications 
    
    monitors = []
    
    # append the monitor request to the log file
    try:
      fh = open(logfile, 'r')
    except FileNotFoundError as err:
      print(err)
    else:
      for line in fh:
        monitors.append(json.loads(line))
      fh.close()
    
    return {"monitors" : monitors[:]}

@Request.application
def application(request):
    # Dispatcher is dictionary {<method_name>: callable}
    dispatcher["echo"] = lambda s: s
    dispatcher["add"] = lambda a, b: a + b

    # Returns a binary string
    #!data = request.data
    # Returns an ascii string
    data = request.get_data(cache=False, as_text=True)

    response = JSONRPCResponseManager.handle(data, dispatcher)
        
    #!print(monitored_pvs)
    return Response(response.json, mimetype='application/json')

if __name__ == '__main__':
    queueLock = threading.Lock()
    workQueue = queue.Queue(100)
    
    # Add logged requests to the workQueue
    try:
      fh = open(logfile, 'r')
    except FileNotFoundError as err:
      #!print(err)
      print("'{0}' doesn't exist; no monitors loaded".format(logfile))
    else:
      for line in fh:
        workQueue.put((createMonitor, json.loads(line)))
      fh.close()
    
    # Spawn EPICS thread
    eTh = epicsThread(1, "epicsThread", workQueue)
    eTh.start()
    
    # Start JSON-RPC server
    run_simple('localhost', 4000, application)

    print("The JSON-RPC server has started")
