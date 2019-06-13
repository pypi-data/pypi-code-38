#!/usr/bin/env python

import sys
import os
import glob
import json
import ConfigParser
import time
from datetime import datetime
import base64
import hashlib
import PyRSS2Gen

def getKey(item):
  return item.source.name

class MonitorFeed(object):

  def __init__(self, instance_name, hosting_name,
      public_url, private_url, feed_url):
    self.rss_item_list = []
    self.report_date = datetime.utcnow()
    self.instance_name = instance_name
    self.hosting_name = hosting_name
    self.public_url = public_url
    self.private_url = private_url
    self.feed_url = feed_url

  def appendItem(self, item_dict, has_string=""):
    event_date = item_dict['result']['change-date']
    report_date = item_dict['result']['date']
    description = item_dict['result'].get('message', '')
    rss_item = PyRSS2Gen.RSSItem(
      categories = [item_dict['status']],
      source = PyRSS2Gen.Source(item_dict['title'], self.public_url),
      title = '[%s] %s' % (item_dict['status'], item_dict['title']),
      description = "\n%s" % (description,),
      link = self.private_url,
      pubDate = event_date,
      guid = PyRSS2Gen.Guid(base64.b64encode("%s, %s, %s, %s" % (self.hosting_name,
                              item_dict['title'], has_string, event_date)),
                            isPermaLink=False)
    )
    self.rss_item_list.append(rss_item)

  def generateRSS(self, output_file):
    ### Build the rss feed
    # try to keep the list in the same order
    sorted(self.rss_item_list, key=getKey)
    rss_feed = PyRSS2Gen.RSS2 (
      title = self.instance_name,
      link = self.feed_url,
      description = self.hosting_name,
      lastBuildDate = self.report_date,
      items = self.rss_item_list
    )

    with open(output_file, 'w') as frss:
      frss.write(rss_feed.to_xml())

def generateStatisticsData(stat_file_path, content):
  # csv document for success/error statictics
  if not os.path.exists(stat_file_path) or os.stat(stat_file_path).st_size == 0:
    with open(stat_file_path, 'w') as fstat:
      data_dict = {
        "date": time.time(),
        "data": ["Date, Success, Error, Warning"]
      }
      fstat.write(json.dumps(data_dict))

  current_state = ''
  if content.has_key('state'):
    current_state = '%s, %s, %s, %s' % (
      content['date'],
      content['state']['success'],
      content['state']['error'],
      '')

  # append to file
  if current_state:
    with open (stat_file_path, mode="r+") as fstat:
      fstat.seek(0,2)
      position = fstat.tell() -2
      fstat.seek(position)
      fstat.write('%s}' % ',"{}"]'.format(current_state))

def writeDocumentList(folder_path):
  # Save document list in a file called _document_list
  public_document_list = [os.path.splitext(file)[0]
                for file in os.listdir(folder_path) if file.endswith('.json')]

  with open(os.path.join(folder_path, '_document_list'), 'w') as lfile:
    lfile.write('\n'.join(public_document_list))

def generateMonitoringData(config, public_folder, private_folder, public_url,
    private_url, feed_url):
  feed_output = os.path.join(public_folder, 'feed')
  # search for all status files
  file_list = filter(
    os.path.isfile,
    glob.glob("%s/promise/*.status.json" % public_folder)
  )

  promises_status_file = os.path.join(private_folder, '_promise_status')
  previous_state_dict = {}
  new_state_dict = {}
  error = success = 0
  monitor_feed = MonitorFeed(
    config.get('monitor', 'title'),
    config.get('monitor', 'root-title'),
    public_url,
    private_url,
    feed_url)

  if os.path.exists(promises_status_file):
    with open(promises_status_file) as f:
      try:
        previous_state_dict = json.loads(f.read())
      except ValueError:
        pass

  for file in file_list:
    try:
      with open(file, 'r') as temp_file:
        tmp_json = json.loads(temp_file.read())

      if tmp_json['result']['failed']:
        promise_status = "ERROR"
        error += 1
      else:
        promise_status = "OK"
        success += 1
      tmp_json['result']['change-date'] = tmp_json['result']['date']
      if previous_state_dict.has_key(tmp_json['name']):
        status, change_date, _ = previous_state_dict[tmp_json['name']]
        if promise_status == status:
          tmp_json['result']['change-date'] = change_date

      tmp_json['status'] = promise_status
      message_hash = hashlib.md5(tmp_json['result'].get('message', '')).hexdigest()
      new_state_dict[tmp_json['name']] = [
        promise_status,
        tmp_json['result']['change-date'],
        message_hash
      ]
      monitor_feed.appendItem(tmp_json, message_hash)
      savePromiseHistory(
        tmp_json['title'],
        tmp_json,
        previous_state_dict.get(tmp_json['name']),
        public_folder
      )
    except ValueError, e:
      # bad json file
      print "ERROR: Bad json file at: %s\n%s" % (file, str(e))
      continue

  with open(promises_status_file, "w") as f:
    json.dump(new_state_dict, f)

  monitor_feed.generateRSS(feed_output)
  return error, success

