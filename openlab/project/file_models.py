# python
import re
import os.path
import random

# django
from django.db import models, transaction
from openlab.users.models import User
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator

# 3rd-ish party
from s3uploader.models import GenericUploadableMixin

# 1st party
from openlab.gallery.models import Photo


from .fields import LicenseField

HASH_LENGTH = 16
MAX = int('0x' + ('F'*HASH_LENGTH), 16) # Max value for hex commit hash
def random_hash():
    i = random.randint(0, MAX)
    s = hex(i)[2:].rjust(HASH_LENGTH, '0')
    return s[:HASH_LENGTH]

random_hash_validator = RegexValidator(regex='^[a-f0-9]{%i}$' % HASH_LENGTH,
            message='Length has to be %i digit lowercase hex' % HASH_LENGTH,
            code='nomatch')

CHARS = re.compile(r'[\W_]+')
def sanitize(s):
    return CHARS.sub('_', s).strip('_')


def project_path_builder(project_id):
    """
    Builds a path to a containing folder based on a project ID
    """
    s = "%06i" % project_id
    return os.path.join(s[:3], s)


class Revision(models.Model):
    class Meta:
        app_label = 'project'
        unique_together = (('project', 'number'), )

    class NotReadyYet(Exception): pass

    creation_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    project = models.ForeignKey("Project",
            related_name="project_revisions",
            help_text=_("Project this revision is for"))

    user = models.ForeignKey(User,
            related_name="project_revisions",
            help_text=_("User who authored the revision"))

    number = models.PositiveIntegerField(
            db_index=True,
            help_text=_("Revision number"))

    hash_code = models.CharField(max_length=HASH_LENGTH,
                        db_index=True,
                        unique=True,
                        validators=[random_hash_validator],
                        help_text=_("Randomized 16 digit hex number "
                                    "to specify this revision (globally "
                                    "unique alternative to revision number)"))

    summary = models.CharField(
            max_length=140,
            verbose_name=_("Summary"),
            blank=True,
            default="",
            help_text=_("Summary of changes in revision"))

    changes = models.TextField(max_length=2048,
            blank=True,
            default="",
            help_text=_("A longer description of changes"))

    is_ready = models.BooleanField(default=False,
            help_text=_('Is it all ready for display '
                        '(e.g. all previews rendered)?'))

    is_uploaded = models.BooleanField(default=False,
            help_text=_('Did the person click "submit" '
                    'and is done uploading / arranging?'))

    deleted = models.BooleanField(default=False,
            db_index=True,
            help_text=_('Field for "soft" deletion '
                        '(seems like perma-delete to user)'))

    UNMODIFIED = ''
    MODIFIED   = 'm'
    ADDED      = 'a'
    DELETED    = 'd'
    RENAMED    = 'r'
    COPIED     = 'c'

    def __str__(self):
        return u"Revision #%i" % self.number


    def get_absolute_url(self):
        return reverse('project_revision', args=[self.project.hubpath, self.number])

    def title(self):
        s = _(u"revision #%i") % self.number
        if self.summary:
            s += '"%s"' % self.summary
        return s


    def save(self, *a, **k):
        if not self.hash_code:
            # Generate new hash code
            self.hash_code = random_hash()

        if not self.number:
            # Generate new hash code
            self.number = self.next_number()

        super(Revision, self).save(*a, **k)

    def next_number(self, *a, **k):
        try:
            last = self.project.project_revisions.all().order_by('-number')[0]
        except IndexError:
            # Probably first revision, start counting at 1
            number = 1
        else:
            number = last.number + 1

        return number


    def get_files_by_folder(self):
        files = FileModel.objects.filter(deleted=False, revision=self)
        return FileModel.by_folder(files)

    def get_file(self, folder, filename):
        """
        Returns the file model that fits this description or None if it cant
        find any.
        """
        kwds = dict(deleted=False, filename=filename)
        if folder is not None:
            kwds['folder'] = folder

        try:
            return self.files.get(**kwds)
        except (FileModel.DoesNotExist, FileModel.MultipleObjectsReturned):
            return None

    def get_my_path(self):
        """
        Returns a path to the folder that stores this data
        """
        # Note: later prefix my hash code for efficiency in Amazon
        project_path = project_path_builder(self.project_id)
        revision = "%03i" % self.number
        return os.path.join(project_path, revision)

    def make_path_for_file(self, folder, filename):
        # Generates a path with the given info
        my_path = self.get_my_path()
        return os.path.join(my_path, folder, filename)


    @classmethod
    def get_or_create_in_progress(cls, project, user):
        d = dict(is_uploaded=False, user=user, project=project)
        try:
            revision = cls.objects.get(**d)
        except Revision.DoesNotExist:
            # First time visiting page, create a new one
            return Revision.objects.create(**d)
        else:
            # Not the first time visiting, return old one
            return revision

    def complete(self):
        """
        Mark as "completed", queue up changes, add event, etc
        """

        not_ready = list(self.files.filter(is_uploaded=False, deleted=False))
        if not_ready:
            raise Revision.NotReadyYet("Attempt to "
                    "'complete' while in progress!")

        # Do in one transaction
        with transaction.atomic():
            self.is_ready = False
            self.is_uploaded = True
            self.project.tip_revision = self
            self.mark_as_tip()
            self.save()
            self.project.save()



    def check_and_set_if_ready(self):
        return self.is_ready # XXX delete


    def get_stat_diff_if_applied(self, include_files=True):
        """
        Get's a "git-style" stat summary of the revision and what would change
        if it were applied to the current title

        e.g. git diff --stat
        """
        # XXX don't think in use, prob broken
        previous_tip_files = self.project.files.filter(
                deleted=False,
                is_tip=True)

        files = list(self.files.filter(is_uploaded=True, deleted=False))
        files_dict = dict(zip(map(lambda f: f.full_file_path, files), files))

        result = []

        for file_model in previous_tip_files:
            path = file_model.full_file_path
            if file_model.full_file_path in files_dict:
                # Existing
                tup = (Revision.MODIFIED, file_model.full_file_path)
                if include_files:
                    tup += (file_model, files_dict[path])
                result.append(tup)

        return result


    def mark_as_tip(self):
        """
        Walk through history marking all the most recent files as "tip"

        NOTE: not the most efficient queries
        """
        changes = self.get_stat_diff_if_applied()
        for stat, path, old_file, new_file in changes:
            old_file.is_tip = False
            old_file.save()

        # Set all (non-removed) files to be tip
        self.files.filter(removed=False).update(is_tip=True)

