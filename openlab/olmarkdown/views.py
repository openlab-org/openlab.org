from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# import the context types
from openlab.project.models import Project
from openlab.team.models import Team
#from openlab.accounts.models import Profile
#from openlab.service.models import Service

@login_required
def preview(request, context_type, context_id):
    # Get text
    text = request.POST.get('text', '')

    model_class = {
            'project': Project,
            'team': Team,
            'profile': Profile,
        }[context_type]

    # TODO add in security check here to make sure private ones aren't accessed
    # by people who can't
    obj = model_class.objects.get(context_id=context_id)

    # Try rendering it
    result = markdown_for_object(text, obj)

    return render(request, 'olmarkdown/preview.html', {'result': result})

