"""
@project：medical_robot_backend
@language：Python3
@create：2019/5/18
@author：qianyang<qianyang@aibayes.com>
@description:none
"""


def object2dict(form):
    form_dict = dict()
    if isinstance(form, object):
        form_attr = [attr for attr in dir(form) if not attr.startswith('__') and not callable(getattr(form, attr))]
        for attr_name in form_attr:
            form_dict[attr_name] = getattr(form, attr_name)
    return form_dict
