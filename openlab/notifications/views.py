from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Notification
from .email import send_digest

@login_required
def all(request, template="notifications/all.html"):
    messages = Notification.objects.filter(user=request.user)

    ctx = {
        'notifies': messages,
        'notifications_tab': True,
        'read': messages.filter(read=True),
        'unread': messages.filter(read=False),
    }

    if request.method == "POST":
        action = request.POST.get('action')
        if action == "clear_all":
            messages.delete()
        if action == "clear":
            message_id = int(request.POST.get('id'))
            messages.filter(id=message_id).delete()
        return redirect(all)

    # Render result FIRST before setting to viewed
    result = render(request, template, ctx)

    # Update all to viewed, just in case
    messages.update(read=True)

    return result

@login_required
def ajax_mark_read(request):
    messages = Notification.objects.filter(user=request.user)
    messages.update(read=True)
    # redirect to top
    return redirect(request.get_full_path())

@login_required
def test_view_email(request, template="notifications/test_email.html"):
    user = request.user
    #notifications = Notification.get_unsent(user=request.user)
    notifications = Notification.objects.filter(user=request.user)
    message = send_digest(user, notifications, skip_send=True)

    ctx = { "message": message, }

    # redirect to top
    return render(request, template, ctx)

