from ..pipe import Pipe


basic_pipe = Pipe()
basic_pipe.add('Lowercase')
basic_pipe.add('AddWhitespaceAroundCJK')
basic_pipe.add('AddWhitespaceAroundPunctuation')
basic_pipe.add('MergeWhiteSpaceCharacters')
basic_pipe.add('StripWhiteSpaceCharacters')
basic_pipe.add('StripAccentToken')
basic_pipe.add('WhiteSpaceTokenizer')
