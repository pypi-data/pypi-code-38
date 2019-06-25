import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-datapipeline", "0.36.0", __name__, "aws-datapipeline@0.36.0.jsii.tgz")
class CfnPipeline(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-datapipeline.CfnPipeline"):
    """A CloudFormation ``AWS::DataPipeline::Pipeline``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html
    Stability:
        stable
    cloudformationResource:
        AWS::DataPipeline::Pipeline
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, name: str, parameter_objects: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["ParameterObjectProperty", aws_cdk.core.IResolvable]]], activate: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]=None, description: typing.Optional[str]=None, parameter_values: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ParameterValueProperty"]]]]]=None, pipeline_objects: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PipelineObjectProperty"]]]]]=None, pipeline_tags: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PipelineTagProperty"]]]]]=None) -> None:
        """Create a new ``AWS::DataPipeline::Pipeline``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            name: ``AWS::DataPipeline::Pipeline.Name``.
            parameter_objects: ``AWS::DataPipeline::Pipeline.ParameterObjects``.
            activate: ``AWS::DataPipeline::Pipeline.Activate``.
            description: ``AWS::DataPipeline::Pipeline.Description``.
            parameter_values: ``AWS::DataPipeline::Pipeline.ParameterValues``.
            pipeline_objects: ``AWS::DataPipeline::Pipeline.PipelineObjects``.
            pipeline_tags: ``AWS::DataPipeline::Pipeline.PipelineTags``.

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
            stable
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            stable
        """
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        """
        Stability:
            stable
        """
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="name")
    def name(self) -> str:
        """``AWS::DataPipeline::Pipeline.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-name
        Stability:
            stable
        """
        return jsii.get(self, "name")

    @name.setter
    def name(self, value: str):
        return jsii.set(self, "name", value)

    @property
    @jsii.member(jsii_name="parameterObjects")
    def parameter_objects(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["ParameterObjectProperty", aws_cdk.core.IResolvable]]]:
        """``AWS::DataPipeline::Pipeline.ParameterObjects``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-parameterobjects
        Stability:
            stable
        """
        return jsii.get(self, "parameterObjects")

    @parameter_objects.setter
    def parameter_objects(self, value: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["ParameterObjectProperty", aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "parameterObjects", value)

    @property
    @jsii.member(jsii_name="activate")
    def activate(self) -> typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::DataPipeline::Pipeline.Activate``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-activate
        Stability:
            stable
        """
        return jsii.get(self, "activate")

    @activate.setter
    def activate(self, value: typing.Optional[typing.Union[typing.Optional[bool], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "activate", value)

    @property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[str]:
        """``AWS::DataPipeline::Pipeline.Description``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-description
        Stability:
            stable
        """
        return jsii.get(self, "description")

    @description.setter
    def description(self, value: typing.Optional[str]):
        return jsii.set(self, "description", value)

    @property
    @jsii.member(jsii_name="parameterValues")
    def parameter_values(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ParameterValueProperty"]]]]]:
        """``AWS::DataPipeline::Pipeline.ParameterValues``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-parametervalues
        Stability:
            stable
        """
        return jsii.get(self, "parameterValues")

    @parameter_values.setter
    def parameter_values(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "ParameterValueProperty"]]]]]):
        return jsii.set(self, "parameterValues", value)

    @property
    @jsii.member(jsii_name="pipelineObjects")
    def pipeline_objects(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PipelineObjectProperty"]]]]]:
        """``AWS::DataPipeline::Pipeline.PipelineObjects``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-pipelineobjects
        Stability:
            stable
        """
        return jsii.get(self, "pipelineObjects")

    @pipeline_objects.setter
    def pipeline_objects(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PipelineObjectProperty"]]]]]):
        return jsii.set(self, "pipelineObjects", value)

    @property
    @jsii.member(jsii_name="pipelineTags")
    def pipeline_tags(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PipelineTagProperty"]]]]]:
        """``AWS::DataPipeline::Pipeline.PipelineTags``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-pipelinetags
        Stability:
            stable
        """
        return jsii.get(self, "pipelineTags")

    @pipeline_tags.setter
    def pipeline_tags(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "PipelineTagProperty"]]]]]):
        return jsii.set(self, "pipelineTags", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _FieldProperty(jsii.compat.TypedDict, total=False):
        refValue: str
        """``CfnPipeline.FieldProperty.RefValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelineobjects-fields.html#cfn-datapipeline-pipeline-pipelineobjects-fields-refvalue
        Stability:
            stable
        """
        stringValue: str
        """``CfnPipeline.FieldProperty.StringValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelineobjects-fields.html#cfn-datapipeline-pipeline-pipelineobjects-fields-stringvalue
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-datapipeline.CfnPipeline.FieldProperty", jsii_struct_bases=[_FieldProperty])
    class FieldProperty(_FieldProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelineobjects-fields.html
        Stability:
            stable
        """
        key: str
        """``CfnPipeline.FieldProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelineobjects-fields.html#cfn-datapipeline-pipeline-pipelineobjects-fields-key
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-datapipeline.CfnPipeline.ParameterAttributeProperty", jsii_struct_bases=[])
    class ParameterAttributeProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-parameterobjects-attributes.html
        Stability:
            stable
        """
        key: str
        """``CfnPipeline.ParameterAttributeProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-parameterobjects-attributes.html#cfn-datapipeline-pipeline-parameterobjects-attribtues-key
        Stability:
            stable
        """

        stringValue: str
        """``CfnPipeline.ParameterAttributeProperty.StringValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-parameterobjects-attributes.html#cfn-datapipeline-pipeline-parameterobjects-attribtues-stringvalue
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-datapipeline.CfnPipeline.ParameterObjectProperty", jsii_struct_bases=[])
    class ParameterObjectProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-parameterobjects.html
        Stability:
            stable
        """
        attributes: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.ParameterAttributeProperty"]]]
        """``CfnPipeline.ParameterObjectProperty.Attributes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-parameterobjects.html#cfn-datapipeline-pipeline-parameterobjects-attributes
        Stability:
            stable
        """

        id: str
        """``CfnPipeline.ParameterObjectProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-parameterobjects.html#cfn-datapipeline-pipeline-parameterobjects-id
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-datapipeline.CfnPipeline.ParameterValueProperty", jsii_struct_bases=[])
    class ParameterValueProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-parametervalues.html
        Stability:
            stable
        """
        id: str
        """``CfnPipeline.ParameterValueProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-parametervalues.html#cfn-datapipeline-pipeline-parametervalues-id
        Stability:
            stable
        """

        stringValue: str
        """``CfnPipeline.ParameterValueProperty.StringValue``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-parametervalues.html#cfn-datapipeline-pipeline-parametervalues-stringvalue
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-datapipeline.CfnPipeline.PipelineObjectProperty", jsii_struct_bases=[])
    class PipelineObjectProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelineobjects.html
        Stability:
            stable
        """
        fields: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.FieldProperty"]]]
        """``CfnPipeline.PipelineObjectProperty.Fields``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelineobjects.html#cfn-datapipeline-pipeline-pipelineobjects-fields
        Stability:
            stable
        """

        id: str
        """``CfnPipeline.PipelineObjectProperty.Id``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelineobjects.html#cfn-datapipeline-pipeline-pipelineobjects-id
        Stability:
            stable
        """

        name: str
        """``CfnPipeline.PipelineObjectProperty.Name``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelineobjects.html#cfn-datapipeline-pipeline-pipelineobjects-name
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-datapipeline.CfnPipeline.PipelineTagProperty", jsii_struct_bases=[])
    class PipelineTagProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelinetags.html
        Stability:
            stable
        """
        key: str
        """``CfnPipeline.PipelineTagProperty.Key``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelinetags.html#cfn-datapipeline-pipeline-pipelinetags-key
        Stability:
            stable
        """

        value: str
        """``CfnPipeline.PipelineTagProperty.Value``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-datapipeline-pipeline-pipelinetags.html#cfn-datapipeline-pipeline-pipelinetags-value
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnPipelineProps(jsii.compat.TypedDict, total=False):
    activate: typing.Union[bool, aws_cdk.core.IResolvable]
    """``AWS::DataPipeline::Pipeline.Activate``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-activate
    Stability:
        stable
    """
    description: str
    """``AWS::DataPipeline::Pipeline.Description``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-description
    Stability:
        stable
    """
    parameterValues: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.ParameterValueProperty"]]]
    """``AWS::DataPipeline::Pipeline.ParameterValues``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-parametervalues
    Stability:
        stable
    """
    pipelineObjects: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.PipelineObjectProperty"]]]
    """``AWS::DataPipeline::Pipeline.PipelineObjects``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-pipelineobjects
    Stability:
        stable
    """
    pipelineTags: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnPipeline.PipelineTagProperty"]]]
    """``AWS::DataPipeline::Pipeline.PipelineTags``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-pipelinetags
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-datapipeline.CfnPipelineProps", jsii_struct_bases=[_CfnPipelineProps])
class CfnPipelineProps(_CfnPipelineProps):
    """Properties for defining a ``AWS::DataPipeline::Pipeline``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html
    Stability:
        stable
    """
    name: str
    """``AWS::DataPipeline::Pipeline.Name``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-name
    Stability:
        stable
    """

    parameterObjects: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union["CfnPipeline.ParameterObjectProperty", aws_cdk.core.IResolvable]]]
    """``AWS::DataPipeline::Pipeline.ParameterObjects``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html#cfn-datapipeline-pipeline-parameterobjects
    Stability:
        stable
    """

__all__ = ["CfnPipeline", "CfnPipelineProps", "__jsii_assembly__"]

publication.publish()
