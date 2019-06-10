import pandas, random
import Sanitizer

class FileHelper():
    @classmethod
    def fileEncodingEnumToPythonEncodingString(cls, args):
        if hasattr(args, 'fileEncoding'):
            if args.fileEncoding == 0:
                return 'utf-8'
            if args.fileEncoding == 1:
                return 'iso-8859-1'
            if args.fileEncoding == 2:
                return 'latin-1'
            if args.fileEncoding == 3:
                return 'ascii'
            if args.fileEncoding == 4:
                return 'utf-16'
            if args.fileEncoding == 5:
                return 'utf-32'
            if args.fileEncoding == 6:
                return 'utf-8-sig'
        else:
            return None

    @classmethod
    def appendRowToRowsPerSampleScheme(cls, rows, row, sampleRandom, maxRows, dataRowIndex):
        if sampleRandom:
            if len(rows) < maxRows:
                rows.append(row)
            else:
                r = int(random.random() * (dataRowIndex + 1))
                if r < maxRows:
                    rows[r] = row
        elif maxRows:
            rows.append(row)
            if len(rows) >= maxRows:
                return False
        else:
            rows.append(row)

        return True

    @classmethod
    def createHeaders(cls, headerRow, numColumns):
        headers = [hrc or 'Column' + str(hri) for hri, hrc in enumerate(headerRow)] + (['Column' + str(c + len(headerRow)) for c in range(0, numColumns - len(headerRow))])
        headers = Sanitizer.makeNamesUnique(headers)
        return headers

    @classmethod
    def createDataFrameAndHeader(cls, headerRow, rows):
        if len(headerRow) > 0 and len(rows) == 0:
            rows.append(headerRow)
            headerRow = []

        df = pandas.DataFrame(rows)
        headers = FileHelper.createHeaders(headerRow, len(df.columns))

        # compensate for a Pandas issue where the header row can't be wider than the dataframe
        # if so, pad the first row with blanks, then re-create dataframe
        if len(headers) > len(df.columns):
            rows[0].extend([None] * (len(headers) - len(rows[0])))
            df = pandas.DataFrame(rows)

        df.columns = headers

        return df