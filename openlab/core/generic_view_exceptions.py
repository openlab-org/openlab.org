from django.http import HttpResponse, HttpResponseRedirect

class ResponseExceptionBase(Exception):
    """
    Simple base class that wraps around a response specified by a sub class
    """
    def __init__(self, *args, **kwds):
        self.response = self.response_class(*args, **kwds)

class RedirectException(ResponseExceptionBase):
    response_class = HttpResponseRedirect

