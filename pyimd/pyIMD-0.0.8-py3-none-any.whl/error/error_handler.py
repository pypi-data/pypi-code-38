# /********************************************************************************
# * Copyright © 2018-2019, ETH Zurich, D-BSSE, Andreas P. Cuny & Gotthold Fläschner
# * All rights reserved. This program and the accompanying materials
# * are made available under the terms of the GNU Public License v3.0
# * which accompanies this distribution, and is available at
# * http://www.gnu.org/licenses/gpl
# *
# * Contributors:
# *     Andreas P. Cuny - initial API and implementation
# *******************************************************************************/

__author__ = 'Andreas P. Cuny'


class ArgumentError(Exception):
    """
    Argument Error class prints error to console.

    Args:
        msg ('str')         Error message
    """
    def __init__(self, msg):
        print(msg)

