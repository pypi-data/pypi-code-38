"""
Set of functions to use to create a CodePipeline pipeline using Troposphere
"""
import re
import sys
from troposphere import (
    ImportValue,
    Select,
    GetAtt,
    Ref,
    Sub
)
from troposphere.codepipeline import (
    Pipeline,
    Stages,
    Actions,
    ActionTypeId,
    InputArtifacts,
    OutputArtifacts,
    ArtifactStore,
    DisableInboundStageTransitions
)
from ozone.filters.arns import (
    iam_role as filter_iamrole,
    s3_bucket as filter_s3bucket,
    lambda_function as filter_lambda
)
from ozone.filters import get_resource_type
from troposphere.codebuild import Project


CFN_TEMPLATE_ARTIFACT_PATH_PATTERN = r'(([\w]+)::([a-z\/]+).(json|yaml|yml))'
NON_ALPHANUM = r'([^\w])'


class PipelineActions(Actions, object):
    """
    """
    _action = None
    _config = {}

    @property
    def config(self):
        return self.__config

    @config.setter
    def config(self, config):
        self.__config = config

    @property
    def action_type(self):
        return self.__action_type

    @action_type.setter
    def action_type(self, action_type):
        self.__action_type = action_type

    @property
    def outputs(self):
        return self.__outputs

    @outputs.setter
    def outputs(self, name):
        self.__outputs = [
            OutputArtifacts(Name=name)
        ]

    def filter_args(self, kwargs, args, valid_types):
        for arg in kwargs.keys():
            if arg not in args:
                raise KeyError(f'Source action requires {arg}')
            if not isinstance(kwargs[arg], valid_types):
                raise TypeError(f'{key} has to be of type', valid_types)


    def output_as_input(self, inputs):
        """
        Takes a list of ouputs OutputArtifacts and transforms it into a list of
        inputs InputArtifacts
        """
        outputs = []
        self.check_output_artifacts(inputs)
        for input_object in inputs:
            outputs.append(InputArtifacts(Name=input_object.Name))
        return outputs


    def check_input_artifacts(self, input_artifacts):
        """
        Args:
            input_artifacts: list of InputArtifacts
        Returns:
            bool if all okay
        Raises:
            TypeError if the list of artifacts is not right
        """
        if not isinstance(input_artifacts, list):
            raise TypeError('input_artifacts must be of type', list)
        for artifact in input_artifacts:
            if not isinstance(artifact, InputArtifacts):
                raise TypeError(f'Input artifact {artifact} must be of type', InputArtifacts)
        return True


    def check_output_artifacts(self, output_artifacts):
        """
        Args:
            output_artifacts: list of InputArtifacts
        Returns:
            bool if all okay
        Raises:
            TypeError if the list of artifacts is not right
        """
        if not isinstance(output_artifacts, list):
            raise TypeError('output_artifacts must be of type', list)
        for artifact in output_artifacts:
            if not isinstance(artifact, OutputArtifacts):
                raise TypeError(f'Output artifact {artifact} must be of type', OutputArtifacts)



class SourceAction(PipelineActions, object):
    """
    Class to create a "Source" Pipeline action
    """
    _actions_args_types = (Ref, Sub, GetAtt, str)
    _supported_providers = ['GitHub', 'CodeCommit']
    _github_args = ['Repo', 'Branch', 'Owner', 'OAuthToken']
    _github_action_type = ActionTypeId(
        Category="Source",
        Owner="ThirdParty",
        Provider="GitHub",
        Version="1"
    )
    _codecommit_args = ['RepositoryName', 'BranchName']
    _codecomit_action_type = ActionTypeId(
        Category="Source",
        Owner="AWS",
        Provider="CodeCommit",
        Version="1"
    )

    __config = {}
    __action_type = None
    __outputs = None

    @property
    def outputs(self):
        return self.__outputs

    @outputs.setter
    def outputs(self, name):
        self.__outputs = [
            OutputArtifacts(Name=name)
        ]


    def __init__(self, name, provider, config):
        self.config = config
        self.set_source_action(provider)
        self.outputs = re.sub(NON_ALPHANUM, '', name)
        super().__init__(
            Name=name,
            ActionTypeId=self.action_type,
            Configuration=self.config,
            OutputArtifacts=self.outputs,
            RunOrder="1"
        )

    def set_source_action(self, provider):
        provider_name = provider.lower()
        args = getattr(self, f'_{provider_name}_args')
        self.action_type = getattr(self, f'_{provider_name}_action_type')
        self.filter_args(self.config, args, self._actions_args_types)
        if provider_name == 'github':
            self.config['PollForSourceChanges'] = False



