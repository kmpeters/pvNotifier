#!/APSshare/anaconda3/x86_64/bin/python
# Python 3.5.2

import xmlrpc.server

import os

pvMonitorList = []

def listContents(dirName):
  return os.listdir(dirName)

def addPvMonitor(pvName):
  if pvName not in pvMonitorList:
    pvMonitorList.append(pvName)
    retVal = True
  else:
    # send back an error eventually
    print("Name already in list")
    retVal = False
  return retVal

def getPvMonitors():
  if len(pvMonitorList) > 0:
    return pvMonitorList
  else:
    return False

if __name__ == "__main__":
  server = xmlrpc.server.SimpleXMLRPCServer(('localhost', 8000))
  
  server.register_function(listContents)
  server.register_introspection_functions()
  server.register_function(addPvMonitor)
  server.register_function(getPvMonitors)
  
  try:
    print("Use Control-C to exit")
    server.serve_forever()
  except KeyboardInterrupt:
    print("Exiting")

  
