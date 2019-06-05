import logging

from scrapy.item import Field, Item

logger = logging.getLogger(__name__)


class DatasetSearchItem(Item):
    """
    A single response from the esgf-search JSON endpoint
    """

    def __init__(self, *args, **kwargs):
        self._values = {}
        if args or kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                try:
                    self[k] = v
                except KeyError:
                    logger.debug("Ignoring DatasetSearch parameter: {}".format(k))

    _id = Field()
    _timestamp = Field()
    _version_ = Field()
    access = Field()
    activity_drs = Field()
    activity_id = Field()
    branch_method = Field()
    cf_standard_name = Field()
    citation_url = Field()
    data_node = Field()
    data_specs_version = Field()
    dataset_id_template_ = Field()
    datetime_start = Field()
    datetime_stop = Field()
    experiment_id = Field()
    frequency = Field()
    further_info_url = Field()
    geo = Field()
    geo_units = Field()
    id = Field()
    index_node = Field()
    instance_id = Field(dblite="UNIQUE")
    institution_id = Field()
    latest = Field()
    master_id = Field()
    member_id = Field()
    mip_era = Field()
    nominal_resolution = Field()
    number_of_aggregations = Field()
    number_of_files = Field()
    pid = Field()
    product = Field()
    project = Field()
    realm = Field()
    retracted = Field()
    size = Field()
    source_id = Field()
    source_type = Field()
    sub_experiment_id = Field()
    table_id = Field()
    title = Field()
    type = Field()
    url = Field()
    variable = Field()
    variable_id = Field()
    variable_long_name = Field()
    variable_units = Field()
    variant_label = Field()
    version = Field()
    downloaded_at = Field()
    verified_at = Field()


class DatasetDetailItem(Item):
    instance_id = Field()
    host = Field()
    files = Field()  # Array of ESGFFileItem's
    output_dir = Field()


class ESGFFileItem(Item):
    url = Field()
    checksum = Field()
    checksum_type = Field()
    size = Field()
    filename = Field()
