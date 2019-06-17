#!/usr/bin/env python
#coding: utf-8
#by yangbin at 2018.11.28
import os

from .conf import *
from .swagger import *
from .helper import *

# Api model to code
'''
root apiPrefix
apiGroup # comment
    apiName [method=get] [auth='<your any auth name>'] [proto=[json, raw, reqRaw, respRaw]] # comment
        reqFiled filedType [required=true] # commen
'''

class ApiParam(object):
    def __init__(self, lineno, line, name, typ, required, comment):
        self.lineno = lineno
        self.line = line
        self.name = name
        self.typ = typ
        self.required = required
        self.comment = comment
        self.children = []
        self.isNest = False

    def addChildren(self, child):
        assert isinstance(child, ApiParam)
        self.children.append(child)
        return self

    @classmethod
    def fromLine(cls, lineno, line):
        if '#' in line:
            itemsline, comment = line.split('#', 1)
            items = itemsline.split()
        else:
            comment = ''
            items = line.split()
        assert_error(len(items) in [2, 3], '无效的参数定义', lineno, line)
        name, typ, required = items[0], items[1], True if len(items) == 2 or items[2].upper() != 'FALSE' else False
        _isList = False
        # list
        if typ.endswith('[]'):
            _isList = True
            typ = typ[:-2]
        if typ.startswith('[]'):
            _isList = True
            typ = typ[2:]
        isNest = False
        # assert_error(typ in TYPEMAPPING, '无效的参数类型定义', lineno, line)
        if typ in TYPEMAPPING:
            typ = TYPEMAPPING[typ]
            _gotyp = '[]' + typ if _isList else typ
        else:
            isNest = True
            _gotyp = '[]struct' if _isList else 'struct'
        p = cls(lineno, line, name, _gotyp, required, comment.strip())
        p.isNest = isNest
        return p
    
    def __repr__(self):
        return '%s %s %s # %s\n' % (self.name, self.typ, self.required, self.comment)

    def code(self):
        if self.required:
            tag = '`json:"%s" query:"%s" validate:"required"`' % (self.name, self.name)
        else:
            tag = '`json:"%s" query:"%s"`' % (self.name, self.name)

        if self.isNest:
            # Items *[]struct{
            # }
            line = '%s *%s{' % (upperFirst(self.name), self.typ)
            for child in self.children:
                line += child.code()
            line += '} %s // %s\n' % (tag, self.comment)
            return line
        else:
            # * 使用指针类型，由于golang 不支持默认参数，不过可以同nil和非nil 来实现
            line = '%s *%s %s // %s\n' % (upperFirst(self.name), self.typ, tag, self.comment)
            return line

