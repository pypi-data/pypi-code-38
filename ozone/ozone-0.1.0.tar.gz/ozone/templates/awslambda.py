from troposphere import (
    Parameter,
    Template,
    Equals,
    GetAtt,
    Ref,
    Sub
)

from troposphere.awslambda import (
    Function,
    LayerVersion,
    Permission,
    Alias,
    Version,
    Code,
    Environment

)
from ozone.outputs import object_outputs
from ozone.filters.arns import (
    iam_role as filter_iamrole,
    lambda_layer as filter_layer
)

def lambda_function(**kwargs):
    function = Function(
        'LambdaFunction',
        Code=Code(
            S3Bucket='replace-me',
            S3Key='replace-me'
        ),
        Handler='function.lambda_handler',
        MemorySize='256',
        Timeout=30
    )
    for key in kwargs.keys():
        if key == 'Layers':
            layers = []
            for layer in kwargs[key]:
                layers.append(filter_layer(layer))
            print(layers)
            setattr(function, key, layers)
        elif key == 'S3Bucket' or key == 'S3Key':
            setattr(function, 'Code', Code(S3Bucket=kwargs['S3Bucket'], S3Key=kwargs['S3Key']))
        elif key == 'Role':
            setattr(function, 'Role', filter_iamrole(kwargs[key]))
        elif key == 'Environment':
            if isinstance(kwargs[key], dict):
                setattr(function, key, Environment(Variables=kwargs[key]))
            elif isinstance(kwargs[key], Environment):
                setattr(function, key, kwargs[key])
        else:
            setattr(function, key, kwargs[key])
    return function


def template(**kwargs):
    """
    Args:

    Returns:
      template Template()
    """
    template = Template()
    release = template.add_parameter(Parameter(
        'ReleaseNewAlias',
        Type="String",
        AllowedValues = ['Yes', 'No'],
        Default = 'No'
    ))
    release_condition = template.add_condition(
        'ReleaseAlias',
        {
            'ReleaseAlias': Equals(
                Ref(release),
                'Yes'
            )
        }
    )
    function = template.add_resource(lambda_function(**kwargs))
    version = template.add_resource(Version(
        'LambdaVersion',
        FunctionName=GetAtt(function, 'Arn')
    ))
    alias = template.add_resource(Alias(
        'LambdaAlias',
        Name = 'prod',
        DependsOn = [release_condition],
        Description = Sub(f'Alias to version ${{{version.title}.Arn}}'),
        FunctionName = Ref(function),
        FunctionVersion = Ref(version)
    ))
    template.add_output(object_outputs(function, True))
    template.add_output(object_outputs(version, True))
    return template
