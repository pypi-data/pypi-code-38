import argparse
import copy
import json
import logging
import os
import signal
import sys
import time
from threading import Thread
from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException
from jupyterhubutils.scanrepo import ScanRepo


class Prepuller(object):
    """Class for generating and reaping the Pods for the prepuller.
    """
    repo = None
    logger = None
    client = None
    args = argparse.Namespace(debug=False,
                              json=True,
                              repo=None,
                              owner="lsstsqre",
                              name="sciplat-lab",
                              port=None,
                              recommended=True,
                              dailies=3,
                              weeklies=2,
                              releases=1,
                              insecure=False,
                              sort="name",
                              list=None,
                              command=["/bin/sh",
                                       "-c",
                                       "echo Prepuller run for $(hostname)" +
                                       "complete at $(date)."],
                              path=("/v2/repositories/lsstsqre/" +
                                    "sciplat-lab/tags/"),
                              no_scan=False,
                              namespace=None,
                              timeout=3300,
                              uid=769
                              )
    images = []
    nodes = []
    pod_specs = {}
    created_pods = []

    def __init__(self, args=None):
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        if args:
            self.args = args
        if self.args and self.args.debug:
            self.logger.setLevel(logging.DEBUG)
            self.logger.debug("Debug logging on.")
        else:
            self.logger.setLevel(logging.INFO)
        namespace = None
        try:
            config.load_incluster_config()
            secrets = "/var/run/secrets/kubernetes.io/serviceaccount/"
            try:
                with open(os.path.join(secrets, "namespace"), "r") as f:
                    namespace = f.read()
            except OSError:
                pass
        except ConfigException:
            try:
                config.load_kube_config()
            except Exception:
                self.logger.critical(sys.argv[0],
                                     " must be run from a system",
                                     " with k8s API access.")
                raise
        if self.args.namespace:
            namespace = self.args.namespace
        if not namespace:
            namespace = os.getenv('PREPULLER_NAMESPACE')
        if not namespace:
            self.logger.warning("Using kubernetes namespace 'default'")
            namespace = "default"
        self.namespace = namespace
        self.client = client.CoreV1Api()
        self.logger.debug("Arguments: %s" % str(args))
        if self.args.command:
            self.command = self.args.command
        if self.args.list:
            for image in self.args.list:
                # Make fully-qualified image name
                colons = image.count(':')
                if colons == 0:
                    image = image + ":latest"
                slashes = image.count('/')
                if slashes == 0:
                    image = "library/" + image
            self.images.append(image)
        # Cheap way to deduplicate lists
        self.images = list(set(self.images))
        if self.images:
            self.images.sort()
        # Not portable to non-Unixy systems.
        if self.args.timeout >= 0:
            self.logger.debug("Setting timeout to %d s." % self.args.timeout)
            signal.signal(signal.SIGALRM, self._timeout_handler)
            signal.alarm(self.args.timeout)

    def _timeout_handler(self, signum, frame):
        self.logger.error(
            "Did not complete in %d s.  Terminating." % self.args.timeout)
        self._destroy_pods(selective=False)
        raise RuntimeError("Timed out")

    def _destroy_pods(self, selective=False):
        """Get a pod list and delete any that are still running if
        selective is False, or any in state "Succeeded" or "Failed"
        if selective is True.
        """
        self.logger.debug("Looking for pods to delete.")
        cleanup = self._get_deletion_list(selective=selective)
        for podname in cleanup:
            self.delete_pod(podname)

    def _get_deletion_list(self, selective=True):
        cleanup = []
        speclist = []
        v1 = self.client
        for x in self.pod_specs:
            speclist.extend(self.pod_specs[x])
        specnames = [self._derive_pod_name(x) for x in speclist]
        podlist = v1.list_namespaced_pod(self.namespace)
        for pod in podlist.items:
            podname = pod.metadata.name
            phase = pod.status.phase
            if podname in specnames:
                if selective:
                    if (phase != "Succeeded" and phase != "Failed"):
                        self.logger.debug("Pod '%s' %s; not cleaning."
                                          % (podname, phase))
                        continue
                self.logger.debug(
                    "Pod '%s' %s; adding to cleanup." % (podname, phase))
                cleanup.append(podname)
        return cleanup

    def update_images_from_repo(self):
        """Scan the repo looking for images.
        """
        if not self.repo:
            self.repo = ScanRepo(host=self.args.repo,
                                 path=self.args.path,
                                 owner=self.args.owner,
                                 name=self.args.name,
                                 dailies=self.args.dailies,
                                 weeklies=self.args.weeklies,
                                 releases=self.args.releases,
                                 recommended=self.args.recommended,
                                 json=True, insecure=self.args.insecure,
                                 sort_field=self.args.sort,
                                 debug=self.args.debug)
        if not self.args.no_scan:
            if self.args.repo:
                self.logger.debug("Scanning images: '%s' " % self.args.repo)
            else:
                self.logger.debug("Scanning Docker repo for images")
            self.repo.scan()
            if self.repo.debug:
                repocopy = copy.deepcopy(self.repo.data)
                for itype in repocopy:
                    for item in repocopy[itype]:
                        uddt = item["updated"]
                        item["updated"] = uddt.isoformat()
                self.logger.debug("Scan Data: " +
                                  json.dumps(repocopy,
                                             sort_keys=True,
                                             indent=4))
            scan_imgs = []
            sections = []
            if self.args.recommended:
                sections.extend(["recommended"])
            sections.extend(["daily", "weekly", "release"])
            for section in sections:
                for entry in self.repo.data[section]:
                    exhost = ''
                    if self.args.repo:
                        exhost = self.args.repo
                        if self.args.port:
                            exhost += ":" + self.args.port + "/"
                    scan_imgs.append(exhost + self.args.owner + "/" +
                                     self.args.name + ":" +
                                     entry["name"])
            current_imgs = [x for x in self.images]
            # Dedupe by running the list through a set.
            current_imgs.extend(scan_imgs)
            current_imgs = list(set(current_imgs))
            if current_imgs:
                current_imgs.sort()
            self.images = current_imgs

    def build_nodelist(self):
        """Make a list of all schedulable nodes, respecting RESTRICT_*
        environment variables.
        """
        v1 = self.client
        logger = self.logger
        logger.debug("Getting schedulable node list.")
        v1nodelist = v1.list_node()
        nodes = []
        for thing in v1nodelist.items:
            spec = thing.spec
            if spec.unschedulable:
                continue
            if spec.taints:
                taints = [x.effect for x in spec.taints]
                if "NoSchedule" in taints:
                    continue
            if self.reject_by_label(thing):
                continue
            nodes.append(thing.metadata.name)
        logger.debug("Schedulable list: %s" % str(nodes))
        self.nodes = nodes

    def reject_by_label(self, node):
        """If node labels are set to restrict Lab spawn, reject nodes that
        are not suitable for Lab/Dask.
        """
        logger = self.logger
        logger.debug("Checking for node labels.")
        if not os.getenv("RESTRICT_LAB_NODES"):
            logger.debug("Lab nodes are not restricted.")
            return False
        labels = node.metadata.labels
        name = node.metadata.name or 'Node Name Unknown'
        if not labels:
            logger.debug("Nodes are not labelled.")
            return False
        lab_ok = labels.get("jupyterlab")
        if lab_ok and lab_ok == "ok":
            logger.debug("Node '%s' is allowed for Lab usage." % name)
            return False
        if not os.getenv("ALLOW_DASK_SPAWN"):
            logger.debug("Lab spawn not allowed for node '%s'." % name)
            return True
        if not os.getenv("RESTRICT_DASK_NODES"):
            logger.debug("Dask allowed and unrestricted.")
            return False
        dask_ok = labels.get("dask")
        if dask_ok and dask_ok == "ok":
            logger.debug("Node '%s' is allowed for Dask usage." % name)
            return False
        logger.debug("Lab/Dask spawn not allowed for node '%s'" % name)
        return True

    def build_pod_specs(self):
        """Build a dict of Pod specs by node, each node having a list of
        specs.
        """
        specs = {}
        for node in self.nodes:
            specs[node] = []
            for img in self.images:
                specs[node].append(self._build_pod_spec(img, node))
        self.pod_specs = specs
        self.logger.debug("Specs: %s" % str(self.pod_specs))

    def _build_pod_spec(self, img, node):
        spec = client.V1PodSpec(
            containers=[
                client.V1Container(
                    command=self.command,
                    image=img,
                    image_pull_policy="Always",
                    name=self._podname_from_image(img),
                    security_context=client.V1PodSecurityContext(
                        run_as_user=self.args.uid)
                )
            ],
            restart_policy="Never",
            node_name=node
        )
        return spec

    def _podname_from_image(self, img):
        iname = '-'.join(img.split('/')[-2:])
        iname = iname.replace(':', '-')
        iname = iname.replace('_', '-')
        return iname

    def clean_completed_pods(self):
        """Get a pod list and delete any that are in the speclist and have
        already run to completion.
        """
        self._destroy_pods(selective=True)

    def start_single_pod(self, spec):
        """Run a pod, with a single container, on a particular node.
        (Assuming that the pod is itself tied to a node in the pod spec.)
        This has the effect of pulling the image for that pod onto that
        node.  The run itself is unimportant.  It returns the name of the
        created pod.
        """
        v1 = self.client
        name = self._derive_pod_name(spec)
        pod = client.V1Pod(spec=spec,
                           metadata=client.V1ObjectMeta(
                               name=name)
                           )
        name = spec.containers[0].name
        self.logger.debug("Running pod %s" % name)
        made_pod = v1.create_namespaced_pod(self.namespace, pod)
        podname = made_pod.metadata.name
        return podname

    def _derive_pod_name(self, spec):
        """Pod name is based on image and node.
        """
        return ("pp-" + self._podname_from_image(spec.containers[0].image) +
                "-" + spec.node_name.split('-')[-1])

    def run_pods(self):
        """Run pods for all nodes.  Parallelize across nodes.
        """
        tlist = []
        for node in self.pod_specs:
            speclist = list(self.pod_specs[node])
            thd = Thread(target=self.run_pods_for_node, args=(node, speclist))
            tlist.append(thd)
            thd.start()
        # Wait for all threads to return
        for thd in tlist:
            self.logger.debug("Wait for thread '%s' to complete" % thd.name)
            thd.join()

    def run_pods_for_node(self, node, speclist):
        """Execute pods one at a time, so we don't overwhelm I/O.
        Execute this method in parallel across all nodes for best
        results.  Each node should have its own I/O, so they should all be
        busy at once.
        """
        self.logger.debug("Running pods for node %s" % node)
        for spec in speclist:
            name = spec.containers[0].name
            self.logger.debug("Running pod '%s' for node '%s'" % (name,
                                                                  node))
            podname = self.start_single_pod(spec)
            self.wait_for_pod(podname)

    def wait_for_pod(self, podname, delay=1, max_tries=3600):
        """Wait for a particular pod to go into phase "Succeeded" or
        "Failed", and then delete the pod.
        Raise an exception if the delay timer expires.
        """
        v1 = self.client
        namespace = self.namespace
        tries = 1
        while True:
            pod = v1.read_namespaced_pod(podname, namespace)
            phase = pod.status.phase
            if phase in ["Failed", "Succeeded"]:
                if phase == "Failed":
                    self.logger.error("Pod '%s' failed" % podname)
                self.delete_pod(podname)
                return
            if tries >= max_tries:
                errstr = ("Pod '%s' did not complete after " % podname +
                          "%d %d s iterations." % (max_tries, delay))
                self.logger.error(errstr)
                raise RuntimeError(errstr)
            pstr = "Wait %d s [%d/%d]for pod '%s' [%s]" % (
                delay, tries, max_tries, podname, phase)
            self.logger.debug(pstr)
            time.sleep(delay)
            tries = tries + 1

    def delete_pod(self, podname):
        """Delete a named pod.
        """
        v1 = self.client
        self.logger.debug("Deleting pod %s" % podname)
        v1.delete_namespaced_pod(podname, self.namespace)
