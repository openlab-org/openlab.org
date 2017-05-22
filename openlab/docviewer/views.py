from django.shortcuts import render

# make sure it gets imported
from . import handlers

def test(request):
    return render(request, 'docviewer/test.html', { })

