import io, os, sys
import json

#from google.auth import compute_engine
#auth = compute_engine.Credentials()

import googleapiclient

from googleapiclient import discovery
from googleapiclient import errors

#import google.auth
#credentials, project = google.auth.default()

project = "secu-si"

inventory = {}

# Projects
"""
projects = googleapiclient.discovery.build('projects', 'v1')

projects_list = projects.list().execute()
for project in projects_list:
    print(project)
"""

# Compute Engine => marchouille
"""
compute = googleapiclient.discovery.build('compute', 'v1')

compute_zones = compute.zones().list(project=project).execute()
inventory['compute_zones'] = compute_zones
list_zones = compute_zones['items']

compute_regions = compute.regions().list(project=project).execute()
inventory['compute_regions'] = compute_regions
list_regions = compute_regions['items']


inventory_compute = {}
inventory_autoscalers = {}

for zone in list_zones:
    zone_name = zone['name']
    print("{} {:6} {}".format(zone['id'], "(" + zone['status'] + ")", zone['name']))
    result_compute = compute.instances().list(project=project, zone=zone_name).execute()
    result_autoscalers = compute.autoscalers().list(project=project, zone=zone_name).execute()
    inventory_compute[zone_name] = result_compute
    inventory_autoscalers[zone_name] = result_autoscalers

inventory_addresses = {}

for region in list_regions:
    region_name = region['name']
    print("{} {:6} {}".format(region['id'], "(" + region['status'] + ")", region['name']))
    result_addresses = compute.addresses().list(project=project, region=region_name).execute()
    inventory_addresses[region_name] = result_addresses

inventory['compute'] = inventory_compute
inventory['autoscaler'] = inventory_autoscalers
inventory['addresses'] = inventory_addresses
"""


# Apps

appengine = googleapiclient.discovery.build('appengine', 'v1')

inventory_appengine = {}

result_apps = appengine.apps().services().list(appsId="secu-si").execute()
apps_list = result_apps['services']

for app in apps_list:
    print(app['id'], app)
    app_desc = appengine.apps().get(appsId="secu-si").execute()
    print(app_desc)
    inventory_appengine[app['id']] = {}
    inventory_appengine[app['id']]['service'] = app
    inventory_appengine[app['id']]['desc'] = app_desc
    
inventory['apps_list'] = inventory_appengine

# Services

#services = googleapiclient.discovery.build('services', 'v1')



# Functions

function =  googleapiclient.discovery.build('cloudfunctions', 'v1')

list_functions = {}

functions_locations = function.projects().locations().list(name="projects/secu-si").execute()
for loc in functions_locations['locations']:
    print(loc)
    loc_name = loc['name']
    result_functions = function.projects().locations().functions().list(parent=loc_name).execute()
    if 'functions' in result_functions: 
        list_functions[loc_name] = result_functions['functions']
        #for func in list_functions:
        #    print(func)
inventory['functions'] = list_functions


# Fin finale

f = open('inv.txt','w')
f.write(json.JSONEncoder().encode(inventory))
f.close()    