def savePromiseHistory(promise_name, state_dict, previous_state_list,
    history_folder):
  if not os.path.exists(history_folder) and os.path.isdir(history_folder):
    self.logger.warning('Bad promise history folder, history is not saved...')
    return

  history_file = os.path.join(
    history_folder,
    '%s.history.json' % promise_name
  )

  # Remove useless informations
  result = state_dict.pop('result')
  state_dict.update(result)
  state_dict.pop('path', '')
  state_dict.pop('type', '')
  if not os.path.exists(history_file) or not os.stat(history_file).st_size:
    with open(history_file, 'w') as f:
      data_dict = {
        "date": time.time(),
        "data": [state_dict]
      }
      json.dump(data_dict, f)
  else:
    if previous_state_list is not None:
      _, change_date, checksum = previous_state_list
      current_sum = hashlib.md5(state_dict.get('message', '')).hexdigest()
      if state_dict['change-date'] == change_date and \
          current_sum == checksum:
        # Only save the changes and not the same info
        return

    state_dict.pop('title', '')
    state_dict.pop('name', '')
    with open (history_file, mode="r+") as f:
      f.seek(0,2)
      f.seek(f.tell() -2)
      f.write('%s}' % ',{}]'.format(json.dumps(state_dict)))

def run(monitor_conf_file):

  config = ConfigParser.ConfigParser()
  config.read(monitor_conf_file)

  base_folder = config.get('monitor', 'private-folder')
  status_folder = config.get('monitor', 'public-folder')
  base_url = config.get('monitor', 'base-url')
  related_monitor_list = config.get("monitor", "monitor-url-list").split()
  statistic_folder = os.path.join(base_folder, 'documents')
  # need webdav to update parameters
  parameter_file = os.path.join(base_folder, 'config', '.jio_documents', 'config.json')

  public_url = "%s/share/public/" % base_url
  private_url = "%s/share/private/" % base_url
  feed_url = "%s/public/feed" % base_url
  status = 'OK'
  global_state_file = os.path.join(base_folder, 'monitor.global.json')
  public_state_file = os.path.join(status_folder, 'monitor.global.json')
  report_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+0000')

  error, success = generateMonitoringData(config, status_folder, base_folder,
                                          public_url, private_url, feed_url)
  if error:
    status = 'ERROR'

  global_state_dict = dict(
    status=status,
    state={
      'error': error,
      'success': success
    },
    type='global', # bwd compatibility
    portal_type='Software Instance',
    date=report_date,
    _links={"rss_url": {"href": feed_url},
            "public_url": {"href": public_url},
            "private_url": {"href": private_url},
            "related_monitor": []
          },
    data={'state': 'monitor_state.data',
          'process_state': 'monitor_process_resource.status',
          'process_resource': 'monitor_resource_process.data',
          'memory_resource': 'monitor_resource_memory.data',
          'io_resource': 'monitor_resource_io.data',
          'monitor_process_state': 'monitor_resource.status'},
    title=config.get('monitor', 'title'),
    specialise_title=config.get('monitor', 'root-title'),
    aggregate_reference=config.get('promises', 'computer-id'),
    ipv4=config.get('promises', 'ipv4'),
    ipv6=config.get('promises', 'ipv6'),
    software_release=config.get('promises', 'software-release'),
    software_type=config.get('promises', 'software-type'),
    partition_id=config.get('promises', 'partition-id'),
  )

  if not global_state_dict['title']:
    global_state_dict['title'] = 'Instance Monitoring'

  if related_monitor_list:
    global_state_dict['_links']['related_monitor'] = [{'href': "%s/share/public" % url}
                          for url in related_monitor_list]

  if os.path.exists(parameter_file):
    with open(parameter_file) as cfile:
      global_state_dict['parameters'] = json.loads(cfile.read())

  # Public information with the link to private folder
  public_state_dict = dict(
    status=status,
    date=report_date,
    _links={'monitor': {'href': '%s/share/private/' % base_url}},
    title=global_state_dict.get('title', ''),
    specialise_title=global_state_dict.get('specialise_title', ''),
  )
  public_state_dict['_links']['related_monitor'] = global_state_dict['_links'].get('related_monitor', [])

  with open(global_state_file, 'w') as fglobal:
    fglobal.write(json.dumps(global_state_dict))

  with open(public_state_file, 'w') as fpglobal:
    fpglobal.write(json.dumps(public_state_dict))

  # write list of files
  writeDocumentList(status_folder)
  writeDocumentList(base_folder)
  writeDocumentList(statistic_folder)

  generateStatisticsData(
    os.path.join(statistic_folder, 'monitor_state.data.json'),
    global_state_dict
  )

  return 0

def main():
  if len(sys.argv) < 2:
    print("Usage: %s <monitor_conf_path>" % sys.argv[0])
    sys.exit(2)
  sys.exit(run(sys.argv[1]))
