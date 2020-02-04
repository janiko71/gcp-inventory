import io, os, sys, time
import json

#from google.auth import compute_engine
#auth = compute_engine.Credentials()

import googleapiclient

from googleapiclient import discovery
from googleapiclient import errors

#import google.auth
#credentials, project = google.auth.default()

MAX_RESULTS = 1000

project = "secu-si"

inventory = {}

t0 = time.time()

# Projects
"""
projects = googleapiclient.discovery.build('projects', 'v1')

projects_list = projects.list().execute()
for project in projects_list:
    print(project)
"""


#client.__getattribute__(detail_function)(**param).get(detail_get_key)

#------------------------------------------------------------------------------------------
def inventory_without_pagination(service, fn_name, params, getter = 'items'):
#------------------------------------------------------------------------------------------

    return inventory_with_pagination(service, fn_name, params, getter, max_results = None)

#------------------------------------------------------------------------------------------
def inventory_with_pagination(service, fn_name, params, getter = 'items', max_results = MAX_RESULTS):
#------------------------------------------------------------------------------------------

    #service = googleapiclient.discovery.build(service, version)
    print(fn_name, params)

    inventory = []
    cont = True
    nextPageToken = None

    if 'maxResults' not in params and max_results != None:
        params['maxResults'] = max_results

    if type(fn_name) == str:
        inventory_function = service.__getattribute__(fn_name)()
    else:
        inventory_function = service
        for fn in fn_name:
            inventory_function = inventory_function.__getattribute__(fn)()

    while cont:
        cont = False
        params['pageToken'] = nextPageToken
        results_list = inventory_function.list(**params).execute()
        if getter in results_list:
                inventory = inventory + results_list[getter]
        if 'nextPageToken' in results_list:
            nextPageToken = results_list['nextPageToken']    
            cont = True

    return inventory

"""
compute_service = googleapiclient.discovery.build('compute', 'v1')
inventory['firewalls.rules'] = inventory_with_pagination(compute_service, "firewalls", {'project': project})
exit(0)

"""

# SQL

def SQL_inventory():

    global inventory

    service_sql = googleapiclient.discovery.build('sqladmin', 'v1beta4')
    inventory['sql'] = inventory_with_pagination(service_sql, "instances", {'project': project})


# Compute Engine => marchouille

def compute_inventory():

    global inventory

    service_compute = googleapiclient.discovery.build('compute', 'v1')

    # Global resources

    compute_services_global = ["regions", "zones", "snapshots", "firewalls", "backendBuckets", "backendServices", "externalVpnGateways", 
                "globalAddresses", "globalForwardingRules", "globalOperations", "interconnects", "networks",
                "routes"]
    compute_informational_services_global = ["interconnectLocations"]   

    #compute_services_global = ["regions", "zones"]

    for service_name in compute_services_global:
        inventory[service_name] = inventory_with_pagination(service_compute, service_name, {'project': project})

    compute_services_by_regions = ["addresses", "forwardingRules", "interconnectAttachments", "regionAutoscalers",
                "regionBackendServices", "regionDisks", "regionOperations", "routers", "subnetworks",
                "vpnGateways", "vpnTunnels"]
    compute_informational_services_by_regions = []            

    compute_services_by_zones = ["autoscalers", "disks", "instances", "networkEndpointGroups", "nodeGroups"]
    compute_informational_services_by_zones = ["acceleratorTypes",]
    # Cas particuliers zones
    # https://cloud.google.com/compute/docs/reference/rest/v1/nodeGroups/list

    # Special lists

    list_zones = inventory['zones']
    list_regions = inventory['regions']

    #for zone in list_zones:
    #    zone_name = zone['name']
    #    print("{} {:6} {}".format(zone['id'], "(" + zone['status'] + ")", zone_name))

    #for region in list_regions:
    #    region_name = region['name']
    #    print("{} {:6} {}".format(region['id'], "(" + region['status'] + ")", region_name))

    for regional_service in compute_services_by_regions:
        regional_inventory = []
        for region in list_regions:
            region_name = region['name']
            regional_inventory = regional_inventory +  inventory_with_pagination(service_compute, regional_service, {'project': project, 'region': region_name})
        inventory[regional_service] = regional_inventory


    for zonal_service in compute_services_by_zones:
        zonal_inventory = []
        for zone in list_zones:
            zone_name = zone['name']
            zonal_inventory = zonal_inventory +  inventory_with_pagination(service_compute, zonal_service, {'project': project, 'zone': zone_name})
        inventory[zonal_service] = zonal_inventory


# Apps
# Special API: you need an additional API call for describing each App

def appengine_inventory():

    global inventory
    service_appengine = googleapiclient.discovery.build('appengine', 'v1')

    inventory_appengine = {}

    apps_list =  inventory_without_pagination(service_appengine, ['apps', 'services'], {'appsId': project}, getter = 'services')

    for app in apps_list:
        app_desc = service_appengine.apps().get(appsId="secu-si").execute()
        print(app_desc)
        inventory_appengine[app['id']] = {}
        inventory_appengine[app['id']]['service'] = app
        inventory_appengine[app['id']]['desc'] = app_desc
        
    inventory['apps_list'] = inventory_appengine

# Services


# Functions
# https://cloud.google.com/functions/docs/apis
# https://cloud.google.com/functions/docs/reference/rest/

def functions_inventory():

    global inventory

    service_functions = googleapiclient.discovery.build('cloudfunctions', 'v1')

    list_functions = {}

    functions_locations = inventory_without_pagination(service_functions, ['projects', 'locations'], 
                                    {'name': "projects/" + project}, getter='locations')

    for loc in functions_locations:

        loc_name = loc['name']
        list_functions[loc_name] = inventory_without_pagination(service_functions, ['projects', 'locations', 'functions'], 
                                        {'parent': loc_name}, getter = 'functions')

    inventory['functions'] = list_functions


# Bigtable

def bigtable_inventory():

    global inventory

    service_bigtable = googleapiclient.discovery.build('bigtableadmin', 'v2')

    inventory['bigtable'] = {}

    inventory['bigtable'] = inventory_without_pagination(service_bigtable, ['projects', 'instances'], 
                                                 {'parent': "projects/" + project}, getter='instances')

    for instance in inventory['bigtable']:
        instance_name = instance['name']
        list_clusters = inventory_without_pagination(service_bigtable, ['projects', 'instances', 'clusters'], 
                                                 {'parent': instance_name}, getter='clusters')
        instance['clusters'] = list_clusters



# Fin finale

f = open('inv.txt','w')
f.write(json.JSONEncoder().encode(inventory))
f.close()  

execution_time = time.time() - t0
print("\n\nAll inventories are done. Duration: {:2f} seconds\n".format(execution_time))