class ApiDef(object):
    def __init__(self, lineno, line, group, api, method, auth, proto, comment):
        self.lineno = lineno
        self.line = line
        self.group = group
        self.api = api
        self.method = method
        self.auth = auth
        self.proto = proto
        self.comment = comment
        self.apiParams = []
        self.apiAlias = []

    def __repr__(self):
        txt = '%s %s %s # %s\n' % (self.api, self.method, self.auth, self.comment)
        for param in self.apiParams:
            isinstance(param, ApiParam)
            txt += ' ' * TAB_WIDTH * 2 + str(param)
        return txt
    
    def apiName(self):
        if '.' in self.api:
            _items = self.api.split('.')
            assert_error(len(_items) >= 2, '无效的api名称定义', self.lineno, self.line)
            return ''.join(map(lambda x: upperFirst(x), _items))
        return upperFirst(self.api)

    def handlerName(self):
        n = self.apiName()
        return n + 'Api' # UserCreateApi

    def apiRouterName(self):
        if '.' in self.api:
            _items = self.api.split('.')
            return self.api.replace('.', '/')
        return self.api

    def reqModelName(self):
        return 'Req%s%s' % (upperFirst(self.group), self.apiName())

    def apiFullName(self):
        return '%s%s' % (self.group, self.apiName())

    def reqModel(self):
        code = 'type %s struct { // %s\n' % (self.reqModelName(), self.comment)
        for param in self.apiParams:
            isinstance(param, ApiParam)
            code += ' ' * TAB_WIDTH + param.code()
        code += 'Context echo.Context `json:"-"`' # append echo.Context
        code += '}\n\n'
        return code
    
    def apiCode(self):
        if self.proto in ['raw', 'respRaw']:
            handler = '%s(r, nil)' % self.handlerName()
        else:
            handler = '%s(r, resp)' % self.handlerName()

        code = ''

        if self.proto == 'raw':
            code = '''
            func %s(c echo.Context) error {
                r := &%s{}
                r.Context = c
                %s
                return RawOKRequest(c)
            }\n
            ''' % (self.apiName(), self.reqModelName(), handler)
        elif self.proto == 'reqRaw':
            code = '''
            func %s(c echo.Context) error {
                r := &%s{}
                r.Context = c
                resp := make(map[string]interface{})
                %s
                return OKRequestWith(c, resp)
            }\n
            ''' % (self.apiName(), self.reqModelName(), handler)
        elif self.proto == 'respRaw':
            code = '''
            func %s(c echo.Context) error {
                r := &%s{}
                if err := c.Bind(r); err != nil {
                    return err
                }
                if err := c.Validate(r); err != nil {
                    return err
                }
                r.Context = c
                %s
                return RawOKRequest(c)
            }\n
            ''' % (self.apiName(), self.reqModelName(), handler)
        else:
            code = '''
            func %s(c echo.Context) error {
                r := &%s{}
                if err := c.Bind(r); err != nil {
                    return err
                }
                if err := c.Validate(r); err != nil {
                    return err
                }
                r.Context = c
                resp := make(map[string]interface{})
                %s
                return OKRequestWith(c, resp)
            }\n
            ''' % (self.apiName(), self.reqModelName(), handler)

        return code

    def apiKitPath(self):
        return 'gopher/app/api/%s/%s_kit.go' % (self.group, self.group)

    def apiResps(self):
        funcKits = GOAPIKITS_CACHE.get(self.apiKitPath(), None)
        if not funcKits:
            return []
        apiFunc = funcKits.funcs.get(self.handlerName(), None)
        if not apiFunc:
            return []
        assert isinstance(apiFunc, GoFunc)
        assert_error(self.handlerName() == apiFunc.name, '未找到函数%s返回值' % self.handlerName(), 0, '')
        return apiFunc.resps

    def apiDoc(self):
        doc = '''
/**
* @api {%s} /%s/%s %s
* @apiGroup %s
* @apiName %s
* @apiDescription %s
''' % (self.method, self.group, self.apiRouterName(), self.apiFullName(), self.group, self.apiFullName(), self.comment)
        if self.auth:
            doc += '* @apiPermission %s\n' % self.auth

        for param in self.apiParams:
            if param.required:
                doc += '* @apiParam {%s} %s %s\n' % (APIDOC_TYPE.get(param.typ, 'Object'), param.name, param.comment)
            else:
                doc += '* @apiParam {%s} [%s] %s\n' % (APIDOC_TYPE.get(param.typ, 'Object'), param.name, param.comment)
        
        funcKits = GOAPIKITS_CACHE.get(self.apiKitPath(), None)
        if funcKits:
            apiFunc = funcKits.funcs.get(self.handlerName(), None)
            if apiFunc:
                assert isinstance(apiFunc, GoFunc)
                assert_error(self.handlerName() == apiFunc.name, '未找到函数%s返回值' % self.handlerName(), 0, '')
                for resp in apiFunc.resps:
                    name, isArray, typ, typObj, comment = resp
                    typ = APIDOC_TYPE.get(typ, 'Object')
                    if isArray:
                        typ = '%s[]' % typ
                    doc += '* @apiSuccess {%s} %s %s\n' % (typ, name, comment + ' ' + typObj)
        doc += '*/\n'
        return doc
    
    @classmethod
    def fromLine(cls, lineno, line, group):
        if '#' in line:
            itemsline, comment = line.split('#', 1)
            items = itemsline.split()
        else:
            comment = ''
            items = line.split()
        assert_error(len(items) in [1, 2, 3, 4], '无效的api定义', lineno, line)
        api, method, auth, proto = items[0], 'GET', None, 'json'
        method = 'GET' if len(items) == 1 or items[1].upper() != 'POST' else 'POST'
        if len(items) in [3, 4]:
            auth = items[2]
            if auth == 'none':
                auth = None
            # assert_error(auth in AUTH_TYPE, '只支持%s' % AUTH_TYPE, lineno, line)

        if len(items) == 4:
            proto = items[3]
            assert_error(proto in PROTO_TYPE, '只支持%s' % PROTO_TYPE, lineno, line)

        return cls(lineno, line, group, api, method, auth, proto, comment.strip())

    def addApiParam(self, apiParam):
        assert isinstance(apiParam, ApiParam)
        self.apiParams.append(apiParam)


