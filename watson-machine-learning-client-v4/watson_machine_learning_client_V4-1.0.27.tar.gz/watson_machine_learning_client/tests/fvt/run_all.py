
import doctest
import test1

doctest.testmod(test1, optionflags=doctest.NORMALIZE_WHITESPACE |
                                   doctest.ELLIPSIS |
                                   doctest.REPORT_ONLY_FIRST_FAILURE
                                   )
