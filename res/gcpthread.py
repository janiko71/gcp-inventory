import sys
from threading import Thread
import config


# =======================================================================================================================
#
#   Class created for (simple) multithreading
#
# =======================================================================================================================

class GCPThread(Thread):

    """
        Class used for threading inventories. It's a very simple class where a thread is created (__init__) with the function
        to call (with its arguments), and instead of executing all inventories in sequence, we create a thread for each of them.

        Inventories are the kind of tasks you can easily parallelize!

    """    

    def __init__(self, thread_name, gcp_inventory_service, project_id):

        """
            Thread Class initialization.  

            :param gcp_inventory_service: name of GCP inventoryservice
            :type gcp_inventory_service: function object
            :param project_id: targetted project 
            :type project_id: string

            :return: nothing
        """ 

        Thread.__init__(self)
        self.thread_name = thread_name
        self.gcp_inventory_service = gcp_inventory_service
        self.project_id = project_id


    def run(self):
        
        """
            Code to execute => the AWS function, in its own thread
        """
        
        config.global_inventory[self.thread_name] = self.gcp_inventory_service(self.project_id)


