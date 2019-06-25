# -*- coding: utf-8 -*-
'''
diacamma.invoice views package

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2015 sd-libre.fr
@license: This file is part of Lucterios.

Lucterios is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Lucterios is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals
from datetime import datetime, timedelta
import logging

from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.db.models.functions import Concat
from django.db.models.query import QuerySet
from django.db.models import Q, Value
from django.conf import settings
from django.utils import six, timezone
from django.apps.registry import apps

from lucterios.framework.xferbasic import XferContainerAbstract
from lucterios.framework.xferadvance import XferAddEditor, XferListEditor, \
    XferSave, TITLE_ADD, TITLE_MODIFY, TITLE_DELETE, TITLE_OK, TITLE_CANCEL,\
    TITLE_CLOSE
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import ActionsManage, MenuManage, \
    FORMTYPE_REFRESH, CLOSE_NO, FORMTYPE_MODAL, CLOSE_YES, SELECT_SINGLE, \
    WrapAction, SELECT_MULTI
from lucterios.framework.xfergraphic import XferContainerAcknowledge, \
    XferContainerCustom
from lucterios.framework.xfercomponents import XferCompLabelForm, \
    XferCompEdit, XferCompImage, XferCompMemo, XferCompSelect
from lucterios.framework.error import LucteriosException, MINOR, IMPORTANT
from lucterios.framework.models import get_value_if_choices

from diacamma.payoff.models import Payoff, Supporting, PaymentMethod, BankTransaction
from diacamma.accounting.models import Third
from lucterios.CORE.models import PrintModel
from lucterios.CORE.parameters import Params


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", condition=lambda xfer, gridname='': abs(xfer.item.get_total_rest_topay()) > 0.001)
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@MenuManage.describ('payoff.add_payoff')
class PayoffAddModify(XferAddEditor):
    icon = "payoff.png"
    model = Payoff
    field_id = 'payoff'
    caption_add = _("Add payoff")
    caption_modify = _("Modify payoff")

    def fillresponse_multisave(self, supportings=(), amount=0.0,
                               mode=0, payer='', reference='',
                               bank_account=0, date=None, fee_bank=0.0, repartition=0):
        if self.item.id is not None:
            self.item.delete()
        Payoff.multi_save(supportings, amount, mode, payer, reference, bank_account, date, fee_bank, repartition)

    def run_save(self, request, *args, **kwargs):
        supportings = self.getparam('supportings', ())
        if len(supportings) > 0:
            multisave = XferContainerAcknowledge()
            multisave.is_view_right = self.is_view_right
            multisave.locked = self.locked
            multisave.model = self.model
            multisave.field_id = self.field_id
            multisave.caption = self.caption
            multisave.closeaction = self.closeaction
            multisave.fillresponse = self.fillresponse_multisave
            return multisave.get(request, *args, **kwargs)
        else:
            return XferAddEditor.run_save(self, request, *args, **kwargs)

    def fillresponse(self):
        if self.item.id is not None:
            self.items = Payoff.objects.filter(entry=self.item.entry)
            amount = 0
            supportings = []
            for item in self.items:
                supportings.append(six.text_type(item.supporting.id))
                amount += item.amount
            self.params['supportings'] = ";".join(supportings)
            self.params['amount'] = amount
        XferAddEditor.fillresponse(self)


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('payoff.delete_payoff')
class PayoffDel(XferDelete):
    icon = "payoff.png"
    model = Payoff
    field_id = 'payoff'
    caption = _("Delete payoff")


@ActionsManage.affect_other(_('change'), 'images/edit.png')
@MenuManage.describ('')
class SupportingThird(XferListEditor):
    icon = "diacamma.accounting/images/thirds.png"
    model = Supporting
    field_id = 'supporting'
    caption = _("Select third")

    def __init__(self, **kwargs):
        self.model = Third
        self.field_id = 'third'
        XferListEditor.__init__(self, **kwargs)
        self.action_list = []
        self.code_mask = ''

    def get_items_from_filter(self):
        items = self.model.objects.annotate(completename=Concat('contact__individual__lastname', Value(' '), 'contact__individual__firstname')).filter(self.filter)
        sort_third = self.getparam('GRID_ORDER%third', '')
        sort_thirdbis = self.getparam('GRID_ORDER%third+', '')
        self.params['GRID_ORDER%third'] = ""
        if sort_third != '':
            if sort_thirdbis.startswith('-'):
                sort_thirdbis = "+"
            else:
                sort_thirdbis = "-"
            self.params['GRID_ORDER%third+'] = sort_thirdbis
        items = sorted(items, key=lambda t: six.text_type(t).lower(), reverse=sort_thirdbis.startswith('-'))
        if self.getparam('show_filter', 0) == 2:
            items = [item for item in items if abs(item.get_total()) > 0.0001]
        res = QuerySet(model=Third)
        res._result_cache = items
        return res

    def fillresponse_header(self):
        if 'status_filter' in self.params:
            del self.params['status_filter']
        contact_filter = self.getparam('filter', '')
        comp = XferCompEdit('filter')
        comp.set_value(contact_filter)
        comp.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        comp.set_location(0, 2, 2)
        comp.is_default = True
        comp.description = _('Filtrer by contact')
        self.add_component(comp)
        self.filter = Q(status=0)
        if self.code_mask != '':
            self.filter &= Q(accountthird__code__regex=self.code_mask)
        if contact_filter != "":
            q_legalentity = Q(contact__legalentity__name__icontains=contact_filter)
            q_individual = (Q(contact__individual__firstname__icontains=contact_filter) | Q(contact__individual__lastname__icontains=contact_filter))
            self.filter &= (q_legalentity | q_individual)

    def fillresponse(self, code_mask=''):
        self.code_mask = code_mask
        XferListEditor.fillresponse(self)
        grid = self.get_components(self.field_id)
        grid.add_action(self.request, SupportingThirdValid.get_action(_('select'), 'images/ok.png'),
                        modal=FORMTYPE_MODAL, close=CLOSE_YES, unique=SELECT_SINGLE, pos_act=0)
        self.actions = []
        self.add_action(WrapAction(TITLE_CLOSE, 'images/close.png'))


@MenuManage.describ('')
class SupportingThirdValid(XferSave):
    redirect_to_show = False
    icon = "diacamma.accounting/images/thirds.png"
    model = Supporting
    field_id = 'supporting'
    caption = _("Select third")


def can_send_email(xfer):
    from django.utils.module_loading import import_module
    if apps.is_installed("lucterios.mailing"):
        fct_mailing_mod = import_module('lucterios.mailing.functions')
        return fct_mailing_mod.will_mail_send()
    else:
        return False


@ActionsManage.affect_show(_("Send"), "lucterios.mailing/images/email.png", condition=can_send_email)
@MenuManage.describ('invoice.change_bill')
class PayableEmail(XferContainerAcknowledge):
    caption = _("Send by email")
    icon = "payments.png"
    model = Supporting
    field_id = 'supporting'

    def fillresponse(self, item_name='', subject='', message='', model=0, modelname=""):
        def replace_tag(contact, text):
            text = text.replace('#name', contact.get_final_child().get_presentation() if contact is not None else '???')
            text = text.replace('#doc', six.text_type(self.item.get_docname()))
            text = text.replace('#reference', six.text_type(self.item.reference))
            return text

        if item_name != '':
            if modelname != '':
                self.model = apps.get_model(modelname)
            self.items = self.model.objects.filter(id__in=self.getparam(item_name, ()))
        self.items = [item.get_final_child() for item in self.items]
        if len(self.items) > 0:
            self.item = self.items[0]
            self.model = self.item.__class__
        if self.getparam("OK") is None:
            dlg = self.create_custom()
            icon = XferCompImage('img')
            icon.set_location(0, 0, 1, 6)
            icon.set_value(self.icon_path())
            dlg.add_component(icon)

            subject = Params.getvalue('payoff-email-subject')
            message = Params.getvalue('payoff-email-message')
            message = message.replace('%(name)s', '#name')
            message = message.replace('%(doc)s', '#doc')
            if len(self.items) > 1:
                edt = XferCompLabelForm('nb_item')
                edt.set_value(len(self.items))
                edt.set_location(1, 1)
                edt.description = _('nb of sending')
                dlg.add_component(edt)
            else:
                contact = self.item.contact.get_final_child()
                subject = replace_tag(contact, subject)
                message = replace_tag(contact, message)
            edt = XferCompEdit('subject')
            edt.set_value(subject)
            edt.set_location(1, 2)
            edt.description = _('subject')
            dlg.add_component(edt)
            memo = XferCompMemo('message')
            memo.description = _('message')
            memo.set_value(message)
            memo.with_hypertext = True
            memo.set_size(130, 450)
            memo.set_location(1, 3)
            dlg.add_component(memo)
            selectors = PrintModel.get_print_selector(2, self.model)[0]
            sel = XferCompSelect('model')
            sel.set_select(selectors[2])
            sel.set_location(1, 4)
            sel.description = selectors[1]
            dlg.add_component(sel)
            dlg.add_action(self.get_action(TITLE_OK, 'images/ok.png'), params={"OK": "YES"})
            dlg.add_action(WrapAction(TITLE_CANCEL, 'images/cancel.png'))
        else:
            if len(self.items) == 1:
                html_message = "<html>"
                html_message += message.replace('{[newline]}', '<br/>\n').replace('{[', '<').replace(']}', '>')
                if self.item.payoff_have_payment() and (len(PaymentMethod.objects.all()) > 0):
                    html_message += get_html_payment(self.request.META.get('HTTP_REFERER', self.request.build_absolute_uri()), self.language, self.item)
                html_message += "</html>"
                self.item.send_email(subject, html_message, model)
            else:
                from lucterios.mailing.models import Message
                model_obj = self.item.__class__
                email_msg = Message.objects.create(subject=subject, body=message, email_to_send="%s:0:%s" % (model_obj.get_long_name(), model))
                email_msg.add_recipient(model_obj.get_long_name(), 'id||8||%s' % ';'.join([six.text_type(item.id) for item in self.items]))
                email_msg.save()
                email_msg.valid()
                email_msg.set_context(self)
                email_msg.sending()


@ActionsManage.affect_show(_("Payment"), "diacamma.payoff/images/payments.png", condition=lambda xfer: xfer.item.payoff_have_payment() and (len(PaymentMethod.objects.all()) > 0))
@MenuManage.describ('')
class PayableShow(XferContainerCustom):
    caption = _("Payment")
    icon = "payments.png"
    model = Supporting
    field_id = 'supporting'

    def fillresponse(self, item_name=''):
        if item_name != '':
            self.item = Supporting.objects.get(id=self.getparam(item_name, 0))
        self.item = self.item.get_final_child()
        payments = PaymentMethod.objects.all()
        if not self.item.payoff_have_payment() or (len(payments) == 0):
            raise LucteriosException(MINOR, _('No payment for this document.'))
        max_row = self.get_max_row() + 1
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 6)
        self.add_component(img)
        self.fill_from_model(1, max_row, True, self.item.get_payment_fields())
        max_row = self.get_max_row() + 1
        lbl = XferCompLabelForm('lb_sep')
        lbl.set_value("{[hr/]}")
        lbl.set_location(1, max_row, 4)
        self.add_component(lbl)
        lbl = XferCompLabelForm('lb_title')
        lbl.set_value_as_infocenter(_("Payement methods"))
        lbl.set_location(1, max_row + 1, 4)
        self.add_component(lbl)
        for paymeth in payments:
            max_row = self.get_max_row() + 1
            lbl = XferCompLabelForm('paymeth_%d' % paymeth.id)
            lbl.description = get_value_if_choices(paymeth.paytype, paymeth.get_field_by_name('paytype'))
            lbl.set_value(paymeth.show_pay(self.request.META.get('HTTP_REFERER', self.request.build_absolute_uri()), self.language, self.item))
            lbl.set_location(1, max_row, 3)
            self.add_component(lbl)
            lbl = XferCompLabelForm('sep_paymeth_%d' % paymeth.id)
            lbl.set_value("{[br/]}")
            lbl.set_location(2, max_row + 1)
            self.add_component(lbl)
        self.add_action(WrapAction(TITLE_CLOSE, 'images/close.png'))


def get_html_payment(absolute_uri, lang, supporting):
    html_message = "<hr/>"
    html_message += "<center><i><u>%s</u></i></center>" % _("Payement methods")
    html_message += "<table width='90%'>"
    for paymeth in PaymentMethod.objects.all():
        html_message += "<tr>"
        html_message += "<td><b>%s</b></td>" % get_value_if_choices(paymeth.paytype, paymeth.get_field_by_name('paytype'))
        html_message += "<td>%s</td>" % paymeth.show_pay(absolute_uri, lang, supporting).replace('{[', '<').replace(']}', '>')
        html_message += "</tr>"
        html_message += "<tr></tr>"
    html_message += "</table>"
    return html_message


@MenuManage.describ('')
class CheckPaymentPaypal(XferContainerAbstract):
    caption = _("Payment")
    icon = "payments.png"

    def get_post(self, request, *args, **kwargs):
        self._initialize(request, *args, **kwargs)
        root_url = self.getparam("url", self.request.META.get('HTTP_REFERER', self.request.build_absolute_uri()))
        try:
            payid = self.getparam("payid", 0)
            payment_meth_list = PaymentMethod.objects.filter(paytype=2)
            payment_meth = payment_meth_list[0]
            support = Supporting.objects.get(id=payid).get_final_child()
            paypal_url = getattr(settings, 'DIACAMMA_PAYOFF_PAYPAL_URL', 'https://www.paypal.com/cgi-bin/webscr')
            paypal_dict = payment_meth.get_paypal_dict(root_url, self.language, support)
            return HttpResponseRedirect("%s?%s" % (paypal_url, paypal_dict))
        except Exception:
            logging.getLogger('diacamma.payoff').exception("CheckPaymentPaypal")
            from django.shortcuts import render_to_response
            dictionary = {}
            dictionary['title'] = six.text_type(settings.APPLIS_NAME)
            dictionary['subtitle'] = settings.APPLIS_SUBTITLE()
            dictionary['applogo'] = settings.APPLIS_LOGO
            dictionary['content1'] = _("It is not possible to pay-off this item with PayPal !")
            dictionary['content2'] = _("This item is deleted, payed or disabled.")
            return render_to_response('info.html', context=dictionary)


@MenuManage.describ('')
class ValidationPaymentPaypal(XferContainerAbstract):
    observer_name = 'PayPal'
    caption = 'ValidationPaymentPaypal'
    model = BankTransaction
    field_id = 'banktransaction'

    def __init__(self, **kwargs):
        XferContainerAbstract.__init__(self, **kwargs)
        self.success = False

    def confirm_paypal(self):
        from urllib.parse import quote_plus
        from requests import post
        paypal_url = getattr(settings, 'DIACAMMA_PAYOFF_PAYPAL_URL', 'https://www.paypal.com/cgi-bin/webscr')
        fields = 'cmd=_notify-validate'
        try:
            for key, value in self.request.POST.items():
                fields += "&%s=%s" % (key, quote_plus(value))
            res = post(paypal_url, data=fields.encode(), headers={"Content-Type": "application/x-www-form-urlencoded", 'Content-Length': six.text_type(len(fields))})
            return res.text
        except Exception:
            logging.getLogger('diacamma.payoff').warning(paypal_url)
            logging.getLogger('diacamma.payoff').warning(fields)
            raise

    def fillresponse(self):
        try:
            self.item.contains = ""
            self.item.payer = self.getparam('first_name', '') + " " + self.getparam('last_name', '')
            self.item.amount = self.getparam('mc_gross', 0.0)
            try:
                payoff_date = datetime.strptime(self.getparam("payment_date", '').replace('PDT', 'GMT'), '%H:%M:%S %b %d, %Y %Z')
                payoff_date += timedelta(hours=7)
                self.item.date = timezone.make_aware(payoff_date)
            except Exception:
                self.item.date = timezone.now()
            param_list = dict(self.request.POST)
            if 'FORMAT' in param_list.keys():
                del param_list['FORMAT']
            self.item.contains += "{[newline]}".join(["%s = %s" % (itemkey, itemvalue[0]) for (itemkey, itemvalue) in param_list.items()])
            conf_res = self.confirm_paypal()
            if conf_res == 'VERIFIED':
                bank_account = None
                for payment_meth in PaymentMethod.objects.filter(paytype=2):
                    if payment_meth.get_items()[0] == self.getparam('receiver_email', ''):
                        bank_account = payment_meth.bank_account
                if bank_account is None:
                    raise LucteriosException(IMPORTANT, "No paypal account!")
                support = Supporting.objects.get(id=self.getparam('custom', 0))
                new_payoff = Payoff()
                new_payoff.supporting = support.get_final_child().support_validated(self.item.date)
                new_payoff.date = self.item.date
                new_payoff.amount = self.item.amount
                new_payoff.payer = self.item.payer
                new_payoff.mode = 2
                new_payoff.bank_account = bank_account
                new_payoff.reference = "PayPal " + self.getparam('txn_id', '')
                new_payoff.bank_fee = self.getparam('mc_fee', 0.0)
                new_payoff.save()
                self.item.status = 1
                self.success = True
            if conf_res == 'INVALID':
                self.item.contains += "{[newline]}--- INVALID ---{[newline]}"
            else:
                self.item.contains += "{[newline]}"
                if conf_res != 'VERIFIED':
                    self.item.contains += "NO VALID:"
                self.item.contains += conf_res.replace('\n', '{[newline]}')
        except Exception as err:
            logging.getLogger('diacamma.payoff').exception("ValidationPaymentPaypal")
            self.item.contains += "{[newline]}"
            self.item.contains += six.text_type(err)
        self.item.save()