class ApiGroup(object):
    def __init__(self, lineno, line, group, comment):
        self.lineno = lineno
        self.line = line
        self.group = group
        self.comment = comment
        self.apis = []

    def __repr__(self):
        txt = '%s // %s\n' % (self.group, self.comment)
        for api in self.apis:
            isinstance(api, ApiDef)
            txt += ' ' * TAB_WIDTH + str(api)
        return txt

    def reqModel(self):
        code = ''
        for api in self.apis:
            isinstance(api, ApiDef)
            code += api.reqModel()
        return code

    def apiCode(self):
        code = '''
        // Code generated by m2c. DO NOT EDIT.
        package %s\n
        import (
            . "%s/ak/helper"
            . "%s/ak/gw/model"
           	. "%s/app/api/%s"
            "github.com/labstack/echo"
        )\n
        ''' % (self.group, MOD, MOD, MOD, self.group)
        for api in self.apis:
            isinstance(api, ApiDef)
            code += api.apiCode()
        return code

    def apiRoute(self):
        code = ''
        for api in self.apis:
            isinstance(api, ApiDef)
            if api.auth:
                code += '%s.%s("/%s", %sApi.%s, authDelegateFunc("%s"))\n' % (self.group, api.method, api.apiRouterName(), self.group, api.apiName(), api.auth)
            else:
                code += '%s.%s("/%s", %sApi.%s)\n' % (self.group, api.method, api.apiRouterName(), self.group, api.apiName())
            
            for apiAlias in api.apiAlias:
                if api.auth:
                    code += 'e.%s("%s", %sApi.%s, authDelegateFunc("%s"))\n' % (api.method, apiAlias, self.group, api.apiName(), api.auth)
                else:
                    code += 'e.%s("%s", %sApi.%s)\n' % (api.method, apiAlias, self.group, api.apiName())
        return code

    def initResps(self):
        if self.apiKitPath() not in GOAPIKITS_CACHE:
            lines = open(self.apiKitPath()).read().splitlines()
            GOAPIKITS_CACHE[self.apiKitPath()] = GoApiKits.fromlines(lines)

    def apiDoc(self):
        if self.apiKitPath() not in GOAPIKITS_CACHE:
            lines = open(self.apiKitPath()).read().splitlines()
            GOAPIKITS_CACHE[self.apiKitPath()] = GoApiKits.fromlines(lines)

        doc = ''
        for api in self.apis:
            doc += api.apiDoc()
        return doc

    def apiKitPath(self):
        return 'gopher/app/api/%s/%s_kit.go' % (self.group, self.group)

    def apiBridgePath(self):
        return 'gopher/ak/gw/bridge/%s/%s.go' % (self.group, self.group)

    @classmethod
    def fromLine(cls, lineno, line):
        if '#' in line:
            itemsline, comment = line.split('#', 1)
            items = itemsline.split()
        else:
            comment = ''
            items = line.split()
        assert_error(len(items) == 1, '无效的api组定义', lineno, line)
        group = items[0]
        assert_error(group.isalpha(), '关键字必须是有效字母', lineno, line)
        return cls(lineno, line, group, comment.strip())

    def addApi(self, api):
        assert isinstance(api, ApiDef)
        self.apis.append(api)

