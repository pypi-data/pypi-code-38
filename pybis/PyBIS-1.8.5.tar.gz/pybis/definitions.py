def openbis_definitions(entity):
    """
    attrs_new: Attributes, that can appear when creating new entities
    attrs_up: Attributes that can be updated
    attrs: Attributes that are displayed when fetched
    multi: multivalue-elements which appear in an entity. E.g. parents or children in a Sample.
    identifier: to update entities, the identifier must be specified. Usually identityName + "Id"
    (Entity-Name in camel-case, starting with lowercase letter, with Id added)
    """
    entities = {
        "Space": {
            "attrs_new": "code description".split(),
            "attrs_up": "description".split(),
            "attrs": "code permId description registrator registrationDate modifier modificationDate".split(),
            "multi": "".split(),
            "identifier": "spaceId",
            "create": { "@type": "as.dto.space.create.SpaceCreation"},
            "update": { "@type": "as.dto.space.upate.SpaceUpdate"},
            "delete": { "@type": "as.dto.space.delete.SpaceDeletionOptions"},
            "fetch":  { "@type": "as.dto.space.fetchoptions.SpaceFetchOptions"},
        },
        "Project": {
            "attrs_new": "code description space attachments".split(),
            "attrs_up": "description space attachments".split(),
            "attrs": "code description permId identifier space leader registrator registrationDate modifier modificationDate attachments".split(),
            "multi": "".split(),
            "identifier": "projectId",
            "create": { "@type": "as.dto.project.create.ProjectCreation"},
            "update": { "@type": "as.dto.project.upate.ProjectUpdate"},
        },
        "Experiment": {
            "attrs_new": "code type project tags attachments".split(),
            "attrs_up": "project tags attachments".split(),
            "attrs": "code permId identifier type project tags registrator registrationDate modifier modificationDate attachments".split(),
            "multi": "tags attachments".split(),
            "identifier": "experimentId",
            "create": { "@type": "as.dto.experiment.create.ExperimentCreation"},
            "update": { "@type": "as.dto.experiment.upate.ExperimentUpdate"},
        },
        "Sample": {
            "attrs_new": "code type project parents children container components space experiment tags attachments".split(),
            "attrs_up": "project parents children container components space experiment tags attachments".split(),
            "attrs": "code permId identifier type project parents children components space experiment tags registrator registrationDate modifier modificationDate attachments container".split(),
            "ids2type": {
                'parentIds': {'permId': {'@type': 'as.dto.sample.id.SamplePermId'}},
                'childIds': {'permId': {'@type': 'as.dto.sample.id.SamplePermId'}},
                'componentIds': {'permId': {'@type': 'as.dto.sample.id.SamplePermId'}},
            },
            "identifier": "sampleId",
            "create": { "@type": "as.dto.sample.create.SampleCreation"},
            "update": { "@type": "as.dto.sample.upate.SampleUpdate"},
            "cre_type": "as.dto.sample.create.SampleCreation",
            "multi": "parents children components tags attachments".split(),
        },
        "SemanticAnnotation": {
            "attrs_new": "permId entityType propertyType predicateOntologyId predicateOntologyVersion predicateAccessionId descriptorOntologyId descriptorOntologyVersion descriptorAccessionId".split(),
            "attrs_up": "entityType propertyType predicateOntologyId predicateOntologyVersion predicateAccessionId descriptorOntologyId descriptorOntologyVersion descriptorAccessionId ".split(),
            "attrs": "permId entityType propertyType predicateOntologyId predicateOntologyVersion predicateAccessionId descriptorOntologyId descriptorOntologyVersion descriptorAccessionId creationDate".split(),
            "ids2type": {
                "propertyTypeId": { 
                    "permId": "as.dto.property.id.PropertyTypePermId"
                },
                "entityTypeId": { 
                    "permId": "as.dto.entity.id.EntityTypePermId"
                },
            },
            "identifier": "permId",
            "cre_type": "as.dto.sample.create.SampleCreation",
            "multi": "parents children components tags attachments".split(),
        },
        "DataSet": {
            "attrs_new": "type code kind experiment sample parents children components containers tags".split(),
            "attrs_up": "parents children experiment sample components containers tags".split(),
            "attrs": "code permId type kind experiment sample parents children components containers tags accessDate dataProducer dataProductionDate registrator registrationDate modifier modificationDate dataStore size measured".split(),

            "ids2type": {
                'parentIds': {'permId': {'@type': 'as.dto.dataset.id.DataSetPermId'}},
                'childIds': {'permId': {'@type': 'as.dto.dataset.id.DataSetPermId'}},
                'componentIds': {'permId': {'@type': 'as.dto.dataset.id.DataSetPermId'}},
                'containerIds': {'permId': {'@type': 'as.dto.dataset.id.DataSetPermId'}},
            },
            "multi": "parents children containers components".split(),
            "identifier": "dataSetId",
        },
        "Material": {
            "attrs_new": "code description type creation tags".split(),
            "attrs_up": "description type creation tags".split(),
            "attrs": "code description type creation registrator registrationDate modifier modificationDate tags".split(),
            "multi": "".split(),
            "identifier": "materialId",
        },
        "Tag": {
            "attrs_new": "code description".split(),
            "attrs_up": "description".split(),
            "attrs": "permId code description registrationDate".split(),
            "multi": "".split(),
            "identifier": "tagId",
        },
        "Vocabulary": {
            "attrs_new": "code description managedInternally internalNameSpace chosenFromList urlTemplate".split(),
            "attrs_up": "description managedInternally internalNameSpace chosenFromList urlTemplate".split(),
            "attrs": "code description managedInternally internalNameSpace chosenFromList urlTemplate registrator registrationDate modifier modificationDate".split(),
            "multi": "".split(),
            "identifier": "vocabularyId",
            "search": { "@type": "as.dto.vocabulary.search.VocabularySearchCriteria" },
            "create": { "@type": "as.dto.vocabulary.create.VocabularyCreation"}, 
            "update": { "@type": "as.dto.vocabulary.upate.VocabularyUpdate"},
            "delete": { "@type": "as.dto.vocabulary.delete.VocabularyDeletionOptions"},
            "fetch":  { "@type": "as.dto.vocabulary.fetchoptions.VocabularyFetchOptions"},
        },
        "VocabularyTerm": {
            "attrs_new": "code vocabularyCode label description official ordinal".split(),
            "attrs_up": "label description official previousTermId".split(),
            "attrs": "code vocabularyCode label description official ordinal registrator registrationDate modifier modificationDate".split(),
            "multi": "".split(),
            "identifier": "vocabularyTermId",
            "create": { "@type": "as.dto.vocabulary.create.VocabularyTermCreation"},
            "update": { "@type": "as.dto.vocabulary.upate.VocabularyTermUpdate"},
            "delete": { "@type": "as.dto.vocabulary.delete.VocabularyTermDeletionOptions"},
            "fetch":  { "@type": "as.dto.vocabulary.fetchoptions.VocabularyTermFetchOptions"},
        },
        "Plugin": {
            "attrs_new": "name description available script available script pluginType pluginKind entityKinds".split(),
            "attrs_up": "description, available script available script pluginType pluginKind entityKinds".split(),
            "attrs": "permId name description registrator registrationDate available script pluginType pluginKind entityKinds".split(),
            "multi": "".split(),
            "identifier": "pluginId",
        },
        "Person": {
            "attrs_new": "userId space".split(),
            "attrs_up": "space".split(),
            "attrs": "permId userId firstName lastName email space registrationDate ".split(),
            "multi": "".split(),
            "identifier": "userId",
        },
        "AuthorizationGroup" : {
            "attrs_new": "code description userIds".split(),
            "attrs_up": "code description userIds".split(),
            "attrs": "permId code description registrator registrationDate modificationDate users".split(),
            "multi": "users".split(),
            "identifier": "groupId",
        },
        "RoleAssignment" : {
            "attrs": "id user authorizationGroup role roleLevel space project registrator registrationDate".split(),
            "attrs_new": "role roleLevel user authorizationGroup role space project".split(),
            "attrs_up": "role roleLevel user authorizationGroup role space project".split(),
        },
        "attr2ids": {
            "space": "spaceId",
            "project": "projectId",
            "sample": "sampleId",
            "samples": "sampleIds",
            "dataSet": "dataSetId",
            "dataSets": "dataSetIds",
            "experiment": "experimentId",
            "experiments": "experimentIds",
            "material": "materialId",
            "materials": "materialIds",
            "container": "containerId",
            "containers": "containerIds",
            "component": "componentId",
            "components": "componentIds",
            "parents": "parentIds",
            "children": "childIds",
            "tags": "tagIds",
            "userId": "userId",
            "users": "userIds",
            "description": "description",
            "vocabulary": "vocabularyId",
        },
        "ids2type": {
            'spaceId': {'permId': {'@type': 'as.dto.space.id.SpacePermId'}},
            'projectId': {'permId': {'@type': 'as.dto.project.id.ProjectPermId'}},
            'experimentId': {'permId': {'@type': 'as.dto.experiment.id.ExperimentPermId'}},
            'tagIds': {'code': {'@type': 'as.dto.tag.id.TagCode'}},
        },
    }
    return entities[entity]

