from __future__ import print_function

import random
import sys
from threading import Thread
from time import sleep

import colorama
from cement.core.exc import CaughtSignal

from orchestrate.common import safe_format
from orchestrate.core.services.base import Service


class FollowPodsRunner(object):
  def __init__(self, kubernetes_service, kube_config, experiment_id, color_off=False, max_pods=10):
    self.kubernetes_service = kubernetes_service
    self._experiment_id = experiment_id
    self._kube_config = kube_config
    self._max_pods = max_pods
    self._pod_names = []
    self._processes = []
    self._colors = [
      colorama.Fore.RESET,
    ] if color_off else [
      colorama.Fore.CYAN,
      colorama.Fore.GREEN,
      colorama.Fore.MAGENTA,
      colorama.Fore.RED,
      colorama.Fore.YELLOW,
      colorama.Fore.BLUE,
    ]

  def wait_for_pod_logs(self, pod_name):
    while self.kubernetes_service.get_pod(pod_name).status.phase == 'Pending':
      sleep(random.uniform(5, 6))

  def execute_follow(self, pod_name, color, kube_config):
    try:
      self.wait_for_pod_logs(pod_name)
      for line in self.kubernetes_service.logs(pod_name, follow=True):
        formatted_line = safe_format(
          "[{}] {}",
          pod_name,
          line.decode('utf-8'),
        )
        if sys.stdout.isatty():
          formatted_line = safe_format(
            "{}{}{}",
            color,
            formatted_line,
            colorama.Style.RESET_ALL,
          )
        sys.stdout.write(formatted_line)
        sys.stdout.flush()
    except Exception:
      print(safe_format("Stopping follow for pod {}", pod_name))

  def follow(self, pod_name, function):
    if pod_name not in self._pod_names:
      if len(self._pod_names) >= self._max_pods:
        print(safe_format("""
    We only support following the logs of {} at the same time.
    If you'd like to see the logs of all pods, you can run `sigopt logs {}`.
    If you'd like to see logs for a specific pod, you can use kubectl directly:
        `sigopt kubectl logs --follow {} --namespace orchestrate`.
        """, self._max_pods, self._experiment_id, pod_name))
        return
      else:
        color = self._colors.pop(0)
        process = Thread(
          target=self.execute_follow,
          args=(pod_name, color, self._kube_config),
          name=pod_name
        )
        process.daemon = True
        process.start()
        self._processes.append(process)
        self._pod_names.append(pod_name)
        self._colors.append(color)

  def done(self):
    return not all([process.is_alive() for process in self._processes])

  def stop(self):
    if not self._pod_names:
      print(safe_format("""
  There are currently no workers for that experiment on this cluster.
  Run `sigopt status {}` to see the status of your experiment.
        """, self._experiment_id))

    for process in self._processes:
      process.join()


class JobLogsService(Service):
  def get_logs(self, experiment_id):
    job_name = self.services.job_runner_service.job_name(experiment_id)
    pod_names = self.services.kubernetes_service.pod_names(job_name)
    for name in pod_names:
      print(safe_format(
        '\nLogs for pod {} in job {} for experiment {}:',
        name,
        job_name,
        experiment_id,
      ))
      try:
        print(self.services.kubernetes_service.logs(name))
      except Exception:
        print(safe_format("""
  There was an error fetching your logs for pod {}.
  To check the status of your experiment, run `sigopt status {}`.
          """, name, experiment_id))

  def follow_logs(self, experiment_id, color_off=False):
    job_name = self.services.job_runner_service.job_name(experiment_id)
    kube_config = self.services.kubernetes_service.kube_config
    follow_pods_runner = FollowPodsRunner(
      self.services.kubernetes_service,
      kube_config,
      experiment_id,
      color_off
    )
    try:
      while True:
        current_pods = self.services.kubernetes_service.pod_names(job_name)
        for pod in current_pods:
          follow_pods_runner.follow(pod, self.services.kubernetes_service.logs)

        if follow_pods_runner.done():
          break
        sleep(1)
      follow_pods_runner.stop()
    except (KeyboardInterrupt, CaughtSignal):
      print(colorama.Fore.RESET + "Interrupted: Exiting...")
