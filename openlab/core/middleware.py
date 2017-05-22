from django.shortcuts import redirect

from django.conf import settings

class WhitelistMiddleware(object):
    def process_request(self, request):
        if getattr(settings, 'OL_WHITELIST_URLS', False):
            return

        if request.path in settings.OL_WHITELIST_URLS:
            return

        if request.user.is_authenticated():
            return

        return 
        return redirect('/user/login/')


