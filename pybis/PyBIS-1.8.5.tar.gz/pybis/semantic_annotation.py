from tabulate import tabulate
from .utils import VERBOSE

class SemanticAnnotation():
    """ Semantic annotation for sample types, property types or property type assignments.
    """

    def __init__(self, openbis_obj, isNew=True, **kwargs):
        self._openbis = openbis_obj
        self._isNew = isNew;
        
        self.permId = kwargs.get('permId')
        self.entityType = kwargs.get('entityType')
        self.propertyType = kwargs.get('propertyType')
        self.predicateOntologyId = kwargs.get('predicateOntologyId')
        self.predicateOntologyVersion = kwargs.get('predicateOntologyVersion')
        self.predicateAccessionId = kwargs.get('predicateAccessionId')
        self.descriptorOntologyId = kwargs.get('descriptorOntologyId')
        self.descriptorOntologyVersion = kwargs.get('descriptorOntologyVersion')
        self.descriptorAccessionId = kwargs.get('descriptorAccessionId')
        self.creationDate = kwargs.get('creationDate')

    def __dir__(self):
        return [
            'permId', 'entityType', 'propertyType', 
            'predicateOntologyId', 'predicateOntologyVersion', 
            'predicateAccessionId', 'descriptorOntologyId',
            'descriptorOntologyVersion', 'descriptorAccessionId', 
            'creationDate', 
            'save()', 'delete()' 
        ]

    def save(self):
        if self._isNew:
            self._create()
        else:
            self._update()
            
    def _create(self):
        
        creation = {
            "@type": "as.dto.semanticannotation.create.SemanticAnnotationCreation"
        }

        if self.entityType is not None and self.propertyType is not None:
            creation["propertyAssignmentId"] = {
                "@type": "as.dto.property.id.PropertyAssignmentPermId",
                "entityTypeId" : {
                    "@type": "as.dto.entitytype.id.EntityTypePermId",
                    "permId" : self.entityType,
                    "entityKind" : "SAMPLE"
                },
                "propertyTypeId" : {
                    "@type" : "as.dto.property.id.PropertyTypePermId",
                    "permId" : self.propertyType
                }
            }
        elif self.entityType is not None:
            creation["entityTypeId"] = {
                "@type": "as.dto.entitytype.id.EntityTypePermId",
                "permId" : self.entityType,
                "entityKind" : "SAMPLE"
            }
        elif self.propertyType is not None:
            creation["propertyTypeId"] = {
                "@type" : "as.dto.property.id.PropertyTypePermId",
                "permId" : self.propertyType
            }
            
        for attr in ['predicateOntologyId', 'predicateOntologyVersion', 'predicateAccessionId', 'descriptorOntologyId', 'descriptorOntologyVersion', 'descriptorAccessionId']:
            creation[attr] = getattr(self, attr)

        request = {
            "method": "createSemanticAnnotations",
            "params": [
                self._openbis.token,
                [creation]
            ]
        }
        
        response = self._openbis._post_request(self._openbis.as_v3, request)
        self._isNew = False
        self.permId = response[0]['permId']
        
        if VERBOSE: print("Semantic annotation successfully created.")
    
    def _update(self):
        
        update = {
            "@type": "as.dto.semanticannotation.update.SemanticAnnotationUpdate",
            "semanticAnnotationId" : {
                "@type" : "as.dto.semanticannotation.id.SemanticAnnotationPermId",
                "permId" : self.permId
            }
        }
        
        for attr in ['predicateOntologyId', 'predicateOntologyVersion', 'predicateAccessionId', 'descriptorOntologyId', 'descriptorOntologyVersion', 'descriptorAccessionId']:
            update[attr] = {
                "@type" : "as.dto.common.update.FieldUpdateValue",
                "isModified" : True,
                "value" : getattr(self, attr)
            }
            
        request = {
            "method": "updateSemanticAnnotations",
            "params": [
                self._openbis.token,
                [update]
            ]
        }
        
        self._openbis._post_request(self._openbis.as_v3, request)
        if VERBOSE: print("Semantic annotation successfully updated.")
    
    def delete(self, reason):
        self._openbis.delete_entity(entity='SemanticAnnotation', id=self.permId, reason=reason)
        if VERBOSE: print("Semantic annotation successfully deleted.")

    def _repr_html_(self):
        attrs = [ 'permId', 'entityType', 'propertyType', 'predicateOntologyId', 'predicateOntologyVersion', 'predicateAccessionId', 'descriptorOntologyId', 'descriptorOntologyVersion', 'descriptorAccessionId', 'creationDate',
        ]

        html = """
            <table border="1" class="dataframe">
            <thead>
                <tr style="text-align: right;">
                <th>attribute</th>
                <th>value</th>
                </tr>
            </thead>
            <tbody>
        """

        for attr in attrs:
            html += "<tr> <td>{}</td> <td>{}</td> </tr>".format(
                attr, getattr(self, attr, '')
            )

        html += """
            </tbody>
            </table>
        """
        return html
        

    def __repr__(self):
        headers = ['attribute', 'value']
        lines = []
        lines.append(['permId', self.permId])
        lines.append(['entityType', self.entityType])
        lines.append(['propertyType', self.propertyType])
        lines.append(['predicateOntologyId', self.predicateOntologyId])
        lines.append(['predicateOntologyVersion', self.predicateOntologyVersion])
        lines.append(['predicateAccessionId', self.predicateAccessionId])
        lines.append(['descriptorOntologyId', self.descriptorOntologyId])
        lines.append(['descriptorOntologyVersion', self.descriptorOntologyVersion])
        lines.append(['descriptorAccessionId', self.descriptorAccessionId])
        lines.append(['creationDate', self.creationDate])
        return tabulate(lines, headers=headers)
