from .property_assignment import PropertyAssignments
from .semantic_annotation import SemanticAnnotation

class SampleType(PropertyAssignments):
    """ Helper class for sample types, adding functionality.
    """

    def add_semantic_annotation(self, **kwargs):
        semantic_annotation = SemanticAnnotation(
            openbis_obj=self.openbis, isNew=True, 
            entityType=self.code, **kwargs
        )
        semantic_annotation.save()
        return semantic_annotation

    def get_semantic_annotations(self):
        return self.openbis.search_semantic_annotations(entityType=self.code)
