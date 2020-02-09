import io, os, sys, time
import json

import googleapiclient

from googleapiclient import discovery
from googleapiclient import errors

import config
import res.meta as meta
from res.gcpthread import GCPThread



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

    result = {}

    # Multiple inventories for global compute services. All services that are globalized 
    # are listed in the table below, in ordre to call dynamically the inventory function

    compute_services_global = ["snapshots", "firewalls", "backendBuckets", "backendServices", "externalVpnGateways", 
                "globalAddresses", "globalForwardingRules", "globalOperations", "interconnects", "networks",
                "routes"]

    #compute_services_global = ["regions", "zones"]

    for service_name in compute_services_global:

        result[service_name] = meta.inventory_with_pagination(service_compute, service_name, {'project': project})

    return result



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

    result = {}

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
            regional_inventory = regional_inventory +  meta.inventory_with_pagination(service_compute, regional_service, {'project': project, 'region': region_name})

        result[regional_service] = regional_inventory

    return result



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

    result = {}

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
            zonal_inventory = zonal_inventory +  meta.inventory_with_pagination(service_compute, zonal_service, {'project': project, 'zone': zone_name})

        result[zonal_service] = zonal_inventory

    return result



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

    apps_list =  meta.inventory_without_pagination(service_appengine, ['apps', 'services'], {'appsId': project}, getter = 'services')

    # For each App, we get some further information

    for app in apps_list:

        app_desc = service_appengine.apps().get(appsId="secu-si").execute()

        inventory_appengine[app['id']] = {}
        inventory_appengine[app['id']]['service'] = app
        inventory_appengine[app['id']]['desc'] = app_desc

    # sending results
        
    return inventory_appengine



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

    functions_locations = meta.inventory_without_pagination(service_functions, ['projects', 'locations'], 
                                    {'name': "projects/" + project}, getter='locations')

    # For each location, we list the functions                                    

    for loc in functions_locations:

        loc_name = loc['name']
        result_list = meta.inventory_without_pagination(service_functions, ['projects', 'locations', 'functions'], 
                                        {'parent': loc_name}, getter = 'functions')
        if len(result_list) != 0:
            list_functions[loc_name] = result_list

    # Sending results

    return list_functions



# ================================================================================
#
#  Service : Cloud GPU
#
# ================================================================================
# 
#  List GCP assets for functions
#
#  https://cloud.google.com/tpu/docs/reference
#  https://cloud.google.com/tpu/docs/reference/rest
#

# --------------------------------------------------
def cloud_gpu_inventory(project):
# --------------------------------------------------
    
    # Connection to the service API

    service_cloud_gpu = googleapiclient.discovery.build('tpu', 'v1')

    # Inventory init

    list_cloud_gpu = {}

    # GPU locations list

    cloud_gpu_locations = meta.inventory_without_pagination(service_cloud_gpu, ['projects', 'locations'], 
                                    {'name': "projects/" + project}, getter='locations')

    # For each location, we list the functions // Not sure it's without pagination, cf API                               

    for loc in cloud_gpu_locations:

        loc_name = loc['name']
        result_list = meta.inventory_without_pagination(service_cloud_gpu, ['projects', 'locations', 'nodes'], 
                                        {'parent': loc_name}, getter = 'nodes')
        if len(result_list) != 0:
            list_cloud_gpu[loc_name] = result_list

    # Sending results

    return list_cloud_gpu