get_definition_for_entity = openbis_definitions   # Alias


fetch_option = {
    "space": {"@type": "as.dto.space.fetchoptions.SpaceFetchOptions"},
    "project": {"@type": "as.dto.project.fetchoptions.ProjectFetchOptions"},
    "person": {"@type": "as.dto.person.fetchoptions.PersonFetchOptions"},
    "users": {"@type": "as.dto.person.fetchoptions.PersonFetchOptions" },
    "user": {"@type": "as.dto.person.fetchoptions.PersonFetchOptions" },
    "owner": {"@type": "as.dto.person.fetchoptions.PersonFetchOptions" },
    "registrator": {"@type": "as.dto.person.fetchoptions.PersonFetchOptions"},
    "modifier": {"@type": "as.dto.person.fetchoptions.PersonFetchOptions"},
    "leader": {"@type": "as.dto.person.fetchoptions.PersonFetchOptions"},
    "authorizationGroup": {"@type": "as.dto.authorizationgroup.fetchoptions.AuthorizationGroupFetchOptions"},
    "experiment": {
        "@type": "as.dto.experiment.fetchoptions.ExperimentFetchOptions",
        "type": {"@type": "as.dto.experiment.fetchoptions.ExperimentTypeFetchOptions"}
    },
    "sample": {
        "@type": "as.dto.sample.fetchoptions.SampleFetchOptions",
        "type": {"@type": "as.dto.sample.fetchoptions.SampleTypeFetchOptions"}
    },
    "samples": {"@type": "as.dto.sample.fetchoptions.SampleFetchOptions"},
    "dataSet": {
        "@type": "as.dto.dataset.fetchoptions.DataSetFetchOptions",
        "type":       {"@type": "as.dto.dataset.fetchoptions.DataSetTypeFetchOptions"},
        "parents":    {"@type": "as.dto.dataset.fetchoptions.DataSetFetchOptions"},
        "children":   {"@type": "as.dto.dataset.fetchoptions.DataSetFetchOptions"},
        "containers": {"@type": "as.dto.dataset.fetchoptions.DataSetFetchOptions"},
        "components": {"@type": "as.dto.dataset.fetchoptions.DataSetFetchOptions"},
    },
    "dataSets": {
        "@type": "as.dto.dataset.fetchoptions.DataSetFetchOptions",
        "properties": {"@type": "as.dto.property.fetchoptions.PropertyFetchOptions"},
        "type": {"@type": "as.dto.dataset.fetchoptions.DataSetTypeFetchOptions"},
    },
    "physicalData": {"@type": "as.dto.dataset.fetchoptions.PhysicalDataFetchOptions"},
    "linkedData": {
        "externalDms": {"@type": "as.dto.externaldms.fetchoptions.ExternalDmsFetchOptions"},
        "@type": "as.dto.dataset.fetchoptions.LinkedDataFetchOptions"
    },
    "roleAssignments": {
        "@type": "as.dto.roleassignment.fetchoptions.RoleAssignmentFetchOptions",
    },
    "properties": {"@type": "as.dto.property.fetchoptions.PropertyFetchOptions"},
    "propertyAssignments": {
        "@type": "as.dto.property.fetchoptions.PropertyAssignmentFetchOptions",
        "propertyType": {
            "@type": "as.dto.property.fetchoptions.PropertyTypeFetchOptions",
            "vocabulary": {
                "@type": "as.dto.vocabulary.fetchoptions.VocabularyFetchOptions",
            }
        }
    },
    "tags": {"@type": "as.dto.tag.fetchoptions.TagFetchOptions"},
    "tag": {"@type": "as.dto.tag.fetchoptions.TagFetchOptions"},
    "attachments": {"@type": "as.dto.attachment.fetchoptions.AttachmentFetchOptions"},
    "attachmentsWithContent": {
        "@type": "as.dto.attachment.fetchoptions.AttachmentFetchOptions",
        "content": {
            "@type": "as.dto.common.fetchoptions.EmptyFetchOptions"
        },
    },
    "script": {
        "@type": "as.dto.common.fetchoptions.EmptyFetchOptions",
    },
    "history": {"@type": "as.dto.history.fetchoptions.HistoryEntryFetchOptions"},
    "dataStore": {"@type": "as.dto.datastore.fetchoptions.DataStoreFetchOptions"},
    "plugin": {"@type": "as.dto.plugin.fetchoptions.PluginFetchOptions"},
    "vocabulary": {
        "@type": "as.dto.vocabulary.fetchoptions.VocabularyFetchOptions",
        "terms": {
            "@type": "as.dto.vocabulary.fetchoptions.VocabularyTermFetchOptions"
        },
    },
    "vocabularyTerm": {"@type": "as.dto.vocabulary.fetchoptions.VocabularyTermFetchOptions"},
    "deletedObjects": { "@type": "as.dto.deletion.fetchoptions.DeletedObjectFetchOptions" },
    "deletion": { "@type": "as.dto.deletion.fetchoptions.DeletionFetchOptions" },
}

def get_fetchoption_for_entity(entity):
    entity = entity[0].lower() + entity[1:]   # make first character lowercase
    try:
        return fetch_option[entity]
    except KeyError as e:
        return {}

def get_type_for_entity(entity, action):
    if action not in "create update delete fetch".split():
        raise ValueError('unknown action: {}'.format(action))

    definition = openbis_definitions(entity)
    return definition[action]

def get_method_for_entity(entity, action):
    if action == "Vocabulary":
        return "{}Vocabularies".format(action)

    return "{}{}s".format(action, entity)
