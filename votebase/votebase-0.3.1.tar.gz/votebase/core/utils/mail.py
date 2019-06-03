from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template import loader
from django.template.context import Context
from django.utils.translation import ugettext as _

from django_rq import job

from votebase.core.utils.helpers import get_absolute_url


def password_recovery(email, password):
    # from
    from_email = u'%s <%s>' % (settings.DEFAULT_EMAIL_FROM_NAME, settings.DEFAULT_EMAIL_FROM)

    subject = _(u'Request for new password')
    text = _(u'Dear user, \n\n you have requested password recovery. Your \
    new password is %(password)s') % {'password': password}

    return send_mail(subject, text, from_email, (email,))


def quiz_result(voter):
    if not voter.user:
        return

    # from
    from_email = u'%s <%s>' % (settings.DEFAULT_EMAIL_FROM_NAME, settings.DEFAULT_EMAIL_FROM)

    subject = _(u'Quiz result')
    template = loader.get_template('mails/quiz_result.html')
    context = Context({
        'survey': voter.survey,
        'voter': voter,
        #'host_url': get_absolute_url(request),
        'host_url': settings.HOST_URL,
        'uri': voter.get_absolute_hash_url(),
    })
    message = template.render(context)
    recipient_list = [voter.user.username, ]

    result = send_mail(subject, message, from_email, recipient_list, fail_silently=False)

    if result != voter.is_quiz_result_sent:
        voter.is_quiz_result_sent = result
        #voter.save(update_fields=['is_quiz_result_sent'])
        voter.save()

    return result


@job
def send_quiz_result_to_voter_in_background(voter):
    quiz_result(voter)


def registration(request, user):
    # TODO: create setting's option to set project name 'Welcome to >VOTEHUB<'

    # from
    from_email = u'%s <%s>' % (settings.DEFAULT_EMAIL_FROM_NAME, settings.DEFAULT_EMAIL_FROM)

    return send_mail(
        _(u'Welcome %(user_name)s!') % {'user_name': user.profile.get_full_name()},
        _(u'Please click on this link to confirm your email address %(url)s%(uri)s') % {
            'url': get_absolute_url(request),
            'uri': reverse(
                'accounts_activate',
                args=(user.get_profile().activation_hash, )),
        },
        from_email, [user.username], fail_silently=True
    )


def new_password(user, random_password):
    # from
    from_email = u'%s <%s>' % (settings.DEFAULT_EMAIL_FROM_NAME, settings.DEFAULT_EMAIL_FROM)

    send_mail(
        _(u'Votehub.net password reset'),
        _(u'Your new password is %(password)s') % {
            'password': random_password
        }, from_email, [user.email], fail_silently=True
    )


def new_voters(round, request):
    # from
    from_email = u'%s <%s>' % (settings.DEFAULT_EMAIL_FROM_NAME, settings.DEFAULT_EMAIL_FROM)

    survey = round.survey

    if round.email_treshold == 1:
        subject = _(u'New voter in your survey')
        message = _(u'You have one new voter in your survey %(survey)s') % {
            'survey': survey.title,
        }
        message_html = _(u'You have one new voter in your survey <a href="%(url)s%(uri)s">%(survey)s</a>') % {
            'survey': survey.title,
            'url': get_absolute_url(request),
            'uri': reverse('statistics_graphs', args=(survey.pk,))
        }
    else:
        subject = _(u'New voters in your survey')
        message = _(u'You have %(voters_count)d new voters in your survey %(survey)s') % {
            'survey': survey.title,
            'voters_count': round.email_treshold,
        }
        message_html = _(u'You have %(voters_count)d new voters in your survey <a href="%(url)s%(uri)s">%(survey)s</a>') % {
            'survey': survey.title,
            'voters_count': round.email_treshold,
            'url': get_absolute_url(request),
            'uri': reverse('statistics_graphs', args=(survey.pk,))
        }

    from django.core.mail import EmailMultiAlternatives
    msg = EmailMultiAlternatives(subject, message, from_email, [survey.user.email])
    msg.attach_alternative(message_html, "text/html")
    msg.send(fail_silently=True)
