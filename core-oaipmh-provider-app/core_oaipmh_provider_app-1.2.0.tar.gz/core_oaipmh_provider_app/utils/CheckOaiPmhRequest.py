"""
Check OAI-PMH request utils.

"""
import core_oaipmh_provider_app.commons.exceptions as oai_provider_exceptions
import re
from core_oaipmh_common_app.utils import UTCdatetime
from core_oaipmh_provider_app import settings


def check_bad_argument(oai_verb, data):
    """ Check OAI Error and Exception - Bad Argument in request.
    Args:
        oai_verb: Verb.
        data: Data.

    Raises:
        BadVerb:
        BadArgument:

    """
    if oai_verb is None:
        error_msg = 'The request did not provide any verb.'
        raise oai_provider_exceptions.BadVerb(error_msg)
    # Check if we have duplicate arguments
    duplicates = [arg for arg in data if len(data.getlist(arg)) > 1]
    if len(duplicates) > 0:
        error_msg = 'An argument ("multiple occurrences of %s") was passed that was not valid for ' \
                    'this verb' % ', '.join(duplicates)
        raise oai_provider_exceptions.BadArgument(error_msg)

    # Build the illegal and required arguments depending of the verb
    if oai_verb == 'Identify':
        legal = ['verb']
        required = ['verb']
    elif oai_verb == 'ListIdentifiers':
        if 'resumptionToken' in data:
            legal = ['verb', 'resumptionToken']
            required = ['verb']
        else:
            legal = ['verb', 'metadataPrefix', 'from', 'until', 'set']
            required = ['verb', 'metadataPrefix']
    elif oai_verb == 'ListSets':
        legal = ['verb', 'resumptionToken']
        required = ['verb']
    elif oai_verb == 'ListMetadataFormats':
        legal = ['verb', 'identifier']
        required = ['verb']
    elif oai_verb == 'ListRecords':
        if 'resumptionToken' in data:
            legal = ['verb', 'resumptionToken']
            required = ['verb']
        else:
            legal = ['verb', 'metadataPrefix', 'from', 'until', 'set']
            required = ['verb', 'metadataPrefix']
    elif oai_verb == 'GetRecord':
        legal = ['verb', 'identifier', 'metadataPrefix']
        required = ['verb', 'identifier', 'metadataPrefix']
    else:
        error_msg = 'The verb "%s" is illegal' % oai_verb
        raise oai_provider_exceptions.BadVerb(error_msg)

    # Check
    check_illegal_and_required(legal, required, data)


def check_illegal_and_required(legal, required, data):
    """ Check OAI Error and Exception - Illegal and required arguments
    Args:
        legal: Legal args.
        required: Required args.
        data: Data

    Raises:
        BadArgument:

    """
    errors = []
    # Check if a parameter doesn't have to be in the request
    illegal = [arg for arg in data if arg not in legal]
    # If yes, add error.
    if len(illegal) > 0:
        for arg in illegal:
            error = 'Arguments ("%s") was passed that was not valid for ' \
                        'this verb' % arg
            errors.append(oai_provider_exceptions.BadArgument(error))
    # Check if a parameter is missing for the request
    missing = [arg for arg in required if arg not in data]
    if len(missing) > 0:
        for arg in missing:
            error = 'Missing required argument - %s' % arg
            errors.append(oai_provider_exceptions.BadArgument(error))
    # Raise exception.
    if len(errors) > 0:
        raise oai_provider_exceptions.OAIExceptions(errors)


def check_identifier(identifier):
    """ Check if the identifier matches the pattern and return the record id.
    Args:
        identifier: Identifier to check.

    Returns:
        Record id.

    Raises:
        IdDoesNotExist:

    """
    # Check if the identifier pattern is OK.
    p = re.compile("%s:%s:id/(.*)" % (settings.OAI_SCHEME, settings.OAI_REPO_IDENTIFIER))
    id_matches = p.search(identifier)
    if id_matches:
        # If yes, we retrieve the record ID
        record_id = id_matches.group(1)
    else:
        raise oai_provider_exceptions.IdDoesNotExist(identifier)

    return record_id


def check_from(date):
    """ Check from date.
    Args:
        date:

    Returns:
        Date.

    Raises:
        BadArgument:

    """
    try:
        return _check_dates(date)
    except:
        error = 'Illegal date/time for "from" (%s)' % date
        raise oai_provider_exceptions.BadArgument(error)


def check_until(date):
    """ Check until date.
    Args:
        date:

    Returns:
        Date.

    Raises:
        BadArgument:

    """
    try:
        return _check_dates(date)
    except:
        error = 'Illegal date/time for "until" (%s)' % date
        raise oai_provider_exceptions.BadArgument(error)


def _check_dates(date):
    """ Check date in parameter.
    Args:
        date: Date.

    Returns:
        Date.

    Raises:
        Exception:

    """
    try:
        return UTCdatetime.utc_datetime_iso8601_to_datetime(date)
    except Exception as e:
        raise e
