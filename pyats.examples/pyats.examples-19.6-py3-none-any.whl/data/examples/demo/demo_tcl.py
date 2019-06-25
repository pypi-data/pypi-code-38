'''Simple Tcl Code

The intention of the the code below is to demonstrate, using raw code, how to
use the Tcl interpreter/integration in pyATS. 

You can run this script directly, but it's better to copy paste each command
into a python interpreter shell and observe/interact with the code.
'''

from pyats import tcl

# evaluating any Tcl code
tcl.eval('set myVar 1')
tcl.eval('source /paty/to/my/library.tcl')
tcl.eval('proc newProcedure {args} {return $args}')
ret = tcl.eval('newProcedure -a 1 -b 2')

# shortcut to Tcl variables
tcl.vars['myNewVar'] = 'value for my new variable'
auto_path = tcl.vars['::auto_path']

# casting Tcl auto-typecasting
tcl.vars['integerVar'] = '1'
assert 1 == tcl.get_int('integerVar')

tcl.eval('keylset klist key.subkey value')
klist = tcl.cast_any(tcl.vars['klist'])
assert type(klist) is tcl.KeyedList
assert klist.key.subkey == 'value'

# detailed integration, eg, logging
tcl.eval('atslog::setLogScreen 1')
tcl.eval('ats_log -info "this is a log message"')

# Q
tcl.q.package('require', 'cAAs')
tcl.q.caas.abstract(device = uut, exec = 'show interface')
tcl.q.router_show(device = uut, cmd = 'show interface')
tcl.q.source('/path/to/my/file.tcl')