class ApiModel(object):
    def __init__(self, root, preifx, version, groups):
        self.root = root
        self.prefix = preifx
        self.version = version
        self.groups = groups

    def __repr__(self):
        txt = 'root %s %s\n' % (self.prefix, self.version)
        for group in self.groups:
            isinstance(group, ApiGroup)
            txt += str(group)
        return txt

    def reqModel(self):
        code = '// Code generated by m2c. DO NOT EDIT.\npackage model\nimport "github.com/labstack/echo"\n'
        for group in self.groups:
            isinstance(group, ApiGroup)
            code += group.reqModel()
        return code

    def apiCode(self):
        code = ''
        for group in self.groups:
            isinstance(group, ApiGroup)
            code += group.apiCode()
        return code

    def apiRoute(self):
        code = '// Code generated by m2c. DO NOT EDIT.\npackage gw\n'
        code += 'import (\n'
        code += ' ' * TAB_WIDTH + '"github.com/labstack/echo"\n'
        for group in self.groups:
            code += '%sApi "%s/ak/gw/bridge/%s"\n' % (group.group, MOD, group.group)
        code += ')\n'

        code += 'type AuthDelegateFunc func(name string) echo.MiddlewareFunc\n'
        code += 'func LoadServiceApi(e *echo.Echo, authDelegateFunc AuthDelegateFunc) (g *echo.Group) {\n'
        code += 'root := e.Group("/%s/%s")\n\n' % (self.prefix, self.version)
        for group in self.groups:
            code += '%s := root.Group("/%s")\n' % (group.group, group.group)
            code += group.apiRoute()
            code += '\n'
        code += 'return root\n'
        code += '}\n'
        return code

    def initResps(self):
        for group in self.groups:
            group.initResps()

    def apiDoc(self):
        doc = '// Code generated by m2c. DO NOT EDIT.\npackage gw\n'
        doc += '''
 /**
 * @apiDefine userAuth 用户登录
 * 当前接口需要用户登录授权
 */
 
 /**
 * @apiDefine adminAuth 管理员登录
 * 当前接口需要管理员登录授权
 */
 '''
        for group in self.groups:
            doc += group.apiDoc()
            doc += '\n'
        return doc

    def genApiKit(self, group):
        isinstance(group, ApiGroup)
        kitPath = group.apiKitPath()
        code = ''
        if not os.path.exists(kitPath):
            code += 'package %s\n' % group.group
            code += 'import (\n'
            code += '. "%s/ak/gw/model"\n' % MOD
            code += ')\n'
            for api in group.apis:
                code += '// %s\n' % api.comment
                code += 'func %s(req *%s, resp map[string]interface{}) {\n' % (api.handlerName(), api.reqModelName())
                code += 'return\n}\n'
        else:
            # append kit
            oldFuncs = getCodeFuncs(kitPath)
            for api in group.apis:
                if api.handlerName() in oldFuncs:
                    continue

                code += '// %s\n' % api.comment
                code += 'func %s(req *%s, resp map[string]interface{}) {\n' % (api.handlerName(), api.reqModelName())
                code += 'return\n}\n'

        appendCode(kitPath, code)

    def genApiCode(self):
        # api model
        modelPath = 'gopher/ak/gw/model/model.go'
        writeCode(modelPath, self.reqModel())

        # api group
        for group in self.groups:
            isinstance(group, ApiGroup)
            code = group.apiCode()
            apiPath = group.apiBridgePath()
            writeCode(apiPath, code)
            self.genApiKit(group)
        
        # route
        routePath = 'gopher/ak/gw/router.go'
        writeCode(routePath, self.apiRoute())

        os.system('gofmt -w gopher/app gopher/ak')

    @classmethod
    def fromLines(cls, lines):
        PREFIX = ''
        VERSION = 'v1'
        lineno = 1
        root = lines[0].strip()
        assert_error(root[0].isalpha(), '开头必须是有效字母', lineno, root)
        items = root.split(' ')
        assert_error(len(items) >= 2, '无效的apimodel', lineno, root)
        assert_error(items[0] == 'root', '无效的apimodel', lineno, root)
        PREFIX = items[1]
        assert_error(PREFIX.isalpha(), '关键字必须是有效字母', lineno, root)
        if len(items) == 3:
            VERSION = items[2]
            assert_error(VERSION.startswith('v'), '版本必须以v开头', lineno, root)
            assert_error(VERSION[1:].isdigit(), '版本必须是数字', lineno, root)

        parentDeep = 0
        groups = []
        currentGroup = None
        currentApi = None
        currentNestParam = []
        for line in lines[1:]:
            lineno += 1

            if not line.strip():
                continue
            
            width = len(line) - len(line.lstrip())
            assert_error(width % TAB_WIDTH == 0, '宽带不是%s的倍数' % TAB_WIDTH, lineno, line)
            deep = width / TAB_WIDTH
            # assert_error(deep <= API_MAX_DEEP_NUM, '深度不能超过%s' % API_MAX_DEEP_NUM, lineno, line)

            line = line.strip()
            # clean nest param
            if deep in [0, 1] and len(currentNestParam) > 0 and currentApi:
                currentNestParam = []

            # group
            if deep == 0:
                currentGroup = ApiGroup.fromLine(lineno, line)
                groups.append(currentGroup)
            # api
            elif deep == 1:
                assert currentGroup
                currentApi = ApiDef.fromLine(lineno, line, currentGroup.group)
                currentGroup.addApi(currentApi)
            # param
            elif deep == 2:
                assert currentApi
                if line.startswith('- alias:'):
                    apiAlias = line.lstrip('- alias:').strip().split(',')
                    currentApi.apiAlias = apiAlias
                else:
                    param = ApiParam.fromLine(lineno, line)
                    if param.isNest:
                        currentNestParam.append(param)
                    currentApi.addApiParam(param)
            else:
                # nest param
                nestParam = currentNestParam[deep-3]
                assert currentApi
                param = ApiParam.fromLine(lineno, line)
                if param.isNest:
                    currentNestParam.append(param)
                nestParam.addChildren(param)

        return cls(root, PREFIX, VERSION, groups)

