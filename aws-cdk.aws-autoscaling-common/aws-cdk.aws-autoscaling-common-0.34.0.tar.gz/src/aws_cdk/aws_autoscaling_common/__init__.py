import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_iam
import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-autoscaling-common", "0.34.0", __name__, "aws-autoscaling-common@0.34.0.jsii.tgz")
@jsii.data_type(jsii_type="@aws-cdk/aws-autoscaling-common.Alarms", jsii_struct_bases=[])
class Alarms(jsii.compat.TypedDict, total=False):
    """
    Stability:
        experimental
    """
    lowerAlarmIntervalIndex: jsii.Number
    """
    Stability:
        experimental
    """

    upperAlarmIntervalIndex: jsii.Number
    """
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-autoscaling-common.ArbitraryIntervals", jsii_struct_bases=[])
class ArbitraryIntervals(jsii.compat.TypedDict):
    """
    Stability:
        experimental
    """
    absolute: bool
    """
    Stability:
        experimental
    """

    intervals: typing.List["ScalingInterval"]
    """
    Stability:
        experimental
    """

@jsii.data_type_optionals(jsii_struct_bases=[])
class _CompleteScalingInterval(jsii.compat.TypedDict, total=False):
    change: jsii.Number
    """
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-autoscaling-common.CompleteScalingInterval", jsii_struct_bases=[_CompleteScalingInterval])
class CompleteScalingInterval(_CompleteScalingInterval):
    """
    Stability:
        experimental
    """
    lower: jsii.Number
    """
    Stability:
        experimental
    """

    upper: jsii.Number
    """
    Stability:
        experimental
    """

@jsii.interface(jsii_type="@aws-cdk/aws-autoscaling-common.IRandomGenerator")
class IRandomGenerator(jsii.compat.Protocol):
    """
    Stability:
        experimental
    """
    @staticmethod
    def __jsii_proxy_class__():
        return _IRandomGeneratorProxy

    @jsii.member(jsii_name="nextBoolean")
    def next_boolean(self) -> bool:
        """
        Stability:
            experimental
        """
        ...

    @jsii.member(jsii_name="nextInt")
    def next_int(self, min: jsii.Number, max: jsii.Number) -> jsii.Number:
        """
        Arguments:
            min: -
            max: -

        Stability:
            experimental
        """
        ...


class _IRandomGeneratorProxy():
    """
    Stability:
        experimental
    """
    __jsii_type__ = "@aws-cdk/aws-autoscaling-common.IRandomGenerator"
    @jsii.member(jsii_name="nextBoolean")
    def next_boolean(self) -> bool:
        """
        Stability:
            experimental
        """
        return jsii.invoke(self, "nextBoolean", [])

    @jsii.member(jsii_name="nextInt")
    def next_int(self, min: jsii.Number, max: jsii.Number) -> jsii.Number:
        """
        Arguments:
            min: -
            max: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "nextInt", [min, max])


@jsii.data_type_optionals(jsii_struct_bases=[])
class _ScalingInterval(jsii.compat.TypedDict, total=False):
    lower: jsii.Number
    """The lower bound of the interval.

    The scaling adjustment will be applied if the metric is higher than this value.

    Default:
        Threshold automatically derived from neighbouring intervals

    Stability:
        experimental
    """
    upper: jsii.Number
    """The upper bound of the interval.

    The scaling adjustment will be applied if the metric is lower than this value.

    Default:
        Threshold automatically derived from neighbouring intervals

    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-autoscaling-common.ScalingInterval", jsii_struct_bases=[_ScalingInterval])
class ScalingInterval(_ScalingInterval):
    """A range of metric values in which to apply a certain scaling operation.

    Stability:
        experimental
    """
    change: jsii.Number
    """The capacity adjustment to apply in this interval.

    The number is interpreted differently based on AdjustmentType:

    - ChangeInCapacity: add the adjustment to the current capacity.
      The number can be positive or negative.
    - PercentChangeInCapacity: add or remove the given percentage of the current
      capacity to itself. The number can be in the range [-100..100].
    - ExactCapacity: set the capacity to this number. The number must
      be positive.

    Stability:
        experimental
    """

__all__ = ["Alarms", "ArbitraryIntervals", "CompleteScalingInterval", "IRandomGenerator", "ScalingInterval", "__jsii_assembly__"]

publication.publish()
