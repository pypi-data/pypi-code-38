try:  # 导入模块
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


from jinja2 import FileSystemLoader,Environment


uml="http://schema.omg.org/spec/UML/2.0"
xmi="{http://schema.omg.org/spec/XMI/2.1}"
_id = xmi+"id"
_type = xmi+"type"
_extension = xmi+'Extension'

PORT =8000

class Tag:
    def __init__(self,name,desc):
        self.name=name
        self.desc=desc

class Path:
    def __init__(self,tag_name,summy,desc):
        self.summy=summy
        self.tag_name=tag_name
        self.desc=desc
        self.action=None
        self.name=None
        self.params=[]
        self.resps=[]

class Path_param:
    def __init__(self,name,type,desc):
        self.name=name
        self.type=type
        self.desc=desc
class Resp:
    def __init__(self,type,code):
        self.type=type
        self.code =code
        self.class_name=''

class Defin:
    def __init__(self,id,name,desc):
        self.id=id
        self.name=name
        self.desc=desc
        self.attrs=[]

class DeAttr:
    def __init__(self,name, type, desc ):
        self.name=name
        self.type=type
        self.desc=desc



class RestFile:
    def __init__(self,name,desc):
        self.name=name
        self.desc=desc
        self.tags=[]
        self.paths=[]
        self.defines=[]


    def has_defin(self,id):
        for defin in self.defines:
            if defin.id==id:
                return True
        return False

    def gen_text(self,templ):
        return templ.render(name=self.name,
                            desc=self.desc,
                            port =PORT,
                            tags=self.tags,
                            paths=self.paths,
                            defines=self.defines)


    # def gen_text(self):
    #     head =f_head.format(desc=self.desc,
    #                         name=self.name,
    #                         tags=self.tags)
    #     if len(self.paths)>0:
    #         head+='paths:\r\n'
    #         for path in self.paths:
    #             head+=path
    #     if len(self.definitions)>0:
    #         head += 'definitions:\r\n'
    #         for defin in self.definitions:
    #             head+=defin
    #
    #
    #     return head



class XmlParser:
    def filter_els(self,parent_el,el_name,el_type):
        els =parent_el.findall(el_name)
        def match_type(el):
            return el.attrib.get(_type,None)==el_type
        return filter(match_type,els)

    def load(self,filename):
        tree = ET.parse(filename)  # 分析XML文件
        root = tree.getroot()
        # print('0', root)
        for idx0,r in enumerate(root):
            # print('%d'%idx0, r.attrib)
            if r.attrib.get('name', None) != 'RootModel':
                continue
            self.r =r

    def _get_exten_value(self,el,name):
        exten =el.find(_extension)
        if exten is not None:
            docu =exten.find(name)
            if docu is not None:
                return docu.attrib.get('value','')
        return ''

    def _get_exten_list(self,el,name):
        exten =el.find(_extension)
        if exten is not None:
            return exten.findall(name)
        return None

    def _get_documentation(self,el):
        return self._get_exten_value(el,'documentation')

    def _get_stereotype(self,el):
        return self._get_exten_value(el,'stereotype')

    #根据class name 找class
    def _get_class_el(self,name):
        pkgs=self.r.findall('packagedElement')
        for pkg in pkgs:
            if pkg.attrib.get(_type, None) =='uml:Model':
                classes =pkg.findall('packagedElement')
                for cls in classes:
                    if cls.attrib.get('name',None)==name :
                        return cls
        return None

    # 根据class id 找class
    def _get_class_el_byid(self,class_id):
        pkgs=self.r.findall('packagedElement')
        for pkg in pkgs:
            if pkg.attrib.get(_type, None) =='uml:Model':
                classes =pkg.findall('packagedElement')
                for cls in classes:
                    if cls.attrib.get(_id,None)==class_id :
                        return cls
        return None

    def _get_class_attr(self,attr):
        name =attr.attrib.get('name','')
        if name.find(':')>=0:
            ls=name.split(':')
            name=ls[0]
            datatype=ls[1]
        else:
          datatype=attr.attrib.get('type','').split('_')[0]
        if datatype=='double':
            datatype='number'
        desc =self._get_documentation(attr)

        return name,datatype,desc

    #取得 message的参数
    def _get_message_args(self,msg):
        args =msg.find('argument')
        if args is not None:
            return args.attrib.get('value',None)
        return None

