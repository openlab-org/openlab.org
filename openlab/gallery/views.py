# django
from django.utils.translation import ugettext as _
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

# third party
#from ajaxuploader.views.base import AjaxFileUploader

# first party
from openlab.core.generic_views import ManageInfo, ManageEditUploadBaseInfo, ViewInfo
from openlab.discussion.views import DiscussableMixin

# local
from .models import Gallery, Photo
from .forms import EditPhotoForm


def _one_of(val, *options):
    assert not val or val in options or val.strip('-') in options
    return val or options[0]


class ManageGalleryBase(ManageInfo):
    template_basename = 'gallery'
    breadcrumb = _("Manage gallery")
    PAGE_SIZE = 30
    def post(self, request, *args, **kwargs):
        # Do form actions
        self.gallery_action = request.POST.get('action')
        self.gallery_file_ids = request.POST.getlist('files')
        return self.get(request, *args, **kwargs)

    def get_more_context(self, request, obj):

        # fetch photos
        gallery = obj.create_gallery_if_necessary()
        queryset = Photo.objects.filter(gallery=gallery)

        if getattr(self, 'gallery_action', None):
            # A POST action is happening!
            assert self.gallery_action == 'delete' # presently only action

            # Further refine queryset with filter based on IDs
            file_ids = self.gallery_file_ids
            files = queryset.filter(id__in=file_ids)

            # Delete all that match query, and return
            files = self.exclude_undeletable(obj, files)
            number = files.count()
            if hasattr(files, "deleted"):
                files.update(deleted=True)
            else:
                # Perform hard delete
                files.delete()
            if self.DELETION_MESSAGE:
                messages.success(request, self.DELETION_MESSAGE % number)


        # Add sortability (disabled for now)
        #ordering = request.GET.get('ordering', '')
        #ordering = _one_of(ordering, "upload_date", "title")
        #ordering = _one_of(ordering, "upload_date", "title")

        # And pagination
        page_number = request.GET.get('page', request.GET.get('page', 1))

        # Paginate results
        results = queryset
        paginator = Paginator(results, self.PAGE_SIZE)
        page = paginator.page(page_number)
        files = page.object_list

        # Manually generate CSRF token for AJAX request
        #csrf_token = get_token(request)

        return {
                'page': page,
                'photos': files,
                'files': files,
                'gallery': gallery,
            }

    def exclude_undeletable(self, obj, files):
        if obj.photo:
            photo = obj.photo
            return files.exclude(id=photo.id)
        else:
            return files


class ManageGalleryEditBase(ManageEditUploadBaseInfo):
    # XXX no longer in use
    template_basename = 'gallery_edit'
    breadcrumb = _("Edit photo details")
    form = EditPhotoForm
    def get_queryset(self, obj):
        gallery = obj.create_gallery_if_necessary()
        return Photo.objects.filter(gallery=gallery)

class ViewGalleryBase(ViewInfo):
    template_basename = "gallery"
    breadcrumb = _('Gallery')
    PAGE_SIZE = 30

    def get_queryset(self, obj):
        if obj.gallery:
            return Photo.objects.filter(gallery=obj.gallery)
        else:
            return Photo.objects.none()

    def get_more_context(self, request, obj):
        # Add sortability
        ordering = request.GET.get('ordering', '')
        ordering = _one_of(ordering, "number", "upload_date", "title")

        # And pagination
        page_number = request.GET.get('page', 1)

        # Paginate results
        queryset = self.get_queryset(obj)
        results = queryset.order_by(ordering)
        paginator = Paginator(results, self.PAGE_SIZE)
        page = paginator.page(page_number)
        files = page.object_list

        return {
                'photos': files,
                'files': files,
            }


class ViewPhotoBase(ViewInfo, DiscussableMixin):
    breadcrumb = _('Photo')
    template_basename = "photo"
    def get_more_context(self, request, obj):
        # Get target photo
        gallery_id = obj.gallery_id
        photo_id = self.kwargs.get('photo_id')
        photo = get_object_or_404(Photo, gallery_id=gallery_id, number=photo_id)
        gallery_id = photo.gallery_id

        # Fetch next and previous photos (by ID, maybe later be by date?)
        photos = Photo.objects.filter(gallery_id=photo.gallery_id)

        try:
            next_photo = photos.filter(
                            number__gt=photo.number).order_by('number')[0:1][0]
        except IndexError:
            next_photo = None

        try:
            previous_photo = photos.filter(
                            number__lt=photo.number).order_by('-number')[0:1][0]
        except IndexError:
            previous_photo = None

        c = {
                'photo': photo,
                'next_photo': next_photo,
                'previous_photo': previous_photo,
            }

        # Insert context for discussion
        c.update(self.get_discussion_context(request, photo, context_object=obj))

        return c

