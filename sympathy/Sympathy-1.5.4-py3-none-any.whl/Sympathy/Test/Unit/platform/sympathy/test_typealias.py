# Copyright (c) 2013, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from sympathy.api import node

json_data = """
{
    "definition": {
        "name": "Example1",
        "type": "python2",
        "description": "Test node",

        "file": "examples.py",
        "class": "Example1",
        "icon": "example.svg",
        "docs": "example1.html",

        "nodeid": "org.sysess.sympathy.examples.example1",
        "author": "Stefan Larsson <stefan.larsson@combine.se>",
        "copyright": "(C)2011-2012 Combine Control Systems AB",
        "version": "1.0",

        "inputs": {
            "in": {
              "type": "greger",
              "name": "Divine Input",
             "index": 0,
                "file": "hubba",
                "scheme": "schematics"
            }
         },

        "outputs": {
            "out": {
                "type":  "table",
                "name":  "Output",
                "index": 0,
                "file": "hubba",
                "scheme": "schematics"
            }
        }
    },

    "parameters": {
        "type": "group",

        "delay": {
            "type":  "group",
            "label": "Delay Group",
            "order": 10,

            "delay": {
                "type":        "float",
                "label":       "Delay",
                "description": "Delay in seconds",
                "value":       0.050
            }
        },

        "examples": {
            "type":  "group",
            "label": "Examples",
            "order": 20,

            "scalars": {
                "type":  "page",
                "label": "Scalars",
                "order": 10,

                "stringfloat": {
                    "type":        "float",
                    "label":       "Float in a line edit",
                    "order":       10,
                    "description": "A float.",
                    "value":       0.1234
                },

                "spinfloat": {
                    "type":         "float",
                    "label":        "Float in a spinbox",
                    "order":        20,
                    "description":  "A float.",
                    "value":        0.1234,
                    "editor": {
                        "type":     "spinbox",
                        "max":      1.0,
                        "min":      0.0,
                        "step":     0.1,
                        "decimals": 4
                    }
                },

                "stringinteger": {
                    "type":        "integer",
                    "label":       "Integer in a line edit",
                    "order":       30,
                    "description": "An integer.",
                    "value":       1234,
                    "editor": {
                        "type":    "lineedit",
                        "max":     2000,
                        "min":     0
                    }
                },

                "spininteger": {
                    "type":        "integer",
                    "label":       "Integer in a spinbox",
                    "order":       40,
                    "description": "An integer.",
                    "value":       1234,
                    "editor": {
                        "type":    "spinbox",
                        "max":     2000,
                        "min":     0,
                        "step":    10
                    }
                }
            },
            "strings": {
                "type":  "page",
                "label": "Strings",
                "order": 20,

                "lineedit": {
                    "type":        "string",
                    "label":       "String in a line edit",
                    "order":       10,
                    "description": "Text on a single line"
                },

                "filename": {
                    "type":        "string",
                    "label":       "String as filename",
                    "order":       20,
                    "description": "A filename including path if needed",
                    "value":       "test.txt",
                    "editor": {
                        "type":    "filename",
                        "filter": ["Image files (*.png *.xpm *.jpg)",
                                   "Text files (*.txt)",
                                   "Any files (*)"]
                    }
                },

                "directory": {
                    "type":        "string",
                    "label":       "String as directory name",
                    "order":       30,
                    "description": "a directory including path if needed",
                    "value":       "MyDirectory",
                    "editor": {
                        "type":    "dirname"
                    }
                }
            },
            "logics": {
                "type":  "page",
                "label": "Logics",
                "order": 30,

                "boolflag": {
                    "type":        "boolean",
                    "label":       "Boolean",
                    "description": "A boolean flag indicating true or false",
                    "value":       true
                }
            },
            "lists": {
                "type":  "page",
                "label": "Lists",
                "order": 40,

                "selection": {
                    "type":  "page",
                    "label": "List selection",
                    "order": 10,

                    "combo": {
                        "type":        "list",
                        "label":       "Combo Box",
                        "description": "A combo box.",
                        "order":       10,
                        "value":       0,
                        "list":       ["First option",
                                       "Second option",
                                       "Third option"],
                        "editor": {
                            "type": "combobox"
                        }
                    },

                    "alist": {
                        "type":        "list",
                        "label":       "List View",
                        "description": "A list.",
                        "order":       20,
                        "value":       0,
                        "list":       ["First option",
                                       "Second option",
                                       "Third option"],
                        "editor": {
                            "type":    "listview"
                        }
                    },

                    "multilist": {
                        "type":            "list",
                        "label":           "List View with multiselect",
                        "description":     "A list with multiselect.",
                        "order":           30,
                        "value":           [],
                        "list":           ["Element 1",
                                           "Element 2",
                                           "Element 3"],
                        "editor": {
                            "type":        "listview",
                            "multiselect": true
                        }
                    }
                },

                "listcreation": {
                    "type":  "page",
                    "label": "List creation",
                    "order": 20,

                    "multiplefiles": {
                        "type":        "list",
                        "label":       "Multiple files",
                        "description": "Selection of multiple files",
                        "list":        [],
                        "editor": {
                            "type":    "multiplefilenames",
                            "filter": ["Image files (*.png *.xpm *.jpg)",
                                       "Text files (*.txt)",
                                       "Any files (*)"]
                        }
                    },

                    "listeditor": {
                        "type":        "list",
                        "label":       "Editable list",
                        "description": "Editable list",
                        "list":       ["Item 1", "Item 2"],
                        "editor": {
                            "type":    "listeditor"
                        }
                    }
                }
            }
        }
    }
}
"""

alias_text = """
{
  "greger": {
    "type": "(y: sytable, t: sytable)",
    "util": "timeseries_util"
    }
}
"""

class MyNode(node.BasicNode):
    def __init__(self):
        
        super(MyNode, self).__init__()

    def execute_basic(self, node_context=None):
        print(node_context)
        pass

if __name__ == '__main__':
    c = MyNode()
    c._sys_execute(json_data, alias_text)
