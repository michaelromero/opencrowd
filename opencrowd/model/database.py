"""
.. module:: database
   :platform: Unix, Mac
   :synopsis: A virtualized class for storing opencrowd components

A virtualized class for storing opencrowd components
"""
import redis
import pickle
import logging

database_logger = logging.getLogger('database')


class Database(object):
    """
    The values below will generally default from opencrowd.config.redis

    :param db_host: database ip address
    :type db_host: str
    :param db_port: port number to access on the database
    :type db_port: int
    """
    def __init__(self, db_host, db_port):
        self.database_host = db_host
        self.database_port = db_port
        self.database = self.connect()

    def connect(self):
        """
        Currently connects to a redis host.

        .. todo:
           Virtualize these methods and create subclasses of Database

        """
        try:
            database = redis.StrictRedis(host=self.database_host,
                                         port=self.database_port,
                                         db=0)
            return database
        except Exception as e:
            database_logger.error("Unable to form connection with redis: {}".format(str(e)))

    def set(self, key, value):
        """
        Pickles the value and sets the database based on k:v

        :param key: the access key to store the value under (HEADER +\
        opencrowd_id)
        :type key: str
        :param value: value to store under the access key
        :type value: object
        """
        value = pickle.dumps(value)
        try:
            self.database[key] = value
        except Exception as e:
            database_logger.error("Unable to store '{}' in database: {}".format(key, str(e)))

    def get(self, key):
        """
        Unpickle the value from the database

        :param key: Key to unpickle (HEADER + opencrowd_id)
        :type key: str
        """
        try:
            pickled_object = self.database[key]
            try:
                unpickled_object = pickle.loads(pickled_object)
                return unpickled_object
            except KeyError as e:
                database_logger.error("KeyError in database: {}".format(str(e)))
        except Exception as e:
            database_logger.error("Unable to query key '{}' from redis: {}".format(key, str(e)))

    def delete(self, key):
        """
        Delete the key and its associated value from the database

        :param key: key and associated value to delete
        :type key: str
        """
        try:
            self.database.delete(key)
        except Exception as e:
            database_logger.error("Unable to delete key: {}. An exception of type {} occured. Arguments: {!r}".format(key, type(e).__name__, e.args))

    def exists(self, opencrowd_id):
        """
        Check if an opencrowd object exists

        :param opencrowd_id: HEADER + id of the object to lookup
        :type opencrowd_id: str
        :returns: True or False
        :rtype: bool
        """
        if self.database.exists(opencrowd_id):
            return True
        else:
            return False

