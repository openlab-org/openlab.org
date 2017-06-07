# django
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

# first party
from openlab.core.generic_views import ManageInfo, RedirectException
from openlab.project.models import Project
from openlab.gallery.models import Photo, Gallery
from openlab.anthrome.anthrome_types import Anthrome

# local
from .forms import EditReleaseMediaForm
from .models import Release


def make_release_context(request, project, is_preview=False, version=None):
    """
    Mixed in to create the template context necessary for displaying a release
    """
    release = project.release

    if is_preview:
        release = Release()
    else:
        if version:
            release = get_object_or_404(Release,
                    project=project, version=version)
        else:
            release = project.release

    if not project.biome:
        # XXX HACK default to urban biome, only for testing until we dont
        # allow unfinished project infos to be published
        project.biome = "11"

    # fetch all relevant projects
    dependencies = list(project.dependencies.all())
    projects = [project] + dependencies

    # get relevant people
    people = [project.user]
    people += [project.team] if project.team else []
    people += list(project.team_access.all())
    people += list(project.user_access.all())
    first_three_people = people if len(people) < 4 else people[:4]

    # Get relevant gallery (will fall back to project gallery if needs be)
    gallery = release.gallery
    gallery_photos = list(gallery.photos.all())

    # For now..:
    files = list(project.get_files())
    if len(files) == 5:
        photos = list(gallery.photos.all())\
            + [files[-2], files[-1]]
    else:
        photos = list(gallery.photos.all())\
                + list(project.tip_revision.files.all())

    return {
            "release": release,
            #"release": project,
            "gallery": gallery,
            "gallery_photos": gallery_photos,
            "photos": photos,
            "project": project,
            "dependencies": dependencies,
            "people": people,
            "first_three_people": first_three_people,
            "projects": projects,
            "anthrome": Anthrome.get_by_number(int(project.biome)),
            "allow_links": request.user.is_authenticated(),
            "full_url": request.build_absolute_uri(),
            "template_override": None,
        }


@login_required
def project_preview(request, project_id, template="project/release/release.html"):
    project = Project.objects.get(id=project_id)
    #can_edit = project.can_edit(request.user)
    #if not can_edit:
    #    raise PermissionDenied("Cannot preview release for this project")

    initial = { 'summary': ' ', 'version': ' ', 'notes': ' ', 'text': ' ', }

    form = EditReleaseMediaForm(request.POST,
            project=project,
            initial=initial,
            instance=None)

    # Valid form: save and set as release
    release = form.save(commit=False)
    release.project = project
    #release.revision = project.tip_revision
    #release.components = {"blank": True}
    release.zip_path = None
    release.size = 0

    # Okay, there is a release, lets format this
    ctx = make_release_context(request, project)
    ctx['template_override'] = 'project/release/base_empty.html'

    return render(request, template, ctx)




class ManageReleasesBase(ManageInfo):#, FormBaseMixin):
    template_basename = 'releases'
    breadcrumb = _("Releases")

    def post(self, request, *a, **k):
        # Return standard look.
        return self.get(request)

    def get_more_context(self, request, obj):
        obj = self.get_object(request)
        if request.method == 'POST':
            release_id = request.POST.get('release_id')
            action = request.POST.get('action')
            # (add in project to query to prevent malicious deletes)
            release = get_object_or_404(Release, id=release_id, project=obj)
            if obj.release == release:
                raise PermissionDenied("Cannot modify active release")

            if action == "revert":
                # Set this release as active release
                obj.release = release
                obj.save()

            elif action == "delete":
                release.delete()

            # redirect to self to prevent double submission
            my_url = request.get_full_path()
            raise RedirectException(my_url)
                
        return {
                'latest_stable': obj.release,
                'releases': obj.releases.all(),
            }


class ManageReleasesNewBase(ManageInfo):#, FormBaseMixin):
    template_basename = 'releases_new'
    breadcrumb = _("New release")

    def post(self, request, *a, **k):
        # Return standard look.
        return self.get(request)

    @staticmethod
    def build_media_gallery(post_data):
        """
        Creates a new Gallery object filled with Photos based on both Photos
        and Files that were selected for this Release. This will appear on the
        public page for this release.
        """
        models = {
                'photo': Photo,
            }

        # create new gallery
        gallery = Gallery.objects.create()

        for value in post_data.values.get('files'):
            model_name, id_  = value.split('_')
            model = models[model_name]
            obj = model.objects.get(id=id_)
            photo = Photo.copy_from(obj)
            photo.gallery = gallery
            photo.save()


    def handle_save(self, form, project):
        # TODO need to put this into a transaction

        # Valid form: save and set as release
        release = form.save(commit=False)
        release.project = project
        release.revision = project.tip_revision

        # Get media gallery
        release.gallery = self.build_media_gallery(self.request.POST)

        # TODO queue up zip generation etc
        release.components = {"blank": True}
        release.zip_path = None
        release.size = 0
        release.save()

        project.release = release
        project.save()
        raise RedirectException(reverse("project", args=(project.hubpath,)))

    def get_more_context(self, request, obj):
        obj = self.get_object(request)

        post = request.POST if request.method == 'POST' else None

        form = EditReleaseMediaForm(post,
                project=obj,
                previous=obj.release,
                instance=None)

        if post and form.is_valid():
            self.handle_save(form, obj)

        #components = auto_componentize(obj, previous=obj.release)
        #media = auto_media(obj, previous=obj.release)
        media = []

        return {
                'form': form,
                'media': media,
            }


class ManageReleasesEditBase(ManageInfo):#, FormBaseMixin):
    template_basename = 'releases_edit'
    breadcrumb = _("Edit release")

    def post(self, request, *a, **k):
        # Return standard look.
        return self.get(request)

    def get_more_context(self, request, obj):
        obj = self.get_object(request)
        version = self.kwargs.get('version')
        releases = list(obj.releases.all())
        #release = filter(lambda r: r.version == version, releases)

        return {
                #'components': components,
                'version': version,
                'releases': releases,
                'template_override': None,
                'release': releases and releases[0],
            }

