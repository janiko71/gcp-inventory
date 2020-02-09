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

    result = meta.inventory_with_pagination(service_sql, "instances", {'project': project})

    # For each instance, we list the databases

    for instance in result:
        instance_name = instance['name']
        db_list = meta.inventory_without_pagination(service_sql, 'databases', {'project': project, 'instance': instance_name})
        instance['db_list'] = db_list
    
    return result




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

    filestores_locations = meta.inventory_without_pagination(service_filestore, ['projects', 'locations'], 
                                    {'name': "projects/" + project}, getter='locations')

    # For each location, we list all available instances                                    

    for loc in filestores_locations:

        loc_name = loc['name']
        result_list = meta.inventory_without_pagination(service_filestore, ['projects', 'locations', 'instances'], 
                                        {'parent': loc_name}, getter = 'instances')
        if len(result_list) != 0:
            list_filestore[loc_name] = result_list

    # Storing results

    return list_filestore



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

    result = {}

    # List of instances

    result = meta.inventory_without_pagination(service_bigtable, ['projects', 'instances'], 
                                                 {'parent': "projects/" + project}, getter='instances')

    # For each instance, we look for clusters                                                 

    for instance in result:
        instance_name = instance['name']
        list_clusters = meta.inventory_without_pagination(service_bigtable, ['projects', 'instances', 'clusters'], 
                                                 {'parent': instance_name}, getter='clusters')
        config.global_inventory['clusters'] = list_clusters

    return result
