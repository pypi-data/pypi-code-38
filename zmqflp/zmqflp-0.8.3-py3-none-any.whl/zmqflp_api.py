"""
flcliapi - Freelance Pattern agent class
Model 3: uses ROUTER socket to address specific services
Author: Min RK <benjaminrk@gmail.com>
Modified by: Curtis Wang <ycwang@u.northwestern.edu>

LRU queue is used to connect to servers to add load balancing
Also allows for a context-manager-based client
"""

