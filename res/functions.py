import io, os, sys, time
import json

import googleapiclient

from googleapiclient import discovery
from googleapiclient import errors


MAX_RESULTS = 1000


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
        if max_results != None:
            params['pageToken'] = nextPageToken
        results_list = inventory_function.list(**params).execute()
        if getter in results_list:
                inventory = inventory + results_list[getter]
        if 'nextPageToken' in results_list:
            nextPageToken = results_list['nextPageToken']    
            cont = True

    return inventory

