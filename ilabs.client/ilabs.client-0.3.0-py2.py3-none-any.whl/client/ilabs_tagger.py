from __future__ import absolute_import, unicode_literals

import lxml.etree as et
from ilabs.client import ilabs_predictor

BRS_NS = "http://innodatalabs.com/brs"

BRS_B = et.QName(BRS_NS, 'b').text
BRS_R = et.QName(BRS_NS, 'r').text
BRS_S = et.QName(BRS_NS, 's').text


class ILabsTagger:
    '''
    Prediction client for all InnodataLabs dense sequence labeling domains.
    Hides the BRS XML format from the user.
    '''

    def __init__(self, *av, **kav):
        self.predictor = ilabs_predictor.ILabsPredictor.init(*av, **kav)

    def upload_feedback(self, filename, annotated_records):
        '''
        Sends feedback to the current domain folder.

        Input:
            * filename - file name.
            * annotated_records - list of annotated records to send. Same
                format as returned by "self.__call__" method.

        See {ilabs.client.ilabs_predictor.ILabsPredictor:feedback}
        '''

        brs_xml = build_brs_from_annotated_records(annotated_records)
        binary_data = et.tostring(brs_xml, xml_declaration=True, encoding='utf-8')
        return self.predictor.upload_feedback(filename, binary_data)

    def __call__(self, records, progress=None):
        '''
        Runs prediction on a collection of records.

        Input:
            * records - a list of strings. Note that empty strings should
                generally be avoided. Some domaind may not tolerate
                empty strings. Also note that very long strings can cause
                performance problems. Internally server would truncate
                unreasonably long strings and return tagging only for the
                first part, with confidence score of zero
            * progress - [optional] a function that takes a single string
                argument. It will be called to report back the progress of
                predictoion process. Can be used in UI to provide user with
                visual feedback

        Output:
            * list of annotations. This list has the same length as input
                "records" list. Each annotation is a list of tuples
                (text, label), where "text" is the labeled text, and "label"
                is the predicted label tagging this text. Concatenating
                "text" part of annotation elements should give the text of the
                input record. "label" values depend on the domain. label
                value of None is allowed and means that this text span is left
                untagged.
            * list of confidence scores. This list is parallel to the input
                "records" list and provides float values of confidence.
                Zero confidence means "not sure". Large positive confidence
                means "very confident".

        Example:

            annotations, confidence = tagger([
                'Princeton University, Princeton, NJ',
                'Department of Defense Office, 432 Honor Lane, Arlington, VA 2345'
            ])

            assert annotations == [
                [
                    ('Princeton University', 'organization'),
                    (', ', None),
                    ('Princeton', 'city'),
                    (', ', None),
                    ('NJ', 'state')
                ],
                [
                    ('Department of Defense Office', 'organization'),
                    (', ', None),
                    ('432 Honor Lane', 'address'),
                    (', ', None),
                    ('Arlington', 'city'),
                    (', ', None),
                    ('VA', 'state'),
                    (' ', None),
                    ('2345', 'state')
                ]
            ]

            assert confidence == [5.2, 0.4]
        '''
        if progress is None:
            progress = ilabs_predictor.noop

        brs_in = build_brs(records)
        progress('created XML file from %d records' % len(brs_in))

        binary_in = et.tostring(brs_in, xml_declaration=True, encoding='utf-8')
        binary_out = self.predictor(binary_in, progress=progress)

        brs_out = et.fromstring(binary_out)

        assert len(brs_in) == len(brs_out)

        predicted_tagging = [list(ann_from_record(r)) for r in brs_out]
        confidence = [float(r.get('c')) if r.get('c') is not None else 0. for r in brs_out]

        # validate that returned records have the same text
        for text, ann in zip(records, predicted_tagging):
            annotated_text = ''.join(txt for txt,_ in ann)
            if text != annotated_text:
                raise RuntimeError('internal prediction error: text changed %r vs %r' % (text, annotated_text))

        return predicted_tagging, confidence


def build_brs(records):
    '''
    Builds BRS file from list of strings. Each string becomes
    a record.
    '''
    b = et.Element(BRS_B, nsmap={'brs': BRS_NS})
    b.text = '\n'
    for text in records:
        r = et.SubElement(b, BRS_R)
        r.text = text
        r.tail = '\n'

    return b

def build_brs_from_annotated_records(annotated_records):
    b = et.Element(BRS_B, nsmap={'brs': BRS_NS})
    b.text = '\n'
    for ann in annotated_records:
        r = record_from_ann(ann)
        b.append(r)
        r.tail = '\n'

    return b

def ann_from_record(r):
    if r.text:
        yield r.text, None

    for c in r:
        if c.text:
            yield c.text, c.get('l')
        if c.tail:
            yield c.tail, None

def record_from_ann(ann, confidence=0.):

    r = et.Element(BRS_R)
    if confidence != 0:
        r.attrib['c'] = '%.2f' % confidence

    for text, label in ann:
        if label is not None:
            et.SubElement(r, BRS_S, {'l': label}).text = text
        elif len(r) == 0:
            r.text = (r.text or '') + text
        else:
            r[-1].tail = (r[-1].tail or '') + text

    return r
