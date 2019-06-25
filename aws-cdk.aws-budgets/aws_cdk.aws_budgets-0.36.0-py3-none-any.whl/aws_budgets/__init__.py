import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-budgets", "0.36.0", __name__, "aws-budgets@0.36.0.jsii.tgz")
class CfnBudget(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-budgets.CfnBudget"):
    """A CloudFormation ``AWS::Budgets::Budget``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-budgets-budget.html
    Stability:
        stable
    cloudformationResource:
        AWS::Budgets::Budget
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, budget: typing.Union["BudgetDataProperty", aws_cdk.core.IResolvable], notifications_with_subscribers: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "NotificationWithSubscribersProperty"]]]]]=None) -> None:
        """Create a new ``AWS::Budgets::Budget``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            budget: ``AWS::Budgets::Budget.Budget``.
            notifications_with_subscribers: ``AWS::Budgets::Budget.NotificationsWithSubscribers``.

        Stability:
            experimental
        """
        props: CfnBudgetProps = {"budget": budget}

        if notifications_with_subscribers is not None:
            props["notificationsWithSubscribers"] = notifications_with_subscribers

        jsii.create(CfnBudget, self, [scope, id, props])

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
    @jsii.member(jsii_name="budget")
    def budget(self) -> typing.Union["BudgetDataProperty", aws_cdk.core.IResolvable]:
        """``AWS::Budgets::Budget.Budget``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-budgets-budget.html#cfn-budgets-budget-budget
        Stability:
            stable
        """
        return jsii.get(self, "budget")

    @budget.setter
    def budget(self, value: typing.Union["BudgetDataProperty", aws_cdk.core.IResolvable]):
        return jsii.set(self, "budget", value)

    @property
    @jsii.member(jsii_name="notificationsWithSubscribers")
    def notifications_with_subscribers(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "NotificationWithSubscribersProperty"]]]]]:
        """``AWS::Budgets::Budget.NotificationsWithSubscribers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-budgets-budget.html#cfn-budgets-budget-notificationswithsubscribers
        Stability:
            stable
        """
        return jsii.get(self, "notificationsWithSubscribers")

    @notifications_with_subscribers.setter
    def notifications_with_subscribers(self, value: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "NotificationWithSubscribersProperty"]]]]]):
        return jsii.set(self, "notificationsWithSubscribers", value)

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _BudgetDataProperty(jsii.compat.TypedDict, total=False):
        budgetLimit: typing.Union[aws_cdk.core.IResolvable, "CfnBudget.SpendProperty"]
        """``CfnBudget.BudgetDataProperty.BudgetLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-budgetlimit
        Stability:
            stable
        """
        budgetName: str
        """``CfnBudget.BudgetDataProperty.BudgetName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-budgetname
        Stability:
            stable
        """
        costFilters: typing.Any
        """``CfnBudget.BudgetDataProperty.CostFilters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-costfilters
        Stability:
            stable
        """
        costTypes: typing.Union[aws_cdk.core.IResolvable, "CfnBudget.CostTypesProperty"]
        """``CfnBudget.BudgetDataProperty.CostTypes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-costtypes
        Stability:
            stable
        """
        timePeriod: typing.Union[aws_cdk.core.IResolvable, "CfnBudget.TimePeriodProperty"]
        """``CfnBudget.BudgetDataProperty.TimePeriod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-timeperiod
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.BudgetDataProperty", jsii_struct_bases=[_BudgetDataProperty])
    class BudgetDataProperty(_BudgetDataProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html
        Stability:
            stable
        """
        budgetType: str
        """``CfnBudget.BudgetDataProperty.BudgetType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-budgettype
        Stability:
            stable
        """

        timeUnit: str
        """``CfnBudget.BudgetDataProperty.TimeUnit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-timeunit
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.CostTypesProperty", jsii_struct_bases=[])
    class CostTypesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html
        Stability:
            stable
        """
        includeCredit: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnBudget.CostTypesProperty.IncludeCredit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includecredit
        Stability:
            stable
        """

        includeDiscount: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnBudget.CostTypesProperty.IncludeDiscount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includediscount
        Stability:
            stable
        """

        includeOtherSubscription: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnBudget.CostTypesProperty.IncludeOtherSubscription``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includeothersubscription
        Stability:
            stable
        """

        includeRecurring: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnBudget.CostTypesProperty.IncludeRecurring``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includerecurring
        Stability:
            stable
        """

        includeRefund: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnBudget.CostTypesProperty.IncludeRefund``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includerefund
        Stability:
            stable
        """

        includeSubscription: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnBudget.CostTypesProperty.IncludeSubscription``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includesubscription
        Stability:
            stable
        """

        includeSupport: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnBudget.CostTypesProperty.IncludeSupport``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includesupport
        Stability:
            stable
        """

        includeTax: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnBudget.CostTypesProperty.IncludeTax``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includetax
        Stability:
            stable
        """

        includeUpfront: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnBudget.CostTypesProperty.IncludeUpfront``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includeupfront
        Stability:
            stable
        """

        useAmortized: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnBudget.CostTypesProperty.UseAmortized``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-useamortized
        Stability:
            stable
        """

        useBlended: typing.Union[bool, aws_cdk.core.IResolvable]
        """``CfnBudget.CostTypesProperty.UseBlended``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-useblended
        Stability:
            stable
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _NotificationProperty(jsii.compat.TypedDict, total=False):
        thresholdType: str
        """``CfnBudget.NotificationProperty.ThresholdType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notification.html#cfn-budgets-budget-notification-thresholdtype
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.NotificationProperty", jsii_struct_bases=[_NotificationProperty])
    class NotificationProperty(_NotificationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notification.html
        Stability:
            stable
        """
        comparisonOperator: str
        """``CfnBudget.NotificationProperty.ComparisonOperator``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notification.html#cfn-budgets-budget-notification-comparisonoperator
        Stability:
            stable
        """

        notificationType: str
        """``CfnBudget.NotificationProperty.NotificationType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notification.html#cfn-budgets-budget-notification-notificationtype
        Stability:
            stable
        """

        threshold: jsii.Number
        """``CfnBudget.NotificationProperty.Threshold``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notification.html#cfn-budgets-budget-notification-threshold
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.NotificationWithSubscribersProperty", jsii_struct_bases=[])
    class NotificationWithSubscribersProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notificationwithsubscribers.html
        Stability:
            stable
        """
        notification: typing.Union[aws_cdk.core.IResolvable, "CfnBudget.NotificationProperty"]
        """``CfnBudget.NotificationWithSubscribersProperty.Notification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notificationwithsubscribers.html#cfn-budgets-budget-notificationwithsubscribers-notification
        Stability:
            stable
        """

        subscribers: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnBudget.SubscriberProperty"]]]
        """``CfnBudget.NotificationWithSubscribersProperty.Subscribers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notificationwithsubscribers.html#cfn-budgets-budget-notificationwithsubscribers-subscribers
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.SpendProperty", jsii_struct_bases=[])
    class SpendProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-spend.html
        Stability:
            stable
        """
        amount: jsii.Number
        """``CfnBudget.SpendProperty.Amount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-spend.html#cfn-budgets-budget-spend-amount
        Stability:
            stable
        """

        unit: str
        """``CfnBudget.SpendProperty.Unit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-spend.html#cfn-budgets-budget-spend-unit
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.SubscriberProperty", jsii_struct_bases=[])
    class SubscriberProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-subscriber.html
        Stability:
            stable
        """
        address: str
        """``CfnBudget.SubscriberProperty.Address``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-subscriber.html#cfn-budgets-budget-subscriber-address
        Stability:
            stable
        """

        subscriptionType: str
        """``CfnBudget.SubscriberProperty.SubscriptionType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-subscriber.html#cfn-budgets-budget-subscriber-subscriptiontype
        Stability:
            stable
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.TimePeriodProperty", jsii_struct_bases=[])
    class TimePeriodProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-timeperiod.html
        Stability:
            stable
        """
        end: str
        """``CfnBudget.TimePeriodProperty.End``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-timeperiod.html#cfn-budgets-budget-timeperiod-end
        Stability:
            stable
        """

        start: str
        """``CfnBudget.TimePeriodProperty.Start``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-timeperiod.html#cfn-budgets-budget-timeperiod-start
        Stability:
            stable
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnBudgetProps(jsii.compat.TypedDict, total=False):
    notificationsWithSubscribers: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnBudget.NotificationWithSubscribersProperty"]]]
    """``AWS::Budgets::Budget.NotificationsWithSubscribers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-budgets-budget.html#cfn-budgets-budget-notificationswithsubscribers
    Stability:
        stable
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudgetProps", jsii_struct_bases=[_CfnBudgetProps])
class CfnBudgetProps(_CfnBudgetProps):
    """Properties for defining a ``AWS::Budgets::Budget``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-budgets-budget.html
    Stability:
        stable
    """
    budget: typing.Union["CfnBudget.BudgetDataProperty", aws_cdk.core.IResolvable]
    """``AWS::Budgets::Budget.Budget``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-budgets-budget.html#cfn-budgets-budget-budget
    Stability:
        stable
    """

__all__ = ["CfnBudget", "CfnBudgetProps", "__jsii_assembly__"]

publication.publish()
