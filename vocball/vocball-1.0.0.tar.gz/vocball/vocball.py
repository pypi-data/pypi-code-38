#!/usr/bin/env python3
#
# This file is part of Vocabulary Football (VocBall).
#
# Copyright (C) 2017-2019 - Thomas Dähnrich <develop@tdaehnrich.de>
#
# VocBall is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# VocBall is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with VocBall. If not, see <http://www.gnu.org/licenses/>.

import sys

from game import Game

app = Game()
status = app.run(sys.argv)
sys.exit(status)
