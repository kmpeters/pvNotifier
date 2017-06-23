#!/APSshare/anaconda3/x86_64/bin/python

import requests
import json


def main():
    url = "http://localhost:4000/jsonrpc"
    headers = {'content-type': 'application/json'}

    # Example echo method
    payload = {
        "method": "addNotification",
        "params": {"pv_name":"kmp3:m1.VAL", "comparison":">", "value":"6.0", "email":"kmpeters@anl.gov", "expiration":"Probably"},
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()

    print(response)
   

if __name__ == "__main__":
    main()
