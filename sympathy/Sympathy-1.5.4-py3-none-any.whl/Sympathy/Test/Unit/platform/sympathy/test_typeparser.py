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
from sympathy.types import types as typeparser


def test_simplify():
    tests = '''
    sytypealias hej1 = sytable
    sytypealias hej11 = sytext
    sytypealias hej2 = [sytable]
    sytypealias hej3 = (august:sytext)
    sytypealias hej5 = [hej1]
    sytypealias hej4 = (herbert:sytext, rudolf:hej3, adolph:hej2)
    sytypealias hej6 = (a:sytext, b:hej7)
    sytypealias hej7 = (c:sytable, d:hej6)
    sytypealias hej8 = (q:hej1, r:hej4)
    sytypealias hej9 = [hej10]
    sytypealias hej12 = (rolf:hej10)
    sytypealias hej13 = [hej12]
    sytypealias hej10 = (a:sytext, b:hej13)
    '''
    types = []
    for line in tests.strip().splitlines():
        types.append(typeparser.from_string_alias(line))
    typeparser.simplify_aliases(types)


def test_positive_parsing():

    passing_tests = '''
    sytypealias hej1 = sytable
    sytypealias hej11 = sytable
    sytypealias hEj1 = sytable
    sytypealias hej12 = sytable
    sytypealias hej13 = sytext
    sytypealias hej2 = [sytable]
    sytypealias hej21 = {sytable}
    sytypealias hej3 = (august:sytext)
    sytypealias hej7 = (august:sytext, nils:sytext)
    sytypealias hej71 = (august:sytext, nils:sytext, andreas: [sytable], jens: {sytable})
    sytypealias hej81 = (august:sytext, nils:sytext, andreas:[(hubert:sytable, joseph:sytext)])
    sytypealias hej10 = [hej9]
    sytypealias hej101 = hej10
    sytypealias hej102 = <a>
    sytypealias hej103 = [<b>]
    sytypealias hej104 = {<b>}
    sytypealias hej105 = (sverker: <b>)
    sytypealias hej106 = (sveriker:<a>, jerker:[<b>])
    '''
    types = {}
    for line in passing_tests.strip().splitlines():
        new_type = typeparser.from_string_alias(line)
        new_type_name = new_type.name()
        if new_type_name in types.keys():
            print('Error: "{}" is already defined'.format(new_type_name))
        else:
            types[new_type_name] = new_type
    for t in types:
        print('{}: {}'.format(t, types[t]))


def test_negative_parsing():
    failing_tests = '''
    sytypealias hej4 = [sytable, sytext]
    sytypealias hej5 = [sytable, sytext, sytable]
    sytypealias hej6 = [sytable, sytext, sytable, sytable, sytable]
    sytypealias hej81 = (august:sytext, nils:sytext, andreas:[sytable, (hubert:sytable)])
    sytypealias hej8 = (august:sytext, nils:sytext, andreas : [sytable, sytext])
    sytypealias hej82 = [sytext, sytable, (arne:sytext, banarne:sytable, conny:[sytable, sytable]), [sytable, sytable]]
    sytypealias hej9 = [sytable, sytable, (this_does_not_work:sytable)]
    sytypealias hej9 = [sytable, sytable, (this does not work:sytable)]
    sytypealias hej9 = [sytable, sytable, (thisworks:sytable,[sytable)]
    sytypealias hej_9 = [sytable, sytext, (thisworks:sytable,[sytable])]
    sytypealias hej91 = [sytable, sytext, thisworks:sytable,[sytable])]
    sytypealias hej92 = <typealias efvert = table>
    sytypealias hej92 = <table>
    sytypealias hej92 = <text>


    sytypealias hej93 = sygeneric 0day
    '''

    for line in failing_tests.strip().splitlines():
        has_failed = False
        try:
            typeparser.from_string_alias(line)
        except (TypeError, AttributeError):
            has_failed = True

        if not has_failed:
            print('"{}" did NOT fail as expected'.format(line))

if __name__ == '__main__':
    test_positive_parsing()
    test_negative_parsing()
    test_simplify()
