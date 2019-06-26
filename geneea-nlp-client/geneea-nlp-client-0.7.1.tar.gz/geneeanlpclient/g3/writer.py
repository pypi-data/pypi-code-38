# Copyright 2019 Geneea Analytics s.r.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Writes the G3 model to a json-based dictionary as returned by Geneea G3 API.
#
# Except the toDict function, all functions and classes defined in this file are only internal helpers.

from typing import Dict

from geneeanlpclient.common.dictutil import JsonType, DictBuilder
from geneeanlpclient.g3.model import G3, Relation, Paragraph, Entity, Tag, Token, TectoToken, Sentence, Sentiment


def toDict(obj: G3) -> JsonType:
    """
    Writes the G3 model to a json-based dictionary to a format as returned by Geneea G3 API.
    """
    raw = {'version': obj.apiVersion}

    if obj.docId:
        raw['id'] = obj.docId
    if obj.language:
        raw['language'] = {'detected': obj.language.detected}
    if obj.paragraphs:
        raw['paragraphs'] = [_toRawPara(p) for p in obj.paragraphs]
    if obj.entities:
        raw['entities'] = [_toRawEntity(x) for x in obj.entities]
    if obj.tags:
        raw['tags'] = [_toRawTag(x) for x in obj.tags]
    if obj.relations:
        raw['relations'] = [_toRawRelation(x) for x in obj.relations]
    if obj.docSentiment:
        raw['docSentiment'] = _toRawSentiment(obj.docSentiment)

    itemSentiments = _toRawItemSentiment(obj)
    if itemSentiments:
        raw['itemSentiments'] = itemSentiments

    if obj.usedChars is not None:
        raw['usedChars'] = obj.usedChars

    if obj.debugInfo:
        raw['debugInfo'] = obj.debugInfo
    if obj.metadata:
        for k, v in obj.metadata.items():
            if k in raw:
                raise ValueError(f'Metadata conflict: "{k}" is already present in the output dictionary')
            raw[k] = v

    return raw


def _toRawMention(mention: Entity.Mention) -> JsonType:
    builder = DictBuilder({
        'id': mention.id,
        'mwl': mention.mwl,
        'text': mention.text,
        'tokenIds': [t.id for t in mention.tokenSupport.tokens]
    })
    builder.addIfNotNone('feats', mention.feats)
    return builder.build()


def _toRawEntity(entity: Entity) -> JsonType:
    builder = DictBuilder({
        'id': entity.id,
        'stdForm': entity.stdForm,
        'type': entity.type
    })

    builder.addIfNotNone('gkbId', entity.gkbId)
    builder.addIfNotNone('feats', entity.feats)
    if entity.mentions:
        builder['mentions'] = [_toRawMention(m) for m in entity.mentions]

    return builder.build()


def _toRawTagMention(mention: Tag.Mention) -> JsonType:
    builder = DictBuilder({
        'id': mention.id,
        'tokenIds': [t.id for t in mention.tokenSupport.tokens]
    })
    builder.addIfNotNone('feats', mention.feats)
    return builder.build()


def _toRawTag(tag: Tag) -> JsonType:
    builder = DictBuilder({
        'id': tag.id,
        'stdForm': tag.stdForm,
        'type': tag.type,
        'relevance': tag.relevance
    })

    builder.addIfNotNone('gkbId', tag.gkbId)
    builder.addIfNotNone('feats', tag.feats)
    builder.addIfNotNone('mentions', [_toRawTagMention(m) for m in tag.mentions])

    return builder.build()


def _toRawArg(arg: Relation.Argument) -> JsonType:
    builder = DictBuilder({
        "type": arg.type,
        "name": arg.name,
    })

    builder.addId("entityId", arg.entity)
    return builder.build()


def _toRawRelationSupport(support: Relation.Support) -> JsonType:
    builder = DictBuilder({})

    builder.addId('tectoId', support.tectoToken)

    if support.tokenSupport:
        builder.addIds('tokenIds', support.tokenSupport.tokens)

    return builder.build()


def _toRawRelation(relation: Relation) -> JsonType:
    builder = DictBuilder({
        'id': relation.id,
        'name': relation.name,
        'textRepr': relation.textRepr,
        'type': relation.type,
        'args': [_toRawArg(a) for a in relation.args],
    })
    builder.addIfNotNone('feats', relation.feats)
    builder.addIfNotNone('support', [_toRawRelationSupport(s) for s in relation.support])

    return builder.build()


def _toRawSentiment(sentiment: Sentiment) -> JsonType:
    return {
        'mean': sentiment.mean,
        'label': sentiment.label,
        'positive': sentiment.positive,
        'negative': sentiment.negative
    }


def _toRawToken(t: Token) -> JsonType:
    builder = DictBuilder({
        'id': t.id,
        'off': t.charSpan.start,
        'text': t.text,
        'corrOff': t.corrCharSpan.start,
        'corrText': t.corrText
    })
    builder.addIfNotNone('dLemma', t.deepLemma)
    builder.addIfNotNone('mTag', t.morphTag)
    builder.addIfNotNone('lemma', t.lemma)
    builder.addId('parId', t.parent)
    builder.addIfNotNone('feats', t.feats)

    if t.pos:
        builder.addIfNotNone('pos', t.pos.toStr())
    if t.fnc:
        builder['fnc'] = t.fnc.name.lower()

    return builder.build()


def _toRawTectoToken(tt: TectoToken) -> JsonType:
    builder = DictBuilder({
        'id': tt.id,
        'tokenIds': [value.id for value in tt.tokenSupport] if tt.tokenSupport else []
    })
    builder.addIfNotNone('lemma', tt.lemma)
    builder.addIfNotNone('feats', tt.feats)
    if tt.fnc:
        builder['fnc'] = tt.fnc.lower()
    builder.addId('parId', tt.parent)
    builder.addId('entityMentionId', tt.entityMention)

    return builder.build()


def _toRawSentence(s: Sentence) -> JsonType:
    raw = {
        'id': s.id,
        'tokens': [_toRawToken(t) for t in s.tokens],
    }

    if s.tectoTokens:
        raw['tecto'] = [_toRawTectoToken(tt) for tt in s.tectoTokens]

    return raw


def _toRawPara(para: Paragraph) -> JsonType:
    raw = {
        'id': para.id,
        'type': para.type,
        'text': para.text,
        'corrText': para.corrText,
        'sentences': [_toRawSentence(s) for s in para.sentences]
    }

    return raw


def _toRawItemSentiment(obj: G3) -> Dict[str, JsonType]:
    id2sentiment = {}

    for s in obj.sentences:
        if s.sentiment:
            id2sentiment[s.id] = _toRawSentiment(s.sentiment)

    for e in obj.entities:
        if e.sentiment:
            id2sentiment[e.id] = _toRawSentiment(e.sentiment)
        for m in e.mentions:
            if m.sentiment:
                id2sentiment[m.id] = _toRawSentiment(m.sentiment)

    for t in obj.tags:
        if t.sentiment:
            id2sentiment[t.id] = _toRawSentiment(t.sentiment)
        for m in t.mentions:
            if m.sentiment:
                id2sentiment[m.id] = _toRawSentiment(m.sentiment)

    for r in obj.relations:
        if r.sentiment:
            id2sentiment[r.id] = _toRawSentiment(r.sentiment)

    return id2sentiment


