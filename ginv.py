import io, os, sys
import json

from google.auth import compute_engine
auth = compute_engine.Credentials()

import googleapiclient
import googleapiclient.discovery

project = "secu-si"

inventory = {}

# Compute Egine
"""
compute = googleapiclient.discovery.build('compute', 'v1')

result_compute_zones = compute.zones().list(project=project).execute()
inventory['compute_zones'] = result_compute_zones

#str_regions = json.dumps(result_compute_zones).replace("\'", "\"")
#json_regions = json.loads(str_regions)

list_zones = result_compute_zones['items']

inventory_compute = {}
for zone in list_zones:
    zone_name = zone['name']
    print("{} {:6} {}".format(zone['id'], "(" + zone['status'] + ")", zone['name']))
    result_compute = compute.instances().list(project=project, zone=zone_name).execute()
    inventory_compute[zone_name] = result_compute

inventory['compute'] = inventory_compute
"""
# Apps

app =  googleapiclient.discovery.build('appengine', 'v1')

result_apps = app.apps().regions()
inventory['apps_regions'] = result_apps

for app in result_apps:
    print(app)

# Fin finale

f = open('inv.txt','w')
f.write(json.JSONEncoder().encode(inventory))
f.close()    