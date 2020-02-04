import time
import logging
import json
import os
from time import gmtime, strftime

import globals

import googleapiclient

from googleapiclient import discovery
from googleapiclient import errors

#
# Environment Variables & File handling & logging
#


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

logger          = logging.getLogger("aws-inventory")
hdlr            = logging.FileHandler(log_filepath+"inventory.log")
formatter       = logging.Formatter("%(asctime)s %(levelname)s %(message)s")


# --- Log handler

hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)

#
# --- Global inventory, for multithreading purpose
#

global_inventory = {}

# --- Project

project = "secu-si"

# --- Regions & Zones

compute_informational_services_global = ["regions", "zones", "interconnectLocations"]   

service_compute = googleapiclient.discovery.build('compute', 'v1')

for service_name in compute_informational_services_global:
    global_inventory[service_name] = globals.inventory_with_pagination(service_compute, service_name, {'project': project})

# Special lists

list_zones = global_inventory['zones']
list_regions = global_inventory['regions']


# --- Counters

nb_svc = 0
nb_units_todo = 0
nb_units_done = 0

