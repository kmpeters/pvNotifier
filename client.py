#!/APSshare/anaconda3/x86_64/bin/python

import requests
import json


def main():
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
if __name__ == "__main__":
    main()
