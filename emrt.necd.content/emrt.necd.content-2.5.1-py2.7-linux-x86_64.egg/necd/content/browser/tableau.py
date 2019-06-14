import os
import simplejson as json

from gzip import GzipFile
from datetime import datetime

from collections import defaultdict
from collections import Counter

from operator import itemgetter
from itertools import chain

from functools import partial

from zope.component.hooks import getSite
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from ZODB.blob import Blob

from Products.Five import BrowserView

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from emrt.necd.content.utils import jsonify
from emrt.necd.content.reviewfolder import QUESTION_WORKFLOW_MAP
from emrt.necd.content.reviewfolder import get_highlight_vocabs
from emrt.necd.content.reviewfolder import translate_highlights
from emrt.necd.content.reviewfolder import get_common


TOKEN_VIEW = os.environ.get("TABLEAU_TOKEN")
TOKEN_SNAP = os.environ.get("TABLEAU_TOKEN_SNAPSHOT")

HISTORICAL_ATTR_NAME = '__tableau_historical_store__'


GET_TIMESTAMP = itemgetter('Timestamp')


try:
    from flatten_json import flatten as do_flatten
except ImportError:
    def do_flatten(json_str):
        return json.dumps(list(chain(*json.loads(json_str))))


def entry_for_cmp(entry):
    """ Return entry data, without Timestamp.
        Suited for comparison.
    """
    return {
        k: v
        for k, v in entry.items()
        if k not in ['Timestamp', 'Modified']
    }


def should_append_entry(latest, entry):
    # If there is no earlier entry, append.
    should_append = True

    # If there is an earlier entry, compare it with
    # this one, append if different.
    if latest:
        cmp_latest = entry_for_cmp(latest)
        cmp_entry = entry_for_cmp(entry)
        if cmp_entry == cmp_latest:
            should_append = False

    return should_append


def update_history_with_snapshot(data, snapshot):
    # type: (str, list) -> dict
    updated = defaultdict(list)
    updated.update(json.loads(data))

    # We do this so that data format is consistent with the one stored
    # in the history (json). JSON deserializes ASCII encoded strings
    # as Unicode, resulting in the comparison of Unicode with ASCII encoded
    # string, which fails and data gets duplicated by should_append_entry.
    snapshot = json.loads(json.dumps(snapshot))

    for entry in snapshot:
        found = updated[entry['ID']]
        latest = found[-1] if found else None

        if should_append_entry(latest, entry):
            found.append(entry)

    return updated


def insert_snapshot(data, snapshot):
    # type: (str, list) -> str
    return json.dumps(update_history_with_snapshot(data, snapshot))


def flatten_historical_data(data):
    """ Return a list of Observation data items, sorted on
        timestamp, latest to oldest.
    """
    return sorted(
        chain.from_iterable(data.values()),
        key=GET_TIMESTAMP,
        reverse=True
    )


def reduce_count_brains(acc, b):
    acc[b.portal_type] += 1
    return acc


def get_qa(catalog, brain):
    path = brain.getPath()
    return catalog.unrestrictedSearchResults(
        portal_type=['Comment', 'CommentAnswer'],
        path=path
    )


def current_status(brain):
    status = brain['observation_status']
    return QUESTION_WORKFLOW_MAP.get(status, status)


def count_answers(len_q, len_a, obs_status):
    wf_is_msc = obs_status == QUESTION_WORKFLOW_MAP['MSC']
    answer_not_submitted = wf_is_msc and len_a and len_q == len_a

    return len_a - 1 if answer_not_submitted else len_a


def count_questions(len_q, len_a, obs_status):
    wf_is_se_or_lr = obs_status in [
        QUESTION_WORKFLOW_MAP['SE'],
        QUESTION_WORKFLOW_MAP['LR']
    ]
    question_not_submitted = wf_is_se_or_lr and len_q and len_q > len_a

    return len_q - 1 if question_not_submitted else len_q


def ipcc_sector(brain):
    return brain['get_ghg_source_sectors'][0]


def author_name(brain):
    return brain['get_author_name'].title()


def convert_flags(vocab, highlights):
    return ', '.join(get_common(highlights, vocab))


def extract_entry(qa, timestamp,
        vocab_description_flags, vocab_conclusion_flags,
        vocab_highlight, brain):
    b_id = brain['id']

    obs_status = brain['observation_status']

    len_a = qa['CommentAnswer'][b_id]
    len_q = qa['Comment'][b_id]

    highlights = translate_highlights(
        vocab_highlight, brain['get_highlight'] or [])

    return {
        'Current status': current_status(brain),
        'IPCC Sector': ipcc_sector(brain),
        'Review sector': brain['get_ghg_source_sectors'],
        'Author': author_name(brain),
        'Questions answered': count_answers(len_q, len_a, obs_status),
        'Questions asked': count_questions(len_q, len_a, obs_status),
        'Timestamp': timestamp,
        'Modified': brain['modified'].asdatetime().isoformat(),
        'Country': brain['country_value'],
        'ID': b_id,
        'URL': brain.getURL(),
        'Description flags': convert_flags(vocab_description_flags, highlights),
        'Conclusion flags': convert_flags(vocab_conclusion_flags, highlights),
        'Potential technical correction': bool(
            brain['observation_is_potential_technical_correction'])

    }


