# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging

from collections import defaultdict
from zuul import model
from zuul.lib.logutil import get_annotated_logger
from zuul.zk import LockException


def add_resources(target, source):
    for key, value in source.items():
        target[key] += value


def subtract_resources(target, source):
    for key, value in source.items():
        target[key] -= value


class Nodepool(object):
    log = logging.getLogger('zuul.nodepool')

    def __init__(self, scheduler):
        self.requests = {}
        self.sched = scheduler
        self.current_resources_by_tenant = {}
        self.current_resources_by_project = {}

    def emitStats(self, request):
        # Implements the following :
        #  counter zuul.nodepool.requests.<state>.total
        #  counter zuul.nodepool.requests.<state>.label.<label>
        #  counter zuul.nodepool.requests.<state>.size.<size>
        #  timer   zuul.nodepool.requests.(fulfilled|failed)
        #  timer   zuul.nodepool.requests.(fulfilled|failed).<label>
        #  timer   zuul.nodepool.requests.(fulfilled|failed).<size>
        #  gauge   zuul.nodepool.current_requests
        if not self.sched.statsd:
            return
        statsd = self.sched.statsd
        pipe = statsd.pipeline()
        state = request.state
        dt = None

        if request.canceled:
            state = 'canceled'
        elif request.state in (model.STATE_FULFILLED, model.STATE_FAILED):
            dt = int((request.state_time - request.requested_time) * 1000)

        key = 'zuul.nodepool.requests.%s' % state
        pipe.incr(key + ".total")

        if dt:
            pipe.timing(key, dt)
        for node in request.nodeset.getNodes():
            pipe.incr(key + '.label.%s' % node.label)
            if dt:
                pipe.timing(key + '.label.%s' % node.label, dt)
        pipe.incr(key + '.size.%s' % len(request.nodeset.nodes))
        if dt:
            pipe.timing(key + '.size.%s' % len(request.nodeset.nodes), dt)
        pipe.gauge('zuul.nodepool.current_requests', len(self.requests))
        pipe.send()

    def emitStatsResources(self):
        if not self.sched.statsd:
            return
        statsd = self.sched.statsd

        for tenant, resources in self.current_resources_by_tenant.items():
            for resource, value in resources.items():
                key = 'zuul.nodepool.resources.tenant.' \
                      '{tenant}.{resource}'
                statsd.gauge(key, value, tenant=tenant, resource=resource)
        for project, resources in self.current_resources_by_project.items():
            for resource, value in resources.items():
                key = 'zuul.nodepool.resources.project.' \
                      '{project}.{resource}'
                statsd.gauge(key, value, project=project, resource=resource)

    def emitStatsResourceCounters(self, tenant, project, resources, duration):
        if not self.sched.statsd:
            return
        statsd = self.sched.statsd

        for resource, value in resources.items():
            key = 'zuul.nodepool.resources.tenant.{tenant}.{resource}'
            statsd.incr(key, value * duration,
                        tenant=tenant, resource=resource)
        for resource, value in resources.items():
            key = 'zuul.nodepool.resources.project.' \
                  '{project}.{resource}'
            statsd.incr(key, value * duration,
                        project=project, resource=resource)

    def requestNodes(self, build_set, job, relative_priority, event=None):
        log = get_annotated_logger(self.log, event)
        # Create a copy of the nodeset to represent the actual nodes
        # returned by nodepool.
        nodeset = job.nodeset.copy()
        req = model.NodeRequest(self.sched.hostname, build_set, job,
                                nodeset, relative_priority, event=event)
        self.requests[req.uid] = req

        if nodeset.nodes:
            self.sched.zk.submitNodeRequest(req, self._updateNodeRequest)
            # Logged after submission so that we have the request id
            log.info("Submitted node request %s", req)
            self.emitStats(req)
        else:
            log.info("Fulfilling empty node request %s", req)
            req.state = model.STATE_FULFILLED
            self.sched.onNodesProvisioned(req)
            del self.requests[req.uid]
        return req

    def cancelRequest(self, request):
        log = get_annotated_logger(self.log, request.event_id)
        log.info("Canceling node request %s", request)
        if request.uid in self.requests:
            request.canceled = True
            try:
                self.sched.zk.deleteNodeRequest(request)
            except Exception:
                log.exception("Error deleting node request:")

    def reviseRequest(self, request, relative_priority=None):
        '''Attempt to update the node request, if it is not currently being
        processed.

        :param: NodeRequest request: The request to update.
        :param relative_priority int: If supplied, the new relative
            priority to set on the request.

        '''
        log = get_annotated_logger(self.log, request.event_id)
        if relative_priority is None:
            return
        try:
            self.sched.zk.lockNodeRequest(request, blocking=False)
        except LockException:
            # It may be locked by nodepool, which is fine.
            log.debug("Unable to revise locked node request %s", request)
            return False
        try:
            old_priority = request.relative_priority
            request.relative_priority = relative_priority
            self.sched.zk.storeNodeRequest(request)
            log.debug("Revised relative priority of "
                      "node request %s from %s to %s",
                      request, old_priority, relative_priority)
        except Exception:
            log.exception("Unable to update node request %s", request)
        finally:
            try:
                self.sched.zk.unlockNodeRequest(request)
            except Exception:
                log.exception("Unable to unlock node request %s", request)

    def holdNodeSet(self, nodeset, autohold_key):
        '''
        Perform a hold on the given set of nodes.

        :param NodeSet nodeset: The object containing the set of nodes to hold.
        :param set autohold_key: A set with the tenant/project/job names
            associated with the given NodeSet.
        '''
        self.log.info("Holding nodeset %s" % (nodeset,))
        (hold_iterations,
         reason,
         node_hold_expiration) = self.sched.autohold_requests[autohold_key]
        nodes = nodeset.getNodes()

        for node in nodes:
            if node.lock is None:
                raise Exception("Node %s is not locked" % (node,))
            node.state = model.STATE_HOLD
            node.hold_job = " ".join(autohold_key)
            node.comment = reason
            if node_hold_expiration:
                node.hold_expiration = node_hold_expiration
            self.sched.zk.storeNode(node)

        # We remove the autohold when the number of nodes in hold
        # is equal to or greater than (run iteration count can be
        # altered) the number of nodes used in a single job run
        # times the number of run iterations requested.
        nodes_in_hold = self.sched.zk.heldNodeCount(autohold_key)
        if nodes_in_hold >= len(nodes) * hold_iterations:
            self.log.debug("Removing autohold for %s", autohold_key)
            del self.sched.autohold_requests[autohold_key]

    def useNodeSet(self, nodeset, build_set=None):
        self.log.info("Setting nodeset %s in use" % (nodeset,))
        resources = defaultdict(int)
        for node in nodeset.getNodes():
            if node.lock is None:
                raise Exception("Node %s is not locked" % (node,))
            node.state = model.STATE_IN_USE
            self.sched.zk.storeNode(node)
            if node.resources:
                add_resources(resources, node.resources)
        if build_set and resources:
            # we have a buildset and thus also tenant and project so we
            # can emit project specific resource usage stats
            tenant_name = build_set.item.layout.tenant.name
            project_name = build_set.item.change.project.canonical_name

            self.current_resources_by_tenant.setdefault(
                tenant_name, defaultdict(int))
            self.current_resources_by_project.setdefault(
                project_name, defaultdict(int))

            add_resources(self.current_resources_by_tenant[tenant_name],
                          resources)
            add_resources(self.current_resources_by_project[project_name],
                          resources)
            self.emitStatsResources()

    def returnNodeSet(self, nodeset, build=None):
        self.log.info("Returning nodeset %s" % (nodeset,))
        resources = defaultdict(int)
        duration = None
        project = None
        tenant = None
        if build:
            project = build.build_set.item.change.project
            tenant = build.build_set.item.pipeline.tenant.name
        if (build and build.start_time and build.end_time and
            build.build_set and build.build_set.item and
            build.build_set.item.change and
            build.build_set.item.change.project):
            duration = build.end_time - build.start_time
            self.log.info("Nodeset %s with %s nodes was in use "
                          "for %s seconds for build %s for project %s",
                          nodeset, len(nodeset.nodes), duration, build,
                          project)
        for node in nodeset.getNodes():
            if node.lock is None:
                self.log.error("Node %s is not locked" % (node,))
            else:
                try:
                    if node.state == model.STATE_IN_USE:
                        if node.resources:
                            add_resources(resources, node.resources)
                        node.state = model.STATE_USED
                        self.sched.zk.storeNode(node)
                except Exception:
                    self.log.exception("Exception storing node %s "
                                       "while unlocking:" % (node,))
        self._unlockNodes(nodeset.getNodes())

        # When returning a nodeset we need to update the gauges if we have a
        # build. Further we calculate resource*duration and increment their
        # tenant or project specific counters. With that we have both the
        # current value and also counters to be able to perform accounting.
        if tenant and project and resources:
            project_name = project.canonical_name
            subtract_resources(
                self.current_resources_by_tenant[tenant], resources)
            subtract_resources(
                self.current_resources_by_project[project_name], resources)
            self.emitStatsResources()

            if duration:
                self.emitStatsResourceCounters(
                    tenant, project_name, resources, duration)

    def unlockNodeSet(self, nodeset):
        self._unlockNodes(nodeset.getNodes())

    def _unlockNodes(self, nodes):
        for node in nodes:
            try:
                self.sched.zk.unlockNode(node)
            except Exception:
                self.log.exception("Error unlocking node:")

    def lockNodeSet(self, nodeset, request_id):
        self._lockNodes(nodeset.getNodes(), request_id)

    def _lockNodes(self, nodes, request_id):
        # Try to lock all of the supplied nodes.  If any lock fails,
        # try to unlock any which have already been locked before
        # re-raising the error.
        locked_nodes = []
        try:
            for node in nodes:
                if node.allocated_to != request_id:
                    raise Exception("Node %s allocated to %s, not %s" %
                                    (node.id, node.allocated_to, request_id))
                self.log.debug("Locking node %s" % (node,))
                self.sched.zk.lockNode(node, timeout=30)
                locked_nodes.append(node)
        except Exception:
            self.log.exception("Error locking nodes:")
            self._unlockNodes(locked_nodes)
            raise

    def _updateNodeRequest(self, request, deleted):
        log = get_annotated_logger(self.log, request.event_id)
        # Return False to indicate that we should stop watching the
        # node.
        log.debug("Updating node request %s", request)

        if request.uid not in self.requests:
            log.debug("Request %s is unknown", request.uid)
            return False

        if request.canceled:
            del self.requests[request.uid]
            self.emitStats(request)
            return False

        # TODOv3(jeblair): handle allocation failure
        if deleted:
            log.debug("Resubmitting lost node request %s", request)
            request.id = None
            self.sched.zk.submitNodeRequest(request, self._updateNodeRequest)
        elif request.state in (model.STATE_FULFILLED, model.STATE_FAILED):
            log.info("Node request %s %s", request, request.state)

            # Give our results to the scheduler.
            self.sched.onNodesProvisioned(request)
            del self.requests[request.uid]

            self.emitStats(request)

            # Stop watching this request node.
            return False

        return True

    def acceptNodes(self, request, request_id):
        log = get_annotated_logger(self.log, request.event_id)

        # Called by the scheduler when it wants to accept and lock
        # nodes for (potential) use.  Return False if there is a
        # problem with the request (canceled or retrying), True if it
        # is ready to be acted upon (success or failure).

        log.info("Accepting node request %s", request)

        if request_id != request.id:
            log.info("Skipping node accept for %s (resubmitted as %s)",
                     request_id, request.id)
            return False

        if request.canceled:
            log.info("Ignoring canceled node request %s", request)
            # The request was already deleted when it was canceled
            return False

        # If we didn't request nodes and the request is fulfilled then just
        # return. We don't have to do anything in this case. Further don't even
        # ask ZK for the request as empty requests are not put into ZK.
        if not request.nodeset.nodes and request.fulfilled:
            return True

        # Make sure the request still exists. It's possible it could have
        # disappeared if we lost the ZK session between when the fulfillment
        # response was added to our queue, and when we actually get around to
        # processing it. Nodepool will automatically reallocate the assigned
        # nodes in that situation.
        try:
            if not self.sched.zk.nodeRequestExists(request):
                log.info("Request %s no longer exists, resubmitting",
                         request.id)
                request.id = None
                request.state = model.STATE_REQUESTED
                self.requests[request.uid] = request
                self.sched.zk.submitNodeRequest(
                    request, self._updateNodeRequest)
                return False
        except Exception:
            # If we cannot retrieve the node request from ZK we probably lost
            # the connection and thus the ZK session. Resubmitting the node
            # request probably doesn't make sense at this point in time as it
            # is likely to directly fail again. So just log the problem
            # with zookeeper and fail here.
            log.exception("Error getting node request %s:", request_id)
            request.failed = True
            return True

        locked = False
        if request.fulfilled:
            # If the request suceeded, try to lock the nodes.
            try:
                self.lockNodeSet(request.nodeset, request.id)
                locked = True
            except Exception:
                log.exception("Error locking nodes:")
                request.failed = True

        # Regardless of whether locking (or even the request)
        # succeeded, delete the request.
        log.debug("Deleting node request %s", request)
        try:
            self.sched.zk.deleteNodeRequest(request)
        except Exception:
            log.exception("Error deleting node request:")
            request.failed = True
            # If deleting the request failed, and we did lock the
            # nodes, unlock the nodes since we're not going to use
            # them.
            if locked:
                self.unlockNodeSet(request.nodeset)
        return True
