#!/APSshare/anaconda3/x86_64/bin/python

import argparse
import sys
import requests
import json

import time

import pprint

url = "http://localhost:4000/jsonrpc"
headers = {'content-type': 'application/json'}

def notMain():
    # Add monitor
    payload = {
        "method": "addNotification",
        "params": {"pv_name":"kmp3:m1.VAL", "comparison":">", "value":"6.0", "email":"kmpeters@anl.gov", "expiration":"Probably"},
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()

    print(response)
   
    # Add a monitor
    payload = {
        "method": "addNotification",
        "params": {"pv_name":"kmp3:m1.VAL", "comparison":"<", "value":"-2.0", "email":"kmpeters@anl.gov", "expiration":"Probably"},
        "jsonrpc": "2.0",
        "id": 1,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()

    print(response)



def listCommand(options):
  pattern = options.pattern
  
  if pattern != None:
    print("pattern hasn't been implemented yet")
  else:
    ### Get all the notifications
    
    idNum = round(time.time())
    #!print(idNum)
    
    # Get the list of monitors
    payload = {
        "method": "listNotifications",
        "params": {},
        "jsonrpc": "2.0",
        "id": idNum,
    }
    
    data = json.dumps(payload)
    response = requests.post(url, data=data, headers=headers).json()

    if (idNum != response['id']):
      print("Error: Response ID (%i) doesn't match Request ID (%i)".format(response['id'], idNum))
    else:
      #!pprint.pprint(response)
      
      data = response['result']
      monitors = data['monitors']
      
      if len(monitors) == 0:
        print("There are no monitors to display")
      else:
        print("pv_name\t\ttest\tvalue\temail")
      
        for monitor in monitors:
          #!pprint.pprint(monitor)
          print("{0}\t{1}\t{2}\t{3}".format(monitor['pv_name'], monitor['comparison'], monitor['value'], monitor['email']))
        

def main(options):
  if options.command == 'list':
    listCommand(options)


if __name__ == "__main__":
  parser = argparse.ArgumentParser("pvNotify.py")
  
  subparsers = parser.add_subparsers(help='commands', dest='command')
  
  # An add command
  add_parser = subparsers.add_parser('add', help='Add notification')
  add_parser.add_argument('pv', action="store", default=None, help='PV to monitor')
  add_parser.add_argument('test', action="store", default=None, help='Comparison (==, !=, <, <=, >, >=)')
  add_parser.add_argument('value', action="store", default=None, help='Notification value')
  add_parser.add_argument('email', action="store", default=None, help='Email addresses to notify')
  
  # A delete command
  delete_parser = subparsers.add_parser('delete', help='Delete notification')
  delete_parser_group = delete_parser.add_mutually_exclusive_group(required=True)
  delete_parser_group.add_argument('-p', action='store', dest='pattern', help='Pattern to match')
  delete_parser_group.add_argument('-i', action='store', dest='index', help='Notification index')
  
  # A list command
  list_parser = subparsers.add_parser('list', help='List notifications')
  list_parser.add_argument('-p', action='store', dest='pattern', help='Pattern to match')

  options = parser.parse_args(sys.argv[1:])
  print(options)
  #!print(vars(options))
  
  main(options)
 
