"""
Definitions of the GA4GH protocol types.
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import json
import inspect
import sys
import array
import base64

from _protocol_version import version  # noqa
from candig.common_pb2 import *  # noqa
from candig.metadata_pb2 import *  # noqa
from candig.metadata_service_pb2 import *  # noqa
from candig.read_service_pb2 import *  # noqa
from candig.reads_pb2 import *  # noqa
from candig.reference_service_pb2 import *  # noqa
from candig.references_pb2 import *  # noqa
from candig.variant_service_pb2 import *  # noqa
from candig.genotype_service_pb2 import *  # noqa
from candig.variants_pb2 import *  # noqa
from candig.allele_annotations_pb2 import *  # noqa
from candig.allele_annotation_service_pb2 import *  # noqa
from candig.sequence_annotations_pb2 import *  # noqa
from candig.sequence_annotation_service_pb2 import *  # noqa
from candig.bio_metadata_pb2 import *  # noqa
from candig.bio_metadata_service_pb2 import *  # noqa
from candig.genotype_phenotype_pb2 import *  # noqa
from candig.genotype_phenotype_service_pb2 import *  # noqa
from candig.rna_quantification_pb2 import *  # noqa
from candig.rna_quantification_service_pb2 import *  # noqa
from candig.peer_service_pb2 import *  # noqa

# METADATA
from candig.clinical_metadata_pb2 import *  # noqa
from candig.clinical_metadata_service_pb2 import *  # noqa
from candig.pipeline_metadata_pb2 import * # noqa
from candig.pipeline_metadata_service_pb2 import * # noqa

# SEARCH
from candig.search_service_pb2 import * # noqa

import candig.common_pb2 as common

import hacks.googhack as googhack

MIMETYPES = [
    "application/json",
    "application/protobuf",
    "application/x-protobuf",
    ]

# This is necessary because we have a package in the same directory as this
# file named 'google', so an 'import google' attempts to import that package
# instead of the top-level google package.
json_format = googhack.getJsonFormat()
message = googhack.getMessage()
struct_pb2 = googhack.getStructPb2()


def setAttribute(values, value):
    """
    Takes the values of an attribute value list and attempts to append
    attributes of the proper type, inferred from their Python type.
    """
    if isinstance(value, int):
        values.add().int32_value = value
    elif isinstance(value, float):
        values.add().double_value = value
    elif isinstance(value, long):
        values.add().int64_value = value
    elif isinstance(value, str):
        values.add().string_value = value
    elif isinstance(value, bool):
        values.add().bool_value = value
    elif isinstance(value, (list, tuple, array.array)):
        for v in value:
            setAttribute(values, v)
    elif isinstance(value, dict):
        for key in value:
            setAttribute(
                values.add().attributes.attr[key].values, value[key])
    else:
        values.add().string_value = str(value)


def deepGetAttr(obj, path):
    """
    Resolves a dot-delimited path on an object. If path is not found
    an `AttributeError` will be raised.
    """
    return reduce(getattr, path.split('.'), obj)


def deepSetAttr(obj, path, val):
    """
    Sets a deep attribute on an object by resolving a dot-delimited
    path. If path does not exist an `AttributeError` will be raised`.
    """
    first, _, rest = path.rpartition('.')
    return setattr(deepGetAttr(obj, first) if first else obj, rest, val)


def encodeValue(value):
    """
    TODO
    """
    if isinstance(value, (list, tuple)):
        return [common.AttributeValue(string_value=str(v)) for v in value]
    else:
        return [common.AttributeValue(string_value=str(value))]


def getValueListName(protocolResponseClass):
    """
    Returns the name of the attribute in the specified protocol class
    that is used to hold the values in a search response.
    """
    return protocolResponseClass.DESCRIPTOR.fields_by_number[1].name


def convertDatetime(t):
    """
    Converts the specified datetime object into its appropriate protocol
    value. This is the number of milliseconds from the epoch.
    """
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = t - epoch
    millis = delta.total_seconds() * 1000
    return int(millis)


def getValueFromValue(value):
    """
    Extract the currently set field from a Value structure
    """
    if type(value) != common.AttributeValue:
        raise TypeError(
            "Expected an AttributeValue, but got {}".format(type(value)))
    if value.WhichOneof("value") is None:
        raise AttributeError("Nothing set for {}".format(value))
    return getattr(value, value.WhichOneof("value"))


def toJson(protoObject, indent=None):
    """
    Serialises a protobuf object as json
    """
    # Using the internal method because this way we can reformat the JSON
    js = json_format.MessageToDict(protoObject, False)
    return json.dumps(js, indent=indent)


def toJsonDict(protoObject):
    """
    Converts a protobuf object to the raw attributes
    i.e. a key/value dictionary
    """
    return json.loads(toJson(protoObject))


def toProtobufString(protoObject):
    """
    Serialises a protobuf object as a base64-encoded protobuf string
    """
    # the base64-encoding shouldn't be necessary, but otherwise
    # currently the "string" with high-bit-set bytes gets helpfully
    # re-coded into corresponding unicode string in transit.
    # Should find and fix that rather than base64 encoding
    return base64.b64encode(protoObject.SerializeToString())


def serialize(protoObject, mimetype_name):
    if mimetype_name in ["application/protobuf", "application/x-protobuf"]:
        return toProtobufString(protoObject)
    else:
        return toJson(protoObject)


def fromJson(json, protoClass):
    """
    Deserialise json into an instance of protobuf class
    """
    return json_format.Parse(json, protoClass(), ignore_unknown_fields=True)


def fromProtobufString(protobuf_string, protoClass):
    """
    Deserialise base-64 encoded native protobuf string
    into an instance of protobuf class
    """
    msg = protoClass()
    msg.ParseFromString(base64.b64decode(protobuf_string))
    return msg


def deserialize(data, mimetype_name, protoClass):
    if mimetype_name in ["application/protobuf", "application/x-protobuf"]:
        return fromProtobufString(data, protoClass)
    else:
        return fromJson(data, protoClass)


def validate(json, protoClass):
    """
    Check that json represents data that could be used to make
    a given protobuf class
    """
    try:
        fromJson(json, protoClass)
        # The json conversion automatically validates
        return True
    except Exception:
        return False


def validateProtobufString(protobufstring, protoClass):
    """
    Check that json represents data that could be used to make
    a given protobuf class
    """
    try:
        fromProtobufString(protobufstring, protoClass)
        # The json conversion automatically validates
        return True
    except Exception:
        return False


def getProtocolClasses(superclass=message.Message):
    """
    Returns all the protocol classes that are subclasses of the
    specified superclass. Only 'leaf' classes are returned,
    corresponding directly to the classes defined in the protocol.
    """
    # We keep a manual list of the superclasses that we define here
    # so we can filter them out when we're getting the protocol
    # classes.
    superclasses = set([message.Message])
    thisModule = sys.modules[__name__]
    subclasses = []
    for name, class_ in inspect.getmembers(thisModule):
        if ((inspect.isclass(class_) and
                issubclass(class_, superclass) and
                class_ not in superclasses)):
            subclasses.append(class_)
    return subclasses


postMethods = [
    ('/callsets/search',
     SearchCallSetsRequest,  # noqa
     SearchCallSetsResponse),  # noqa
    ('/datasets/search',
     SearchDatasetsRequest,  # noqa
     SearchDatasetsResponse),  # noqa
    ('/readgroupsets/search',
     SearchReadGroupSetsRequest,  # noqa
     SearchReadGroupSetsResponse),  # noqa
    ('/reads/search',
     SearchReadsRequest,  # noqa
     SearchReadsResponse),  # noqa
    ('/references/search',
     SearchReferencesRequest,  # noqa
     SearchReferencesResponse),  # noqa
    ('/referencesets/search',
     SearchReferenceSetsRequest,  # noqa
     SearchReferenceSetsResponse),  # noqa
    ('/variants/search',
     SearchVariantsRequest,  # noqa
     SearchVariantsResponse),  # noqa
    ('/genotypes/search',
     SearchGenotypesRequest,  # noqa
     SearchGenotypesResponse),  # noqa
    ('/datasets/search',
     SearchDatasetsRequest,  # noqa
     SearchDatasetsResponse),  # noqa
    ('/biosamples/search',
     SearchBiosamplesRequest,  # noqa
     SearchBiosamplesResponse),  # noqa
    ('/experiments/search',
     SearchExperimentsRequest,  # noqa
     SearchExperimentsResponse),  # noqa
    ('/analyses/search',
     SearchAnalysesRequest,  # noqa
     SearchAnalysesResponse),  # noqa
    ('/callsets/search',
     SearchCallSetsRequest,  # noqa
     SearchCallSetsResponse),  # noqa
    ('/featuresets/search',
     SearchFeatureSetsRequest,  # noqa
     SearchFeatureSetsResponse),  # noqa
    ('/features/search',
     SearchFeaturesRequest,  # noqa
     SearchFeaturesResponse),  # noqa
    ('/continuoussets/search',
     SearchContinuousSetsRequest,  # noqa
     SearchContinuousSetsResponse),  # noqa
    ('/continuous/search',
     SearchContinuousRequest,  # noqa
     SearchContinuousResponse),  # noqa
    ('/variantsets/search',
     SearchVariantSetsRequest,  # noqa
     SearchVariantSetsResponse),  # noqa
    ('/variantannotations/search',
     SearchVariantAnnotationsRequest,  # noqa
     SearchVariantAnnotationSetsResponse),  # noqa
    ('/variantannotationsets/search',
     SearchVariantAnnotationSetsRequest,  # noqa
     SearchVariantAnnotationSetsResponse),  # noqa
    ('/rnaquantificationsets/search',
     SearchRnaQuantificationSetsRequest,  # noqa
     SearchRnaQuantificationSetsResponse),  # noqa
    ('/rnaquantifications/search',
     SearchRnaQuantificationsRequest,  # noqa
     SearchRnaQuantificationsResponse),  # noqa
    ('/expressionlevels/search',
     SearchExpressionLevelsRequest,  # noqa
     SearchExpressionLevelsResponse), # noqa
    ('/search',
     SearchQueryRequest,  # noqa
     SearchQueryResponse),  # noqa
    ]
