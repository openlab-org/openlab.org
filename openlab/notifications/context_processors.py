from .models import Notification

MAX_FOR_MENU = 10

def notifications(request):
    if not request.user.is_authenticated():
        return {}

    messages = list(Notification.objects.filter(user=request.user)[:MAX_FOR_MENU])
    if not messages:
        return {}

    unread = filter(lambda m: not m.read, messages)
    read = filter(lambda m: m.read, messages)
    return {
        'notifications': {
            'read': read,
            'unread': unread,
        }
    }

