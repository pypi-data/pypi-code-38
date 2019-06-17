"""
Common functions to return outputs
"""

from troposphere import (
    Output,
    GetAtt,
    Export,
    Ref,
    Sub
)
from troposphere.iam import Role
from troposphere.awslambda import LayerVersion
from ozone.filters import get_resource_type


def object_outputs(template_resource, supports_arn=False, export=False,
                   append_title=False, name_is_id=False):
    """
    Args:
      template_object: Troposphere resource object to extract outputs from
      export: bool: Exports the value to the Region for other stacks to use
      suports_arn: bool: If the object supports GetAtt(object, 'Arn'), set to true to add the
                         ARN to the outputs
      kwargs:
        key-pair values to add more tags
    Returns:
        outputs: list: list of Output() object for the Troposphere template
    """

    outputs = []
    object_type = get_resource_type(template_resource)
    name_ext = 'Name'
    if name_is_id:
        name_ext = 'Id'
    suffix = name_ext
    export_name = f'${{AWS::StackName}}-{object_type}'
    if append_title:
        export_name = f'${{AWS::StackName}}-{object_type}-{template_resource.title}'
    output = Output(
        f'{template_resource.title}{name_ext}',
        Value=Ref(template_resource)
    )
    if export:
        setattr(
            output, 'Export',
            Export(Sub(f'{export_name}-{suffix}'))
        )
    outputs.append(output)
    if supports_arn:
        output = Output(
            f'{template_resource.title}Arn',
            Value=GetAtt(template_resource, 'Arn')
        )
        if export:
            setattr(output, 'Export',
                    Export(Sub(f'{export_name}-Arn'))
            )
        outputs.append(output)
    if isinstance(template_resource, Role):
        output = Output(
            f'{template_resource.title}UniqueId',
            Value=GetAtt(template_resource, 'RoleId')
        )
        if export:
            setattr(
                output, 'Export',
                Export(Sub(f'{export_name}-RoleId'))
            )
        outputs.append(output)
    elif isinstance(template_resource, LayerVersion):
        output = Output(
            f'{template_resource.title}Arn',
            Value=Ref(template_resource)
        )
        if export:
            setattr(
                output, 'Export',
                Export(Sub(f'{export_name}-Arn'))
            )
        outputs.append(output)
    return outputs


def comments_outputs(comments, export=False):
    """
    Args:
      comments: list: list of key pair values to add outputs not related to an object
      export: bool: set to True if the value should be exported in the region
    Returns:
        outputs: list: list of Output() object for the Troposphere template
    """
    outputs = []
    if isinstance(comments, list):
        for comment in comments:
            if isinstance(comment, dict):
                keys = list(comment.keys())
                args = {
                    'title': keys[0],
                    'Value': comment[keys[0]]
                }
                if export:
                    args['Export'] = Export(Sub(f'${{AWS::StackName}}-{keys[0]}'))
                outputs.append(Output(**args))
    return outputs

