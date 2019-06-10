import logging
from dli.siren import siren_to_entity, siren_to_dict
from dli.client.exceptions import (
    CatalogueEntityNotFoundException,
    MissingMandatoryArgumentException
)
from dli.client.utils import ensure_count_is_valid, filter_out_unknown_keys, to_camel_cased_dict

logger = logging.getLogger(__name__)


class PackageFunctions:

    _KNOWN_FIELDS = {"name",
                     "description",
                     "keywords",
                     "topic",
                     "access",
                     "internalData",
                     "dataSensitivity",
                     "contractIds",
                     "termsAndConditions",
                     "derivedDataNotes",
                     "derivedDataRights",
                     "distributionNotes",
                     "distributionRights",
                     "internalUsageNotes",
                     "internalUsageRights",
                     "documentation",
                     "publisher",
                     "techDataOpsId",
                     "accessManagerId",
                     "managerId",
                     "collectionIds",
                     "intendedPurpose"}
    """
    A mixin providing common package operations
    """

    @property
    def __root(self):
        return self.ctx.memoized(
            self.get_root_siren().packages_root,
            "packages_root"
        )

    def get_package(self, id=None, name=None):
        """
        Fetches package metadata for an existing package.

        :param str id: The id of the package.
        :param str name: The name of the package.

        :returns: A package instance
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                # Look up by package id
                package = client.get_package('my_package_id') 
                # or
                package = client.get_package(id='my_package_id')

                # Alternatively look up by package name
                package = client.get_package(name='my_package')

        """
        if id is not None:
            return siren_to_entity(self._get_package(package_id=id))

        if name is not None:
            return siren_to_entity(self._get_package(name=name))

        raise ValueError("Either package id or name must be specified to look up package")

    def get_package_datasets(self, package_id, count=100):
        """
        Returns a list of all datasets registered under a package.

        :param str package_id: The id of the package.
        :param int count: Optional. Count of datasets to be returned. Defaults to 100.

        :returns: List of all datasets registered under the package.
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                datasets = client.get_package_datasets(
                    package_id,
                    count=100
                )
        """
        if not package_id:
            raise MissingMandatoryArgumentException('package_id')

        ensure_count_is_valid(count)

        package = self._get_package(package_id=package_id)

        datasets = package.get_datasets(
            page_size=count
        ).get_entities(rel="dataset")
        return [siren_to_entity(d) for d in datasets]

    def register_package(
        self,
        name,
        description,
        topic,
        access,
        internal_data,
        data_sensitivity,
        terms_and_conditions,
        publisher,
        access_manager_id,
        tech_data_ops_id,
        manager_id,
        keywords=None,
        contract_ids=None,
        derived_data_notes=None,
        derived_data_rights=None,
        distribution_notes=None,
        distribution_rights=None,
        internal_usage_notes=None,
        internal_usage_rights=None,
        documentation=None,
        collection_ids=None,
        intended_purpose=None
    ):
        """
        Submit a request to create a new package in the Data Catalogue.

        Packages are parent structures that contain metadata relating
        to a group of Datasets.

        See description for each parameter, and whether they are optional or mandatory.

        :param str name: A descriptive name of a package. It should be unique across the Data Catalogue.
        :param str description: A short description of a package.
        :param str topic: Topic the data in the package is about. Not applicable, if the package is not industry specific.
        :param str access: Accepted values are: `Restricted` or `Unrestricted`.
                            If access to the package is flagged as `Restricted`,
                            access manager_id will have to grant or deny access to the underlying data.
                            If access is flagged as `Unrestricted`, user will be able to gain
                            access instantaneously after submitting the access request form.
        :param str internal_data: Accepted values are: `Yes`, `No` or `Both`.
                            Package is marked as `Yes` if underlying data is created internally at IHS Markit, 
                            or `No` if externally, e.g. S&P, Russell, etc.
        :param str data_sensitivity: Accepted values are: `Private`, `Public` or `Top Secret`. Sensitivity level of the data contained within the package
        :param str terms_and_conditions: Not provided, empty or blank will result in ValueError.
                            Default T&C can be obtained through `get_default_package_terms_and_conditions` function.
        :param str publisher: Business unit or legal entity responsible for the content.
                              For example, S&P, Dow Jones, IHS Markit.
        :param str access_manager_id: Account ID for the Data Lake Account representing
                                      IHS Markit business unit that is responsible for managing access to the packages on Data Catalogue.
        :param str tech_data_ops_id: Account ID for the Data Lake Account representing
                                IHS Markit business unit that is responsible for uploading the data to Data Lake.
        :param str manager_id: Mandatory Account ID for the Data Lake Account representing
                            IHS Markit business unit that is responsible for creating and maintaining metadata for packages and datasets
                            on Data Catalogue.
        :param list[str] keywords: Optional. List of keywords that can be used to find this
                         package through the search interface.

        :param list[str] contract_ids: Optional. Internally, this will be the Salesforce contract ID and/or CARM ID. Externally, this could be any ID.
        :param str derived_data_notes: Optional. Provides details, comments on derived data.
                                   Extension to the Derived Data Rights field.
        :param str derived_data_rights: Optional. Accepted values are `Yes`, `No`, `With Limitations`, `N/A`.
                                    A flag to indicate whether we have rights to derived data.
        :param str distribution_notes: Optional. Provides details, comments on data distribution rights.
                                   Extension to the Distribution Rights field.
        :param str distribution_rights: Optional. Accepted values are `Yes`, `No`, `With Limitations`, `N/A`.
                                    A flag to indicate whether data can be distributed.
        :param str internal_usage_notes: Optional. Provides details, comments on internal data usage.
                                     Extension to Internal Usage Rights.
        :param str internal_usage_rights: Optional. Accepted values are: `Yes`, `No`, `With Limitations`, `N/A`.
                                      A flag to indicate whether data can be used internally.
        :param str documentation: Optional. Documentation about this package in markdown format.
        :param list[str] collection_ids: Optional. List of ids of collections attached to this package.
        :param str intended_purpose: Optional. Provides details about intended usage of the data contained 
                                     in the package, e.g. permanent storage, temporary storage, POC.
        :returns: Created package
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                package = client.register_package(
                    name="my package",
                    description="my package description",
                    topic="Automotive",
                    access="Restricted",
                    internal_data="Yes",
                    data_sensitivity="Public",
                    terms_and_conditions="Terms",
                    publisher="my publisher"
                )
        """

        self._validate_terms_and_conditions(terms_and_conditions)

        payload = {
            "name": name,
            "description": description,
            "keywords": keywords,
            "topic": topic,
            "access": access,
            "internalData": internal_data,
            "dataSensitivity": data_sensitivity,
            "contractIds": contract_ids,
            "termsAndConditions": terms_and_conditions,
            "derivedDataNotes": derived_data_notes,
            "derivedDataRights": derived_data_rights,
            "distributionNotes": distribution_notes,
            "distributionRights": distribution_rights,
            "internalUsageNotes": internal_usage_notes,
            "internalUsageRights": internal_usage_rights,
            "documentation": documentation,
            "publisher": publisher,
            "techDataOpsId": tech_data_ops_id,
            "accessManagerId": access_manager_id,
            "managerId": manager_id,
            "collectionIds": collection_ids,
            "intendedPurpose": intended_purpose
        }

        payload = {k: v for k, v in payload.items() if v is not None}
        return siren_to_entity(self.__root.create_package(__json=payload))

    def edit_package(
        self,
        package_id,
        **kwargs
    ):
        """
        Updates one or more fields in a package.
        If keyword argument is not specified field keeps its old value.
        Optional enum and text type fields can be unset by passing ``None``.

        :param str package_id: Package ID of the package being edited.

        Keyword arguments:

        :keyword str name: Optional. A descriptive name of a package. It should be unique across the Data Catalogue.
        :keyword str description: Optional. A short description of a package.
        :keyword str topic: Optional. Topic the data in the package is about. Not applicable, if the package is not industry specific.
        :keyword str access: Optional. Accepted values are: `Restricted` or `Unrestricted`.
                            If access to the package is flagged as `Restricted`,
                            access manager will have to grant or deny access to the underlying data.
                            If access is flagged as `Unrestricted`, user will be able to gain
                            access instantaneously after submitting the access request form.
        :keyword str internal_data: Optional. Accepted values are: `Yes`, `No` or `Both`.
                            Package is marked as `Yes` if underlying data is created internally at IHS Markit, 
                            or `No` if externally, e.g. S&P, Russell, etc.
        :keyword str data_sensitivity: Optional. Accepted values are: `Private`, `Public` or `Top Secret`. Sensitivity level of the data contained within the package
        :keyword str terms_and_conditions: Optional. Terms and conditions for the package. Default T&C can be obtained through `get_default_package_terms_and_conditions`
                                        function. None, empty or blank string will result in ValueError.
        :keyword str publisher: Optional. Business unit or legal entity responsible for the content.
                              For example, S&P, Dow Jones, IHS Markit.        
        :keyword list[str] keywords: Optional. List of keywords that can be used to find this
                         package through the search interface.
        :keyword str access_manager_id: Optional. Account ID for the Data Lake Account representing IHS Markit
                        business unit that is responsible for managing access
                        to the packages on Data Catalogue.
        :keyword str tech_data_ops_id: Optional. Account ID for the Data Lake Account representing
                          IHS Markit business unit that is responsible for uploading
                          the data to Data Lake.
        :keyword str manager_id: Optional. Account ID for the Data Lake Account representing IHS Markit
                        business unit that is responsible for creating and
                        maintaining metadata for packages and datasets on Data Catalogue.
        :keyword list[str] contract_ids: Optional. Internally, this will be the Salesforce contract ID and/or CARM ID. Externally, this could be any ID.
        :keyword str derived_data_notes: Optional. Provides details, comments on derived data.
                                   Extension to the Derived Data Rights field.
        :keyword str derived_data_rights: Optional. Accepted values are `Yes`, `No`, `With Limitations`, `N/A`.
                                    A flag to indicate whether we have rights to derived data.
        :keyword str distribution_notes: Optional. Provides details, comments on data distribution rights.
                                   Extension to the Distribution Rights field.
        :keyword str distribution_rights: Optional. Accepted values are `Yes`, `No`, `With Limitations`, `N/A`.
                                    A flag to indicate whether data can be distributed.
        :keyword str internal_usage_notes: Optional. Provides details, comments on internal data usage.
                                     Extension to Internal Usage Rights.
        :keyword str internal_usage_rights: Optional. Accepted values are: `Yes`, `No`, `With Limitations`, `N/A`.
                                      A flag to indicate whether data can be used internally.
        :keyword str documentation: Optional. Documentation about this package in markdown format.
        :keyword list[str] collection_ids: Optional. List of ids of collections attached to this package.
        :keyword str intended_purpose: Optional. Provides details about intended usage of the data contained
                                     in the package, e.g. permanent storage, temporary storage, POC.

        :returns: The updated Package.
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                package = client.edit_package(
                    package_id="my-package-id",
                    description="Updated my package description",
                )
        """
        if not package_id:
            raise MissingMandatoryArgumentException('package_id')

        fields = filter_out_unknown_keys(to_camel_cased_dict(kwargs), PackageFunctions._KNOWN_FIELDS)
        self._validate_fields(fields)

        package = self._get_package(package_id=package_id)
        # we can't just post back the siren object for some reason
        # as it can't be deserialised
        package_as_dict = siren_to_dict(package)

        # clean the package dict with fields that aren't known to us
        for key in list(package_as_dict.keys()):
            if key not in PackageFunctions._KNOWN_FIELDS:
                del package_as_dict[key]

        package_as_dict.update(fields)

        result = package.edit_package(__json=package_as_dict)
        return siren_to_entity(result)

    def delete_package(self, package_id):
        """
        Performs deletion of an existing package. This will delete all underlying datasets for the package as well.

        :param str package_id: The id of the package to be deleted.

        :returns: None

        - **Sample**

        .. code-block:: python

                client.delete_package(package_id)

        """
        if not package_id:
            raise MissingMandatoryArgumentException('package_id')

        package = self._get_package(package_id=package_id)
        if package:
            package.delete_package(package_id=package_id)

    @staticmethod
    def get_default_package_terms_and_conditions():
        """
        Returns a string representing the default Terms And Conditions for packages created in DataLake.

        :returns: The default DataLake Terms And Conditions
        :rtype: str
        """
        return ('By submitting this Data request and checking the "Accept Terms and Conditions" '
            'box, you acknowledge and agree to the following:\n'
            '\n'
            '* To promptly notify the relevant Access Manager/Producer of your intended use '
            'of the Data;\n'
            '* To obtain the terms and conditions relevant to such use for such Data from '
            'the Producer;\n'
            '* To distribute such terms and conditions to each member of your '
            'Consumer Group who may use the Data;\n'
            '* To use the Data solely for such intended use, subject to such terms and '
            'conditions;\n'
            '* To ensure that the Data is only accessed by members of your Consumer Group, '
            'and only used by such members for such intended use, subject to such terms and '
            'conditions;\n'
            '* To adhere to any additional requests of Producer with respect to the Data '
            '(including but not limited to ceasing use of the Data and deleting the Data, '
            'and ensuring other members of the Consumer Group do so, upon revocation of your '
            'license by Producer).\n'
            '\n'
            'Please refer to the <a href="/terms-of-use" target="_blank">EULA</a> for any '
            'defined terms used above. '
            'The <a href="/terms-of-use" target="_blank">EULA</a> '
            'is the document you agreed to adhere to by accessing the Lake.')

    #
    # Private functions
    #
    def _get_package(self, **kwargs):

        package = self.__root.get_package(**kwargs)

        if not package:
            raise CatalogueEntityNotFoundException('Package', params=kwargs)

        return package

    @staticmethod
    def _validate_fields(fields):
        if 'termsAndConditions' in fields:
            PackageFunctions._validate_terms_and_conditions(fields.get("termsAndConditions"))

    @staticmethod
    def _validate_terms_and_conditions(field):
        if not field or not field.strip():
            raise ValueError("Terms and conditions must be defined "
                             "and be non empty, non blank string")
