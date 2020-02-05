import io, os, sys, time
import json

import res.functions as func
from res.gcpthread import GCPThread

import config

#from google.auth import compute_engine
#auth = compute_engine.Credentials()

import googleapiclient

from googleapiclient import discovery
from googleapiclient import errors

#import google.auth
#credentials, project = google.auth.default()


global global_inventory
global_inventory = {}


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
inventory['firewalls.rules'] = func.inventory_with_pagination(compute_service, "firewalls", {'project': project})
exit(0)

"""

# ================================================================================
#
#  Service : SQL
#
# ================================================================================
# 
#  List GCP assets for SQL (instances)
#
#  https://cloud.google.com/sql/docs/mysql/admin-api/rest/
#

# --------------------------------------------------
def SQL_inventory(project):
# --------------------------------------------------

    # Connection to the service API

    service_sql = googleapiclient.discovery.build('sqladmin', 'v1beta4')

    # Get the inventory (of instances)

    global_inventory['sql'] = func.inventory_with_pagination(service_sql, "instances", {'project': project})

    # For each instance, we list the databases

    for instance in global_inventory['sql']:
        instance_name = instance['name']
        db_list = func.inventory_without_pagination(service_sql, 'databases', {'project': project, 'instance': instance_name})
        instance['db_list'] = db_list



# ================================================================================
#
#  Service : Compute (global)
#
# ================================================================================
# 
#  List global GCP assets for compute services (cf. compute_services_global list)
#
#  https://cloud.google.com/compute/docs/apis
#  https://cloud.google.com/compute/docs/reference/rest/v1/
#

# --------------------------------------------------
def compute_inventory_global(project):
# --------------------------------------------------

    # Connection to the service API

    service_compute = googleapiclient.discovery.build('compute', 'v1')

    # Multiple inventories for global compute services. All services that are globalized 
    # are listed in the table below, in ordre to call dynamically the inventory function

    compute_services_global = ["snapshots", "firewalls", "backendBuckets", "backendServices", "externalVpnGateways", 
                "globalAddresses", "globalForwardingRules", "globalOperations", "interconnects", "networks",
                "routes"]

    #compute_services_global = ["regions", "zones"]

    for service_name in compute_services_global:

        global_inventory[service_name] = func.inventory_with_pagination(service_compute, service_name, {'project': project})



# ================================================================================
#
#  Service : Compute (regional)
#
# ================================================================================
# 
#  List regional GCP assets for compute services (cf. compute_services_by_regions list)
#
#  https://cloud.google.com/compute/docs/apis
#  https://cloud.google.com/compute/docs/reference/rest/v1/
#

# --------------------------------------------------
def compute_inventory_regional(project):
# --------------------------------------------------

    # Connection to the service API

    service_compute = googleapiclient.discovery.build('compute', 'v1')

    # Multiple inventories for regional compute services. All services that are regionalized 
    # are listed in the table below, in ordre to call dynamically the inventory function

    compute_services_by_regions = ["addresses", "forwardingRules", "interconnectAttachments", "regionAutoscalers",
                "regionBackendServices", "regionDisks", "regionOperations", "routers", "subnetworks",
                "vpnGateways", "vpnTunnels"]

    list_regions = config.list_regions

    # Loop on every service

    for regional_service in compute_services_by_regions:

        regional_inventory = []

        # Loop on every available region

        for region in list_regions:

            region_name = region['name']
            regional_inventory = regional_inventory +  func.inventory_with_pagination(service_compute, regional_service, {'project': project, 'region': region_name})

        global_inventory[regional_service] = regional_inventory



# ================================================================================
#
#  Service : Compute (zonal)
#
# ================================================================================
# 
#  List zonal GCP assets for compute services (cf. compute_services_by_zones list)
#
#  https://cloud.google.com/compute/docs/apis
#  https://cloud.google.com/compute/docs/reference/rest/v1/
#

# --------------------------------------------------
def compute_inventory_zonal(project):
# --------------------------------------------------    

    # Connection to the service API

    service_compute = googleapiclient.discovery.build('compute', 'v1')

    # Multiple inventories for regional compute services. All zonal services are
    # listed in the table below, in ordre to call dynamically the inventory function

    compute_services_by_zones = ["autoscalers", "disks", "instances", "networkEndpointGroups", "nodeGroups"]
    compute_informational_services_by_zones = ["acceleratorTypes",]

    list_zones = config.list_zones

    # Loop on every service

    for zonal_service in compute_services_by_zones:

        zonal_inventory = []

        # Loop on every zone

        for zone in list_zones:
            
            zone_name = zone['name']
            zonal_inventory = zonal_inventory +  func.inventory_with_pagination(service_compute, zonal_service, {'project': project, 'zone': zone_name})

        global_inventory[zonal_service] = zonal_inventory



# ================================================================================
#
#  Service : Apps (App Engine)
#
# ================================================================================
# 
#  List GCP assets for App Engine (services)
#
#  Special API: you need an additional API call for describing each App
#
#  https://cloud.google.com/appengine/docs/admin-api/apis
#  https://cloud.google.com/appengine/docs/admin-api/reference/rest/
#

# --------------------------------------------------
def appengine_inventory(project):
# --------------------------------------------------    

    # Connection to the service API

    service_appengine = googleapiclient.discovery.build('appengine', 'v1')

    # Inventory init

    inventory_appengine = {}

    # App Engine services list

    apps_list =  func.inventory_without_pagination(service_appengine, ['apps', 'services'], {'appsId': project}, getter = 'services')

    # For each App, we get some further information

    for app in apps_list:

        app_desc = service_appengine.apps().get(appsId="secu-si").execute()

        inventory_appengine[app['id']] = {}
        inventory_appengine[app['id']]['service'] = app
        inventory_appengine[app['id']]['desc'] = app_desc

    # Storing results
        
    global_inventory['apps_list'] = inventory_appengine



# ================================================================================
#
#  Service : Functions
#
# ================================================================================
# 
#  List GCP assets for functions
#
#  https://cloud.google.com/functions/docs/apis
#  https://cloud.google.com/functions/docs/reference/rest/
#

# --------------------------------------------------
def functions_inventory(project):
# --------------------------------------------------
    
    # Connection to the service API

    service_functions = googleapiclient.discovery.build('cloudfunctions', 'v1')

    # Inventory init

    list_functions = {}

    # Function locations list

    functions_locations = func.inventory_without_pagination(service_functions, ['projects', 'locations'], 
                                    {'name': "projects/" + project}, getter='locations')

    # For each location, we list the functions                                    

    for loc in functions_locations:

        loc_name = loc['name']
        result_list = func.inventory_without_pagination(service_functions, ['projects', 'locations', 'functions'], 
                                        {'parent': loc_name}, getter = 'functions')
        if len(result_list) != 0:
            list_functions[loc_name] = result_list

    # Storing results

    global_inventory['functions'] = list_functions



# ================================================================================
#
#  Service : Filestore
#
# ================================================================================
# 
#  List GCP assets for Filestore (instances)
#
#  https://cloud.google.com/filestore/docs/apis
#  https://cloud.google.com/filestore/docs/reference/rest/
#

# --------------------------------------------------
def filestore_inventory(project):
# --------------------------------------------------    

    # Connection to the service API

    service_filestore = googleapiclient.discovery.build('file', 'v1')

    # Inventory init

    list_filestore = {}

    # Filestore locations list

    filestores_locations = func.inventory_without_pagination(service_filestore, ['projects', 'locations'], 
                                    {'name': "projects/" + project}, getter='locations')

    # For each location, we list all available instances                                    

    for loc in filestores_locations:

        loc_name = loc['name']
        result_list = func.inventory_without_pagination(service_filestore, ['projects', 'locations', 'instances'], 
                                        {'parent': loc_name}, getter = 'instances')
        if len(result_list) != 0:
            list_filestore[loc_name] = result_list

    # Storing results

    global_inventory['filestore'] = list_filestore



# ================================================================================
#
#  Service : Bigtable (admin)
#
# ================================================================================
# 
#  List GCP assets for Bigtable (instances)
#
#  https://cloud.google.com/bigtable/docs/apis
#  https://cloud.google.com/bigtable/docs/reference/admin/rest
#

# --------------------------------------------------
def bigtable_inventory(project):
# --------------------------------------------------    

    # Connection to the service API

    service_bigtable = googleapiclient.discovery.build('bigtableadmin', 'v2')

    # Inventory init

    global_inventory['bigtable'] = {}

    # List of instances

    global_inventory['bigtable'] = func.inventory_without_pagination(service_bigtable, ['projects', 'instances'], 
                                                 {'parent': "projects/" + project}, getter='instances')

    # For each instance, we look for clusters                                                 

    for instance in global_inventory['bigtable']:
        instance_name = instance['name']
        list_clusters = func.inventory_without_pagination(service_bigtable, ['projects', 'instances', 'clusters'], 
                                                 {'parent': instance_name}, getter='clusters')
        global_inventory['clusters'] = list_clusters



# -------------------------------------------------------------------
#
#                       Let's rock'n roll...
#
# -------------------------------------------------------------------

thread_list = []

thread_list.append(GCPThread("sql", SQL_inventory, project))
thread_list.append(GCPThread("appengine", appengine_inventory, project))
thread_list.append(GCPThread("compute", compute_inventory_global, project))
thread_list.append(GCPThread("compute", compute_inventory_regional, project))
thread_list.append(GCPThread("compute", compute_inventory_zonal, project))
thread_list.append(GCPThread("functions", functions_inventory, project))
thread_list.append(GCPThread("bigtable", bigtable_inventory, project))
thread_list.append(GCPThread("filestore", filestore_inventory, project))

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
f.write(json.JSONEncoder().encode(global_inventory))
f.close()  

execution_time = time.time() - t0
print("\n\nAll inventories are done. Duration: {:2f} seconds\n".format(execution_time))