import time
import logging
import json
import os
from time import gmtime, strftime

import googleapiclient

from googleapiclient import discovery
from googleapiclient import errors

import res.functions as func

#
# Environment Variables & File handling & logging
#

#global global_inventory

# --- Format for displaying actions

display = "OwnerID : {} ! {:6.2f} % ! Region : {:16} ! {} ({}){}"


# --- Initial values for inventory files names

t = gmtime()
timestamp = strftime("%Y%m%d%H%M%S", t)
filepath = "./output/"
os.makedirs(filepath, exist_ok=True)


# --- logging variables

log_filepath    = "./log/"
os.makedirs(log_filepath, exist_ok=True)

logger          = logging.getLogger("gcp-inventory")
hdlr            = logging.FileHandler(log_filepath+"inventory.log")
formatter       = logging.Formatter("%(asctime)s %(levelname)s %(message)s")


# --- Log handler

hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)


# --- Project

project = "secu-si"

# --- Regions & Zones

info_inventory = {}

compute_informational_services_global = ["regions", "zones", "interconnectLocations"]   

service_compute = googleapiclient.discovery.build('compute', 'v1')

for service_name in compute_informational_services_global:
    info_inventory[service_name] = func.inventory_with_pagination(service_compute, service_name, {'project': project})

# Special lists

list_zones = info_inventory['zones']
list_regions = info_inventory['regions']


# --- Counters

nb_svc = 0
nb_units_todo = 0
nb_units_done = 0


#
# --- Global inventory, for multithreading purpose
#
global_inventory = {}


