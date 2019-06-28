# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/5/30
@author:qianyang<qianyang@aibayes.com>
@description:none
"""
from bayeslibs.config import BayesLibsConfig

__all__ = ['BayesLibsConfig']

if __name__ == '__main__':
    BayesLibsConfig('192.168.0.192', 5000).connect()