class SequencetoRest(XmlParser):
    def __init__(self):
        self.rests = []

    def _handle_class_params(self,class_type,cls,path):
        if cls is not None:
            if class_type=='inquery':
                attrs =self.filter_els(cls,'ownedAttribute','uml:Property')
                for attr in attrs:
                    name,datatype,desc=self._get_class_attr(attr)
                    path.params.append(Path_param(name,datatype,desc))


    def _handle_message_params(self,path,msg):
        tags= self._get_exten_list(msg,'tag')
        for tag in tags:
            keys=tag.keys()
            for key in keys:
                value =tag.attrib.get(key,None) #class id
                if value is not None:
                    cls = self._get_class_el_byid(value)
                    self._handle_class_params(key, cls, path)


    def _add_definitions(self,rs,cls,cls_id):
        defin =Defin(cls_id,cls.attrib.get('name',''),self._get_documentation(cls))
        rs.defines.append(defin)
        attrs = self.filter_els(cls, 'ownedAttribute', 'uml:Property')
        for attr in attrs:
            attr_name, datatype, desc = self._get_class_attr(attr)
            defin.attrs.append(DeAttr(attr_name, datatype, desc))


    def _handle_msg_tag(self,tag,path,rs):
        keys=tag.keys()

        # key like str|obj|array:response_code
        for key in keys:
            value =tag.attrib.get(key,None)
            ls =key.split("_")
            resp=Resp(ls[0],ls[1])
            path.resps.append(resp)
            cls = self._get_class_el_byid(value)
            if cls is not None:
                resp.class_name=cls.attrib.get('name','')

                #add definitions
                if rs.has_defin(value)==False:
                    self._add_definitions(rs,cls,value)





    def  _get_rest_path(self,rs,path,interact):
        path.action =self._get_stereotype(interact)

        #get message

        msgs =self.filter_els(interact,'message','uml:Message')
        for msg in msgs :
            if  (self._get_stereotype(msg)=='send'):
                path.name=msg.attrib.get('name','')
                self._handle_message_params(path,msg)

            #response msg
            elif  (msg.attrib.get(_type,None)=='uml:Message') and (self._get_stereotype(msg)=='ack'):
                tags = self._get_exten_list(msg, 'tag')
                for tag in tags:
                    self._handle_msg_tag( tag, path,rs)


    def _handle_package(self,pkg):
    # each package is a rest file
        rs = RestFile(pkg.attrib.get('name', ''),self._get_documentation(pkg))
        self.rests.append(rs)

        collabs =self.filter_els(pkg,'packagedElement',"uml:Collaboration")

        for collab in collabs:
            tag_name = collab.attrib.get('name', '')
            rs.tags.append(Tag(tag_name ,self._get_documentation(collab)))

        #get Interaction
            interacts =self.filter_els(collab,'ownedMember','uml:Interaction')
            for interact in interacts:
                path=Path(tag_name,interact.attrib.get('name', ''),
                          self._get_documentation(interact))
                rs.paths.append(path)
                self._get_rest_path(rs,path,interact)
                #
                #rs.paths.append(self._get_rest_path(interact,tag_name,rs))

    def parse_xml_data(self):  ##
    # get package
        pkgs =self.filter_els(self.r,'packagedElement',"uml:Package")
        for pkg in pkgs:
            self._handle_package(pkg)

if __name__ == '__main__':

    load=FileSystemLoader('./template')
    env =Environment(loader=load)
    t=env.get_template('swagger_file')


    rests = SequencetoRest()
    rests.load(r"/home/vagrant/data/docs/test.xmi")
    rests.parse_xml_data()
    for rest in rests.rests:
        print(rest.gen_text(t))