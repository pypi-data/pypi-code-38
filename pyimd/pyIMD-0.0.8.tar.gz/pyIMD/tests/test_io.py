# /********************************************************************************
# * Copyright © 2018-2019, ETH Zurich, D-BSSE, Andreas P. Cuny & Gotthold Fläschner
# * All rights reserved. This program and the accompanying materials
# * are made available under the terms of the GNU Public License v3.0
# * which accompanies this distribution, and is available at
# * http://www.gnu.org/licenses/gpl
# *
# * Contributors:
# *     Andreas P. Cuny - initial API and implementation
# *******************************************************************************/

import numpy as np
import pandas as pd
from unittest import TestCase, main
from pyIMD.io.read_from_disk import read_from_text, read_from_file


class TestIO(TestCase):

    def testReadFromText(self):
        df1 = pd.DataFrame(np.round(np.random.rand(10, 7)), columns=['Timestamp(s)', 'Normal deflection(V)',
                                                                     'Lateral deflection(V)', 'Sum(V)', 'Amplitude(mV)',
                                                                     'Phase(deg)', 'Frequency shift(Hz)'])
        df1.to_csv('testReadFromText.csv', index=False,  sep='\t')
        files = ['testReadFromText.csv']

        delimiter = '\t'
        read_from_row = 5

        df = pd.DataFrame()
        for f in files:
            df = df.append(read_from_text(f, delimiter, read_from_row))

        self.assertEqual(df.shape, (5, 7))

    def testReadFromFileCSV(self):
        df1 = pd.DataFrame(np.round(np.random.rand(10, 7)), columns=['Timestamp(s)', 'Normal deflection(V)',
                                                                     'Lateral deflection(V)', 'Sum(V)', 'Amplitude(mV)',
                                                                     'Phase(deg)', 'Frequency shift(Hz)'])
        df1.to_csv('testReadFromFileCSV.csv', index=False,  sep='\t')
        files = ['testReadFromFileCSV.csv']

        delimiter = '\t'

        df = pd.DataFrame()
        for f in files:
            df = df.append(read_from_file(f, delimiter))

        self.assertEqual(df.shape, (10, 7))

    def testReadFromFileTxt(self):
        df1 = pd.DataFrame(np.round(np.random.rand(10, 7)), columns=['Timestamp(s)', 'Normal deflection(V)',
                                                                     'Lateral deflection(V)', 'Sum(V)', 'Amplitude(mV)',
                                                                     'Phase(deg)', 'Frequency shift(Hz)'])
        df1.to_csv('testReadFromFileTxt.txt', index=False,  sep='\t')
        files = ['testReadFromFileTxt.txt']

        delimiter = '\t'

        df = pd.DataFrame()
        for f in files:
            df = df.append(read_from_file(f, delimiter))

        self.assertEqual(df.shape, (10, 7))

    def testReadFromFileNoEnding(self):
        df1 = pd.DataFrame(np.round(np.random.rand(10, 7)), columns=['Timestamp(s)', 'Normal deflection(V)',
                                                                     'Lateral deflection(V)', 'Sum(V)', 'Amplitude(mV)',
                                                                     'Phase(deg)', 'Frequency shift(Hz)'])
        df1.to_csv('testReadFromFileNoEnding', index=False,  sep='\t')
        files = ['testReadFromFileNoEnding']

        delimiter = '\t'

        df = pd.DataFrame()
        for f in files:
            df = df.append(read_from_file(f, delimiter))

        self.assertEqual(df.shape, (10, 7))

    def testReadFromFileTxt2Col(self):
        df1 = pd.DataFrame(np.round(np.random.rand(10, 2)), columns=['Timestamp(s)', 'Frequency shift(Hz)'])
        df1.to_csv('testReadFromFileTxt2Col.txt', index=False,  sep='\t')
        files = ['testReadFromFileTxt2Col.txt']

        delimiter = '\t'

        df = pd.DataFrame()
        for f in files:
            df = df.append(read_from_file(f, delimiter))

        self.assertEqual(df.shape, (10, 7))


if __name__ == "__main__":
    main()
