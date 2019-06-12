#!/usr/bin/env python
# -*- coding: utf-8 -*-

class PodiumApplicationAlreadyRegistered(Exception):
    """This exception is raised if the user calls register_podium_application
    more than once"""
    pass

class PodiumApplicationNotRegistered(Exception):
    """This exception is raised if a request is attempted without first
    calling register_podium_application"""
    pass

class NoEndpointOrIdsProvided(Exception):
    """This exception is raised if a request is attempted
    without providing an endpoint or required ids.
    """
    pass