class BuildAction(PipelineActions, object):
    """
    """
    __config = {}
    _codebuild_action_type = ActionTypeId(
        Category="Build",
        Owner="AWS",
        Version="1",
        Provider="CodeBuild"
    )

    @property
    def build_name(self):
        return self.__build_name

    @build_name.setter
    def build_name(self, name):
        build_resource = get_resource_type(Project)
        if isinstance(name, (Sub, Ref, Select, ImportValue)):
            self.__build_name =  name
        else:
            self.__build_name = ImportValue(f'{name}-{build_resource}-Name')

    @property
    def project_name(self):
        return self.__build_name

    @project_name.setter
    def project_name(self, name):
        self.__project_name = name


    def __init__(self, name, inputs, project_name, primary_source=None):
        self.check_output_artifacts(inputs)
        self.inputs = self.output_as_input(inputs)
        self.project_name = project_name
        self.build_name = project_name
        if len(inputs) > 5:
            raise ValueError('CodeBuild does not support more than 5 input artifacts')
        self.config = {}
        self.config['ProjectName'] = self.project_name
        if primary_source is not None:
            self.config['PrimarySource'] = primary_source
        elif len(inputs) > 1:
            self.config['PrimarySource'] = self.inputs[0].Name
        self.action_type = self._codebuild_action_type
        self.outputs = re.sub(NON_ALPHANUM, '', project_name)

        super().__init__(
            Name=self.build_name,
            InputArtifacts=self.inputs,
            ActionTypeId=self.action_type,
            Configuration=self.config,
            OutputArtifacts=self.outputs,
            RunOrder="1"
        )


class DeployAction(PipelineActions, object):
    """
    """
    _max_inputs_cloudformation = 10
    _valid_providers = ['CloudFormation'] # unsuported yet, 'CodeDeploy', 'S3']

    def __init__(self, name, inputs, provider, **kwargs):
        self.check_output_artifacts(inputs)
        self.inputs = self.output_as_input(inputs)
        if provider not in self._valid_providers:
            raise ValueError(f'provider {provider} is not a supported provider', self._valid_providers)
        action_provider = provider.lower()
        try:
            klass = getattr(self, action_provider)
            deployer = klass(**kwargs)
        except AttributeError:
            raise AttributeError(f'Error importing {action_provider}')
        if 'RunOrder' in kwargs.keys() and isinstance(kwargs['RunOrder'], str):
            setattr(deployer.action, 'RunOrder', kwargs['RunOrder'])
        if 'Name' in kwargs.keys() and isinstance(kwargs['Name'], str):
            setattr(deployer.action, 'Name', kwargs['Name'])
        super().__init__(
            Name=name,
            InputArtifacts=self.inputs,
            ActionTypeId=deployer.action_type,
            Configuration=deployer.config,
            RunOrder="1"
        )


    class cloudformation():
        """
        For Cloudformation deployment
        """
        required_keys = ['RoleArn', 'StackName', 'TemplatePath']

        action_type = ActionTypeId(
            Category="Deploy",
            Owner="AWS",
            Version="1",
            Provider="CloudFormation"
        )
        def __init__(self, **kwargs):
            assert all(key in kwargs.keys() for key in self.required_keys)
            pattern = re.compile(CFN_TEMPLATE_ARTIFACT_PATH_PATTERN)
            template_path = kwargs['TemplatePath']
            if not (kwargs['TemplatePath'].startswith('https://s3.amazonaws.com') or
                    pattern.match(kwargs['TemplatePath'])):
                raise ValueError(
                    'TemplatePath must either be a full path to S3'
                    f'or use the pattern {CFN_TEMPLATE_ARTIFACT_PATH_PATTERN}'
                )
            self.config = {
                'StackName': kwargs['StackName'],
                'ActionMode': 'CREATE_UPDATE',
                'RoleArn': filter_iamrole(kwargs['RoleArn']),
                'TemplatePath': kwargs['TemplatePath']
            }
            if 'ActionMode' in kwargs.keys():
                self.config['ActionMode'] = kwargs['ActionMode']





class InvokeAction(PipelineActions, object):
    """
    """
    def __init__(self, name, inputs, function_name, **kwargs):
        self.check_output_artifacts(inputs)
        self.inputs = self.output_as_input(inputs)
        self.config = {
            'FunctionName': filter_lambda(function_name)
        }
        if 'UserParameters' in kwargs.keys():
            self.config['UserParameters'] = kwargs['UserParameters']
        self.outputs = re.sub(NON_ALPHANUM, '', name)
        super().__init__(
            Name="GenerateCfnTemplate",
            InputArtifacts=self.inputs,
            OutputArtifacts=self.outputs,
            ActionTypeId=ActionTypeId(
                Category="Invoke",
                Owner="AWS",
                Version="1",
                Provider="Lambda"
            ),
            Configuration=self.config,
            RunOrder="1"
        )


class CodePipeline(Pipeline, object):
    """
    """

    _stages_list = []

    @property
    def stages_list(self):
        return self._stages_list

    @stages_list.setter
    def stages_list(self, stages):
        for stage in stages:
            self._stages_list.append(Stages(Name=stage[0], Actions=stage[1]))


    def __init__(self, title, role, bucket, stages, name=None, **kwargs):
        """
        Args:
            title: Name of the object in the template
        """
        self.stages_list = stages

        super().__init__(
            title,
            Stages=self.stages_list,
            RestartExecutionOnUpdate=True,
            RoleArn=filter_iamrole(role),
            ArtifactStore=ArtifactStore(
                Type="S3",
                Location=bucket
            )
        )

