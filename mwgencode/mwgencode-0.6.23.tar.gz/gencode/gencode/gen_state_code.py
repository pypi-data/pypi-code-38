import os

from gencode.importxmi.import_states import ImportStates
from gencode.utils import saveUTF8File


class Gen_State_Code():
    def __init__(self,root_path,xmifile):
        self.state_imp = ImportStates()
        self.state_imp.impxml(xmifile)
        self.root_path = root_path
        self.codes = []

    def _gen_state_code(self):
        def get_states_code():
            self.codes.append('  ')
            for states in self.state_imp.states:
                for key,values in states.items():
                    self.codes.append('%s = ['%key)
                    for state in values:
                        state_doc = '        #%s:%s'%(state['name'],state['doc'])
                        state_doc = state_doc+ ','.join([";%s:%s"%(ent['name'],ent['doc']) for ent in state['onenter']])
                        state_doc = state_doc + ','.join([";%s:%s" % (ext['name'], ext['doc']) for ext in state['onexit']])
                        self.codes.append(state_doc)
                        state_code = "        State(name='%s',"%state['name']
                        on_enter_code = ','.join(["'%s'"%ent['name'] for ent in state['onenter']])
                        if on_enter_code:
                            state_code = state_code+ "on_enter=[%s],"%on_enter_code
                        on_exit_code = ','.join(["'%s'"%ext['name'] for ext in state['onexit']])
                        if on_exit_code:
                            state_code = state_code + "on_exit=[%s],"%on_exit_code
                        state_code = state_code + 'ignore_invalid_triggers=True,'
                        state_code = state_code + '),'
                        self.codes.append(state_code)
                    self.codes.append(']')

        def get_trans_code():
            self.codes.append('  ')
            def get_conditions(trg):
                return ','.join(["'%s'" % g for g in trg['guard'].split('&')])

            self.codes.append('transitions = [')
            for trg in self.state_imp.trans:
                trg_code = "    {'trigger': '%s', "%trg['trigger']
                trg_code = trg_code + "'source': '%s', "%trg['source']
                trg_code = trg_code +"'dest': '%s', "%trg['target']
                if trg['guard']:
                    code_guard = ','.join(["'%s'" % g for g in trg['guard'].split('&')])
                    trg_code = trg_code +"'conditions' : [%s], "%code_guard
                if  trg['after']:
                    trg_code = trg_code +"'after' : '%s',"%trg['after']
                if trg['before']:
                    trg_code = trg_code +"'before' : '%s_before',"%trg['before'].split('(')[0]
                trg_code = trg_code +'},'
                self.codes.append(trg_code)
            self.codes.append(']')


        self.codes.append('from transitions import State')
        self.codes.append('  ')
        get_states_code()
        get_trans_code()
        filename = os.path.join(self.root_path, 'states.py')
        if os.path.exists(filename):
            print('the file is exists,filename:%s'%filename)
            print('codes :')
            for c in self.codes:
                print(c)
            return
        saveUTF8File(filename,self.codes)

    def gen_state_code(self):
        self.codes = []
        self._gen_state_code()

    def _gen_model_code(self):
        self.codes.append('from transitions import Machine')
        self.codes.append('from fsm.states import states,transitions')
        self.codes.append('import logging')
        self.codes.append('from transitions import logger')
        self.codes.append(' ')
        self.codes.append('logger.setLevel(logging.DEBUG)')
        self.codes.append(' ')
        self.codes.append('class State_Model(object):')
        self.codes.append('    def __init__(self):')
        self.codes.append('        self._add_extend_state()')
        self.codes.append("        self.machine = Machine(model=self, states=states, transitions=transitions, initial='free')")
        self.codes.append('')

        def gen_add_extend_state():
            self.codes.append('    def _add_extend_state(self):')
            self.codes.append('        #fault = State(name="fault", )')
            self.codes.append('        #states.append(fault)')
            self.codes.append("        #transitions.append({'trigger': 'fail', 'source': '*', 'dest': 'fault',})")
            self.codes.append("        #transitions.append({'trigger': 'fix', 'source': 'fault', 'dest': 'free',})")
            self.codes.append("        pass")

        def gen_failure_recovery():
            self.codes.append('def failure_recovery(statemodel,state):')
            self.codes.append('    if state == statemodel.state:')
            self.codes.append('        return')
            for sts in self.state_imp.states:
                for key, values in sts.items():
                    for value in values:
                        self.codes.append("    elif state == '%s':"%value['name'])
                        self.codes.append("        statemodel.to_%s()"%value['name'])
            self.codes.append("    logger.debug('recovery state to (%s)' % statemodel.state)")

        def get_func():
            for sts in self.state_imp.states:
                for key,values in sts.items():
                    for value in values:
                        for ent in value['onenter']:
                            self.codes.append('')
                            self.codes.append('    #%s' % ent['doc'])
                            self.codes.append('    def %s(self):' % ent['name'])
                            self.codes.append('        logger.debug("onenter:%s")' % ent['name'])
                        for ext in value['onexit']:
                            self.codes.append('')
                            self.codes.append('    #%s' % ext['doc'])
                            self.codes.append('    def %s(self):' % ext['name'])
                            self.codes.append('        logger.debug("onexit:%s")' % ext['name'])
            for tr in self.state_imp.trans:
                if tr['before']:
                    self.codes.append('')
                    self.codes.append('    #%s' % tr['doc'])
                    # check_in(carid) 解析成 ['check_in','carid)']
                    func_bfr =tr['before'].split('(')
                    args_bfr = lambda x :', %s:'%func_bfr[1] if len(func_bfr)>1 else '):'
                    self.codes.append('    def %s_before(self %s:' % (func_bfr[0],args_bfr(func_bfr)))
                    self.codes.append('        logger.debug("before:%s")' % tr['before'])
                if tr['after']:
                    self.codes.append('')
                    self.codes.append('    #%s' % tr['doc'])
                    self.codes.append('    def %s(self):' % tr['after'])
                    self.codes.append('        logger.debug("after:%s")' % tr['after'])
                if tr['guard']:
                    for g in tr['guard'].split('&'):
                        self.codes.append('')
                        self.codes.append('    #%s' % tr['doc'])
                        self.codes.append('    def %s(self):' % g)
                        self.codes.append('        logger.debug("guard:%s")' % g)

        gen_add_extend_state()
        get_func()
        gen_failure_recovery()
        filename = os.path.join(self.root_path, 'model.py')
        if os.path.exists(filename):
            print('the file is exists,filename:%s'%filename)
            print('code :')
            for c in self.codes:
                print(c)
            return
        saveUTF8File(filename,self.codes)

    def gen_model_code(self):
        self.codes = []
        self._gen_model_code()


if __name__ == '__main__':
    g = Gen_State_Code(r"d:\temp",r"D:\mwwork\projects\iparking\docs-parking\parking-state.xml")
    # g.gen_state_code()
    g.gen_model_code()
    # def state(self):
    #     gen_code = Gen_State_Code(os.path.join(self.rootpath, 'fsm'), self.modelfile)
    #     gen_code.gen_state_code()
    #     gen_code.gen_model_code()



