try:  # 导入模块
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

uml="http://schema.omg.org/spec/UML/2.0"
xmi="{http://schema.omg.org/spec/XMI/2.1}"
_id = xmi+"id"
_type = xmi+"type"
_extension = xmi+'Extension'

class ImportStates():
    def __init__(self):
        self._objects = {}
        self.states = []
        self.trans = []

    def _getDoc(self,attr):
        extens = attr.find(_extension)
        if extens is not None:
            # print('     extens:',extens.attrib)
            cls_doc = extens.find('documentation')
            if cls_doc is not None:
                return cls_doc.attrib.get('value')
        return ''

    def _handle_subv(self, subv, state):
        # print('subv:',subv.attrib)
        # if subv.attrib.get(_type,None) != 'uml:State':
        #     return None
        region = subv.find('region', None)
        if region:
            self._handle_region(region, subv.attrib.get('name') + '_')
        def getEnter(subv):
            enters = subv.findall('entry')
            result = []
            for enter in enters:
                result.append({'name':enter.attrib.get('name'),'doc':self._getDoc(enter)})
            return result

        def getExit(subv):
            enters = subv.findall('exit')
            result = []
            for enter in enters:
                result.append({'name': enter.attrib.get('name'), 'doc': self._getDoc(enter)})
            return result
        return {'type':'state', 'id':subv.attrib.get(_id),
                            'name':subv.attrib.get('name'),'doc':self._getDoc(subv),
                            'onenter':getEnter(subv),'onexit':getExit(subv)}

    def _handle_tran(self, tran):
        def getTriger(tran):
            trgs = tran.findall('trigger')
            for trg in trgs:
                if trg.attrib.get(_type)=='uml:Trigger':
                    if trg.attrib.get('name') != '':
                        return trg.attrib.get('name')
            # 如果没有trigger则直接返回tran的name
            result = tran.attrib.get('name').split('(')[0]
            if result:
                return result

        def getGuard(tran):
            guard =  tran.find('guard')
            if guard is not None:
                result = guard.attrib.get('specification')
                if result is not None:
                    return result
            return ''

        def getBefore(tran):
            result  =  tran.attrib.get('name',None)
            if result:
                return result
            return ''

        def getEffect(tran):
            effe = tran.find('effect')
            # print(tran.attrib)
            if effe is not None:
                result = effe.attrib.get('name')
                if result is not None:
                    return result
            return ''
        # print(tran.attrib)
        try:
            return {'trigger': getTriger(tran),
                    'doc': self._getDoc(tran),
                    'source': self._objects[tran.attrib.get('source')]['name'],
                    'target': self._objects[tran.attrib.get('target')]['name'],
                    'guard': getGuard(tran),
                    'before':getBefore(tran),
                    'after': getEffect(tran)}
        except Exception as e:
            # print('--------------',tran.attrib)
            # print('--------------',e)
            return None

            # print('tran:',tran.attrib)

    def _handle_region(self, region, state=''):
        state_d = {}
        for subv in region.findall('subvertex'):
            if subv.attrib.get(_type, None) != 'uml:State':
                continue
            state_o = self._handle_subv(subv, state)
            if state_o is not None:
                self._objects[state_o['id']] = state_o
                state_d.setdefault(state + 'states',[]).append(state_o)
        if state_d:
            self.states.append(state_d)

        for tran in region.findall('transition'):
            if tran.attrib.get(_type) != 'uml:Transition':
                continue
            tran_o = self._handle_tran(tran)
            if tran_o:
                self.trans.append(tran_o)


    def _handle_pkgElm(self, pkgElms):
        for pkg in pkgElms:
            if pkg.attrib.get(_type, None) != 'uml:StateMachine':
                continue
            region =  pkg.find('region',None)
            if region is None :
                continue
            self._handle_region(region)

    def impxml(self,file):
        self._objects = {}
        self.states = []
        self.trans = []
        tree = ET.parse(file)  # 分析XML文件
        root = tree.getroot()
        # print('0', root)
        for idx0,r in enumerate(root):
            # print('%d'%idx0, r.attrib)
            if r.attrib.get('name', None) != 'RootModel':
                continue
            self._handle_pkgElm(r.findall('packagedElement'))


if __name__ == '__main__':
    i = ImportStates()
    i.impxml(r"D:\mwwork\projects\iparking\docs-parking\parking-state.xml")
    # print(i._objects)
    # print(i.states)
    print(i.trans)
    # i.impxml(r"test.xml")