'''
This file is part of the EdTech library project at Full Sail University.

    Foobar is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Foobar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

    Copyright © 2015 Full Sail University.
'''

import ConfigParser
import datetime

class Config(object):
    """Manage a configuration file."""
    def __init__(self, filename):
        self.HasSection = "hasSection"
        self.DateFormat = "%Y-%m-%d"

        self.config = ConfigParser.SafeConfigParser()
        self.file = filename + ".cfg"
        self.config.read(self.file)

    def __del__(self):
        with open(self.file, "wb") as configFile: self.config.write(configFile)

    def GetFile(self): return self.file

    def Section(self, section):
        try: self.config.get(section, self.HasSection)
        except:
            self.config.add_section(section)
            self.config.set(section, self.HasSection, "true")
        return section

    def GetDate(self, section, name, default):
        try: val = datetime.datetime.strptime(self.config.get(section, name), self.DateFormat).date()
        except:
            val = default
            self.config.set(section, name, str(val))
        return val
    def GetInt(self, section, name, default):
        try: val = int(self.config.get(section, name))
        except:
            val = default
            self.SetInt(section, name, val)
        return val
    def GetChar(self, section, name, default):
        try: val = self.config.get(section, name)[0]
        except:
            val = default
            self.config.set(section, name, val)
        return val
    def GetStr(self, section, name, default):
        try: val = self.config.get(section, name)
        except:
            val = default
            self.SetStr(section, name, val)
        return val

    def SetInt(self, section, name, val): self.SetStr(section, name, str(val))
    def SetStr(self, section, name, val): self.config.set(section, name, val)
