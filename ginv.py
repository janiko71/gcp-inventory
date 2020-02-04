import io, os, sys, time
import json

import config
import globals
from gcpthread import GCPThread

#from google.auth import compute_engine
#auth = compute_engine.Credentials()

import googleapiclient

from googleapiclient import discovery
from googleapiclient import errors

#import google.auth
#credentials, project = google.auth.default()




config.global_inventory = {}

project = config.project

t0 = time.time()

# Projects
"""
projects = googleapiclient.discovery.build('projects', 'v1')

projects_list = projects.list().execute()
for project in projects_list:
    print(project)
"""


"""
compute_service = googleapiclient.discovery.build('compute', 'v1')
inventory['firewalls.rules'] = globals.inventory_with_pagination(compute_service, "firewalls", {'project': project})
exit(0)

"""

# SQL

def SQL_inventory(project):

    service_sql = googleapiclient.discovery.build('sqladmin', 'v1beta4')
    config.global_inventory['sql'] = globals.inventory_with_pagination(service_sql, "instances", {'project': project})


# Compute Engine => marchouille

def compute_inventory(project):

    service_compute = googleapiclient.discovery.build('compute', 'v1')

    # Global resources

    compute_services_global = ["snapshots", "firewalls", "backendBuckets", "backendServices", "externalVpnGateways", 
                "globalAddresses", "globalForwardingRules", "globalOperations", "interconnects", "networks",
                "routes"]

    #compute_services_global = ["regions", "zones"]

    for service_name in compute_services_global:
        config.global_inventory[service_name] = globals.inventory_with_pagination(service_compute, service_name, {'project': project})

    compute_services_by_regions = ["addresses", "forwardingRules", "interconnectAttachments", "regionAutoscalers",
                "regionBackendServices", "regionDisks", "regionOperations", "routers", "subnetworks",
                "vpnGateways", "vpnTunnels"]
    compute_informational_services_by_regions = []            

    compute_services_by_zones = ["autoscalers", "disks", "instances", "networkEndpointGroups", "nodeGroups"]
    compute_informational_services_by_zones = ["acceleratorTypes",]
    # Cas particuliers zones
    # https://cloud.google.com/compute/docs/reference/rest/v1/nodeGroups/list

    # Special lists

    list_zones = config.list_zones
    list_regions = config.list_regions

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
            regional_inventory = regional_inventory +  globals.inventory_with_pagination(service_compute, regional_service, {'project': project, 'region': region_name})
        config.global_inventory[regional_service] = regional_inventory


    for zonal_service in compute_services_by_zones:
        zonal_inventory = []
        for zone in list_zones:
            zone_name = zone['name']
            zonal_inventory = zonal_inventory +  globals.inventory_with_pagination(service_compute, zonal_service, {'project': project, 'zone': zone_name})
        config.global_inventory[zonal_service] = zonal_inventory


# Apps
# Special API: you need an additional API call for describing each App

def appengine_inventory(project):

    global inventory
    service_appengine = googleapiclient.discovery.build('appengine', 'v1')

    inventory_appengine = {}

    apps_list =  globals.inventory_without_pagination(service_appengine, ['apps', 'services'], {'appsId': project}, getter = 'services')

    for app in apps_list:
        app_desc = service_appengine.apps().get(appsId="secu-si").execute()
        print(app_desc)
        inventory_appengine[app['id']] = {}
        inventory_appengine[app['id']]['service'] = app
        inventory_appengine[app['id']]['desc'] = app_desc
        
    config.global_inventory['apps_list'] = inventory_appengine

# Services


# Functions
# https://cloud.google.com/functions/docs/apis
# https://cloud.google.com/functions/docs/reference/rest/

def functions_inventory(project):

    global inventory

    service_functions = googleapiclient.discovery.build('cloudfunctions', 'v1')

    list_functions = {}

    functions_locations = globals.inventory_without_pagination(service_functions, ['projects', 'locations'], 
                                    {'name': "projects/" + project}, getter='locations')

    for loc in functions_locations:

        loc_name = loc['name']
        list_functions[loc_name] = globals.inventory_without_pagination(service_functions, ['projects', 'locations', 'functions'], 
                                        {'parent': loc_name}, getter = 'functions')

    config.global_inventory['functions'] = list_functions


# Bigtable

def bigtable_inventory(project):

    global inventory

    service_bigtable = googleapiclient.discovery.build('bigtableadmin', 'v2')

    config.global_inventory['bigtable'] = {}

    config.global_inventory['bigtable'] = globals.inventory_without_pagination(service_bigtable, ['projects', 'instances'], 
                                                 {'parent': "projects/" + project}, getter='instances')

    for instance in config.global_inventory['bigtable']:
        instance_name = instance['name']
        list_clusters = globals.inventory_without_pagination(service_bigtable, ['projects', 'instances', 'clusters'], 
                                                 {'parent': instance_name}, getter='clusters')
        config.global_inventory['clusters'] = list_clusters

#
# Let's rock'n roll
#

thread_list = []

thread_list.append(GCPThread("sql", SQL_inventory, project))
thread_list.append(GCPThread("compute", compute_inventory, project))
thread_list.append(GCPThread("appengine", appengine_inventory, project))
thread_list.append(GCPThread("functions", functions_inventory, project))
thread_list.append(GCPThread("bigtable", bigtable_inventory, project))


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