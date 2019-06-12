# -*- coding: utf-8 -*-

from collections import Counter

import sqlalchemy as sa
from sqlalchemy import orm

from bigtiger.forms.models import SQLAichemyModel
from bigtiger.utils.tree import tree_node, tree_sorted
from bigtiger.utils.unique import get_uuid
from bigtiger.core.exceptions import DBError, SuspiciousOperation

from bigtiger.contrib.admin.db_admin import (
    db, AuthPermission, AuthGroupPermissions, AuthPermissionRelation)

from bigtiger.contrib.admin.models.auth_permission_relation import AuthPermissionRelationModel


class AuthPermissionModel(SQLAichemyModel):
    """用户管理|权限信息 Model
    """

    def __init__(self):
        self.session = db.get_session()

    def _get_sorted(self, sort, order):
        if sort and order:
            return getattr(getattr(AuthPermission, sort), order)()
        return None

    def get_one(self, _id):
        row = self.session.query(AuthPermission).filter(
            AuthPermission.id == _id).first_dict()
        return row

    def get_all(self, sort=None, order=None):
        query = self.session.query(AuthPermission)
        _sorted = self._get_sorted(sort, order)
        if _sorted is not None:
            query = query.order_by(_sorted)
        rows = query.all_dict()
        return rows

    def get_refer(self, _id):

        q_authgrouppermissions = self.session.query(sa.literal('AuthGroupPermissions').label('ref_code'), sa.literal('用户管理|组权限信息').label('ref_desc'),
                                                    sa.func.count('*').label('ref_count')).select_from(AuthGroupPermissions).filter(AuthGroupPermissions.permission_id == _id)

        q_authpermissionrelation = self.session.query(sa.literal('AuthPermissionRelation').label('ref_code'), sa.literal('用户管理|权限关系').label('ref_desc'),
                                                      sa.func.count('*').label('ref_count')).select_from(AuthPermissionRelation).filter(AuthPermissionRelation.permission_id == _id)

        q_authpermissionrelation = self.session.query(sa.literal('AuthPermissionRelation').label('ref_code'), sa.literal('用户管理|权限关系').label('ref_desc'),
                                                      sa.func.count('*').label('ref_count')).select_from(AuthPermissionRelation).filter(AuthPermissionRelation.chailds == _id)

        query = sa.union_all(q_authgrouppermissions,
                             q_authpermissionrelation, q_authpermissionrelation)
        t = orm.aliased(query)
        rows = self.session.query(t).all_dict()
        return rows

    def add(self, entity):
        row = AuthPermission(**entity)
        self.session.add(row)
        self.session.commit()

    def modify(self, _id, new_entity):
        self.session.query(AuthPermission).filter(
            AuthPermission.id == _id).update(new_entity)
        self.session.commit()

    def delete(self, _id):

        relationModel = AuthPermissionRelationModel()
        # 当前菜单及下级菜单
        childs = relationModel.get_list_permission_id(_id)

        if childs and len(childs) > 1:
            raise SuspiciousOperation('该菜单有下级菜单，请先删除下级菜单。')

        try:
            self.session.query(AuthPermissionRelation).filter(
                AuthPermissionRelation.permission_id == _id).delete()

            self.session.query(AuthPermissionRelation).filter(
                AuthPermissionRelation.chailds == _id).delete()

            self.session.query(AuthGroupPermissions).filter(
                AuthGroupPermissions.permission_id == _id).delete()

            self.session.query(AuthPermission).filter(
                AuthPermission.id == _id).delete()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise DBError('删除数据失败，请重试。')

    def get_detail(self, _id):
        s = self.session
        t1 = orm.aliased(AuthPermission, name='AuthPermission')
        t2 = orm.aliased(AuthPermissionRelation)

        q2 = s.query(t2.permission_id.label('parent_id')).select_from(t2).filter(
            t2.chailds == t1.id).filter(t2.depth == 1).correlate(t1).limit(1).as_scalar()

        row = s.query(t1, q2.label('parent_id')).select_from(t1).filter(
            t1.id == _id).first()

        if row is None:
            return None

        return dict(row.AuthPermission.to_dict(), parent_id=row.parent_id)

    def get_page_query(self, query, limit, offset, sort=None, order=None):
        raise NotImplementedError

    def get_list_query(self, query, sort=None, order=None):
        raise NotImplementedError

    def get_list_system(self):
        """获取系统所有的权限(包含禁用菜单及隐藏菜单)
        """
        s = self.session
        t1 = orm.aliased(AuthPermission, name='AuthPermission')
        t2 = orm.aliased(AuthPermissionRelation)

        q1 = s.query(t2).select_from(t2).filter(
            t2.permission_id == s.query(t1.id).select_from(t1).filter(t1.remark == 'root').limit(1)).subquery()
        q2 = s.query(t2.permission_id.label('parent_id')).select_from(t2).filter(
            t2.chailds == t1.id).filter(t2.depth == 1).correlate(t1).limit(1).as_scalar()

        rows = s.query(t1, q1.c.depth, q2.label('parent_id')).select_from(
            t1).outerjoin(q1, q1.c.chailds == t1.id).all()

        lst = []
        for row in rows:
            p = row.AuthPermission.to_dict()
            if p.get('is_debug', None) and p.get('menu_url_debug', None):
                p.update({'menu_url_alias': p['menu_url_debug']})
            p['depth'] = row.depth
            p['parent_id'] = row.parent_id
            lst.append(p)
        return lst

    def get_list_system_tree(self):
        lst = self.get_list_system()
        return tree_sorted(lst, key=lambda item: item['order_number'], join=lambda item,
                           parent_item: item['parent_id'] == parent_item['id'])

    def get_tree_node(self):
        def gen_node(item):
            if item['parent_id'] is None:
                return {'id': item['id'], 'text': item['menu_name'], 'checked': False,
                        'state': 'open', 'children': []}
            else:
                return {'id': item['id'], 'text': item['menu_name'],
                        'checked': False, 'state': 'closed', 'children': None, 'data': item}

        lst = self.get_list_system()
        lst = filter(lambda item: item['status'] == 1 and item['is_enable'] == 1, lst)
        return tree_node(lst, key=lambda item: item['order_number'], join=lambda item,
                         parent_item: item['parent_id'] == parent_item['id'], node=gen_node)

    def get_list_groups(self, groups):
        """通过角色的ids获取权限
        """
        sys_list = self.get_list_system()

        s = self.session
        t3 = orm.aliased(AuthGroupPermissions)
        rows = s.query(sa.distinct(t3.permission_id).label(
            'permission_id')).select_from(t3).filter(t3.group_id.in_(groups)).all()
        lst = [row.permission_id for row in rows]
        return [item for item in sys_list if item['is_enable'] == 1 and (item['id'] in lst or item['status'] == 0)]

    def tran_import(self, lst):
        raise NotImplemented

    def tran_add(self, entity, parent_id):
        if parent_id is None:
            raise ValueError('parent_id is null.')

        permission_id = entity['id']

        try:
            row = AuthPermission(**entity)
            self.session.add(row)

            # 根据上级菜单Relation添加本级菜单的Relation。
            relationModel = AuthPermissionRelationModel()
            relations = relationModel.get_list_chailds(parent_id)

            for item in relations:
                item['id'] = get_uuid()
                item['depth'] += 1
                item['chailds'] = permission_id
                row = AuthPermissionRelation(**item)
                self.session.add(row)

            relation = {'id': get_uuid(), 'permission_id': permission_id,
                        'chailds': permission_id, 'depth': 0}
            row = AuthPermissionRelation(**relation)
            self.session.add(row)

            self.session.commit()
        except Exception:
            self.session.rollback()
            raise DBError('新增数据失败，请重试。')

    def tran_modify(self, entity, parent_id):
        if parent_id is None:
            raise ValueError('parent_id is null.')

        permission_id = entity['id']

        try:
            relationModel = AuthPermissionRelationModel()
            # 上级菜单的relation
            relations = relationModel.get_list_chailds(parent_id)
            # 当前菜单及下级菜单
            childs = relationModel.get_list_permission_id(permission_id)

            for item in childs:
                # 删除当前菜单及下级菜单的relations，其中下级菜单与当前菜单的相对层级关系不变，只需删除移动后绝对层级关系要变化的部分。
                self.session.query(AuthPermissionRelation).filter(
                    AuthPermissionRelation.chailds == item['chailds']).filter(AuthPermissionRelation.depth.__gt__(item['depth'])).delete()

                # 根据新的上级菜单的relations，添加当前菜单及下级菜单绝对层级关系变化的部分。
                for relation in relations:
                    r = {}
                    r['id'] = get_uuid()
                    r['permission_id'] = relation['permission_id']
                    r['chailds'] = item['chailds']
                    r['depth'] = item['depth'] + relation['depth'] + 1
                    row = AuthPermissionRelation(**r)
                    self.session.add(row)

            self.session.commit()
        except Exception:
            self.session.rollback()
            raise DBError('修改数据失败，请重试。')

    def tran_delete(self, pks):
        raise NotImplemented
