"""
BuildProject
============

The BuildProject is an object which inherits of the Troposphere object properties
but uses wrapper methods in order to populate / assign values to these. Just because,
I am Lazy.

TriggerGroup
============

TriggerGroup is an object that builds the list of WebhookFilter for Codebuild Triggers Webhook
It performs all sorts of validation to ensure we are doing things right, and allows a more
human friendly way to pass arguments in order to build your filter group.

"""

import re
#from ast import literal_eval
from troposphere.codebuild import (
    Environment,
    Source,
    Project,
    Artifacts,
    EnvironmentVariable,
    ProjectTriggers,
    WebhookFilter
)
from troposphere.iam import (
    Role,
    Policy
)
from ozone.resources.iam.roles import role_trust_policy
from ozone.filters.arns import (
    s3_bucket as filter_s3bucket,
    iam_role as filter_iamrole
)
from ozone.resources.iam.policies import (
    AWS_LAMBDA_BASIC_EXEC
)
from ozone.resolvers.codebuild.runtime import generate_runtime_mapping_and_parameters


AT_LEAST = lambda x, y: bool(set(x) <= set(y))
ISSET = lambda x, y: x in y and y[x]
KEYISSET = lambda x, y: bool(x in y.keys() and y[x])

IS_PR = 1024
IS_PUSH = 1025


CERTIFICATE_ARN = r'(^(arn:aws:s3:::[a-z0-9-.]+)\/([a-zA-Z0-9\/]+)(.pem|.zip|.crt)$)'
CERTIFICATE_PATTERN = re.compile(CERTIFICATE_ARN)

PR_PATTERNS = [
    'PULL_REQUEST_CREATED',
    'PULL_REQUEST_UPDATED',
    'PULL_REQUEST_REOPENED'
]
WEBHOOK_PATTERNS = ['PUSH'] + PR_PATTERNS
PR_TYPES = [
    'HEAD_REF',
    'BASE_REF',
    'BASE_REF',
    'ACTOR_ACCOUNT_ID'
]
PUSH_TYPES = ['ACTOR_ACCOUNT_ID', 'HEAD_REF', 'FILE_PATH']
WEBHOOK_TYPES = [
    'EVENT',
    'ACTOR_ACCOUNT_ID',
    'HEAD_REF',
    'BASE_REF',
    'FILE_PATH'
]
VALID_FOR_PUSH = ['FILE_PATH', 'ACTOR_ACCOUNT_ID', 'HEAD_REF']


def role_build(bucket_name):
    """
    returns:
        iam.Role
    """
    bucket_name = filter_s3bucket(bucket_name)
    role = Role(
        "CodeBuildRole",
        Path='/cicd/codebuild/',
        AssumeRolePolicyDocument=role_trust_policy('codebuild'),
        ManagedPolicyArns=[
            AWS_LAMBDA_BASIC_EXEC
        ],
        Policies=[
            Policy(
                PolicyName="S3Access",
                PolicyDocument={
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            'Effect': 'Allow',
                            'Resource': [
                                bucket_name
                            ],
                            'Action': [
                                's3:PutObject',
                                's3:PutObjectVersion',
                                's3:GetObject',
                                's3:GetObjectVersion'
                            ]
                        }
                    ]
                }
            )
        ]
    )
    return role


