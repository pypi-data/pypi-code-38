# -*- coding: utf-8 -*-
# Copyright 2017 - 2019 ibelie, Chen Jie, Joungtao. All rights reserved.
# Use of this source code is governed by The MIT License
# that can be found in the LICENSE file.

import sys
if sys.version_info[0] == 3:
	from properform import properform
else:
	import properform

getattr(properform, sys.argv[1])(*sys.argv[2:])
