"""
Static Pipeline representation to create a CodePipeline dedicated to building
Lambda Layers
"""

from troposphere import (
    Parameter,
    Template,
    GetAtt,
    Ref,
    Sub
)

from ozone.handlers.lambda_tools import check_params_exist
from ozone.resources.iam.roles.pipeline_role import pipelinerole_build
from ozone.resources.devtools.pipeline import (
    SourceAction,
    BuildAction,
    DeployAction,
    InvokeAction,
    CodePipeline
)
from ozone.outputs import object_outputs


def template(**kwargs):
    """
    """

    template_required_params = [
        'BucketName',
        'Source', 'LayerBuildProjects', 'LayersMergeProject',
        'LayerName', 'GeneratorFunctionName', 'CloudformationRoleArn'
    ]
    check_params_exist(template_required_params, kwargs)
    template = Template()
    token =  template.add_parameter(Parameter(
        'GitHubOAuthToken',
        Type="String",
        NoEcho=True
    ))
    role = pipelinerole_build(
        UseCodeCommit=True,
        UseCodeBuild=True,
        UseLambda=True,
        UseCloudformation=True,
        Bucket=kwargs['BucketName']
    )
    if kwargs['Source']['Provider'].lower() == 'github':
        kwargs['Source']['Config']['OAuthToken'] = Ref(token)
    source = SourceAction(
        name='SourceCode',
        provider=kwargs['Source']['Provider'],
        config=kwargs['Source']['Config']
    )
    build_actions = []
    builds_projects = kwargs['LayerBuildProjects']
    for project in builds_projects:
        build_actions.append(BuildAction(
            project,
            source.outputs,
            project
        ))
    build_outputs = []
    for action in build_actions:
        build_outputs += action.outputs

    merge_action = BuildAction(
        'MergeAction',
        build_outputs,
        kwargs['LayersMergeProject']
    )
    invoke = InvokeAction(
        'GenerateTemplateForCfn',
        merge_action.outputs,
        function_name=kwargs['GeneratorFunctionName']
    )

    input_name = invoke.outputs[0].Name
    deploy = DeployAction(
        'DeployToCfn',
        invoke.outputs,
        'CloudFormation',
        StackName=f'layer-{kwargs["LayerName"]}',
        RoleArn=kwargs['CloudformationRoleArn'],
        TemplatePath=f'{input_name}::tmp/template.json'
    )
    stages = [
        ('Source', [source]),
        ('BuildLayers', build_actions),
        ('MergeLayers', [merge_action]),
        ('GenerateCfnTemplate', [invoke]),
        ('DeployWithCfn', [deploy]),
    ]

    pipeline = CodePipeline(
        'Pipeline',
        GetAtt(role, 'Arn'),
        kwargs['BucketName'],
        stages
    )
    template.add_resource(role)
    template.add_resource(pipeline)
    template.add_output(object_outputs(pipeline, True))
    return template
