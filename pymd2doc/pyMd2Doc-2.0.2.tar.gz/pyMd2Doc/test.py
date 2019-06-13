# -*- coding: utf-8 -*-
import os
import createDoc


strs = u'''# 1. aaa
eweeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
## 1.1 bbbbbbb
eweeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
eweeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
eweeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
eweeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee

## 1.2 bbbbbbbnnnkn
eweeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
# 2. cc
# 3. d
## 3.1 dddd11111
## 3.2 d222222
### 3.2.1 d22222222222222
## 3.3 656565
# 4. e'''


if __name__ == "__main__":
    createDoc.createByString(strs, "123")
