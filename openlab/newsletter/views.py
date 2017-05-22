import requests

from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from openlab.project.models import Project

from .models import Subscription


MG_NEWSLETTER_LIST = 'announcements@openlab.org'
MG_NEWSLETTER_LIST_URL = (
    "https://api.mailgun.net/v3/lists/%s/members"
        % MG_NEWSLETTER_LIST
)


def mailgun_add_list_member(addr):
    key = settings.MAILGUN_PRIVATE_API_KEY
    auth = ('api', key)
    data = {'subscribed': True, 'address': addr}
    return requests.post(MG_NEWSLETTER_LIST_URL, auth=auth, data=data)


def _subscribe_user(user, project):
    ctype = ContentType.objects.get_for_model(project)

    subscription = Subscription.objects.create(
        user=user, content_type=ctype, object_id=project.id)
    return subscription


def _subscribe_email_addr(email_address, project):
    ctype = ContentType.objects.get_for_model(project)

    subscription = Subscription.objects.create(
            email_address=email_address,
            content_type=ctype,
            object_id=project.id)

    return subscription


def _subscribe_email_addr_global(email_address):
    '''
    Subscribe given email address to global Open Lab email address (store in
    DB), also subscribe with mail gun
    '''
    subscription = Subscription.objects.create(email_address=email_address)
    mailgun_add_list_member(email_address)
    return subscription


def global_subscribe_endpoint(request):
    '''
    Subscribes user to newsletter of project
    '''
    referer = request.META.get('HTTP_REFERER', '/')
    red = HttpResponseRedirect(referer)
    if request.method != "POST":
        raise Http404("POST required")

    email_addr = request.POST.get('the_email_address', '')
    # TODO this is a hack, validate email address properly
    if '@' not in email_addr or '.' not in email_addr:
        messages.error(request, 'Whoops! Invalid email specified.')
        return red
    _subscribe_email_addr_global(email_addr)
    messages.success(request, """
        Thank you for your interest in Open Lab! We'll keep you informed about
        future Open Lab development.
    """)

    return red

def subscribe_endpoint(request, content_type="", content_id=0,
                            template="newsletter/subscribed.html"):
    '''
    Subscribes user to newsletter of project
    '''
    if content_type != "project":
        raise Http404("Could not find content type")
    project = get_object_or_404(Project, id=content_id)
    referer = request.META.get('HTTP_REFERER', '/')
    red = HttpResponseRedirect(referer)
    if request.method != "POST":
        return red

    if request.user.is_authenticated():
        _subscribe_user(request.user, project)
        return red

    email_addr = request.POST.get('email_address', '')
    if not email_addr:
        return red

    _subscribe_email_addr(email_addr, project)

    ctx = {
        'referrer': referer,
        'email_address': email_addr,
        'project': project,
    }

    return render(request, template, ctx)

def unsubscribe(request): pass
