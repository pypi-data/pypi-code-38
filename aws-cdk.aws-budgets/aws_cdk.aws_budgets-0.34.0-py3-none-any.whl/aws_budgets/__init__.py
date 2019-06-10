import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.cdk
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-budgets", "0.34.0", __name__, "aws-budgets@0.34.0.jsii.tgz")
class CfnBudget(aws_cdk.cdk.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-budgets.CfnBudget"):
    """A CloudFormation ``AWS::Budgets::Budget``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-budgets-budget.html
    Stability:
        experimental
    cloudformationResource:
        AWS::Budgets::Budget
    """
    def __init__(self, scope: aws_cdk.cdk.Construct, id: str, *, budget: typing.Union["BudgetDataProperty", aws_cdk.cdk.Token], notifications_with_subscribers: typing.Optional[typing.Union[typing.Optional[aws_cdk.cdk.Token], typing.Optional[typing.List[typing.Union[aws_cdk.cdk.Token, "NotificationWithSubscribersProperty"]]]]]=None) -> None:
        """Create a new ``AWS::Budgets::Budget``.

        Arguments:
            scope: - scope in which this resource is defined.
            id: - scoped id of the resource.
            props: - resource properties.
            budget: ``AWS::Budgets::Budget.Budget``.
            notificationsWithSubscribers: ``AWS::Budgets::Budget.NotificationsWithSubscribers``.

        Stability:
            experimental
        """
        props: CfnBudgetProps = {"budget": budget}

        if notifications_with_subscribers is not None:
            props["notificationsWithSubscribers"] = notifications_with_subscribers

        jsii.create(CfnBudget, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, properties: typing.Any) -> typing.Mapping[str,typing.Any]:
        """
        Arguments:
            properties: -

        Stability:
            experimental
        """
        return jsii.invoke(self, "renderProperties", [properties])

    @classproperty
    @jsii.member(jsii_name="resourceTypeName")
    def RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class.

        Stability:
            experimental
        """
        return jsii.sget(cls, "resourceTypeName")

    @property
    @jsii.member(jsii_name="budgetName")
    def budget_name(self) -> str:
        """
        Stability:
            experimental
        """
        return jsii.get(self, "budgetName")

    @property
    @jsii.member(jsii_name="propertyOverrides")
    def property_overrides(self) -> "CfnBudgetProps":
        """
        Stability:
            experimental
        """
        return jsii.get(self, "propertyOverrides")

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _BudgetDataProperty(jsii.compat.TypedDict, total=False):
        budgetLimit: typing.Union[aws_cdk.cdk.Token, "CfnBudget.SpendProperty"]
        """``CfnBudget.BudgetDataProperty.BudgetLimit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-budgetlimit
        Stability:
            experimental
        """
        budgetName: str
        """``CfnBudget.BudgetDataProperty.BudgetName``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-budgetname
        Stability:
            experimental
        """
        costFilters: typing.Union[typing.Mapping[typing.Any, typing.Any], aws_cdk.cdk.Token]
        """``CfnBudget.BudgetDataProperty.CostFilters``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-costfilters
        Stability:
            experimental
        """
        costTypes: typing.Union[aws_cdk.cdk.Token, "CfnBudget.CostTypesProperty"]
        """``CfnBudget.BudgetDataProperty.CostTypes``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-costtypes
        Stability:
            experimental
        """
        timePeriod: typing.Union[aws_cdk.cdk.Token, "CfnBudget.TimePeriodProperty"]
        """``CfnBudget.BudgetDataProperty.TimePeriod``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-timeperiod
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.BudgetDataProperty", jsii_struct_bases=[_BudgetDataProperty])
    class BudgetDataProperty(_BudgetDataProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html
        Stability:
            experimental
        """
        budgetType: str
        """``CfnBudget.BudgetDataProperty.BudgetType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-budgettype
        Stability:
            experimental
        """

        timeUnit: str
        """``CfnBudget.BudgetDataProperty.TimeUnit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-timeunit
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.CostTypesProperty", jsii_struct_bases=[])
    class CostTypesProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html
        Stability:
            experimental
        """
        includeCredit: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnBudget.CostTypesProperty.IncludeCredit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includecredit
        Stability:
            experimental
        """

        includeDiscount: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnBudget.CostTypesProperty.IncludeDiscount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includediscount
        Stability:
            experimental
        """

        includeOtherSubscription: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnBudget.CostTypesProperty.IncludeOtherSubscription``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includeothersubscription
        Stability:
            experimental
        """

        includeRecurring: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnBudget.CostTypesProperty.IncludeRecurring``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includerecurring
        Stability:
            experimental
        """

        includeRefund: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnBudget.CostTypesProperty.IncludeRefund``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includerefund
        Stability:
            experimental
        """

        includeSubscription: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnBudget.CostTypesProperty.IncludeSubscription``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includesubscription
        Stability:
            experimental
        """

        includeSupport: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnBudget.CostTypesProperty.IncludeSupport``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includesupport
        Stability:
            experimental
        """

        includeTax: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnBudget.CostTypesProperty.IncludeTax``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includetax
        Stability:
            experimental
        """

        includeUpfront: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnBudget.CostTypesProperty.IncludeUpfront``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-includeupfront
        Stability:
            experimental
        """

        useAmortized: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnBudget.CostTypesProperty.UseAmortized``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-useamortized
        Stability:
            experimental
        """

        useBlended: typing.Union[bool, aws_cdk.cdk.Token]
        """``CfnBudget.CostTypesProperty.UseBlended``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-costtypes.html#cfn-budgets-budget-costtypes-useblended
        Stability:
            experimental
        """

    @jsii.data_type_optionals(jsii_struct_bases=[])
    class _NotificationProperty(jsii.compat.TypedDict, total=False):
        thresholdType: str
        """``CfnBudget.NotificationProperty.ThresholdType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notification.html#cfn-budgets-budget-notification-thresholdtype
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.NotificationProperty", jsii_struct_bases=[_NotificationProperty])
    class NotificationProperty(_NotificationProperty):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notification.html
        Stability:
            experimental
        """
        comparisonOperator: str
        """``CfnBudget.NotificationProperty.ComparisonOperator``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notification.html#cfn-budgets-budget-notification-comparisonoperator
        Stability:
            experimental
        """

        notificationType: str
        """``CfnBudget.NotificationProperty.NotificationType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notification.html#cfn-budgets-budget-notification-notificationtype
        Stability:
            experimental
        """

        threshold: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnBudget.NotificationProperty.Threshold``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notification.html#cfn-budgets-budget-notification-threshold
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.NotificationWithSubscribersProperty", jsii_struct_bases=[])
    class NotificationWithSubscribersProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notificationwithsubscribers.html
        Stability:
            experimental
        """
        notification: typing.Union[aws_cdk.cdk.Token, "CfnBudget.NotificationProperty"]
        """``CfnBudget.NotificationWithSubscribersProperty.Notification``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notificationwithsubscribers.html#cfn-budgets-budget-notificationwithsubscribers-notification
        Stability:
            experimental
        """

        subscribers: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnBudget.SubscriberProperty"]]]
        """``CfnBudget.NotificationWithSubscribersProperty.Subscribers``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notificationwithsubscribers.html#cfn-budgets-budget-notificationwithsubscribers-subscribers
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.SpendProperty", jsii_struct_bases=[])
    class SpendProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-spend.html
        Stability:
            experimental
        """
        amount: typing.Union[jsii.Number, aws_cdk.cdk.Token]
        """``CfnBudget.SpendProperty.Amount``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-spend.html#cfn-budgets-budget-spend-amount
        Stability:
            experimental
        """

        unit: str
        """``CfnBudget.SpendProperty.Unit``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-spend.html#cfn-budgets-budget-spend-unit
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.SubscriberProperty", jsii_struct_bases=[])
    class SubscriberProperty(jsii.compat.TypedDict):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-subscriber.html
        Stability:
            experimental
        """
        address: str
        """``CfnBudget.SubscriberProperty.Address``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-subscriber.html#cfn-budgets-budget-subscriber-address
        Stability:
            experimental
        """

        subscriptionType: str
        """``CfnBudget.SubscriberProperty.SubscriptionType``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-subscriber.html#cfn-budgets-budget-subscriber-subscriptiontype
        Stability:
            experimental
        """

    @jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudget.TimePeriodProperty", jsii_struct_bases=[])
    class TimePeriodProperty(jsii.compat.TypedDict, total=False):
        """
        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-timeperiod.html
        Stability:
            experimental
        """
        end: str
        """``CfnBudget.TimePeriodProperty.End``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-timeperiod.html#cfn-budgets-budget-timeperiod-end
        Stability:
            experimental
        """

        start: str
        """``CfnBudget.TimePeriodProperty.Start``.

        See:
            http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-timeperiod.html#cfn-budgets-budget-timeperiod-start
        Stability:
            experimental
        """


@jsii.data_type_optionals(jsii_struct_bases=[])
class _CfnBudgetProps(jsii.compat.TypedDict, total=False):
    notificationsWithSubscribers: typing.Union[aws_cdk.cdk.Token, typing.List[typing.Union[aws_cdk.cdk.Token, "CfnBudget.NotificationWithSubscribersProperty"]]]
    """``AWS::Budgets::Budget.NotificationsWithSubscribers``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-budgets-budget.html#cfn-budgets-budget-notificationswithsubscribers
    Stability:
        experimental
    """

@jsii.data_type(jsii_type="@aws-cdk/aws-budgets.CfnBudgetProps", jsii_struct_bases=[_CfnBudgetProps])
class CfnBudgetProps(_CfnBudgetProps):
    """Properties for defining a ``AWS::Budgets::Budget``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-budgets-budget.html
    Stability:
        experimental
    """
    budget: typing.Union["CfnBudget.BudgetDataProperty", aws_cdk.cdk.Token]
    """``AWS::Budgets::Budget.Budget``.

    See:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-budgets-budget.html#cfn-budgets-budget-budget
    Stability:
        experimental
    """

__all__ = ["CfnBudget", "CfnBudgetProps", "__jsii_assembly__"]

publication.publish()
