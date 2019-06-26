"""
Copyright 2018 Thomas Bollmeier <entwickler@tbollmeier.de>

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""   
import os

class Output(object):
    
    def __init__(self):
        pass
    
    def open(self):
        pass
    
    def close(self):
        pass
    
    def write(self, text):
        raise NotImplementedError

    def writeln(self, text):
        self.write(text + "\n")
        

class StdOut(Output):
    
    def __init__(self):
        Output.__init__(self)
    
    def write(self, text):
        print(text, end="")
        
        
class FileOut(Output):
    
    def __init__(self, filepath):
        Output.__init__(self)
        self._filepath = filepath
        self._fp = None
        
    def open(self):
        self._fp = open(self._filepath, "w")
        
    def close(self):
        if self._fp:
            self._fp.close()
            self._fp = None
    
    def write(self, text):
        self._fp.write(text)
    