#!/APSshare/anaconda3/x86_64/bin/python
# Python 3.5.2

import xmlrpc.client

proxy = xmlrpc.client.ServerProxy("http://localhost:8000")

print("> listContents")
print(proxy.listContents("."))
print()
# Introspection functions
#!print("> listMethods")
#!print(proxy.system.listMethods())
#!print("> help system.listMethods")
#!print(proxy.system.methodHelp("system.listMethods"))
#!print
#!print("> methodSignature(system.listMethods")
#!print(proxy.system.methodSignature("system.listMethods"))

print(proxy.getPvMonitors())
print(proxy.addPvMonitor("kmp3:m1.DMOV"))
print(proxy.getPvMonitors())
print(proxy.addPvMonitor("kmp3:m2.MSTA"))
print(proxy.getPvMonitors())
print(proxy.addPvMonitor("kmp3:m1.DMOV"))
print(proxy.getPvMonitors())
