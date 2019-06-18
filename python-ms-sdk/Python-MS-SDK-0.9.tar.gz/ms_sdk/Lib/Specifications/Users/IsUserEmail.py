from ms_sdk.Lib.Filters.FilterOperators import FilterOperators
from ms_sdk.Lib.Specifications.Basic.FilterSpecification import FilterSpecification
from ms_sdk.Lib.Specifications.Users.UserSpecification import UserSpecification


class IsUserEmail(FilterSpecification, UserSpecification):

    def __init__(self, email):
        self.email = email

    def asFilter(self):
        """
        :rtype dict:
        """
        return {'email': {FilterOperators.EQUAL : self.email}}

    def isSatisfiedBy(self, user):
        """
        :param User user:
        :rtype bool:
        """
        return self.email == self.email
