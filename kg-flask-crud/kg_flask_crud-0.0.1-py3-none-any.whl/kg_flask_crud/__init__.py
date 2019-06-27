import os
import jwt
from functools import wraps
from flask import make_response, jsonify
from flask_restplus import Api, Resource, fields, Namespace
from flask import Flask, abort, request, jsonify, g, url_for, redirect

PUBLIC_KEY = os.environ['PUBLIC_KEY']
def requires_auth(roles): # Remove ability to send token as parameter in request
    def requires_auth_decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            def decode_token(token):
                return jwt.decode(token.encode("utf-8"), PUBLIC_KEY, algorithms='RS256')
            if roles != []:
                try:
                    decoded = decode_token(str(request.headers['Token']))
                except Exception as e:
                     return make_response(jsonify({'message': str(e)}), 401)
                if set(roles).isdisjoint(decoded['roles']):
                    return make_response(jsonify({'message': 'Not authorized for this endpoint'}),401)
            return f(*args, **kwargs)
        return decorated
    return requires_auth_decorator
ns_token = Namespace('auth_test', description='Authorization_test')
@ns_token.route('/')
class ResourceRoute(Resource):
    @ns_token.doc('token_resource',security='token')
    @requires_auth(['user','moderator','admin'])
    def get(self):
        return jsonify({'message': 'Success'})


# Special case with tags
def request_to_class(dbclass,json_request): # Make classmethod
    tags = []
    for k,v in json_request.items():
        if k == 'tags' and v != []:
            dbclass.tags = []
            set_tags = list(set(v))
            for tag in set_tags:
                tags_in_db = Tag.query.filter_by(tag=tag).all()
                if len(tags_in_db) == 0:
                    tags.append(Tag(tag=tag))
                else:
                    tags.append(tags_in_db[0])
            for tag in tags:
                dbclass.tags.append(tag)
        elif k in dbclass.many_to_many and v != []:
            cls = dbclass.many_to_many[k]
            obj = getattr(dbclass,k)
            obj = []
            [obj.append(cls.query.filter_by(uuid=uuid).first()) for uuid in list(set(v))]
        else:
            setattr(dbclass,k,v)
    return dbclass


def crud_get_list(cls,full=None):
    return jsonify([obj.toJSON(full=full) for obj in cls.query.all()])

def crud_post(cls,post,database):
    obj = request_to_class(cls(),post)
    database.session.add(obj)
    database.session.commit()
    return jsonify(obj.toJSON())

def crud_get(cls,uuid,full=None,jsonify_results=True):
    obj = cls.query.filter_by(uuid=uuid).first()
    if obj == None:
        return jsonify([])
    if jsonify_results == True:
        return jsonify(obj.toJSON(full=full))
    else:
        return obj

def crud_delete(cls,uuid,database,constraints={}):
    if constraints != {}:
        for constraint in constraints['delete']:
            if cls.query.filter_by(**{constraint: uuid}).first() != None:
                return make_response(jsonify({'message': 'UUID used elsewhere'}),501)
    database.session.delete(cls.query.get(uuid))
    database.session.commit()
    return jsonify({'success':True})

def crud_put(cls,uuid,post,database):
    obj = cls.query.filter_by(uuid=uuid).first()
    updated_obj = request_to_class(obj,post)
    db.session.commit()
    return jsonify(obj.toJSON())

class CRUD():
    def __init__(self, namespace, cls, model, name, view_auth=[], edit_auth=['admin'], delete_constraints={}, security='token',validate_json=False, custom_post=False, custom_put=False ):
        self.ns = namespace
        self.cls = cls
        self.model = model
        self.name = name

        @self.ns.route('/')
        class ListPostRoute(Resource):
            @self.ns.doc('{}_list'.format(self.name))
            @requires_auth(view_auth)
            def get(self):
                return crud_get_list(cls)
            if custom_post == False:
                @self.ns.doc('{}_create'.format(self.name),security=security)
                @self.ns.expect(model)
                @requires_auth(edit_auth)
                def post(self):
                    if validate_json == True:
                        try:
                            validate(instance=request.get_json(),schema=cls.validator)
                        except Exception as e:
                            return make_response(jsonify({'message': 'Schema validation failed: {}'.format(e)}),400)
                    if 'uuid' in request.get_json():
                        if cls.query.filter_by(uuid=request.get_json()['uuid']).first() == None:
                            return crud_post(cls,request.get_json(),db)
                        else:
                            return make_response(jsonify({'message': 'UUID taken'}),501)
                    return crud_post(cls,request.get_json(),db)
            else:
                print('Custom post and list for {}'.format(name))

        @self.ns.route('/<uuid>')
        class GetDelPutRoute(Resource):
            @self.ns.doc('{}_get'.format(self.name))
            @requires_auth(view_auth)
            def get(self,uuid):
                return crud_get(cls,uuid)

            @self.ns.doc('{}_delete'.format(self.name),security=security)
            @requires_auth(edit_auth)
            def delete(self,uuid):
                return crud_delete(cls,uuid,db,delete_constraints)

            if custom_put == False:
                @self.ns.doc('{}_put'.format(self.name),security=security)
                @self.ns.expect(self.model)
                @requires_auth(edit_auth)
                def put(self,uuid):
                    return crud_put(cls,uuid,request.get_json(),db)

        @self.ns.route('/full/')
        class FullListRoute(Resource):
            @self.ns.doc('{}_full'.format(self.name))
            @requires_auth(view_auth)
            def get(self):
                return crud_get_list(cls,full='full')

        @self.ns.route('/full/<uuid>')
        class FullRoute(Resource):
            @requires_auth(view_auth)
            @self.ns.doc('{}_full_single'.format(self.name))
            def get(self,uuid):
                return crud_get(cls,uuid,full='full')

        if validate_json == True:
            @self.ns.route('/validator')
            class ValidatorRoute(Resource):
                @self.ns.doc('{}_validator'.format(self.name))
                @requires_auth(view_auth)
                def get(self):
                    return make_response(jsonify(cls.validator),200)

def create_crud(name,description,cls,view_auth=[],edit_auth=['admin'],delete_constraints={},security='token',validate_json=False,custom_post=False,custom_put=False):
    ns_obj = Namespace(name,description=description)
    obj_model = ns_obj.schema_model(name,cls.validator)
    CRUD(ns_obj,cls,obj_model,name,view_auth=view_auth,edit_auth=edit_auth,delete_constraints=delete_constraints,security=security,validate_json=validate_json,custom_post=custom_post,custom_put=custom_put)
    return ns_obj

