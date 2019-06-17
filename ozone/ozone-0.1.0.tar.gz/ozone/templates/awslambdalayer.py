#!/usr/bin/env python
"""
Script to create a new Lambda Layer CFN template via Troposphere
"""

from datetime import datetime
from troposphere.awslambda import (
    LayerVersion, Content, LayerVersionPermission
)
from troposphere import (
    Parameter,
    Template,
    Sub,
    Ref
)
from ozone.handlers.lambda_tools import check_params_exist
from ozone.outputs import object_outputs

from datetime import datetime as dt
DATE = dt.utcnow().strftime('%Y%m%d%H%M%S')

def template(make_public=False, **kwargs):
    required_params = ['Runtimes', 'Bucket', 'Key']
    check_params_exist(required_params, kwargs)
    template = Template()
    layer_name = template.add_parameter(Parameter(
        'LayerName',
        Type="String",
        AllowedPattern="[a-zA-Z0-9-]*"
    ))
    template.set_description('Default template for Lambda Layer version')
    template.set_transform('AWS::Serverless-2016-10-31')
    version = template.add_resource(LayerVersion(
        f'LayerVersion{DATE}',
        DeletionPolicy='Retain',
        CompatibleRuntimes=kwargs['Runtimes'],
        Description=Sub(f'Layer ${{{layer_name.title}}}'),
        LayerName=Ref(layer_name),
        Content=Content(
            S3Bucket=kwargs['Bucket'],
            S3Key=kwargs['Key']
        )
    ))
    if make_public:
        PERM = template.add_resource(LayerVersionPermission(
            f'LambdaVersionPermission{DATE}',
            DeletionPolicy='Retain',
            Principal='*',
            LayerVersionArn=Ref(version),
            Action='lambda:GetLayerVersion'
        ))
    template.add_output(object_outputs(version, export=True))
    return template
