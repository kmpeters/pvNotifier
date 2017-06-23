#!/APSshare/anaconda3/x86_64/bin/python

""" Example of json-rpc usage with Wergzeug and requests.

NOTE: there are no Werkzeug and requests in dependencies of json-rpc.
NOTE: server handles all url paths the same way (there are no different urls).

"""

from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

from jsonrpc import JSONRPCResponseManager, dispatcher

import epics

import queue
import threading

from sys import stdout

monitored_pvs = {}

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
    self.notify_value = notify_value
    self.compare = None
    self.email = email

  def createMon(self):
    # Create the PV opject with monitors
    self.pv_obj = epics.PV(pv_name, callback=self.monCallback, connect_callback=self.connCallback)
    
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
      
  def monCallback(self, **kw):
    self.last_val = self.val
    self.val = kw['value']
    # Check to see if notify conidition is satisfied
    if self.compare(self.val, self.notify_value):
      # Check to see if a notification needs to be sent
      if not self.compare(self.last_val, self.notify_value):
        # Add the job of sending the email notification to the work queue
        stdout.write("NOTIFICATION CONDITION!")
        stdout.flush()

  def connCallback(self, **kw):
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
      data = q.get()
      ### This will send the emails
      print(data, "Hi Kevin")
      queueLock.release()
      print ("%s processing %s" % (threadName, data))
    else:
      queueLock.release()
      
      # Spend approximately one second waiting for channel-access monitors
      for i in range(100):
        epics.poll(evt=1.e-2, iot=0.1)


def createMonitor(pv_name, comparison, value, email):
  ###
  key=pv_name+";"+comparison+";"+value
  monitored_pvs[key] = pvMon(pv_name, comparison, value, email)



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
    # Call a function to create a monitor with an email notification callback
    createMonitor(kw["pv_name"], kw["comparison"], kw["value"], kw["email"])
    return "Kevin was here"

@Request.application
def application(request):
    # Dispatcher is dictionary {<method_name>: callable}
    dispatcher["echo"] = lambda s: s
    dispatcher["add"] = lambda a, b: a + b

    response = JSONRPCResponseManager.handle(
        request.get_data(cache=False, as_text=True), dispatcher)
        
    print(monitored_pvs)
    return Response(response.json, mimetype='application/json')

if __name__ == '__main__':
    queueLock = threading.Lock()
    workQueue = queue.Queue(10)
    # Spawn EPICS thread
    eTh = epicsThread(1, "epicsThread", workQueue)
    eTh.start()
    
    # Start JSON-RPC server
    run_simple('localhost', 4000, application)