from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse

register = template.Library()

login_html = """
    <a data-toggle="modal"  href='' data-target="#loginModal">登陆</a>/
                                   <a data-toggle="modal" href=''
                                   data-target="#registerModal">注册</a>
    """
join_vip_html = """
    <a href="{url}" class="btn btn-primary  btn-xs">加入VIP预约</a>
    """.format(url=reverse('uc:join_vip'))

order_service_html = """
    <a class="btn btn-primary btn-xs" style="color: #FFFFFF"
                                   href="{% url 'order' shop_id=shop_info.id %}">预定</a>
"""


@register.filter(name='show_vip_block')
def show_vip_block(field_val, request):
    if not request.user.is_active:
        return mark_safe(login_html)
    if not request.user.has_perm('resources.view_vip'):
        return mark_safe(join_vip_html)
    return mark_safe(field_val)


@register.filter(name='vip_order_service')
def vip_order_service(field_val, request):
    if not request.user.is_active:
        return mark_safe(login_html)
    if not request.user.has_perm('resources.view_vip'):
        return mark_safe(join_vip_html)
    return mark_safe(field_val)


@register.simple_tag
def show_shop_real(shop, request, field_name='title'):
    if not request.user.has_perm('resources.view_vip'):
        return shop.title
    else:
        return shop.real_title


@register.simple_tag
def show_vip_buy(request, group, style='btn btn-primary'):
    if not request.user.is_active:
        vip_buy_login_html = """
        <button class="{style}" data-toggle="modal"
                                                data-target="#loginModal">
                                            登陆/注册
                                        </button>
        """.format(style=style)
        return mark_safe(vip_buy_login_html)
    if not request.user.has_perm('resources.view_vip'):
        vip_buy_join_html = """
        <a href="{url}" class="{style}">
                                            加入VIP<i class="m-icon-swapright m-icon-white"></i>
                                        </a>
        """.format(url=reverse('uc:go_pay', args=[1, group.id]), style=style)
        return mark_safe(vip_buy_join_html)
    vip_more_join_html = """
            <a href="{url}" class="{style}">
                                                续费<i class="m-icon-swapright m-icon-white"></i>
                                            </a>
            """.format(url=reverse('uc:go_pay', args=[1, group.id]), style=style)
    return mark_safe(vip_more_join_html)
