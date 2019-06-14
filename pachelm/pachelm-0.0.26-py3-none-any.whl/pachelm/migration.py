import json
import glob
from pprint import pprint
from deepdiff import DeepDiff
import python_pachyderm.client.pps.pps_pb2 as proto
from google.protobuf.json_format import ParseDict, MessageToDict
from pachelm.utils import convert, force_number, map_nested_dicts_modify, map_nested_dicts_modify_key

IGNORED_FROM_DIFF_FIELDS = [ 'created_at', 'salt', 'spec_commit', 'state', 'version']

# fields = [field.name for field in proto.PipelineInfo.DESCRIPTOR.fields]
# deprecated: scale_down_threshold
# no usecases/docs: hashtree_spec
FIELDS = [
    "transform", "parallelism_spec", "egress", "update",
    "output_branch", "resource_requests",
    "resource_limits", "input", "description", "cache_size", "enable_stats",
    "reprocess", "batch", "max_queue_size", "service", "chunk_spec",
    "datum_timeout", "job_timeout", "salt", "standby", "datum_tries",
    "scheduling_spec", "pod_spec", "pod_patch"
]

class PachydermMigration(object):

    def __init__(self, ctx):
        self.pfs = ctx.pfs
        self.pps = ctx.pps
        self.ctx = ctx

    def up(self):
        """ Setup """
        return

    def down(self):
        """ Teardown """
        return

    def invoke_up(self):
        """ Tearup Wrapper Method"""
        self.up()

    def invoke_down(self):
        """ Teardown Wrapper Method """
        self.down()

    def create_repo(self, repo_name, *args, **kwargs):
        if not self.is_resource_already_exist(repo_name):
            self.pfs.create_repo(repo_name, *args, **kwargs)
    
    def delete_repo(self, repo_name, *args, **kwargs):
        if self.is_resource_already_exist(repo_name):
            self.pfs.delete_repo(repo_name, *args, **kwargs)

    def create_pipeline_from_file(self, filePath):
        """ Create Pipeline from pachyderm pipeline json config file. """
        pipelineConfig = self.__load_json_config(filePath)
        parsed = ParseDict(pipelineConfig, proto.PipelineInfo(), ignore_unknown_fields=True)
        pipelineName = parsed.pipeline.name
        updated = self._has_pipeline_config_changed(pipelineName)
        if updated: 
            print(self._diff(pipelineName))
            print('%s Updating...' % (pipelineName))

        if (not self.is_resource_already_exist(pipelineName)) or updated:
            configDict = MessageToDict(parsed, including_default_value_fields=False)
            onlyPythonPachydermKeysConfigDict = { convert(oldKey): value for oldKey, value in configDict.items() if convert(oldKey) in FIELDS }
            convertedDict = map_nested_dicts_modify_key(onlyPythonPachydermKeysConfigDict, convert)
            map_nested_dicts_modify(convertedDict, force_number)
            self.pps.create_pipeline(pipelineName, **convertedDict, update=updated)

    def delete_pipeline_from_file(self, filePath):
        obj = self.__load_json_config(filePath)
        pipelineName = obj.get('pipeline').get('name')
        if self.is_resource_already_exist(pipelineName):
            self.pps.delete_pipeline(pipelineName)

    def get_pipeline(self, pipeline):
        try:
            inspected = self.pps.inspect_pipeline(pipeline)
            messageDict = MessageToDict(inspected, including_default_value_fields=False)
            pipelineInfo = { convert(k) : v for k, v in messageDict.items() if convert(k) not in IGNORED_FROM_DIFF_FIELDS }
            map_nested_dicts_modify(pipelineInfo, force_number)
            return pipelineInfo
        except Exception:
            return None

    def get_repo(self, repo):
        try:
            inspected = self.pfs.inspect_repo(repo)
            repoInfo = MessageToDict(inspected, including_default_value_fields=False)
            map_nested_dicts_modify(repoInfo, force_number)
            return repoInfo
        except Exception:
            return None

    def __load_json_config(self, filePath):
        with open(filePath, 'r') as f:
            loaded = json.loads(f.read())
        return { k: v for k, v in loaded.items() if k not in IGNORED_FROM_DIFF_FIELDS }

    def _diff(self, pipeline, jsonConfigPath=None):
        pipelineInfo = self.get_pipeline(pipeline)
        configPath = jsonConfigPath or self.ctx.find_pipeline_config(pipeline).get('path')
        loaded = self.__load_json_config(configPath)
        return DeepDiff(pipelineInfo, loaded, verbose_level=2)
    
    def _has_pipeline_config_changed(self, *args):
        return self._diff(*args) != {}
    
    def is_resource_already_exist(self, resource):
        if self.get_pipeline(resource) or self.get_repo(resource):
            print('resource %s already exists...' % (resource))
            return True
        return False

    # don't forget to delete path not being used.
    def put_file(self, repo, branch, path_unused, globPattern):
        files = glob.glob(self.ctx.dataDir + '/'+ globPattern, recursive=True)
        print(files)
        with self.pfs.commit(repo, branch) as c:
            for filePath in files:
                path = (filePath.replace(self.ctx.dataDir, ''))
                print(path, filePath)
                self._put_file(c, repo, branch, path, filePath)

    def _put_file(self, c, repo, branch, path, filePath):
        print("%s --> %s" % (filePath, path))
        f = open(filePath, 'rb')
        self.pfs.put_file_bytes(c, path, f.read())
        f.close()
            

# def put_file_bytes(	self, commit, path, value, delimiter=0, target_file_datums=0, target_file_bytes=0)

# verify is pipeline/repo already exists. [complete]
# inspect status of existing deployment.
# for pipeline check integrity of pipeline config.json is there any change on those field. [complete]

# delete or updating prompt with some info about diff.

# migration till specified migration, all migrations before these was migrate.
# rollback to specified migration all migrations after that was rollback
# error getting pipelineInfo: could not read existing PipelineInfo from PFS: commit 0186370b401a477394e4adc816bb64cf not found in repo __spec__
