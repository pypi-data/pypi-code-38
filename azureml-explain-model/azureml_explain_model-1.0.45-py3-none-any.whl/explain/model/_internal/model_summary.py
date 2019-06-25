# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines a structure for gathering and storing the parts of an explanation asset."""


class ModelSummary():
    """A structure for gathering and storing the parts of an explanation asset."""
    def __init__(self):
        """Initializes data structures to hold summary information"""
        self.artifacts = []
        self.meta_dict = {}

    def add_from_get_model_summary(self, name, artifact_metadata_tuple):
        """
        Updates artifacts and metadata with new information
        :param artifact_metadata_tuple: the tuple of artifacts and metadata to add to existing
        :type artifact_metadata_tuple: (list[dict], dict)
        """
        self.artifacts += artifact_metadata_tuple[0]
        self.meta_dict[name] = artifact_metadata_tuple[1]

    def get_artifacts(self):
        """
        Gets the list of artifacts
        :rtype: list[list[dict]]
        """
        return self.artifacts

    def get_metadata_dictionary(self):
        """
        Gets the combined dictionary of metadata
        :rtype: dict
        """
        return self.meta_dict
