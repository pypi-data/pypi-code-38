#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date: Wed 19 Oct 23:43:22 2016

from bob.pad.base.algorithm import Algorithm

import logging

logger = logging.getLogger("bob.pad.voice")


class DummyAlgorithm(Algorithm):
    """This class is used to test all the possible functions of the tool chain,
    but it does basically nothing."""

    def __init__(self, **kwargs):
        """Generates a test value that is read and written"""

        # call base class constructor registering that this tool performs everything.
        Algorithm.__init__(
            self,
            performs_projection=False,
            requires_projector_training=False,
            **kwargs
        )

    def score(self, toscore):
        """Returns the evarage value of the probe"""
        logger.info("score() score %f", toscore)

        return toscore


algorithm = DummyAlgorithm()
