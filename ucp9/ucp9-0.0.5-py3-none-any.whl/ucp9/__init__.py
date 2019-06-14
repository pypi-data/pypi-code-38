from ucp9.main import ucp9

"""
[C9CONV]

This module provides a transcoding service:
- FROM: An arbitrary unicode character.
- TO: A cp932-compatible, semantically similar but differently encoded version of the same character.

Author:
    Tran Anh Nhan
    
License:
    MIT License
    
Usage:
    import ucp9
    ucp9.convert(string, option)
        [string]: a string that contains cp932-incompatible characters
        [option]:
            - "keep": keep the cp932-inconvertible characters. NOTE: the return string WON'T be cp932-compatible.
            - "remove": remove the cp932-inconvertible characters.
            - "replace": replace the cp932-inconvertible characters with "?"
"""

convert = ucp9
