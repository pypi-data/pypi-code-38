import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-datapipeline", "0.35.0", __name__, "aws-datapipeline@0.35.0.jsii.tgz")
class CfnPipeline(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-datapipeline.CfnPipeline"):
    """A CloudFormation ``AWS::DataPipeline::Pipeline``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html
    Stability:
        experimental
    cloudformationResource:
        AWS::DataPipeline::Pipeline
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, name: str, parameter_objects: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union["ParameterObjectProperty", aws_cdk.cdk.IResolvable]]], activate: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]=None, description: typing.Optional[str]=None, parameter_values: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ParameterValueProperty"]]]]]=None, pipeline_objects: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "PipelineObjectProperty"]]]]]=None, pipeline_tags: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "PipelineTagProperty"]]]]]=None) -> None:
        """Create a new ``AWS::DataPipeline::Pipeline``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::DataPipeline::Pipeline.Name``.
            parameterObjects: ``AWS::DataPipeline::Pipeline.ParameterObjects``.
            activate: ``AWS::DataPipeline::Pipeline.Activate``.
            description: ``AWS::DataPipeline::Pipeline.Description``.
            parameterValues: ``AWS::DataPipeline::Pipeline.ParameterValues``.
            pipelineObjects: ``AWS::DataPipeline::Pipeline.PipelineObjects``.
            pipelineTags: ``AWS::DataPipeline::Pipeline.PipelineTags``.

        Stability:
            experimental
        """
        props: CfnPipelineProps = {"name": name, "parameterObjects": parameter_objects}

        if activate is not None:
            props["activate"] = activate

        if description is not None:
            props["description"] = description

        if parameter_values is not None:
            props["parameterValues"] = parameter_values

        if pipeline_objects is not None:
            props["pipelineObjects"] = pipeline_objects

        if pipeline_tags is not None:
            props["pipelineTags"] = pipeline_tags

        jsii.create(CfnPipeline, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            props: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="cfnResourceTypeName")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "cfnResourceTypeName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::DataPipeline::Pipeline.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-name
        Stability:
            experimental
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="parameterObjects")
    def parameter_objects(self) -> typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union["ParameterObjectProperty", aws_cdk.cdk.IResolvable]]]:
        """``AWS::DataPipeline::Pipeline.ParameterObjects``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-parameterobjects
        Stability:
            experimental
        """
        return jsii.get(self, "parameterObjects")

    @parameter_objects.setter
    def parameter_objects(self, value: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union["ParameterObjectProperty", aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "parameterObjects", value)

    @property
    @jsii.member(jsii_name="activate")
    def activate(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]:
        """``AWS::DataPipeline::Pipeline.Activate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-activate
        Stability:
            experimental
        """
        return jsii.get(self, "activate")

    @activate.setter
    def activate(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.cdk.IResolvable]]]):
        return jsii.set(self, "activate", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::DataPipeline::Pipeline.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-description
        Stability:
            experimental
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="parameterValues")
    def parameter_values(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ParameterValueProperty"]]]]]:
        """``AWS::DataPipeline::Pipeline.ParameterValues``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-parametervalues
        Stability:
            experimental
        """
        return jsii.get(self, "parameterValues")

    @parameter_values.setter
    def parameter_values(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "ParameterValueProperty"]]]]]):
        return jsii.set(self, "parameterValues", value)

    @property
    @jsii.member(jsii_name="pipelineObjects")
    def pipeline_objects(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "PipelineObjectProperty"]]]]]:
        """``AWS::DataPipeline::Pipeline.PipelineObjects``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-pipelineobjects
        Stability:
            experimental
        """
        return jsii.get(self, "pipelineObjects")

    @pipeline_objects.setter
    def pipeline_objects(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "PipelineObjectProperty"]]]]]):
        return jsii.set(self, "pipelineObjects", value)

    @property
    @jsii.member(jsii_name="pipelineTags")
    def pipeline_tags(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "PipelineTagProperty"]]]]]:
        """``AWS::DataPipeline::Pipeline.PipelineTags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-pipelinetags
        Stability:
            experimental
        """
        return jsii.get(self, "pipelineTags")

    @pipeline_tags.setter
    def pipeline_tags(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.IResolvable, "PipelineTagProperty"]]]]]):
        return jsii.set(self, "pipelineTags", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _FieldProperty(jsii.compat.TypedDict, total=False):
        refValue: str
        """``CfnPipeline.FieldProperty.RefValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelineobjects-fields.html#cfn-datapipeline-pipeline-pipelineobjects-fields-refvalue
        Stability:
            experimental
        """
        stringValue: str
        """``CfnPipeline.FieldProperty.StringValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelineobjects-fields.html#cfn-datapipeline-pipeline-pipelineobjects-fields-stringvalue
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-datapipeline.CfnPipeline.FieldProperty", jsii_struct_bases=[_FieldProperty])
    class FieldProperty(_FieldProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelineobjects-fields.html
        Stability:
            experimental
        """
        key: str
        """``CfnPipeline.FieldProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelineobjects-fields.html#cfn-datapipeline-pipeline-pipelineobjects-fields-key
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-datapipeline.CfnPipeline.ParameterAttributeProperty", jsii_struct_bases=[])
    class ParameterAttributeProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-parameterobjects-attributes.html
        Stability:
            experimental
        """
        key: str
        """``CfnPipeline.ParameterAttributeProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-parameterobjects-attributes.html#cfn-datapipeline-pipeline-parameterobjects-attribtues-key
        Stability:
            experimental
        """

        stringValue: str
        """``CfnPipeline.ParameterAttributeProperty.StringValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-parameterobjects-attributes.html#cfn-datapipeline-pipeline-parameterobjects-attribtues-stringvalue
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-datapipeline.CfnPipeline.ParameterObjectProperty", jsii_struct_bases=[])
    class ParameterObjectProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-parameterobjects.html
        Stability:
            experimental
        """
        attributes: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnPipeline.ParameterAttributeProperty"]]]
        """``CfnPipeline.ParameterObjectProperty.Attributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-parameterobjects.html#cfn-datapipeline-pipeline-parameterobjects-attributes
        Stability:
            experimental
        """

        id: str
        """``CfnPipeline.ParameterObjectProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-parameterobjects.html#cfn-datapipeline-pipeline-parameterobjects-id
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-datapipeline.CfnPipeline.ParameterValueProperty", jsii_struct_bases=[])
    class ParameterValueProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-parametervalues.html
        Stability:
            experimental
        """
        id: str
        """``CfnPipeline.ParameterValueProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-parametervalues.html#cfn-datapipeline-pipeline-parametervalues-id
        Stability:
            experimental
        """

        stringValue: str
        """``CfnPipeline.ParameterValueProperty.StringValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-parametervalues.html#cfn-datapipeline-pipeline-parametervalues-stringvalue
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-datapipeline.CfnPipeline.PipelineObjectProperty", jsii_struct_bases=[])
    class PipelineObjectProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelineobjects.html
        Stability:
            experimental
        """
        fields: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnPipeline.FieldProperty"]]]
        """``CfnPipeline.PipelineObjectProperty.Fields``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelineobjects.html#cfn-datapipeline-pipeline-pipelineobjects-fields
        Stability:
            experimental
        """

        id: str
        """``CfnPipeline.PipelineObjectProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelineobjects.html#cfn-datapipeline-pipeline-pipelineobjects-id
        Stability:
            experimental
        """

        name: str
        """``CfnPipeline.PipelineObjectProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelineobjects.html#cfn-datapipeline-pipeline-pipelineobjects-name
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-datapipeline.CfnPipeline.PipelineTagProperty", jsii_struct_bases=[])
    class PipelineTagProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelinetags.html
        Stability:
            experimental
        """
        key: str
        """``CfnPipeline.PipelineTagProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelinetags.html#cfn-datapipeline-pipeline-pipelinetags-key
        Stability:
            experimental
        """

        value: str
        """``CfnPipeline.PipelineTagProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelinetags.html#cfn-datapipeline-pipeline-pipelinetags-value
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnPipelineProps(jsii.compat.TypedDict, total=False):
    activate: typing.Union[bool, aws_cdk.cdk.IResolvable]
    """``AWS::DataPipeline::Pipeline.Activate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-activate
    Stability:
        experimental
    """
    description: str
    """``AWS::DataPipeline::Pipeline.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-description
    Stability:
        experimental
    """
    parameterValues: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnPipeline.ParameterValueProperty"]]]
    """``AWS::DataPipeline::Pipeline.ParameterValues``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-parametervalues
    Stability:
        experimental
    """
    pipelineObjects: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnPipeline.PipelineObjectProperty"]]]
    """``AWS::DataPipeline::Pipeline.PipelineObjects``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-pipelineobjects
    Stability:
        experimental
    """
    pipelineTags: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union[aws_cdk.cdk.IResolvable, "CfnPipeline.PipelineTagProperty"]]]
    """``AWS::DataPipeline::Pipeline.PipelineTags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-pipelinetags
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-datapipeline.CfnPipelineProps", jsii_struct_bases=[_CfnPipelineProps])
class CfnPipelineProps(_CfnPipelineProps):
    """Properties for defining a ``AWS::DataPipeline::Pipeline``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html
    Stability:
        experimental
    """
    name: str
    """``AWS::DataPipeline::Pipeline.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-name
    Stability:
        experimental
    """

    parameterObjects: typing.Union[aws_cdk.cdk.IResolvable, typing.List[typing.Union["CfnPipeline.ParameterObjectProperty", aws_cdk.cdk.IResolvable]]]
    """``AWS::DataPipeline::Pipeline.ParameterObjects``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-parameterobjects
    Stability:
        experimental
    """

__all__ = ["CfnPipeline", "CfnPipelineProps", "__jsii_assembly__"]

publication.publish()
