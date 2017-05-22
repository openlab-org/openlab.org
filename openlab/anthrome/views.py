from django.core.urlresolvers import reverse

from django.core.paginator import Paginator
from django.utils.translation import ugettext as _

from django.shortcuts import render
#from project.models import Project
#from quickblog.models import Post

from openlab.anthrome.anthrome_types import Anthrome, AnthromeGroup
#from moderation.models import FeaturedProject


def _first_two(results):
    paginator = Paginator(results, 2)
    page = paginator.page(1)
    return page.object_list

def landingpage(request):
    return showcase(request, template='anthrome/landingpage.html')


def showcase(request, template="core/index.html"):
    new_projects = []
    #new_posts = _first_two(Post.objects.order_by('-publish_date').select_related())
    new_posts = []
    #showcase_projects = FeaturedProject.get_featured_projects()
    showcase_projects = []
    return render(request, template, {
            'viewing': "home",
            'anthromes': Anthrome.all(),
            'anthrome_groups': AnthromeGroup.all(),
            'new_projects': new_projects,
            'showcase_projects': showcase_projects,
            #'popularbooks': popbooks,
            #'randombooks': randombooks,
            'new_posts': new_posts or [],
        })


def anthrome(request, slug):
    a = Anthrome.by_slug(slug)
    #results = Project.objects.order_by('creation_date').select_related('city')
    results = [] # TODO

    paginator = Paginator(results, 30)
    page = paginator.page(1)

    # Planet is just home
    request.breadcrumbs(_("Planet"), '')

    if a.parent:
        request.breadcrumbs(_(a.parent.label),
                reverse('anthrome.views.anthrome', args=(a.parent.slug_dasherized,)))

    request.breadcrumbs(_(a.label), request.get_full_path())

    if not a:
        raise Exception("...")

    return render(request, 'anthrome/anthrome.html', {
            'anthrome': a,
            'projects': page.object_list,
        })

