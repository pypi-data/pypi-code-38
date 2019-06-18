from ms_sdk.Lib.Filters.FilterOperators import FilterOperators
from ms_sdk.Lib.Specifications.Basic.FilterSpecification import FilterSpecification
from ms_sdk.Lib.Specifications.Users.UserSpecification import UserSpecification


class IsUserSubscriber(FilterSpecification, UserSpecification):

    def asFilter(self):
        """
        :rtype dict:
        """
        return {'isSubscriber': {FilterOperators.EQUAL: 1 }}

    def isSatisfiedBy(self, user):
        """
        :param User user:
        :rtype bool:
        """
        return user.id and user.isSubscriber