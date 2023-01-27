#!/APSshare/anaconda3/x86_64/bin/python

import epics
import datetime as dt
import os

# Note: the pvs.txt file has one monitor per line. Arguments are space-separated. Email list is comma-separated.
# Example pvs.txt:
# kmp3:m1.VAL > 65.0 kmpeters@anl.gov
# kmp3:m2.VAL < 0.0 kpetersn@anl.gov,kmpeters@anl.gov

filename = "pvs.txt"

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
      #!print("self.last_val =", self.last_val, "; self.val =", self.val)
      self.monCallbackInit = True
      # Check to see notification condition is violated at startup
      if self.compare(self.val, self.notify_value):
        # Print a warning
        print("[{}]: {} is {} which is {} {}, at startup. No emails sent.".format(dt.datetime.fromtimestamp(kw["timestamp"]), kw["pvname"], kw["value"], self.notify_comparison, self.notify_value))
    else:
      self.last_val = self.val
      self.val = kw['value']
      #!print("self.last_val =", self.last_val, "; self.val =", self.val)
      
      # Check to see if notify condition is satisfied
      if self.compare(self.val, self.notify_value):
        # Check to see if a notification needs to be sent
        if not self.compare(self.last_val, self.notify_value):
          # Send the notification
          ts = dt.datetime.fromtimestamp(kw["timestamp"])
          val = kw["value"]
          print("[{}]: {} is {} which is {} {}, emailing {}".format(ts, kw["pvname"], val, self.notify_comparison, self.notify_value, self.email))
          if self.email.count('@') > 0:
            self.notifyEmail(val, ts)

  def connCallback(self, **kw):
    if self.connCallbackInit == False:
      # Ignore the first callback, which happens when the PV first connects
      self.connCallbackInit = True
    else:
      print("connection change:\n", "  ", kw['pvname'], kw['conn'])

  def notifyEmail(self, value, timestamp):
      # Build the email message
      message = "Subject: pvNotifier: {} {} {}\n".format(self.pv_name, self.notify_comparison, self.notify_value)
      message += "To: {}\n".format(self.email)
      message += "\n"
      message += "Time: {}\n".format(timestamp)
      message += "PV: {}\n".format(self.pv_name)
      message += "Value: {}\n".format(value)
      message += "Trigger condition: {} {}\n".format(self.notify_comparison, self.notify_value)
      
      # Send the email
      email_command = "echo \"{}\" | sendmail -t".format(message)
      os.system(email_command)


if __name__ == '__main__':
  #
  monitors = []
  
  # Do the stuff
  fh = open(filename, "r")
  for line in fh:
    args = line.strip().split(" ")
    if len(args) == 4:
      print(args)
      pv, compare, value, email = args
      
      pvMonObj = pvMon(pv, compare, value, email)
      monitors.append(pvMonObj)
      pvMonObj.createMon()
   
  #print(monitors)
  
  # Wait for monitors
  while True:
    epics.poll(evt=1.0e-5, iot=0.1)
