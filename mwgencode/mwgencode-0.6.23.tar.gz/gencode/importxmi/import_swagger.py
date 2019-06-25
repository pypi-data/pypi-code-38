try:  # 导入模块
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from mwutils.utils import none2default
from gencode import (ImportBase,uml,xmi,_id,_type,_extension
             )
class ImportSwagger(ImportBase):
    def __init__(self):
        self.swagger= {'title':'swagger','version':'v1.0','doc':'please add swagger package to uml'}
        self.packages = []
        self.objects_bo = {}
        self.datatypes = []
        self.singals = []
        self.pts = []
        self.classes = []

    def _handle_swagger(self, pkg_swg):
        # 记录swagger package 信息
        self.swagger['title'], self.swagger['version'],*_ = \
           none2default(self.get_stereotype(pkg_swg), ['swagger', 'v1.0'])
        self.swagger['resp_xml'] = 'xml' in self.get_stereotype(pkg_swg)
        self.swagger['doc'] = self.get_doc(pkg_swg)
        pkgs = pkg_swg.findall('packagedElement')
        def set_lk_flag(op):
            '''
            给lk关联的datatype打上lk的标志，便于产生lk的datatype
            :param id:
            :return:
            '''
            def set_flg(obj,type):
                for attr in obj['attrs']:
                    if attr['type'] == 'object':
                        obj_attr = self.objects_bo[attr['typename']]
                        if obj_attr['type'] not in ('uml:DataType', 'uml:Class'):
                            raise Exception('[%s.%s]的类型必须为：DataType 或Class'
                                             % (obj['name'],attr['name']))
                        # 返回的类型只能允许result和return的attr才要做lookup
                        if type=='return' and attr['name'] not in ('result','return'):
                            continue
                        obj_attr['haslkobj'] = True
                        for dt in self.datatypes:
                            if dt['id']==attr['typename']:
                                dt['haslkobj'] = True
                                break;

            try:
                in_obj = self.objects_bo[op['in']['typename']]
                set_flg(in_obj,'in')
            except Exception as e:
                raise Exception('[%s.%s.%s] 发生错误， error:%s'%(op['pkg_name'],op['name'],in_obj['name'],e))
            try:
                return_obj = self.objects_bo[op['return']['typename']]
                set_flg(return_obj,'return')
            except Exception as e:
                raise Exception('[%s.%s.%s] 发生错误， error:%s' % (op['pkg_name'],op['name'], return_obj['name'], e))

        def add_datatype(pkg_dt):
            if pkg_dt.attrib.get(_type, None) == 'uml:DataType':
                datatype = self.get_bo_class(pkg_dt)
                datatype['haslkobj'] = self.objects_bo[pkg_dt.attrib.get(_id)].get('haslkobj', False)
                self.datatypes.append(datatype)
            elif pkg_dt.attrib.get(_type, None) == 'uml:Signal':
                signal = self.get_bo_class(pkg_dt)
                signal['pkg_name'] = pkg.attrib.get('name')
                ops_lk = []
                for op in signal['ops']:
                    op['pkg_name'] = signal['pkg_name']
                    if 'lk' in op['stereotype']:
                        op_cp = op.copy()
                        op['stereotype'].remove('lk')
                        op_cp['stereotype'] = ['lk']
                        op_cp['name']='%s_%s'%(op['name'],'lk')
                        ops_lk.append(op_cp)
                        # 给op关联的物件设为lk
                        set_lk_flag(op)
                signal['ops'].extend(ops_lk)
                self.singals.append(signal)
            elif pkg_dt.attrib.get(_type, None) == 'uml:PrimitiveType':
                # self.objects_bo['AAAAAAFeCiNYUToFjYA=']
                self.pts.append(self.get_bo_class(pkg_dt))
            elif pkg_dt.attrib.get(_type, None) == 'uml:Class':
                datatype = self.get_bo_class(pkg_dt)
                datatype['haslkobj'] = self.objects_bo[pkg_dt.attrib.get(_id)].get('haslkobj',False)
                self.datatypes.append(datatype)
                # self.pts.append(self.get_bo_class(pkg_dt))
        # def add_datatype_from_pts():
        #     '''
        #     把不在swagger下的class加到datatypes中，以便能正确的产生swagger类
        #     :return:
        #     '''
        #     for pt in self.pts:
        #         for attr in pt.get('attrs',[]):
        #             if attr['type']=='object':
        #                 ref_class = self.objects_bo[attr['typename']]
        #                 for datatype in self.datatypes:
        #                     if datatype['id']==ref_class['id']:
        #                         break
        #                 else:
        #                     self.datatypes.append(ref_class)
        #


        # swagger下的每个package是一个tag
        for pkg in pkgs:
            package = {'name':pkg.attrib.get('name'), 'doc':self.get_doc(pkg)}
            # 只允许容器类才能加入
            if pkg.attrib.get(_type, None) in['uml:Package','uml:Model','uml:Component']:
                self.packages.append(package)
            else:
                add_datatype(pkg)
            pkgs_datatype = pkg.findall('packagedElement')
            for pkg_dt in pkgs_datatype:
                add_datatype(pkg_dt)
        # 增加不在swagger package中的类
        # add_datatype_from_pts()

    def _handle_pkgElm(self, pkgElms):
        for pkg in pkgElms:
            # 记录swagger信息
            if pkg.attrib.get('name', None) != 'swagger' :
                continue
            self.swagger['title'],self.swagger['version'],*_ = \
                       self.get_stereotype(pkg)
            self.swagger['doc'] = self.get_doc(pkg)
            self._handle_swagger(pkg)

    def impxml(self,file):
        tree = ET.parse(file)  # 分析XML文件
        root = tree.getroot()
        for idx0,r in enumerate(root):
            if r.attrib.get('name', None) != 'RootModel':
                continue
            # 加入所有的数据类型的class
            for bo_cls in self.find_bo_classes(r):
                self.objects_bo[bo_cls['id']]=(self.get_bo_class(bo_cls['obj']))
            # 处理所有package
            self._handle_pkgElm(r.findall('packagedElement'))

if __name__ == '__main__':
    i = ImportSwagger()
    i.impxml(r"D:\mwwork\projects\its\mobile_gateway_server\docs\uml analyse.xml")
    # print(i.trans)
    # print(i.objects_pkg)
    print('swagger',i.swagger)
    print('datatypes',i.datatypes)
    print('singals',i.singals)
    print('p', i.pts)
    # i.impxml(r"test.xml")

