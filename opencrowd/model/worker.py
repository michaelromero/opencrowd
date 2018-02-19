"""
.. module:: worker
   :platform: Unix, Mac
   :synopsis: a worker represents a unique human and their contributions to
   opencrowd HITs

A worker represents a unique human and their contributions to opencrowd HITs. A
worker can own qualifications based on their performance, be blocked and
unblocked, or awarded bonuses based on the quality of their work, among other
things.

.. moduleauthor:: Michael Romero <michaelrom@zillowgroup.com>
"""

import json
import logging
from opencrowd.model.database import Database
from opencrowd.config.redis import DB_PORT, DB_HOST
from opencrowd.config.opencrowd import WORKER_HEADER

manager_logger = logging.getLogger('manager')
worker_logger = logging.getLogger('worker')

class Manager(object):
    """
    The Manager class is for, well, managing opencrowd's worker base.
    """
    def __init__(self):
        pass

    @staticmethod
    def manage_worker(worker):
        if not Manager.worker_exists(worker.worker_id):
            print('not found')
        exit(1)
            # create worker via worker id
        # update worker
        pass

    @staticmethod
    def worker_exists(worker_id):
        """
        Check if a worker exists

        :param worker_id: id of the worker to check
        :type worker_id: str
        :returns: True or False
        :rtype: bool
        """
        database = Database(DB_HOST, DB_PORT)
        return database.exists(WORKER_HEADER + worker_id)

    @staticmethod
    def worker_delete(worker_id):
        """
        Delete a worker if it exists

        :param worker_id: id of the worker to check
        :type worker_id: str
        :returns: True or False
        :rtype: bool
        """
        database = Database(DB_HOST, DB_PORT)
        try:
            if database.exists(WORKER_HEADER + worker_id):
                database.delete(WORKER_HEADER + worker_id)
        except Exception as e:
            manager_logger.error("Unable to delete worker '{}': {}".format(worker_id, str(e)))

    @staticmethod
    def process_assignment(assignment):
        print(assignment)
        exit(1)


        pass

class Worker(object):
    """
    A worker represents a unique human and their contributions to opencrowd
    HITs. Workers are generated and saved automatically via project/task/HIT
    updates.

    :param worker_id: The unique ID (generally via AMT) of the worker
    :type worker_id: str
    """
    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.save()

    def save(self):
        """
        Utilize the Database class to save this object
        """
        database = Database(DB_HOST, DB_PORT)
        database.set(WORKER_HEADER, self)
        worker_logger.debug("Saving worker:{}".format(self.worker_id))


