# -*- coding: utf-8 -*-
from congo.communication import get_email_message_model, get_email_recipient_model, get_sms_recipient_model
from congo.utils.classes import Message, MetaData
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.http.response import Http404
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
import logging


def unsubscribe(request, object_id, token, mode = 'email'):
    meta = MetaData(request, _("Wypisz się z newslettera"))
    show_form = False

    if mode == 'email':
        recipient_model = get_email_recipient_model()
    elif mode == 'sms':
        recipient_model = get_sms_recipient_model()

    try:
        recipient = recipient_model.objects.get(id = object_id, is_tester = False, is_active = True)
        if recipient.check_token(token):
            if request.method == "POST":
                recipient.is_active = False
                recipient.save()

                message = Message.success(_("Adres <b>%s</b> został usunięty z naszej listy subskrybentów.") % recipient.email)

                extra = {}
                extra['extra_info'] = {'recipient': recipient}
                logger = logging.getLogger('system.communication.unsubscribe')
                logger.info("Użytkownik wypisał się z newslettera", extra = extra)
            else:
                message = Message.question(_("Czy na pewno chcesz usunąć adres <b>%s</b> z listy naszych subskrybentów?") % recipient.email)
                show_form = True
        else:
            message = Message.info(_("Niestety wypisanie z listy subskrybentów nie powiodło się. Prosimy o kontakt z biurem obsługi."))

    except recipient_model.DoesNotExist:
        message = Message.info(_("Przepraszamy, ale podany adres e-mail nie znajduje się na naszej liście subskrybentów."))

    context = {
        'meta': meta,
        'message': message,
        'show_form': show_form,
    }

    return render(request, 'congo/communication/unsubscribe.html', context)

@permission_required('communication.view_emailmessage')
def email_preview(request, message_id):
    message_model = get_email_message_model()
    recipient_model = get_email_recipient_model()

    email_message = get_object_or_404(message_model, id = message_id)

    text_content, html_content = email_message.render_template_tags()
    recipient = None

    email = request.GET.get('email')
    if email:
        try:
            recipient = recipient_model.objects.get(email = email)
        except recipient_model.DoesNotExist:
            pass
    else:
        try:
            recipient = recipient_model.objects.get(email = request.user.email)

        except AttributeError:
            raise Http404

        except recipient_model.DoesNotExist:
            try:
                recipient = recipient_model.objects.filter(is_tester = True, is_active = True)[0]
            except IndexError:
                pass

    if recipient:
        text_content, html_content = email_message.render_recipient_tags(text_content, html_content, recipient)

    if request.GET.get('format') == 'text':
        meta = MetaData(request, email_message.subject)

        extra_context = {
            'meta': meta,
            'content': text_content,
        }

        return render(request, 'congo/communication/email_preview.html', extra_context)

    else:
        format_menu = """<tr><td><a href="?format=text" style="display: inline-block; font-size: 14px; color: #777; margin: 15px">%s</a></td></tr>""" % _("Przełącz do formatu tekstowego")
        content = html_content.replace("<!-- X -->", format_menu)
        return HttpResponse(content)

# @permission_required('communication.view_smsmessage', raise_exception = True)
# def sms(request, message_id, token):
#    sms_message = get_object_or_404(SMSMessage, id = message_id)
#
#    if not sms_message.check_token(token):
#        raise Http404()
#
#    content = sms_message.get_content()
#
#    recipient = None
#    user_id = request.GET.get('user_id')
#    if user_id:
#        try:
#            recipient = SMSRecipient.objects.get(user_id = user_id)
#        except SMSRecipient.DoesNotExist:
#            pass
#    else:
#        try:
#            recipient = SMSRecipient.objects.get(user = request.user)
#        except SMSRecipient.DoesNotExist:
#            pass
#    if recipient:
#        content = sms_message.render_recipient_tags(content, recipient)
#
#    extra_context = {
#        'sms_message': sms_message,
#        'content': content,
#    }
#
#    return render_to_response('sms.html', extra_context, context_instance = RequestContext(request))
#
# @permission_required('communication.view_smsrecipientgroup', raise_exception = True)
# def email_recipient_group(request, message_id):
#
#    try:
#        recipient_group = EmailRecipientGroup.objects.get(id = message_id)
#    except EmailRecipientGroup.DoesNotExist:
#        raise Http404()
#
#    extra_context = {
#        'recipient_group': recipient_group,
#    }
#
#    return render_to_response('recipient_group.html', extra_context, context_instance = RequestContext(request))
#
# @permission_required('communication.view_smsrecipientgroup', raise_exception = True)
# def sms_recipient_group(request, message_id):
#
#    try:
#        recipient_group = SMSRecipientGroup.objects.get(id = message_id)
#    except SMSRecipientGroup.DoesNotExist:
#        raise Http404()
#
#    extra_context = {
#        'recipient_group': recipient_group,
#    }
#
#    return render_to_response('recipient_group.html', extra_context, context_instance = RequestContext(request))
#
# @secure_allowed
# def unsubscribe(request, message_id, token):
#    try:
#        recipient = EmailRecipient.objects.get(id = message_id, is_tester = False)
#    except EmailRecipient.DoesNotExist:
#        recipient = None
#
#    if recipient:
#        if recipient.check_token(token):
#            recipient.is_active = False
#            recipient.save()
#
#            content = _("The e-mail address <b>%s</b> was removed from our list of newsletter subscribers.") % recipient.email
#        else:
#            content = _("Unsubscribing our newsletter failed because the link was incorrect.")
#    else:
#        content = _("Sorry, but there is no requested e-mail address on our list of newsletter subscribers.")
#
#    extra_context = {
#        'title': _('Unsubscribing newsletter'),
#        'content': content,
#    }
#
#    return render_to_response('unsubscribe.html', extra_context, context_instance = RequestContext(request))
