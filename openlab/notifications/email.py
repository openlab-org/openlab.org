
from django.core import mail
from django.conf import settings
from django.template import loader, Context

from .models import Notification


def _mark_as_sent(user):
    Notification.objects.filter(user=user).update(mailed=True)

def send_digest(user, notifications, skip_send=False):
    profile = user.profile

    # Check if user disabled email notifications
    if not profile.email_notification:
        if not skip_send:
            _mark_as_sent(user)
        return None

    # Check preference for template
    is_plaintext = profile.plaintext_email

    # Create context
    to_email = user.email.strip().lower()
    from_email = settings.NOTIFICATIONS_FROM_EMAIL
    email_type = "digest" # later can add 'alert'



    ctx = {
        'user': user,
        'profile': profile,
        'notifications': notifications,
        'settings': settings,
        'email': to_email,
        'email_type': email_type,
        'count': len(notifications),

        # basic stuff
        'STATIC_URL': settings.STATIC_URL,
    }


    # Get domain properly for absolute URLs in the email
    if settings.ENV == "dev":
        ctx['DOMAIN'] = 'http://local.host:8000'
    elif settings.ENV == "test":
        ctx['DOMAIN'] = 'http://labrat.openlab.org'
    elif settings.ENV == "prod":
        ctx['DOMAIN'] = 'http://labrat.openlab.org'

    if ctx['STATIC_URL'].startswith('/'):
        ctx['STATIC_URL'] = ctx['DOMAIN'] + ctx['STATIC_URL']

    # Get & render HTML (or txt) content
    base_path = "notifications/email/"
    ext = 'html' if not is_plaintext else 'txt'
    template_path = base_path + "body.%s" % (ext)
    body_template = loader.get_template(template_path)
    html_content = body_template.render(Context(ctx))

    if not html_content:
        raise ValueError("Was about to send blank email.")

    # Get & render subject line (using normal template loader)
    template_path = base_path + "subject.txt"
    subject_template = loader.get_template(template_path)
    subject_content = subject_template.render(Context(ctx)).strip()

    if not subject_content:
        raise ValueError("Was about to send without subject.")

    message = mail.EmailMessage(subject_content, html_content,
                                from_email, [to_email])
    if not is_plaintext:
        # Main content is now text/html
        message.content_subtype = "html"

    if not skip_send:
        try:
            message.send()
        except Exception as e:
            logger.error(">>> Could not connect to SMTP! [%s]" % e)
        else:
            _mark_as_sent(user)

    return message



