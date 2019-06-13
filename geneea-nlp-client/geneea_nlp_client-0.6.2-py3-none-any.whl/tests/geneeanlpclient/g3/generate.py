"""
Code used to generate all possible analysis output for the testing minidocument. Used to g3.test reader
"""

import itertools
import json
import sys
from typing import Collection, Iterable, List

from pathlib import Path

from geneeanlpclient.common.restutil import remoteCall
from geneeanlpclient import g3


def powerset(items: Collection[g3.AnalysisType]) -> Iterable[List[g3.AnalysisType]]:
    return (list(xs) for xs in itertools.chain.from_iterable(itertools.combinations(items, r) for r in range(len(items)+1)))


def main():
    basicAnalyses = [a for a in g3.AnalysisType.__members__.values() if a != g3.AnalysisType.ALL]
    for analyses in filter(None, powerset(basicAnalyses)):
        print(analyses, file=sys.stderr)

        for mentions in [True, False]:
            for iSentiment in [True, False]:

                with g3.Client.create() as analyzer:
                    requestBuilder = g3.Request.Builder()
                    requestBuilder.setOptions(
                        analyses=analyses,
                        returnMentions=mentions,
                        returnItemSentiment=iSentiment)
                    request = requestBuilder.build(
                        id='1',
                        title='Angela Merkel in New Orleans',
                        text='Angela Merkel left Germany. She moved to New Orleans to learn jazz. That\'s amazing.'
                    )

                    # analyzer.analyze(request)
                    raw = remoteCall(
                        inputData=request,
                        url=analyzer.url,
                        serialize=lambda x: json.dumps(x.toDict()),
                        deserialize=lambda x: json.loads(x),
                        session=analyzer.session
                    )

                    analysisStr = '_'.join(a.name for a in g3.AnalysisType if a in analyses)
                    mentionsStr = '_M' if mentions else ''
                    iSentimentStr = '_IS' if iSentiment else ''
                    with open(Path('examples') / f'example_{analysisStr}{mentionsStr}{iSentimentStr}.json', 'w', encoding='utf8') as writer:
                        writer.write(json.dumps(raw, indent=3, sort_keys=True))


if __name__ == '__main__':
    main()
