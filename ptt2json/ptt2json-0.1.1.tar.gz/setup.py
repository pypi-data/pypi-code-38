# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ptt2json']

package_data = \
{'': ['*']}

install_requires = \
['pyquery>=1.4,<2.0', 'requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'ptt2json',
    'version': '0.1.1',
    'description': 'A simple python library to extract pages and posts information from https://www.ptt.cc/bbs/ to json format',
    'long_description': '# Ptt2Json\n\nA simple python library to extract pages and posts information from https://www.ptt.cc/bbs/ to json format\n\n```python\n>>> from ptt2json import *\n>>> ptt = PttPage(boardname="Gossiping")\n>>> print(ptt.posts)\n\n[{\'url\': \'/bbs/Gossiping/M.1560591164.A.B9C.html\',\n  \'post_id\': \'M.1560591164.A.B9C\',\n  \'timestamp\': \'1560591164\',\n  \'title\': \'[新聞] 暴動！財經女神訪歐曬日光浴 白皙長腿惹\',\n  \'nrec\': \'\',\n  \'author\': \'cycling\',\n  \'mark\': \'\'},\n {\'url\': \'/bbs/Gossiping/M.1560591174.A.B05.html\',\n  \'post_id\': \'M.1560591174.A.B05\',\n  \'timestamp\': \'1560591174\',\n  \'title\': \'[新聞] 韓國瑜造勢到底多少人? 椅子精算師四叉貓算給你\',\n  \'nrec\': \'\',\n  \'author\': \'sweat992001\',\n  \'mark\': \'\'},\n {\'url\': \'/bbs/Gossiping/M.1560591182.A.50D.html\',\n  \'post_id\': \'M.1560591182.A.50D\',\n  \'timestamp\': \'1560591182\',\n  \'title\': \'Re: [新聞] 大烏龍！攝影師砸30萬修MacBook 最後發現\',\n  \'nrec\': \'\',\n  \'author\': \'YHOTV4096\',\n  \'mark\': \'\'},\n  ...]\n```\n\n## PttPage\n\n```\n[\n\t{\n\t\t"url": str,\n\t\t"post_id": str,\n\t\t"timestamp": str,  # unix time\n\t\t"title": str,      \n\t\t"nrec": str,       # 推噓文相加總和\n\t\t"author": str,\n\t\t"mark":            # 標記\n\t},\n\t...\n]\n```\n\n## PttPost\n\n```\n{\n\t"article_id": str,\n    "article_title": str,\n    "author": str,\n    "board": str,\n    "content": str,\n    "timestamp": int,\n    "ip": str,           # ipv4 address \n    "ip_country": str,   # ip <-> country mapping\n    "message_count": {\n         "all": str,     # 推、噓、箭頭總數\n         "boo": str,     # 噓文\n         "count": str,   # 推 - 噓文\n         "neutral": str, # 箭頭\n         "push": str,    # 推文\n    },\n    "messages": [\n    \t{\n    \t\t"push_tag": str, # 評論符號\n    \t\t"push_userid": str,\n    \t\t"push_content": str,\n    \t\t"push_ipdatetime # ip 與時間（無日期）\n    \t}\n    ],\n    "url": str,\n    "is_404": 是否刪文,\n}\n\n```\n\n',
    'author': 'LImoritakeU',
    'author_email': 'LImoritakeU@gmail.com',
    'url': 'https://github.com/LImoritakeU/ptt2json',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
