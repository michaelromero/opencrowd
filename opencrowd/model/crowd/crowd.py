"""
.. module:: crowd
  :platform: Unix, Mac
  :synopsis: a virtual class for extending crowd sources

A virtual class for extending crowd sources in the future
    .. todo::
       Further virtualize AmazonMechanicalTurk as a template for future crowds.

"""

import logging

crowd_logger = logging.getLogger('crowd')


class Crowd(object):
    """
    A virtual class for extending crowd sources in the future
    """
    def __init__(self):
        pass

    def generate_crowdsource_connection(self):
        """
        Needs to return a crowd object capable of ... [todo]
        """
        raise NotImplementedError

    def push(self, HIT):
        """
        One of the virtualized functions mentioned above
        """
        raise NotImplementedError
