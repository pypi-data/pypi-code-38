# -*- coding: utf-8 -*-
# Copyright 2017 - 2019 ibelie, Chen Jie, Joungtao. All rights reserved.
# Use of this source code is governed by The MIT License
# that can be found in the LICENSE file.

from __future__ import print_function

import threading
import traceback
import warnings
import time
import os
import re

class Travis(object):
	ORIGIN_REGX = re.compile(r'https://github.com/(?P<user>[^/]+)/(?P<project>[^\.]+).git', re.I)
	DOCKER_PATH = __file__.replace('travis.py', 'docker')
	RUNNER = 'runner'
	IMAGES = {
		'android': 'travis-amethyst',
		'erlang':  'travis-amethyst',
		'haskell': 'travis-amethyst',
		'perl':    'travis-amethyst',
		'default': 'travis-garnet',
		'go':      'travis-garnet',
		'jvm':     'travis-garnet',
		'node_js': 'travis-garnet',
		'php':     'travis-garnet',
		'python':  'travis-garnet',
		'ruby':    'travis-garnet',
	}

	@property
	def docker(self):
		client = getattr(self, '_docker_client', None)
		if client is None:
			import docker
			client = docker.from_env(version = 'auto')
			self._docker_client = client
		return client

	def check(self, name):
		'''Check docker image with travis language name or image name.'''
		image = self.IMAGES.get(name, name)
		return self.docker.api.images(image, quiet = True)

	def build(self, name):
		'''Build docker image with travis language name or image name.'''
		if self.check(name): return True
		from docker.utils.json_stream import json_stream
		image = self.IMAGES.get(name, name)
		path = os.path.abspath(os.path.join(self.DOCKER_PATH, image))
		response = self.docker.api.build(path = path, tag = image, rm = True)
		imageID = None
		for event in json_stream(response):
			if 'error' in event:
				print(event['error'])
				return False
			elif 'stream' in event:
				print(event['stream'], end = '')
				match = re.search(r'(^Successfully built |sha256:)([0-9a-f]+)$', event['stream'])
				if match:
					imageID = match.group(2)
			else:
				print(event)
		return imageID is not None

	def _run(self, task_name, log_dir, mem_limit, cpu_list, cpu_sema, **kwargs):
		def __run():
			try:
				container = self.docker.containers.create(
					name = task_name, cpuset_cpus = cpu,
					mem_limit = mem_limit, **kwargs)
				container.start()

				logs = container.logs(stream = True)
				not os.path.isdir(log_dir) and os.makedirs(log_dir)
				with open('%s/%s.txt' % (log_dir, task_name), 'w') as f:
					for log in logs:
						f.write(log)

				exit_status = container.wait()['StatusCode']
				print('%s travis exit status:' % task_name, exit_status)

				container.remove()
			except Exception as e:
				warnings.warn('Travis runner "%s" error:\n%s' % (task_name, traceback.format_exc()), RuntimeWarning)

			cpu_list.add(cpu)
			cpu_sema.release()

		cpu_sema.acquire()
		cpu = cpu_list.pop()
		threading.Thread(target = __run).start()

	def _getGitInfo(self, git_repo):
		info = {
			'user': 'UNKNOWN',
			'project': 'UNKNOWN',
		}
		cwd = os.getcwd()
		os.chdir(git_repo)
		with os.popen('git config --get remote.origin.url') as proc:
			line = proc.readline()
			while line:
				m = self.ORIGIN_REGX.match(line)
				if m:
					info['user'] = m.group('user')
					info['project'] = m.group('project')
				line = proc.readline()
		os.chdir(cwd)
		return info

	def run(self, git_repo, commits, language = 'default', log_dir = '', mem_limit = '1G', cpu_count = 1, repeat_count = 1, yaml_files = (), extra_commands = (), extra_volumes = {}, environment = {}):
		if not self.build(language): return
		gitInfo = self._getGitInfo(git_repo)
		repoDir = '/home/travis/%s' % self.RUNNER
		workDir = '/home/travis/build'
		yamlDir = '/home/travis/travisYAML'
		command = [
			'mkdir -p %s/%s' % (self.RUNNER, gitInfo['project']),
			'cd %s/%s' % (self.RUNNER, gitInfo['project']),
			'git clone %s . ' % repoDir,
			'git remote set-url origin https://github.com/%s/%s.git' % (self.RUNNER, gitInfo['project']),
			'git checkout %(commit)s',
			'ls' if not yaml_files else 'cp %s/%%(yaml_file)s .travis.yml' % yamlDir,
			'~/travis_compile > ci.sh',
			'git remote set-url origin %s' % repoDir,
			'bash ci.sh',
		]
		command.extend(extra_commands)
		command = '/bin/bash -lc "%s"' % ' && '.join(command)

		cpu_list = set(map(str, xrange(cpu_count)))
		cpu_sema = threading.Semaphore(cpu_count)
		volumes = {
			git_repo: {'bind': repoDir, 'mode': 'ro'},
		}
		volumes.update(extra_volumes)
		log_dir = os.path.abspath(log_dir)
		image = self.IMAGES.get(language, 'default')

		for i, commit in enumerate(commits):
			if yaml_files:
				yaml_file = os.paht.abspath(yaml_files[0 if i >= len(yaml_files) else i])
				volumes[os.path.dirname(yaml_file)] = {'bind': yamlDir, 'mode': 'ro'}
				cmd = command % {
					'commit': commit,
					'yaml_file': os.path.basename(yaml_file),
				}
			else:
				cmd = command % {
					'commit': commit,
				}

			needSleep = False
			for j in xrange(repeat_count):
				if repeat_count > 1:
					task_name = '%s_%s_%d' % (gitInfo['project'], commit[:10], j)
				else:
					task_name = '%s_%s' % (gitInfo['project'], commit[:10])

				needSleep = True
				self._run(task_name, log_dir, mem_limit, cpu_list, cpu_sema,
					image = image, command = cmd, user = 'travis',
					tmpfs = {workDir: 'exec,uid=2000,gid=2000'},
					working_dir = workDir, volumes = volumes,
					environment = environment)
			needSleep and time.sleep(30)

		for _ in xrange(cpu_count):
			cpu_sema.acquire()
