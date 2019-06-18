from ms_sdk.Resourses.Events import *
from ms_sdk.Resourses.Marketing import *
from ms_sdk.Resourses.Shop import *
from ms_sdk.Resourses.Users import *
from ms_sdk.Resourses.Grapher import *
from ms_sdk.Resourses.Products import *
from ms_sdk.Resourses.Prices.ProductPriceConfigurationsResource import ProductPriceConfigurationsResource
from ms_sdk.Resourses.Documents.DocumentsResource import DocumentsResource
from ms_sdk.Resourses.Users.UserEventsResource import UserEventsResource


class ServiceInjectorMixin:

    # Products
    def attributeDisplayTypes(self):
        """
        Client self
        :return AttributeDisplayTypesResource:
        """
        return AttributeDisplayTypesResource(self)

    def attributes(self):
        """
        Client self
        :return AttributesResource:
        """
        return AttributesResource(self)

    def attributeGroupsEntities(self):
        """
        Client self
        :return AttributeGroupsEntitiesResource:
        """
        return AttributeGroupsEntitiesResource(self)

    def attributeGroups(self):
        """
        Client self
        :return AttributeGroupsResource:
        """
        return AttributeGroupsResource(self)

    def attributeTypes(self):
        """
        Client self
        :return AttributeTypesResource:
        """
        return AttributeTypesResource(self)

    def attributeValues(self):
        """
        Client self
        :return AttributeValuesResource:
        """
        return AttributeValuesResource(self)

    def products(self):
        """
        Client self
        :return ProductsResource:
        """
        return ProductsResource(self)

    def brands(self):
        """
        Client self
        :return BrandsResource:
        """
        return BrandsResource(self)

    def options(self):
        """
        Client self
        :return OptionsResource:
        """
        return OptionsResource(self)

    def catalogItems(self):
        """
        Client self
        :return CatalogItemsResource:
        """
        return CatalogItemsResource(self)

    def entities(self):
        """
        Client self
        :return EntitiesResource:
        """
        return EntitiesResource(self)

    def entityAttributes(self):
        """
        Client self
        :return EntityAttributesResource:
        """
        return EntityAttributesResource(self)

    def entityAttributeValues(self):
        """
        Client self
        :return EntityAttributeValuesResource:
        """
        return EntityAttributeValuesResource(self)

    def media(self):
        """
        Client self
        :return MediaResource:
        """
        return MediaResource(self)

    def mediaTypes(self):
        """
        Client self
        :return MediaTypesResource:
        """
        return MediaTypesResource(self)

    def functionalNames(self):
        """
        Client self
        :return FunctionalNamesResource:
        """
        return FunctionalNamesResource(self)

    def productAttributeValues(self):
        """
        Client self
        :return ProductAttributeValuesResource:
        """
        return ProductAttributeValuesResource(self)

    # Documents
    def documents(self):
        """
        Client self
        :return DocumentsResource:
        """
        return DocumentsResource(self)

    # Grapher service
    def correlations(self):
        """
        Client self
        :return CorrelationsResource:
        """
        return CorrelationsResource(self)

    def grid(self):
        """
        Client self
        :return GridResource:
        """
        return GridResource(self)

    # Events service
    def events(self):
        """
        Client self
        :return EventsResource:
        """
        return EventsResource(self)

    # Triggers service
    def triggers(self):
        """
        Client self
        :return EventsResource:
        """
        return TriggerResource(self)

    # Users service
    def users(self):
        """
        Client self
        :return UsersResource:
        """
        return UsersResource(self)

    def userEvents(self):
        """
        Client self
        :return UserEventsResource:
        """
        return UserEventsResource(self)

    def companies(self):
        """
        Client self
        :return CompaniesResource:
        """
        return CompaniesResource(self)

    def messages(self):
        """
        Client self
        :return MessagesResource:
        """
        return MessagesResource(self)

    def wishListItems(self):
        """
        Client self
        :return WishListItemsResource:
        """
        return WishListItemsResource(self)

    # Prices service
    def productPriceConfigurations(self):
        """
        Client self
        :return ProductPriceConfigurationsResource:
        """
        return ProductPriceConfigurationsResource(self)

    # Shop service
    def currencies(self):
        """
        Client self
        :return CurrenciesResource:
        """
        return CurrenciesResource(self)

    def currenciesRate(self):
        """
        Client self
        :return CurrenciesRateResource:
        """
        return CurrenciesRateResource(self)

    def invoices(self):
        """
        Client self
        :return InvoicesResource:
        """
        return InvoicesResource(self)

    def orderItems(self):
        """
        Client self
        :return OrderItemsResource:
        """
        return OrderItemsResource(self)

    def deliveryProviders(self):
        """
        Client self
        :return DeliveryProvidersResource:
        """
        return DeliveryProvidersResource(self)

    def paymentMethods(self):
        """
        Client self
        :return PaymentMethodsResource:
        """
        return PaymentMethodsResource(self)

    def deliveryPayments(self):
        """
        Client self
        :return DeliveryPaymentsResource:
        """
        return DeliveryPaymentsResource(self)

    def paymentProviders(self):
        """
        Client self
        :return PaymentProvidersResource:
        """
        return PaymentProvidersResource(self)

    def vats(self):
        """
        Client self
        :return VatsResource:
        """
        return VatsResource(self)