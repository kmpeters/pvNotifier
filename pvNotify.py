#!/APSshare/anaconda3/x86_64/bin/python

import argparse
import sys
import requests
import json

def notMain():
    url = "http://localhost:4000/jsonrpc"
    headers = {'content-type': 'application/json'}

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

    # Get the list of monitors
    payload = {
        "method": "listNotifications",
        "params": {},
        "jsonrpc": "2.0",
        "id": 2,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()

    print(response)

def main(options):
  pass


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
 