def validate_token(request, token=TOKEN_VIEW):
    return request.get('tableau_token') == token if token else False


def get_snapshot(context):
    catalog = getToolByName(context, 'portal_catalog')
    timestamp = datetime.now().isoformat()

    # Grab QA information. It's much faster to fetch the data
    # directly from the indexes than it is to query for it.
    idx_type = catalog._catalog.indexes['portal_type']._index
    idx_path = catalog._catalog.indexes['path']._unindex

    b_comment = idx_type['Comment']
    b_comment_answer = idx_type['CommentAnswer']

    p_comment = [idx_path[x] for x in b_comment]
    p_comment_answer = [idx_path[x] for x in b_comment_answer]

    qa = dict(
        Comment=Counter(p.split('/')[3] for p in p_comment),
        CommentAnswer=Counter(p.split('/')[3] for p in p_comment_answer),
    )


    vocab_description_flags, vocab_conclusion_flags, vocab_highlight = (
        get_highlight_vocabs(context)
    )

    entry = partial(extract_entry, qa, timestamp,
        vocab_description_flags, vocab_conclusion_flags, vocab_highlight)

    brains = catalog.unrestrictedSearchResults(
        portal_type=['Observation'],
        path='/'.join(context.getPhysicalPath())
    )

    return map(entry, brains)


def write_historical_data(context, content):
    target = context.aq_inner.aq_self

    # get and clear existing data
    blob = getattr(target, HISTORICAL_ATTR_NAME).open('r+')
    blob.seek(0)
    blob.truncate()

    # gzip
    gzip = GzipFile(fileobj=blob, mode='w')
    gzip.write(content)

    gzip.close()

    # get gzipped data
    blob.seek(0)
    compressed = blob.read()

    blob.close()

    # return the compressed and uncompressed sizes
    return len(compressed), len(content)


def get_historical_data(context):
    """ Returns the raw string, since json.load is much too slow. """
    target = context.aq_inner.aq_self

    # create empty Blob, if missing
    if not hasattr(target, HISTORICAL_ATTR_NAME):
        setattr(target, HISTORICAL_ATTR_NAME, Blob())
        write_historical_data(context, '{}')

    # gunzip data
    blob = getattr(target, HISTORICAL_ATTR_NAME).open('r')
    gzip = GzipFile(fileobj=blob, mode='r')

    data = gzip.read()

    gzip.close()
    blob.close()

    return data


class TableauView(BrowserView):
    def __call__(self):
        data = dict(status=401)
        request = self.request

        if validate_token(request):
            data = get_snapshot(self.context)
        else:
            request.RESPONSE.setStatus(401)

        return jsonify(request, data, sort_keys=False, indent=None)


class TableauHistoricalView(BrowserView):
    def __call__(self):
        data = dict(status=401)
        request = self.request

        if validate_token(request):
            context = self.context

            data = get_historical_data(context)
            snapshot = get_snapshot(context)
            data = flatten_historical_data(
                update_history_with_snapshot(data, snapshot))

        else:
            request.RESPONSE.setStatus(401)

        header = request.RESPONSE.setHeader
        header("Content-Type", "application/json")
        header("Surrogate-control", "no-store")

        return json.dumps(data)


class TableauCreateSnapshotView(BrowserView):
    def __call__(self):
        data = dict(status=401)
        request = self.request

        if validate_token(request, TOKEN_SNAP):
            context = self.context
            historical = get_historical_data(context)
            historical = insert_snapshot(historical, get_snapshot(context))
            compressed, content = write_historical_data(
                context, historical)
            data['size'] = compressed
            data['deflated'] = content
            data['status'] = 200
        else:
            request.RESPONSE.setStatus(401)

        return jsonify(request, data, sort_keys=False, indent=None)


class ConnectorView(BrowserView):

    index = ViewPageTemplateFile('./templates/tableau_connector.pt')

    def __call__(self):
        request = self.request

        # Make sure the response doesn't get cached in proxies.
        request.RESPONSE.setHeader('Surrogate-control', 'no-store')

        if validate_token(request):
            return self.index(
                portal_url=getSite().absolute_url(),
            )

        request.RESPONSE.setStatus(401)