class TriggerGroup():
    """
    Webhook Filter Group
    """

    @property
    def group(self):
        """
        Returns self.__group
        """
        return self.__group

    @group.setter
    def group(self, group):
        """
        Initializes self.__group or append items to it
        """
        if group is None:
            self.__group = []
        else:
            self.__group = group


    def get_evals(self, **kwargs):
        """
        Dictionary with multiple eval functions which allow to not have
        10kB long lines for an if and reuse everywhere I need it

        :returns: evals, dict()
        """
        evals = {
            'base_forpr': eval(
                ' KEYISSET("OnUpdate", kwargs) or '
                ' KEYISSET("OnCreate", kwargs) or '
                ' KEYISSET("OnReopen", kwargs) '
            ),
            'right_forpr': eval(
                '('
                ' KEYISSET("OnUpdate", kwargs) or '
                ' KEYISSET("OnCreate", kwargs) or '
                ' KEYISSET("OnReopen", kwargs) '
                ') and '
                'KEYISSET("SourceBranch", kwargs) and '
                'KEYISSET("DestBranch", kwargs)'
            ),
            'base_forpush': eval(
                'KEYISSET("OnPush", kwargs) and not'
                '('
                ' KEYISSET("OnUpdate", kwargs) or '
                ' KEYISSET("OnCreate", kwargs) or '
                ' KEYISSET("OnReopen", kwargs)'
                ')'
            )
        }
        return evals

    def validate_args(self, **kwargs):
        """
        Validates arguments are coherent with what you are trying to achieve (PR vs PUSH detection)
        I have taken the opiniated mindset that if you are expecting PR activities,
        you can't use PUSH because PUSH doesn't support a BASE_REF therefore makes the payload
        of the webhook in case of a PR unexploitable.
        Also filters out the fields that the API and Console would yell about if you tried to use
        them (ie. use FILE_PATH for PR_*)

        :returns: globally defined value to identify whether we are creating a webhook filter
        for a PR or a PUSH
        """
        evals = self.get_evals(**kwargs)
        args = list(kwargs.keys())
        if evals['base_forpr'] and evals['right_forpr']:
            if KEYISSET('FilePath', kwargs):
                raise AttributeError('A PR webhook does not support FILE_PATH')
            if KEYISSET('OnPush', kwargs):
                raise AttributeError(
                    'PUSH only supports HEAD_REF branch.'
                    ' The Payload from GIT will not contain the branch to compare to ..'
                )
            return IS_PR
        elif evals['base_forpush']: # and evals['right_forpush']:
            if KEYISSET('DestBranch', kwargs):
                raise AttributeError('DestBranch is not supported for PUSH')
            return IS_PUSH
        return None

    def set_push(self, **kwargs):
        """
        Defines a webhook filter that makes sense for push
        :returns: filters, list()
        """
        filters = []
        if KEYISSET('SourceBranch', kwargs):
            filters.append(
                WebhookFilter(
                    Type="HEAD_REF",
                    Pattern=f'^ref/heads/{kwargs["SourceBranch"]}'
                )
            )
        if KEYISSET('Tags', kwargs):
            filters.append(
                WebhookFilter(
                    Type="HEAD_REF",
                    Pattern=f'^ref/tags/{kwargs["Tags"]}'
                )
            )
        if KEYISSET('NotSourceBranch', kwargs):
            filters.append(
                WebhookFilter(
                    Type='HEAD_REF',
                    Pattern=f'^ref/heads/{kwargs["NotSourceBranch"]}',
                    ExcludeMatchedPattern=True
                )
            )
        if KEYISSET('FilePath', kwargs):
            filters.append(
                WebhookFilter(
                    Type='FILE_PATH',
                    Pattern=f'{kwargs["FilePath"]}',
                )
            )
        if KEYISSET('UserName', kwargs):
            filters.append(
                WebhookFilter(
                    Type='ACTOR_ACCOUNT_ID',
                    Pattern=f'^ref/heads/{kwargs["UserName"]}',
                )
            )
        filters.append(
            WebhookFilter(
                Type='EVENT',
                Pattern="PUSH"
            )
        )
        return filters

    def set_pr(self, source_branch, dest_branch, kwargs):
        """
        .. returns: filters, list()
        """
        filters = []
        source_branch = WebhookFilter(
            Type='HEAD_REF',
            Pattern=f'^ref/heads/{source_branch}'
        )
        filters.append(source_branch)
        dest_branch = WebhookFilter(
            Type='BASE_REF',
            Pattern=f'^ref/heads/{dest_branch}'
        )
        filters.append(dest_branch)
        if KEYISSET('NotSourceBranch', kwargs):
            not_dest_branch = WebhookFilter(
                Type="HEAD_REF",
                Pattern=f"^ref/heads/{kwargs['NotSourceBranch']}",
                ExcludeMatchedPattern=True
            )
            filters.append(not_dest_branch)
        if KEYISSET('NotSourceBranch', kwargs):
            not_source_branch = WebhookFilter(
                Type="BASE_REF",
                Pattern=f"^ref/heads/{kwargs['NotDestBranch']}",
                ExcludeMatchedPattern=True
            )
            filters.append(not_source_branch)


        event_pattern = []
        if KEYISSET('OnCreate', kwargs):
            event_pattern.append('PULL_REQUEST_CREATED')
        if KEYISSET('OnUpdate', kwargs):
            event_pattern.append('PULL_REQUEST_UPDATED')
        event = WebhookFilter(
            Type='EVENT',
            Pattern=','.join(event_pattern)
        )
        filters.append(event)
        return filters


    def __init__(self, **kwargs):
        """
        Sets a trigger for PR between two branches
        """
        self.group = None
        args = list(kwargs.keys())
        filter_is = self.validate_args(**kwargs)
        if filter_is == IS_PR:
            self.group = self.set_pr(
                kwargs['SourceBranch'], kwargs['DestBranch'],
                kwargs
            )
        elif filter_is == IS_PUSH:
            self.group = self.set_push(**kwargs)
        else:
            raise ValueError('The parameters for the webhook are not valid')


