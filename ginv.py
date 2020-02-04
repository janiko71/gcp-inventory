import io, os, sys
import json

#from google.auth import compute_engine
#auth = compute_engine.Credentials()

import googleapiclient

from googleapiclient import discovery
from googleapiclient import errors

#import google.auth
#credentials, project = google.auth.default()

MAX_RESULTS = 5

project = "secu-si"

inventory = {}

# Projects
"""
projects = googleapiclient.discovery.build('projects', 'v1')

projects_list = projects.list().execute()
for project in projects_list:
    print(project)
"""


#client.__getattribute__(detail_function)(**param).get(detail_get_key)
#------------------------------------------------------------------------------------------
def inventory_with_pagination(service, fn_name, params, max_results = MAX_RESULTS):
#------------------------------------------------------------------------------------------

    #service = googleapiclient.discovery.build(service, version)

    inventory = []
    cont = True
    nextPageToken = None

    if 'maxResults' not in params:
        params['maxResults'] = max_results

    if type(fn_name) == str:
        inventory_function = service.__getattribute__(fn_name)()
    else:
        for fn_name in fn_names:
            inventory_function = inventory_function.__getattribute__(fn_name)()

    while cont:
        cont = False
        params['pageToken'] = nextPageToken
        results_list = inventory_function.list(**params).execute()
        if 'items' in results_list:
                inventory = inventory + results_list['items']
        if 'nextPageToken' in results_list:
            nextPageToken = results_list['nextPageToken']    
            cont = True

    return inventory


compute_service = googleapiclient.discovery.build('compute', 'v1')
inventory['firewalls.rules'] = inventory_with_pagination(compute_service, "firewalls", {'project': project})
exit(0)

"""

# SQL

inventory['sql'] = {}
sql = googleapiclient.discovery.build('sqladmin', 'v1beta4')
list_sql = sql.instances().list(project=project).execute()
if 'items' in list_sql:
    inventory['sql'] = list_sql['items']

    

# Compute Engine => marchouille

compute = googleapiclient.discovery.build('compute', 'v1')

# Global resources

inventory['snapshots'] = {}
list_snapshots = compute.snapshots().list(project=project).execute()
if 'items' in list_snapshots:
    inventory['snapshots'] = list_snapshots['items']

inventory['firewalls.rules'] = {}
list_firewalls = compute.firewalls().list(project=project, maxResults=10, pageToken=None).execute()
if 'items' in list_firewalls:
    inventory['firewalls.rules'] = list_firewalls['items']
if 'nextPageToken' in list_firewalls:
    nextPageToken = list_firewalls['nextPageToken']    

inventory['compute_zones'] = {}
list_zones = compute.zones().list(project=project).execute()
if 'items' in list_zones:
    inventory['compute_zones'] = list_zones['items']

inventory['compute_regions'] = {}
list_regions = compute.regions().list(project=project).execute()
if 'items' in list_regions:
    inventory['compute_regions'] = list_regions['items']

inventory['backendBuckets'] = {}
list_backendBuckets = compute.backendBuckets().list(project=project, maxResults=10, pageToken=None).execute()
if 'items' in list_backendBuckets:
    inventory['backendBuckets'] = list_backendBuckets

inventory['backendServices'] = {}
list_backendServices = compute.backendServices().list(project=project, maxResults=10, pageToken=None).execute()
if 'items' in list_backendServices:
    inventory['backendServices'] = list_backendServices    

inventory_compute = {}
inventory_autoscalers = {}
inventory_disks = {}

for zone in list_zones['items']:
    zone_name = zone['name']
    print("{} {:6} {}".format(zone['id'], "(" + zone['status'] + ")", zone['name']))
    list_compute = compute.instances().list(project=project, zone=zone_name).execute()
    if 'items' in list_compute:
        inventory_compute[zone_name] = list_compute
    list_autoscalers = compute.autoscalers().list(project=project, zone=zone_name, maxResults=10, pageToken=None).execute()
    if 'items' in list_autoscalers:
        inventory_autoscalers[zone_name] = list_autoscalers
    list_disks = compute.disks().list(project=project, zone=zone_name, maxResults=10, pageToken=None).execute()
    if 'items' in list_disks:
        inventory_disks[zone_name] = list_disks
    list_disks = compute.disks().list(project=project, zone=zone_name, maxResults=10, pageToken=None).execute()
    if 'items' in list_disks:
        inventory_disks[zone_name] = list_disks


inventory_addresses = {}

for region in list_regions['items']:
    region_name = region['name']
    print("{} {:6} {}".format(region['id'], "(" + region['status'] + ")", region['name']))
    list_addresses = compute.addresses().list(project=project, region=region_name, maxResults=10, pageToken=None).execute()
    if 'items' in list_addresses:
        inventory_addresses[region_name] = list_addresses

inventory['compute'] = inventory_compute
inventory['autoscalers'] = inventory_autoscalers
inventory['addresses'] = inventory_addresses
inventory['disks'] = inventory_disks


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

"""

# Functions
# https://cloud.google.com/functions/docs/apis
# https://cloud.google.com/functions/docs/reference/rest/

function = googleapiclient.discovery.build('cloudfunctions', 'v1')

list_functions = {}

functions_locations = function.projects().locations().list(name="projects/secu-si").execute()
for loc in functions_locations['locations']:
    print(loc)
    loc_name = loc['name']
    result_functions = function.projects().locations().functions().list(parent=loc_name, pageSize=51).execute()
    if 'nextPageToken' in result_functions:
        nextPageToken = result_functions['nextPageToken']
    if 'functions' in result_functions: 
        list_functions[loc_name] = result_functions['functions']
        #for func in list_functions:
        #    print(func)
inventory['functions'] = list_functions


# Fin finale

f = open('inv.txt','w')
f.write(json.JSONEncoder().encode(inventory))
f.close()    