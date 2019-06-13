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

"""
Analyzes several texts and extracts the named entities contained in them, including individual mentions
"""

import datetime
import sys

import geneeanlpclient.g3 as g3

USER_KEY = None    # fill your API key (or define it as env variable, and remove as a parameter in create)

TEXTS = [
    'I was in Paris last week. The Eiffel tower is great.',
    'You should try Prague, too.',
    'But I always love to go back to London. Going there next Tuesday.',
]


def main():
    print('USER_KEY', USER_KEY, file=sys.stderr)

    requestBuilder = g3.Request.Builder(
        analyses=[g3.AnalysisType.ENTITIES],
        referenceDate=datetime.datetime.now().strftime('%Y-%m-%d'),
        returnMentions=True
    )

    with g3.Client.create(userKey=USER_KEY) as analyzer:
        for idx, text in enumerate(TEXTS):
            result = analyzer.analyze(requestBuilder.build(id=str(idx), text=text))

            print(text)
            for e in result.entities:
                print(f'\t{e.type}: {e.stdForm}')

                for m in e.mentions:
                    # for each mention print a snippet - the mention in its context
                    prevToken = m.tokenSupport.tokens[0].previous()
                    nextToken = m.tokenSupport.tokens[-1].next()
                    snippet: str = f'{prevToken.text if prevToken else ""} [{m.text}] {nextToken.text if nextToken else ""}'
                    print(f'\t\t{m.mwl}: {snippet}')


if __name__ == '__main__':
    main()
