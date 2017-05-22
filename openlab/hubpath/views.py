from django.shortcuts import redirect
from django.http import Http404
from .models import HubPathBase
from django.http import HttpResponseRedirect

def team_or_user(request, hubpath):
    """
    "Catch all" that redirects to given HubPath.
    """
    try:
        obj = HubPathBase.hubpath_objects.get(hubpath=hubpath)
    except HubPathBase.DoesNotExist:
        raise Http404
    return HttpResponseRedirect(obj.get_absolute_url())

