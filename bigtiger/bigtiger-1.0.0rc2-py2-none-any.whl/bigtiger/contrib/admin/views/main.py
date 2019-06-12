# -*- coding: utf-8 -*-

'''
Created on 2014-5-18
@author: linkeddt.com
'''

from __future__ import unicode_literals

import json

from bigtiger.utils.tree import tree_sorted
from bigtiger.views.generic import (PermissionMixin, SysConfContextMixin,
                                    TemplateResponseMixin, View)
from django.shortcuts import HttpResponseRedirect
from django.utils.safestring import mark_safe


def menu_order(menus):
    return sorted(menus, key=lambda e: e['order_number'], reverse=False)


def gen_menu_tree(parent_menu, menus):
    parent_menu_id = parent_menu['id']
    parent_menu_depth = (parent_menu['depth'] or 0) + 1

    chlid_menus = [item for item in menus if item['parent_id']
                   == parent_menu_id and item['depth'] == parent_menu_depth]
    chlid_menus = menu_order(chlid_menus)

    if chlid_menus:
        parent_menu['childs'] = chlid_menus
        for item in chlid_menus:
            gen_menu_tree(item, menus)


class MainView(SysConfContextMixin, PermissionMixin, TemplateResponseMixin, View):
    template_name = "admin/main.htm"

    def get(self, request, *args, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)

        ps = self.get_session_permissions()
        if ps is None:
            return HttpResponseRedirect('/')

        ps = filter(lambda item: item['status'] == 1, ps)

        root_menu = [item for item in ps if item['parent_id'] is None].pop()
        gen_menu_tree(root_menu, ps)

        cols = self.gen_menu_cols(root_menu)
        context['root_menu'] = root_menu
        context['menusJson'] = mark_safe(json.dumps(root_menu))
        context['cols'] = cols
        return self.render_to_response(context)

    def gen_menu_cols(self, root_menu):
        """ 构建菜单清单中的菜单数据(最多3级)，用于模板的显示
        """
        cols = []

        childs1 = root_menu.get('childs', [])
        for item in childs1:
            rows = []
            menu_name = item['menu_name']
            menu_id = item['id']

            childs2 = item.get('childs', None)
            if childs2:
                for item2 in childs2:
                    childs3 = item2.get('childs', None)
                    if childs3 is None:
                        rows.append(item2)
                    else:
                        for item3 in childs3:
                            rows.append(item3)
                col = {'menu_name': menu_name,
                       'rows': rows, 'menu_id': menu_id}
                cols.append(col)
        return cols