class GoFunc(object):
    def __init__(self, name):
        self.name = name
        self.params = []
        self.resps = []

    def __str__(self):
        return '%s - %s - %s' % (self.name, self.params, self.resps)

GOAPIKITS_CACHE = {}
class GoApiKits(object):
    def __init__(self):
        self.funcs = {}
    
    @classmethod
    def fromlines(cls, lines):
        kit = cls()
        current_gofunc = None
        for line in lines:
            # func start
            if line.startswith('func'):
                if 'Api(req' not in line: # not api func
                    continue
                idx = line.find('(')
                funcname = line[:idx].split()[1]

                current_gofunc = GoFunc(funcname)

                left = line[idx+1:]
                idx = left.find(')')
                right = left[:idx]
                for ps in right.split(','):
                    current_gofunc.params.append(set(ps.split()))


            # func end
            if line.startswith('}'):
                if current_gofunc:
                    kit.funcs[current_gofunc.name] = current_gofunc

                current_gofunc = None

            # not in func
            if current_gofunc is None:
                continue

            # func body
            line = line.strip()
            if not line.startswith('resp'):
                continue
            
            comment = ''
            value_type = 'object'
            typObj = ''
            isArray = False

            idx = line.rfind('//')
            if idx != -1:
                # comment for type doc
                comment = line[idx+2:].strip()
                if comment.startswith('@'):
                    typObj = comment.split(' ', 1)[0].strip('@')
                    comment = comment.lstrip('@%s' % typObj).strip()
                elif comment.startswith('object='):
                    typObj = comment.split(' ', 1)[0].lstrip('object=')
                    comment = comment.lstrip('object=%s' % typObj).strip()
                else:
                    vcs = comment.split(' ', 1)
                    if len(vcs) == 2:
                        value_type, comment = vcs
                        # value_type = APIDOC_TYPE.get(value_type, 'object')

                if typObj.startswith('[]'):
                    isArray = True
                    typObj = typObj.lstrip('[]')
            
            t = line[5]
            if t == '"':
                # resp["xxx"]
                line = line[6:]
                idx = line.find('"]')
            else:
                # resp[value]
                line = line[5:]
                idx = line.find(']')
            resp = line[:idx]
            current_gofunc.resps.append((resp, isArray, value_type, typObj, comment))
        return kit
