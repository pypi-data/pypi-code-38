"""x notification function"""
# -*- encoding: utf-8 -*-
#
# This file is free software by d0n <d0n@janeiskla.de>
#
# You can redistribute it and/or modify it under the terms of the GNU -
# Lesser General Public License as published by the Free Software Foundation
#
# This is distributed in the hope that it will be useful somehow.
#
# !WITHOUT ANY WARRANTY!
#
# Without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
from os import environ

from system.user.find import userfind

def xenv():
	usr = userfind()
	home = userfind(usr, 'home')
	dmngr = '/org/freedesktop/DisplayManager'
	environ['XDG_RUNTIME_DIR'] = '/run/user/%s'%userfind(usr, 'uid')
	environ['XDG_SEAT_PATH'] = '%s/Seat0'%dmngr
	environ['XDG_SESSION_PATH'] = '%s/Session0'%dmngr
	environ['XDG_CONFIG_HOME'] = '%s/.config'%home
	environ['XAUTHORITY'] = '%s/.Xauthority'%home
	environ['DISPLAY'] = ':0'
