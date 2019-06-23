#!/usr/bin/env python
#coding: utf-8
#by yangbin at 2018.11.28

import os
from .apimodel import ApiModel, ApiDef
from .objmodel import ObjModel
from conf import Color

# OpenAPI Swargger https://swagger.io/specification/v2

SWAGGER_INDEX = '''
<!-- HTML for static distribution bundle build -->
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.22.0/swagger-ui.css" >
    <style>
      html
      {
        box-sizing: border-box;
        overflow: -moz-scrollbars-vertical;
        overflow-y: scroll;
      }

      *,
      *:before,
      *:after
      {
        box-sizing: inherit;
      }

      body
      {
        margin:0;
        background: #fafafa;
      }
    </style>
  </head>

  <body>
    <div id="swagger-ui"></div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.22.0/swagger-ui-bundle.js"> </script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.22.0/swagger-ui-standalone-preset.js"> </script>
    <script>
    window.onload = function() {
      // Begin Swagger UI call region
      let hash = window.location.hash
      let url = window.location.href
      url = url.replace(hash, '') + '.yaml'
      const ui = SwaggerUIBundle({
        url: url,
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIStandalonePreset
        ],
        plugins: [
          SwaggerUIBundle.plugins.DownloadUrl
        ],
        layout: "StandaloneLayout"
      })
      // End Swagger UI call region

      window.ui = ui
    }
  </script>
  </body>
</html>
'''

class SwaggerInformation(object):
    def __init__(self, title, description, version):
        self.title = title
        self.description = description
        self.version = version

    def todict(self):
        return {'title': self.title, 'description': self.description, 'version': self.version}

