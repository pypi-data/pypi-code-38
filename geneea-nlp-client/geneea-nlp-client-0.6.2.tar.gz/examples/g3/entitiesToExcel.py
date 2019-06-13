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
Extracts entities form G3 results stored as json-per-line to an excel file using pandas.

call as

```
python entitiesToExcel.py -i g3resutls.jsonl -o output.xlsx
```

or

```
python entitiesToExcel.py < g3resutls.jsonl > output.xlsx
```
"""

import argparse
import datetime
import sys

from typing import Tuple, Iterable, TextIO

from geneeanlpclient import g3

import pandas as pd

USER_KEY = None    # fill your API key here (or define it as env variable, and remove as a parameter in create)


def getEntities(file: TextIO) -> Iterable[Tuple[str, str, str, str]]:
    requestBuilder = g3.Request.Builder(
        analyses=[g3.AnalysisType.ENTITIES],
        referenceDate=datetime.datetime.now().strftime('%Y-%m-%d'),
    )

    with g3.Client.create(userKey=USER_KEY) as analyzer:
        for idx, text in enumerate(file):
            result = analyzer.analyze(requestBuilder.build(id=str(idx), text=text))
            for e in result.entities:
                yield result.docId, e.id, e.stdForm, e.type


def main(args):
    print('USER_KEY', USER_KEY, file=sys.stderr)

    with open(args.input, encoding='utf8') if args.input else sys.stdin as file:
        records = getEntities(file)

        df = pd.DataFrame(records, columns=['docid', 'entityid', 'stdform', 'type'])
        writer = pd.ExcelWriter(args.output, engine='xlsxwriter')
        df.to_excel(writer, index=False, header=True)
        writer.save()


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", "--input", help="Input file, one text per line in utf8")
    argparser.add_argument("-o", "--output", help="The resulting excel file; columns: docid, entity type, entity std form")
    main(argparser.parse_args())

