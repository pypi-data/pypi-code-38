import random
from collections import namedtuple

def readJson(args):
    dfc = None

    programText = args.program if hasattr(args, 'program') else None
    programEntry = args.entry if hasattr(args, 'entry') else None
    maxRows = args.maxRows if hasattr(args, 'maxRows') and args.maxRows != None and args.maxRows >= 0 else None
    sampleType = args.sampleType if hasattr(args, 'sampleType') else None
    fileEncoding = FileHelper.fileEncodingEnumToPythonEncodingString(args)
    path = args.path[0] # For now we don't support mulltifile json load.

    sampleRandom = True if sampleType and (sampleType == 3 or sampleType == 4) else False
    if sampleRandom:
        random.seed(args.blockId)

    if (programText == None or programEntry == None):
        try:
            with open(path, 'r', encoding = fileEncoding) as dataFile:
                pass
        except UnicodeError as e:
            # this means program was never generated because wrong encoding was selected
            raise EvaluationError(str(e), 'WrongEncoding')
        raise EvaluationError('JSON read program was not generated', 'JSONReadError')
    else:
        headerRow = list()
        rows = list()
        try:
            dataText = None

            with open(path, 'r', encoding = fileEncoding) as dataFile:
                dataText = dataFile.read()

            programCode = compile(programText, '<string>', 'exec')
            exec(programCode)

            headerRowGen = eval(programEntry + '_incremental(dataText)')
            headerRow = [name for name,_ in next(headerRowGen)]
            headerRow = Sanitizer.makeNamesUnique(headerRow)

            rowsGen = eval(programEntry +'_values_only(dataText)')
            for i, rowGen in enumerate(rowsGen):
                row = [cell for cell in rowGen]
                continueProcessingRows = FileHelper.appendRowToRowsPerSampleScheme(rows, row, sampleRandom, maxRows, i)
                if continueProcessingRows == False:
                    break
        except UnicodeError as e:
            raise EvaluationError(str(e), 'WrongEncoding')
        except StopIteration as e: # dataGen from PROSE will raise StopIteration in case they can't read JSON string
            raise EvaluationError(str(e), 'WrongEncoding')

        dfc = FileHelper.createDataFrameAndHeader(headerRow, rows)

    return dfc
