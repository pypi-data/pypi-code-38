"""Google Label Manager API."""

import re

from bits.google.services.base import Base
from googleapiclient.discovery import build


class LabelManager(Base):
    """LabelManager class."""

    def __init__(self, credentials, api_key):
        """Initialize a class instance."""
        self.labelmanager = build(
            'labelmanager',
            'v1alpha1',
            credentials=credentials,
            discoveryServiceUrl='https://labelmanager.googleapis.com/$discovery/rest?version=v1alpha1&key=%s' % (api_key),
        )

    def get_label_dictionary(self, resource):
        """Get label dictioanry."""
        name = '%s/labelDictionary' % (resource)
        if re.match('organizations/', resource):
            return self.labelmanager.organizations().getLabelDictionary(name=name).execute()
        elif re.match('folders/', resource):
            return self.labelmanager.folders().getLabelDictionary(name=name).execute()
        elif re.match('projects/', resource):
            return self.labelmanager.projects().getLabelDictionary(name=name).execute()

    def lookup_effective_label_dictionary(self, resource):
        """Lookup effective label dictionary."""
        if re.match('organizations/', resource):
            return self.labelmanager.organizations().lookupEffectiveLabelDictionary(resource=resource).execute()
        elif re.match('folders/', resource):
            return self.labelmanager.folders().lookupEffectiveLabelDictionary(resource=resource).execute()
        elif re.match('projects/', resource):
            return self.labelmanager.projects().lookupEffectiveLabelDictionary(resource=resource).execute()

    def update_label_dictionary(self, resource, body):
        """Update label dictionary."""
        params = {
            'name': '%s/labelDictionary' % (resource),
            'body': body,
        }
        if re.match('organizations/', resource):
            return self.labelmanager.organizations().updateLabelDictionary(**params).execute()
        elif re.match('folders/', resource):
            return self.labelmanager.folders().updateLabelDictionary(**params).execute()
        elif re.match('projects/', resource):
            return self.labelmanager.projects().updateLabelDictionary(**params).execute()
