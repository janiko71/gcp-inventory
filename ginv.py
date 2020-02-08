import io, os, sys, time
import json

import googleapiclient

from googleapiclient import discovery
from googleapiclient import errors

import config
import res.functions as func
import res.compute as compute
import res.storage as storage
from res.gcpthread import GCPThread

#import google.auth
#credentials, project = google.auth.default()


#global config.global_inventory


project = config.project

t0 = time.time()

# Projects
"""
projects = googleapiclient.discovery.build('projects', 'v1')

projects_list = projects.list().execute()
for project in projects_list:
    print(project)
"""





# -------------------------------------------------------------------
#
#                       Let's rock'n roll...
#
# -------------------------------------------------------------------

thread_list = []

thread_list.append(GCPThread("sql", storage.SQL_inventory, project))
thread_list.append(GCPThread("appengine", compute.appengine_inventory, project))
thread_list.append(GCPThread("compute", compute.compute_inventory_global, project))
thread_list.append(GCPThread("compute", compute.compute_inventory_regional, project))
thread_list.append(GCPThread("compute", compute.compute_inventory_zonal, project))
thread_list.append(GCPThread("functions", compute.functions_inventory, project))
thread_list.append(GCPThread("bigtable", storage.bigtable_inventory, project))
thread_list.append(GCPThread("filestore", storage.filestore_inventory, project))

# -------------------------------------------------------------------
#
#                         Thread management
#
# -------------------------------------------------------------------

for th in thread_list:
    th.start()

for th in thread_list:
    th.join()



# -------------------------------------------------------------------
#
#                        The End
#
# -------------------------------------------------------------------

print(config.global_inventory)

f = open('inv.txt','w')
f.write(json.JSONEncoder().encode(config.global_inventory))
f.close()  

execution_time = time.time() - t0
print("\n\nAll inventories are done. Duration: {:2f} seconds\n".format(execution_time))