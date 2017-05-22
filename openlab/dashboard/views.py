from django.core.urlresolvers import reverse

from django.core.paginator import Paginator
from django.utils.translation import ugettext as _

from django.shortcuts import render

from actstream import registry
from actstream.models import user_stream, Action

# 1st party
#from quickblog.models import Post
from openlab.users.models import User
from openlab.project.models import Project, Team

def dashboard(request):
    #new_projects = Project.objects.order_by('-creation_date').select_related('city')[:7]
    #new_posts = _first_two(Post.objects.order_by('-publish_date').select_related())
    #showcase_projects = FeaturedProject.get_featured_projects()

    # TODO move somewhere else
    registry.register(User)
    results = user_stream(request.user)

    if not results:
        results = Action.objects.all()
        is_generic = True
    else:
        is_generic = False

    paginator = Paginator(results, 30)
    page = paginator.page(1)
    stream = page.object_list

    projects = Project.objects.filter(user=request.user)
    teams = list(Team.objects.filter(members=request.user) |
                    Team.objects.filter(user=request.user))

    team_projects = []
    for team in teams:
        t_projects = Project.objects.filter(team=team)
        team_projects.append((team, t_projects))

    return render(request, 'dashboard/index.html', {
            'viewing': "home",
            'dashboard_tab': True,
            'stream': stream,
            'projects': projects,
            'stream_is_generic': is_generic,

            'teams': teams,
            'my_projects': projects,
            'team_projects': team_projects,
            #'anthromes': Anthrome.all(),
            #'anthrome_groups': AnthromeGroup.all(),
            #'new_projects': new_projects,
            #'showcase_projects': showcase_projects,
            #'new_posts': new_posts or [],
        })


