from django.db import models
from django.utils.translation import ugettext as _

from olmarkdown.models import OLMarkdownBase
from hubpath.models import hubpath_objects


class WikiSite(models.Model):
    # WikiSite is a collection of wiki pages


    # TODO next ORM change delete this --v-- and enable the bottom 3
    index = models.ForeignKey('WikiPage', null=True, blank=True,
                    related_name="index_page",
                    help_text=_("The index page for this site"))

    # if the wiki can be edited by any user
    public_editable = models.BooleanField(default=True,
                    verbose_name=_("Enable public editing"),
                    help_text=_("Turn this on to enable the wiki to be editable by anyone"))
    is_disabled = models.BooleanField(default=False,
                    verbose_name=_("Disable Wiki"),
                    help_text=_("Temporarily disable the wiki system, for both "
                        "editing and viewing (without deleting it)."))
    is_public = models.BooleanField(default=True,
                    verbose_name=_("Wiki is visible to all"),
                    help_text=_("Disable to hide the wiki to non-contributors"))

class WikiPage(OLMarkdownBase):
    class Meta:
        unique_together = (('site', 'slug'), )
        index_together = (('site', 'slug'), )

    site = models.ForeignKey(WikiSite,
                    help_text=_("The site this page belongs to."))

    title = models.CharField(verbose_name=_("Page title"), max_length=255)

    slug = models.SlugField()

    text = models.TextField(
            verbose_name=_("Page text"),
            help_text=_("The content of the Wikipage. <em>(Markdown syntax is available.)</em>"))

    creation_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_olmarkdown_source(self):
        """
        The source is just stored in "text"
        """
        return self.text

    def fetch_olmarkdown_context_object(self):
        """
        Get the Team, Project, or Service that this wikipage is in the context
        of.
        """
        try:
            obj = hubpath_objects.arbitrary_get(site_id=self.site_id)
        except hubpath_objects.DoesNotExist:
            # Orphaned??
            return self
        else:
            return obj




