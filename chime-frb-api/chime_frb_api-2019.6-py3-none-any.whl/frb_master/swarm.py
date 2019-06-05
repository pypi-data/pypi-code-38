#!/usr/bin/env python
# -*- coding: utf-8 -*-

from chime_frb_api.core import API


class Swarm(API):
    """
    CHIME/FRB Swarm API

    Attributes
    ----------
    base_url : str
        Base URL at which the is accessible.
    """

    def __init__(self, base_url: str = "http://frb-vsop.chime:8001"):
        API.__init__(self, base_url=base_url)

    def get_jobs(self):
        """
        Returns the name of all jobs on the analysis cluster.
        """
        return self._get("/v1/swarm/jobs")

    def get_job_status(self, job_name: str):
        """
        Get status of all jobs matching job name

        Parameters
        ----------
        job_name : str
            Name of the job

        Returns
        -------
            { job_name : STATUS } : dict

            Where STATUS can be,
            NEW         The job was initialized.
            PENDING     Resources for the job were allocated.
            ASSIGNED    Docker assigned the job to nodes.
            ACCEPTED    The job was accepted by a worker node.
            PREPARING   Docker is preparing the job.
            STARTING    Docker is starting the job.
            RUNNING     The job is executing.
            COMPLETE    The job exited without an error code.
            FAILED      The job exited with an error code.
            SHUTDOWN    Docker requested the job to shut down.
            REJECTED    The worker node rejected the job.
            ORPHANED    The node was down for too long.
            REMOVE      The job is not terminal but the associated job was removed
        """
        return self._get("/v1/swarm/job-status/{}".format(job_name))

    def spawn_job(
        self,
        image_name: str,
        command: list,
        arguments: list,
        job_name: str,
        mount_archiver: bool = True,
        swarm_network: bool = True,
        job_mem_limit: int = None,
        job_mem_reservation: int = None,
    ):
        """
        Spawn a job on the CHIME/FRB Analysis Cluster

        Parameters
        ----------

        image_name : str
            Name of the container image to spawn the job with
            e.g. chimefrb/iautils:latest

        command : list
            The command to be run in the container

        arguments : list
            Arguments to the command

        job_name : string
            Unique name for the cluster job

        mount_archiver : bool
            Mount Site Data Archivers

        swarm_network : bool
            Mount Cluster Network

        job_mem_limit : int
            Represents the memory limit of the created container in bytes

        job_mem_reservation : int
            Represents the minimum memory reserved of the created container in bytes
        """
        payload = {
            "image_name": image_name,
            "command": command,
            "arguments": arguments,
            "job_name": job_name,
            "mount_archiver": mount_archiver,
            "swarm_network": swarm_network,
            "job_mem_reservation": job_mem_reservation,
            "job_mem_limit": job_mem_limit,
        }
        return self._post("/v1/swarm/spawn-job", payload)

    def get_logs(self, job_name: str):
        """
        Return logs from a CHIME/FRB Job

        Parameters
        ----------
        job_name : string
            Unique name for the cluster job

        Returns
        -------
            dict
        """
        return self._get("/v1/swarm/logs/{}".format(job_name))

    def prune_jobs(self,job_name):
        """
        Prune jobs with COMPLETED status regex match to job_name

        Parameters
        ----------
        job_name : string
            Unique name for the cluster job

        Returns
        -------
            dict: {job_name : boolean}
        """
        return self._get("/v1/swarm/prune-job/{}".format(job_name))

    def kill_job(self, job_name):
        """
        Kill a job with ANY status and exact match to job_name

        Parameters
        ----------
        job_name : string
            Unique name for the cluster job

        Returns
        -------
            dict: {job_name : boolean}
        """
        return self._get("/v1/swarm/kill-job/{}".format(job_name))
