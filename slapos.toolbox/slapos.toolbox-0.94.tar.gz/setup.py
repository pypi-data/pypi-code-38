from setuptools import setup, find_packages
import glob
import os

version = '0.94'
name = 'slapos.toolbox'
long_description = open("README.rst").read() + "\n"

for f in sorted(glob.glob(os.path.join('slapos', 'README.*.rst'))):
  long_description += '\n' + open(f).read() + '\n'

long_description += open("CHANGES.txt").read() + "\n"

# Provide a way to install additional requirements
additional_install_requires = []
try:
  import argparse
except ImportError:
  additional_install_requires.append('argparse')

setup(name=name,
      version=version,
      description="SlapOS toolbox.",
      long_description=long_description,
      classifiers=[
          "Programming Language :: Python",
        ],
      keywords='slapos toolbox',
      license='GPLv3',
      namespace_packages=['slapos'],
      packages=find_packages(),
      include_package_data=True,
      maintainer="Nexedi",
      maintainer_email="info@nexedi.com",
      url="https://lab.nexedi.com/nexedi/slapos.toolbox",
      install_requires=[
        'Flask', # needed by servers
        'atomize', # needed by pubsub
        'feedparser', # needed by pubsub
        'apache_libcloud>=0.4.0', # needed by cloudmgr
        'lockfile', # used by equeue
        'lxml', # needed for xml parsing
        'paramiko', # needed by cloudmgr
        'psutil', # needed for playing with processes in portable way
        'setuptools', # namespaces
        'slapos.core', # as it provides library for slap
        'xml_marshaller', # needed to dump information
        'GitPython', #needed for git manipulation into slaprunner
        'croniter', # needed to know cron schedule
        'pytz', # needed to manipulate timezone
        'tzlocal', # needed to manipulate timezone
        'passlib',
        'netifaces',
        'erp5.util',
        'PyRSS2Gen',
        'dnspython',
        'requests',
        'jsonschema',
        'zc.buildout',
        'pycurl',
      ] + additional_install_requires,
      extras_require = {
        'lampconfigure':  ["mysqlclient"], #needed for MySQL Database access
        'zodbpack': ['ZODB3'], # needed to play with ZODB
        'flask_auth' : ["Flask-Auth"],
      },
      tests_require = [
        'mock',
        'cryptography',
      ],
      zip_safe=False, # proxy depends on Flask, which has issues with
                      # accessing templates
      entry_points={
        'console_scripts': [
          'agent = slapos.agent.agent:main',
          'apache-mpm-watchdog = slapos.promise.apache_mpm_watchdog:main',
          'check-computer-memory = slapos.promise.check_computer_memory:main',
          'check-web-page-http-cache-hit = slapos.promise.check_web_page_http_cache_hit:main',
          'check-feed-as-promise = slapos.checkfeedaspromise:main',
          'check-apachedex-result = slapos.promise.check_apachedex_result:main',
          'check-slow-queries-digest-result = slapos.promise.check_slow_queries_digest_result:main',
          'clouddestroy = slapos.cloudmgr.destroy:main',
          'cloudgetprivatekey = slapos.cloudmgr.getprivatekey:main',
          'cloudgetpubliciplist = slapos.cloudmgr.getpubliciplist:main',
          'cloudlist = slapos.cloudmgr.list:main',
          'cloudmgr = slapos.cloudmgr.cloudmgr:main',
          'cloudstart = slapos.cloudmgr.start:main',
          'cloudstop = slapos.cloudmgr.stop:main',
          'equeue = slapos.equeue:main',
          'generatefeed = slapos.generatefeed:main',
          'htpasswd = slapos.htpasswd:main',
          'is-local-tcp-port-opened = slapos.promise.is_local_tcp_port_opened:main',
          'is-process-older-than-dependency-set = slapos.promise.is_process_older_than_dependency_set:main',
          'killpidfromfile = slapos.systool:killpidfromfile', # BBB
          'monitor.bootstrap = slapos.monitor.monitor:main',
          'monitor.collect = slapos.monitor.collect:main',
          'monitor.statistic = slapos.monitor.build_statistic:main',
          'monitor.runpromise = slapos.monitor.runpromise:main',
          'monitor.genstatus = slapos.monitor.globalstate:main',
          'monitor.configwrite = slapos.monitor.monitor_config_write:main',
          'runResiliencyUnitTestTestNode = slapos.resiliencytest:runUnitTest',
          'runResiliencyScalabilityTestNode = slapos.resiliencytest:runResiliencyTest',
          'runApacheDex = slapos.apachedex:main',
          'lampconfigure = slapos.lamp:run [lampconfigure]',
          'onetimedownload = slapos.onetimedownload:main',
          'onetimeupload = slapos.onetimeupload:main',
          'pubsubnotifier = slapos.pubsub.notifier:main',
          'pubsubserver = slapos.pubsub:main',
          'qemu-qmp-client = slapos.qemuqmpclient:main',
          'rdiffbackup.genstatrss = slapos.resilient.rdiffBackupStat2RSS:main',
          'runner-exporter = slapos.resilient.runner_exporter:runExport',
          'runner-importer-post-notification-run = slapos.resilient.runner_importer:postNotificationRun',
          'backup-identity-script-excluding-path = slapos.resilient.identity_script_excluding_path:calculateSignature',
          'securedelete = slapos.securedelete:main',
          'slapos-kill = slapos.systool:kill',
          'slaprunnertest = slapos.runner.runnertest:main',
          'slaprunnerteststandalone = slapos.runner.runnertest:runStandaloneUnitTest',
          'zodbpack = slapos.zodbpack:run [zodbpack]',
          'networkbench = slapos.networkbench:main',
          'cachechecker = slapos.cachechecker:web_checker_utility'
        ]
      },
      test_suite='slapos.test',
    )
