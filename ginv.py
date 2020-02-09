import io, os, sys, time
import json

import googleapiclient

from googleapiclient import discovery
from googleapiclient import errors

import config
import res.meta as meta
import res.compute as compute
import res.storage as storage
from res.gcpthread import GCPThread

#import google.auth
#credentials, project = google.auth.default()

t0 = time.time()

    
# -------------------------------------------------------------------
#
#                       Let's rock'n roll...
#
# -------------------------------------------------------------------

thread_list = []
    
for project in config.projects_list:

    # Projects

    project_name = project['name']

    """
    thread_list.append(GCPThread("sql", storage.SQL_inventory, project_name))
    thread_list.append(GCPThread("appengine", compute.appengine_inventory, project_name))
    thread_list.append(GCPThread("compute", compute.compute_inventory_global, project_name))
    thread_list.append(GCPThread("compute", compute.compute_inventory_regional, project_name))
    thread_list.append(GCPThread("compute", compute.compute_inventory_zonal, project_name))
    thread_list.append(GCPThread("functions", compute.functions_inventory, project_name))
    thread_list.append(GCPThread("bigtable", storage.bigtable_inventory, project_name))
    thread_list.append(GCPThread("filestore", storage.filestore_inventory, project_name))
    """
    thread_list.append(GCPThread("tpu", compute.cloud_gpu_inventory, project_name))

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

f = open('inv.txt','w')
f.write(json.JSONEncoder().encode(config.global_inventory))
f.close()  

execution_time = time.time() - t0
print("\n\nAll inventories are done. Duration: {:2f} seconds\n".format(execution_time))