def file_path_builder(instance, filename):
    return instance.path_builder(filename)

class FileModel(models.Model, GenericUploadableMixin):
    class Meta:
        app_label = 'project'

    class S3UploadableMeta:
        file_field = 'path'
        is_ready_field = 'is_uploaded'

        @staticmethod
        def get_object(request, filename, variables):
            """
            Either creates a new file model or fetches the relevant one
            """
            revision_id = variables['revision_id']
            folder = variables['folder']
            revision = Revision.objects.get(id=revision_id)
            project = revision.project
            search_folder = folder if folder.strip() else None

            # Make sure we are the same user, this is a good security check
            if request.user != revision.user:
                raise Exception("Wrong user trying to edit revision.")

            ### Condition 1: updating a file in THIS revision
            original_file = revision.get_file(search_folder, filename)
            if original_file:
                # Set old one as soft-deleted, create new
                # (does not replace, to prevent S3 "storage leak")
                original_file.deleted = True
                original_file.save()

            ### Condition 2: updating a TIP file
            tip_file = project.get_file(search_folder, filename)

            ### Finally, create a new FileModel
            f = FileModel(
                        revision=revision,
                        filename=filename,
                        project=revision.project,
                        folder=folder,
                        replaces=tip_file,
                        user=request.user
                    )
            return f

        @staticmethod
        def generate_filename(file_model, original_filename):
            revision = file_model.revision
            return revision.get_path_for_file(
                        file_model.folder, original_filename)


    creation_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    # The uploader
    user = models.ForeignKey(User,
            help_text=_("Last person to change the file"))

    filename = models.CharField(max_length=255,
            help_text=_("Original filename of file"))

    folder = models.CharField(max_length=255,
            help_text=_("Folder path of the file"))

    project = models.ForeignKey("Project",
            related_name="files",
            help_text=_("Project associated with this file"))

    is_tip = models.BooleanField(
            default=False,
            db_index=True,
            help_text=_("Do these files represent the 'correct'/"
                        "most recent version?"))

    revision = models.ForeignKey("Revision",
            related_name="files",
            help_text=_("Revision this file was uploaded to"))

    file_license = LicenseField(
            blank=True,
            help_text=_("License for this file "
                "(defaults to project's license)"))

    #######################################
    # XXX not sure if these are useful any more
    title = models.CharField(max_length=255,
            blank=True,
            help_text=_("Title of this file"))

    credits = models.TextField(max_length=2048,
            blank=True,
            help_text=_("Author credits for this file"))

    description = models.TextField(max_length=2048,
            blank=True,
            help_text=_("A longer description, or notes about this file"))

    photo = models.ForeignKey(Photo,
            null=True, blank=True,
            help_text=_("Relevant photo for this file"))
    #######################################

    path = models.FileField(
            #upload_to=lambda i, f: i.path_builder(f),
            upload_to=file_path_builder,
            help_text=_("Actual file"))

    size = models.PositiveIntegerField(
            default=0,
            help_text=_("Size in bytes of the file"))

    is_uploaded = models.BooleanField(default=False,
            help_text=_('Has the file successfully finished uploading?'))

    replaces = models.ForeignKey("FileModel",
            null=True, blank=True,
            help_text=_("The file that this file replaces in the previous revision"))

    removed = models.BooleanField(default=False,
            help_text=_('Is this file being deleted in this revision?'))

    deleted = models.BooleanField(default=False,
            db_index=True,
            help_text=_('Field for "soft" deletion '
                        '(seems like perma-delete to user)'))

    def save(self, *a, **k):
        super(FileModel, self).save(*a, **k)


    @property
    def revision_stat(self):
        if self.removed:
            return Revision.DELETED
        elif self.replaces:
            return Revision.MODIFIED
        else:
            return Revision.ADDED

    @property
    def size_mb(self):
        """
        Size in megabytes, rounded to 2 decimals
        """
        return int((self.size / 1024.0 / 1024.0)*100.0) / 100.0


    @property
    def license(self):
        return self.file_license or self.project.license


    @staticmethod
    def make_title_from_filename(filename):
        """
        Beautifies a filename
        """
        s = os.path.splitext(filename)[0]

        # Split & combine all non-word characters
        s = u' '.join(re.split(r"[\W_-]+", s)).strip().capitalize()
        return s


    def path_builder(self, filename):
        """
        Builds a path based on a file
        """
        # Put files in directories based on their individual version numbers
        path = self.revision.make_path_for_file(self.folder, filename)
        return path


    def __str__(self):
        return self.full_path


    @property
    def full_file_path(self):
        if not self.folder:
            return self.filename
        return u"%s/%s" % (self.folder, self.filename)


    @property
    def full_path(self):
        return u"%s/%s" % (self.project.hubpath, self.full_file_path)

    def change_into_replacement(self, revision):
        """
        Changes this file model into a "replacement" one for the given revision
        """
        old_id = self.id
        self.id = None
        self.replaces_id = old_id
        self.revision = revision
        self.is_tip = False

    def get_absolute_url(self):
        return reverse('project_file', args=[self.project.hubpath, self.id])

    @property
    def annotations(self):
        # XXX 100% not used
        # Tacks on shortcut fields for display
        if hasattr(self, '_annotations'):
            return self._annotations
        annotations = {}
        annotations.is_remove
        self._annotations = annotations
        return annotations

    @classmethod
    def by_folder(cls, files):
        folders = sorted(set(map(lambda f: f.folder, files)) | set([""]))
        files_by_folder = []
        for folder in folders:
            files_by_folder.append((
                    folder,
                    filter(lambda f: f.folder == folder, files)
                ))

        return files_by_folder