class SwaggerTag(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def todict(self):
        return {'name': self.name, 'description': self.description}

class Swagger(object):
    def __init__(self, host, basePath=''):
        self.swaggerVersion = '2.0'
        self.host = host
        self.basePath = basePath
        self.schemes = ['https']
        self.produces = ['application/json']
        self.tags = [] # groups
        self.paths = {} # apis {"/login", SwaggerItem}
        self.definitions = {} # models, properties_name: properties
        self.info = None

    def goType2SwaggerType(self, typ):
        # array, boolean, integer, null, number, object, string
        if typ.startswith('[]'):
            return 'array'

        if typ.startswith('str'):
            return 'string'

        if typ.startswith('num'):
            return 'number'

        if typ.startswith('int'):
            return 'number'

        if typ.startswith('float'):
            return 'number'

        if typ.startswith('bool'):
            return 'boolean'

        if typ.startswith('map'):
            return 'object'

        return 'object'


    def setInfo(self, title, description, version):
        self.info = SwaggerInformation(title, description, version)

    def addTag(self, name, description):
        self.tags.append(SwaggerTag(name, description))

    def addPath(self, name, sgItem):
        assert isinstance(sgItem, SwaggerItem)
        assert name not in self.paths
        self.paths[name] = sgItem

    def addDefinition(self, name, sgProp):
        assert isinstance(sgProp, SwaggerPropertie)
        assert name not in self.definitions, Color.red('definition "%s" conflict.' % name)
        self.definitions[name] = sgProp

    def todict(self):
        d = {'swagger': self.swaggerVersion, 'host': self.host, 'basePath': self.basePath}
        d['schemes'] = self.schemes
        dps = {}
        for k, v in self.paths.iteritems():
            dps[k] = v.todict()
        d['paths'] = dps
        dds = {}
        for k, v in self.definitions.iteritems():
            dds[k] = v.todict()
        d['definitions'] = dds
        d['tags'] = map(lambda x: x.todict(), self.tags)
        if self.info:
            d['info'] = self.info.todict()
        return d


class SwaggerItem(object):
    def __init(self, postop=None, getop=None):
        self.path = '' # /user/login
        self.postop = postop # post operation
        self.getop = getop # get operation

    def setGetOperation(self, op):
        assert isinstance(op, SwaggerOperation)
        self.getop = op

    def setPostOperation(self, op):
        assert isinstance(op, SwaggerOperation)
        self.postop = op
    
    def todict(self):
        d = {}
        if hasattr(self, 'getop') and self.getop:
            d['get'] = self.getop.todict()
        if hasattr(self, 'postop') and self.postop:
            d['post'] = self.postop.todict()
        return d


class SwaggerOperation(object):
    def __init__(self, summary, description, operationID):
        self.summary = summary # short desc
        self.description = description
        self.operationID = operationID # apiName
        self.tags = [] # apiGroup
        self.consumes = [] # req content-type
        self.produces = [] # resp content-type
        self.parameters = []
        self.responses = []
        # self.security = None

    def addTag(self, tag):
        self.tags.append(tag)

    def addProduce(self, produce):
        self.produces.append(produce)

    def addParam(self, param):
        assert isinstance(param, SwaggerParameter)
        self.parameters.append(param)

    def addResp(self, resp):
        assert isinstance(resp, SwaggerResponse)
        self.responses.append(resp)

    def todict(self):
        d = {'summary': self.summary, 'description': self.description, 'operationId': self.operationID}
        if len(self.tags) > 0:
            d['tags'] = self.tags
        if len(self.consumes) > 0:
            d['consumes'] = self.consumes
        else:
            d['consumes'] = ['application/json']
        if len(self.produces) > 0:
            d['produces'] = self.produces
        else:
            d['produces'] = ['application/json']
        if len(self.parameters) > 0:
            d['parameters'] = map(lambda x: x.todict(), self.parameters)
        if len(self.responses) > 0:
            respd = {}
            for resp in self.responses:
                respd[resp.status_code] = resp.todict()
            d['responses'] = respd
        return d


class SwaggerParameter(object):
    def __init__(self, in_, name, description, required=True):
        self.in_ = in_
        self.name = name # param_name
        self.description = description
        self.required = required

        self.schema = None # in body

        self.type = '' # not in body
        self.format = '' # not in body
        self.items = [] # not in body, array item type

        self.default = None

    def setSchema(self, sc):
        assert isinstance(sc, SwaggerSchema)
        self.schema = sc

    def setInQuery(self, type, format):
        self.type = type
        self.format = format

    def addParameterItems(self, item):
        assert isinstance(item, SwaggerParameterItems)
        self.items.append(item)

    def todict(self):
        d = {'in': self.in_, 'name': self.name, 'description': self.description, 'required': self.required}
        if self.in_ == 'body' and self.schema:
            d['schema'] = self.schema.todict()
        else:
            if self.type:
                d['type'] = self.type
            # if self.format:
            #     d['format'] = self.format
            if len(self.items) > 0:
                d['items'] = map(lambda x: x.todict(), self.items)
        if self.default:
            d['default'] = self.default
        return d

class SwaggerParameterItems(object):
    def __init__(self, type, format):
        self.type = type
        self.format = format
        self.default = None
        self.items = [] # nest

    def addParameterItems(self, item):
        assert isinstance(item, SwaggerParameterItems)
        self.items.append(item)

    def todict(self):
        d = {}
        if self.type:
            d['type'] = self.type
        # if self.format:
        #     d['format'] = self.format

        if self.default:
            d['default'] = self.default

        if len(self.items) > 0:
            d['items'] = map(lambda x: x.todict(), self.items)
        return d


class SwaggerSchema(object):
    def __init__(self, type, ref, title, format, description, ):
        self.type = type # array / object
        self.ref = ref
        self.title = title
        self.format = format
        self.description = description

        self.required = [] # param_name in properties
        self.items = None # type array's item schema
        self.properties = {} # param_name : propertie
        self.enum = [] # options
        self.example = {} # param_name : param_value

    def addRequiredParam(self, name):
        self.required.append(name)

    def addPropItem(self, name, prop):
        assert isinstance(prop, SwaggerPropertie)
        self.properties[name] = prop

    def setArrayItems(self, schemaItem):
        assert isinstance(schemaItem, SwaggerSchema)
        self.type = 'array'
        self.items = schemaItem

    def todict(self):
        d = {}
        if self.ref:
            d['$ref'] = self.ref
        elif self.items:
            d['items'] = self.items.todict()
        else:
            # d.update({'description': self.description})
            d.update({'title': self.title, 'description': self.description})
            if self.type:
                d['type'] = self.type
            # if self.format:
            #     d['format'] = self.format

        if len(self.required) > 0:
            d['required'] = self.required

        dp = {}
        for k, v in self.properties.iteritems():
            dp[k] = v.todict()
        if len(dp) > 0:
            d['properties'] = dp
        if len(self.enum) > 0:
            d['enum'] = self.enum

        if len(self.example) > 0:
            d['example'] = self.example
        return d

class SwaggerPropertie(object):
    def __init__(self, name, type, ref, title, format, description):
        self.name = name
        self.type = type
        self.ref = ref
        self.title = title
        self.format = format
        self.description = description
        self.required = []
        self.default = None
        self.items = None # type == array, set items
        self.additionalProperties = None

        self.properties = {}
    
    def setPropArrayItem(self, item):
        assert isinstance(item, SwaggerPropertie)
        self.items = item

    def addPropertie(self, name, item):
        assert isinstance(item, SwaggerPropertie)
        self.properties[name] = item

    def addRequiredParam(self, name):
        self.required.append(name)

    def todict(self):
        d = {}
        if self.ref:
            d['$ref'] = self.ref
        else:
            d.update({'type': self.type, 'description': self.description})
            # d.update({'type': self.type, 'title': self.title, 'description': self.description})
            # if self.format:
            #     d['format'] = self.format
        if len(self.required) > 0:
            d['required'] = self.required
        if self.default:
            d['default'] = self.default
        if self.items and self.type == 'array':
            d['items'] = self.items.todict()
        if self.additionalProperties:
            d['additionalProperties'] = self.additionalProperties.todict()
        
        dp = {}
        for k, v in self.properties.iteritems():
            dp[k] = v.todict()
        if len(dp) > 0:
            d['properties'] = dp
        return d

class SwaggerResponse(object):
    def __init__(self, description, status_code='200'):
        self.status_code = status_code
        self.description = description
        self.schema = None

    def setSchema(self, sc):
        assert isinstance(sc, SwaggerSchema)
        self.schema = sc

    def todict(self):
        d = {'description': self.description}
        if self.schema:
            d['schema'] = self.schema.todict()
        return d

class GoStruct(object):
    def __init__(self, name, isArray, comment):
        self.name = name
        self.isArray = isArray
        self.comment = comment
        self.fields = []

# apidef -> swagger model def
def _apiParams2SwaggerDef(sg, sgdef, params):
    for pa in params:
        if pa.required:
            sgdef.addRequiredParam(pa.name)

        typ = sg.goType2SwaggerType(pa.typ)
        ref = ''
        # items
        paramProp = SwaggerPropertie(pa.name, typ, ref, pa.name, typ, pa.comment)

        if len(pa.children) > 0:
            childs = SwaggerPropertie('item', 'object', '', '', '', pa.comment)
            # items.item
            childs = _apiParams2SwaggerDef(sg, childs, pa.children)
            paramProp.setPropArrayItem(childs)

        elif typ == 'array':
            itemType = sg.goType2SwaggerType(pa.typ.strip('[]'))
            childs = SwaggerPropertie('item', itemType, '', '', '', pa.comment)
            paramProp.setPropArrayItem(childs)

        # object.field
        sgdef.addPropertie(pa.name, paramProp)
    return sgdef


def _getGoStruct(lines):
    cs = None
    si = {}
    for line in lines:
        # not in type struct
        if not line.strip().startswith('type') and 'struct' not in line and not cs:
            continue
        
        # type struct define
        if line.strip().startswith('type') and 'struct' in line:
            items = line.strip().split(' ')
            assert len(items) >= 4
            cs = items[1]

            si[cs] = []
            continue # next line

        # end struct, do not strip line
        if line.startswith('}'):
            cs = None
            continue # next line

        # struct body
        idx = line.find('//')
        comment = ''
        if idx != -1:
            comment = line[idx+2:].strip()
            line = line[:idx].strip()
        
        typObj = ''
        tag = ''
        idx = line.find('`')
        if idx != -1:
            tag = line[idx+7:line.find('"', idx+7)]
            line = line[:idx].strip()

        # xx string, trick way to split by N space
        items = ' '.join(line.split(' ')).split()

        # case:
        # type Obj struct {
        #     OtherObj
        #     xxx string
        # }
        if len(items) == 0:
            continue

        if len(items) == 1: # object inject
            objname = items[0]
            typ = 'object'
            if objname.startswith('[]'):
                typ = '[]object'

            typObj = objname.lstrip('[]').lstrip('*')
            typObj = typObj.split(".")[-1]
        else:
            typ = items[1]
            if tag == '':
                tag = items[0]

        requried = True
        if 'omitempty' in tag:
            requried = False

        # `name,omitempty xx,xxx`
        idx = tag.find(',')
        if idx != -1:
            tag = tag[:idx]

        isArray = False

        if typ.startswith('[]'):
            isArray = True
            typ = typ.lstrip('[]')

        if typ.startswith('*'):
            typ = typ.lstrip('*')

        if len(items) > 1 and typ not in ['string', 'int64', 'bool']: # not in base type
            typObj = typ
            typ = 'Object'
            # comment for type doc
            # comment = line[idx+2:].strip()
            # if comment.startswith('[]'):
            #     isArray = True
            #     comment = comment.lstrip('[]')

            if comment.startswith('@'):
                typObj = comment.split(' ')[0].lstrip('@')
                comment = comment.lstrip('@%s' % typObj).strip()
            elif comment.startswith('object='):
                typObj = comment.split(' ')[0].lstrip('object=')
                comment = comment.lstrip('object=%s' % typObj).strip()

            if typObj.startswith('[]'):
                isArray = True
                typObj = typObj.lstrip('[]')

        i = (requried, tag, isArray, typ, typObj, comment)

        si[cs].append(i)
    return si
        


def genSwaggerContent(url, title, description, version):
    # sg
    sg = Swagger(url)
    sg.setInfo(title, description, version)

    # user defines
    infoPath = 'gopher/app/info/info.go'
    lines = open(infoPath).read().splitlines()
    ds = _getGoStruct(lines)
    for item in ds.iteritems():
        name, props = item
        propItem = SwaggerPropertie(name, 'object', '', name, 'object', name)

        for prop in props:
            requried, param, isArray, typ, refObj, comment = prop
            if requried:
                propItem.addRequiredParam(param)

            typ = sg.goType2SwaggerType(typ)

            ref = ''
            if refObj:
                typ = 'object'
                ref = '#/definitions/%s' % refObj

            paramProp = SwaggerPropertie(param, typ, ref, name, typ, comment)
            if isArray:
                swprArray = SwaggerPropertie('', 'array', '', '', 'array', comment) # here ref need stuff
                swprArray.setPropArrayItem(paramProp)
                propItem.addPropertie(param, swprArray)
            else:
                propItem.addPropertie(param, paramProp)

        sg.addDefinition(name, propItem)
    
    # model defines
    lines = open('objmodel.txt', 'rb').readlines()
    objModel = ObjModel.fromLines(lines)
    objModel.checkObjCode() 
    # obj
    for topobj in objModel.root.children:
        objs = topobj.getObjs()
        for obj in objs:
            objname, comment, objfields = obj
            propItem = SwaggerPropertie(objname, 'object', '', objname, 'object', comment)

            for prop in objfields:
                param, isArray, typ, comment = prop
                propItem.addRequiredParam(param)

                ref = ''
                typ = sg.goType2SwaggerType(typ)

                paramProp = SwaggerPropertie(param, typ, ref, param, typ, comment)
                propItem.addPropertie(param, paramProp)

            sg.addDefinition(objname, propItem)


    # api
    lines = open('apimodel.txt', 'rb').readlines()
    apiModel = ApiModel.fromLines(lines)
    apiModel.initResps()
    for group in apiModel.groups:
        sg.addTag(group.group, group.comment)

        for api in group.apis:
            path = SwaggerItem()
            op = SwaggerOperation(api.apiName(), api.comment, api.apiFullName())
            if api.proto == 'raw':
                op.addProduce('application/octet-stream')
            else:
                op.addProduce('application/json')

            op.addTag(api.group)

            # api req model
            propItem = SwaggerPropertie(api.reqModelName(), 'object', '', api.reqModelName(), 'object', api.comment)
            propItem = _apiParams2SwaggerDef(sg, propItem, api.apiParams)
            sg.addDefinition(api.reqModelName(), propItem)

            # request param
            paramIn = 'query' if api.method.lower() == 'get' else 'body'
            if paramIn == 'body':
                swpa = SwaggerParameter(paramIn, 'body', api.comment, True) 
                swpa.schema = SwaggerSchema('object', '#/definitions/%s' % api.reqModelName(), api.apiFullName(), '', api.comment)
                op.addParam(swpa)
            else:
                for pa in api.apiParams:
                    swpa = SwaggerParameter(paramIn, pa.name, pa.comment, pa.required)
                    swpa.setInQuery(sg.goType2SwaggerType(pa.typ), pa.typ)
                    op.addParam(swpa)

            # response
            scrp = SwaggerSchema('object', '', api.apiFullName(), '', api.comment)
            for rp in api.apiResps():
                name, isArray, typ, typObj, comment = rp 
                scrp.addRequiredParam(name)

                typ = sg.goType2SwaggerType(typ)
                ref = ''
                if typObj:
                    ref = '#/definitions/%s' % typObj
                    typ = 'object'

                # single object or array object
                swpr = SwaggerPropertie(name, typ, ref, name, typ, comment) # here ref need stuff
                if not isArray:
                    scrp.addPropItem(name, swpr)
                else:
                    swprArray = SwaggerPropertie('', 'array', '', '', 'array', comment) # here ref need stuff
                    swprArray.setPropArrayItem(swpr)
                    scrp.addPropItem(name, swprArray)

            swrp = SwaggerResponse(api.comment)
            swrp.setSchema(scrp)
            op.addResp(swrp)

            if api.method.lower() == 'get':
                path.setGetOperation(op)
            else:
                path.setPostOperation(op)

            apiName = '/api/%s/%s/%s' % (apiModel.version, api.group, api.apiRouterName())
            sg.addPath(apiName, path)
    

    d = sg.todict()
    from yaml import safe_dump
    return safe_dump(d)


def genSwaggerYaml(savePath, url, title, description, version):
    content = genSwaggerContent(url, title, description, version)
    fp = open(savePath, 'wb')
    fp.write('# Code generated by m2c. DO NOT EDIT.\n')
    fp.write(content)
    fp.close()


def genSwaggerGwGo(savePath, url, title, description, version):
    save_path = 'gopher/ak/gw/swagger.go'
    content = genSwaggerContent(url, title, description, version)
    fp = open(savePath, 'wb')
    code = '''
// Code generated by m2c. DO NOT EDIT.
package gw

const SWAGGER_INDEX = `
%s
`

const SWAGGER_CONTENT = `
%s
`
    ''' % (SWAGGER_INDEX, content)
    fp.write(code)
    fp.close()
    os.system('gofmt -w gopher/ak/gw')
