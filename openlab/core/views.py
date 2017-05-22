from django.shortcuts import render

from openlab.dashboard.views import dashboard
from openlab.anthrome.views import showcase, landingpage

def index(request):
    """
    Logged in users get their dashboard.

    Logged out users get the anthrome showcase thing
    """
    if request.user.is_authenticated():
        return dashboard(request)
    else:
        return landingpage(request)


def code(request):
    # For now just render plain template
    return render(request, 'core/code.html', {})


def site_credits(request):
    # For now just render plain template
    return render(request, 'core/credits.html', {})


def press_kit(request):
    # For now just render plain template
    return render(request, 'core/press_kit.html', {})


def help(request, page):
    from django.core.mail import send_mail
    MY_EMAIL = 'michaelpb@gmail.com'
    successful_contact = False

    if request.method=="POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.clean()
            from_email = form.cleaned_data['email_address']
            successful_contact = True
            args = [
                "Form submission (%s)" % \
                    form.cleaned_data['email_address'],
                "From '%(name)s <%(email)s>':\n%(msg)s" % {
                    'name': form.cleaned_data['name'],
                    'email': form.cleaned_data['email_address'],
                    'msg': form.cleaned_data['message']
                } + "\n--------------\n" +
                "Request info: " + repr(dict({
                    'request.path': request.path,
                    'request.META': request.META,
                })),
                "admin@openlab.org",
                [MY_EMAIL,],
            ]
            send_mail(*args)
            args = [
                _("openlab.org comment"), 
                _("""Hi %(name)s,\n\nThank you for message! 
                We'll try to get back to you as soon as possible.
                \n\n--------------\n\n%(msg)s\n
                """.replace('\t','')) % {
                    'name': form.cleaned_data['name'],
                    'msg': form.cleaned_data['message']
                },
                "admin@openlab.org",
                [form.cleaned_data['email_address']],
            ]
            send_mail(*args)
            form = ContactForm()
    else:
        form = ContactForm()

    d = {'page': page, 'form': form,
                'successful_contact': successful_contact }

    if page == 'credits':
        d['users'] = {
                'backer': Profile.objects.filter(badges__name='backer'),
                'beta': Profile.objects.filter(badges__name='beta'),
                'contributor': Profile.objects.filter(badges__name='contributor'),
            }

    return render(request, 'core/help.html', d)