class BuildProject(Project):
    """
    Class to create a CodeBuild project
    """

    _source_must_haves = ['Location']
    _source_types = ["S3", "CODEPIPELINE", "GITHUB"]

    _compute_types = {
        'small': 'BUILD_GENERAL1_SMALL',
        'medium': 'BUILD_GENERAL1_MEDIUM',
        'large': 'BUILD_GENERAL1_LARGE'
    }

    def use_codecommit(self, args):
        """
        Sets source for CodeCommit
        """
        assert all(k in args.keys() for k in self._source_must_haves)
        source = Source(
            Type="CODECOMMIT",
            Location=args['Location']
        )
        return source

    def use_s3_source(self, args):
        """
        Defines the source for S3
        """
        assert all(k in args.keys() for k in self._source_must_haves)
        source = Source(
            Type="S3",
            NamespaceType="S3",
            Location=args['Location']
        )
        return source

    def use_codepipeline_source(self, args):
        """
        Defines the source for CodePipeline
        """
        assert all(k in args.keys() for k in self._source_must_haves)
        source = Source(
            Type="CODEPIPELINE",
            NamespaceType="NONE",
            Packaging="ZIP"
        )
        return source

    def use_github_source(self, args):
        """
        Defines the source for GitHub and GitHub Entreprise
        """
        assert all(k in args.keys() for k in self._source_must_haves)
        github_pattern = re.compile(r'^(https://github.com\/)')
        assert github_pattern.match(args['Location'])
        source = Source(
            Type="GITHUB",
            Location=args['Location']
        )
        return source


    def define_source(self, kwargs):
        """
        Set source
        """

        if 'Source' not in kwargs.keys():
            raise KeyError('Source must be present')
        source_info = kwargs['Source']
        source = None
        for source_type in self._source_types:
            if source_info['Type'] == source_type:
                try:
                    func = getattr(self, f'use_{source_type.lower()}_source')
                    source = func(kwargs['Source'])
                except AttributeError as error:
                    raise AttributeError(f'Source Type {source_info["Type"]} is not supported')

        if 'BuildSpec' in source_info.keys():
            setattr(source, 'BuildSpec', source_info['BuildSpec'])
        return source


    def define_artifacts(self, kwargs):
        artifact = Artifacts(
            Type="NO_ARTIFACTS"
        )
        if 'UseCodePipeline' in kwargs.keys():
            artifact = Artifacts(
                Type="CODEPIPELINE",
                Packaging="ZIP"
            )
        return artifact


    def define_env(self, kwargs):
        if 'BuildEnvVars' in kwargs.keys() and kwargs['BuildEnvVars']:
            for var in kwarg['BuildEnvVars']:
                if not isinstance(var, EnvironmentVariable):
                    raise TypeError('Environment variables must be of type', EnvironmentVariable)
            env_vars = kwargs['BuildEnvVars']
        else:
            env_vars = []
        if kwargs['OS'] == 'WINDOWS':
            env_type = 'WINDOWS_CONTAINER'
        else:
            env_type = 'LINUX_CONTAINER'
        if 'Image' in kwargs.keys():
            image = kwargs['Image']
        else:
            image = self.find_image(
                kwargs['OS'], kwargs['RuntimeLanguage'], kwargs['RuntimeVersion']
            )

        env = Environment(
            ComputeType=self._compute_types[kwargs['ComputeType']],
            Type=env_type,
            EnvironmentVariables=env_vars,
            Image=image
        )
        if 'Certificate' in kwargs.keys() and CERTIFICATE_PATTERN.match(kwarg['Certificate']):
            setattr(env, 'Certificate', kwargs['Certificate'])
        return env


    def find_image(self, os, language, version):
        """
        Args:
          os: Operating System of the base image
          language: Codebuild name of the language to use
          version: Version of the runtime to use
        Returns:
          codebuild image matching os, language and latest version
        """
        return "aws/codebuild/python:3.6.5"


    def define_triggers(self, kwargs):
        """
        Defines Codebuild triggers
        """
        tropo_filters = []
        webhook_filters = []
        filters = kwargs['FilterGroups']
        if not isinstance(filters, list):
            raise TypeError('filters must be of type', list)
        for filter_ in filters:
            if (
                    isinstance(filter_, list) and
                    len(filter_) >= 2 and
                    isinstance(filter_[0], WebhookFilter)
            ):
                tropo_filters.append(filter_)
            elif isinstance(filter_, list) and not isinstance(filter_[0], WebhookFilter):
                for hookfilter in filter_:
                    if not AT_LEAST(['Type', 'Pattern'], hookfilter.keys()):
                        raise AttributeError('WebHook must have at least Type and Pattern defined')
                    if hookfilter['Type'] not in WEBHOOK_TYPES:
                        raise ValueError('Type must be one of the', WEBHOOK_TYPES)
                    if hookfilter['Type'] == 'EVENT' and not (
                            AT_LEAST(hookfilter['Pattern'].split(','), WEBHOOK_PATTERNS)):
                        raise ValueError('Type EVENT only accepts one of', WEBHOOK_PATTERNS)
                    hook = WebhookFilter(
                        Type=hookfilter['Type'],
                        Pattern=hookfilter['Pattern']
                    )
                    webhook_filters.append(hook)
                tropo_filters.append(webhook_filters)
        trigger = ProjectTriggers(Webhook=True, FilterGroups=tropo_filters)
        return trigger



    def __init__(self, title, role, **kwargs):
        """
        Initializes a new Project
        """
        super().__init__(
            title,
            BadgeEnabled=True,
            Source=self.define_source(kwargs),
            Artifacts=self.define_artifacts(kwargs),
            Environment=self.define_env(kwargs),
            ServiceRole=filter_iamrole(role),
        )
        if 'UseWebhooks' in kwargs.keys() and 'FilterGroups' in kwargs.keys():
            setattr(self, 'Triggers', self.define_triggers(kwargs))
        defined = list(self.properties)
        definable = list(self.props.keys())
        to_define = list(set(definable)^set(defined))
        for key in to_define:
            if KEYISSET(key, kwargs):
                setattr(self, key, kwargs[key])
