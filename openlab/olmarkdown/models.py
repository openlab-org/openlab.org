from datetime import datetime
from django.utils.html import strip_tags

from django.db import models
from django.utils.translation import ugettext as _

from django.utils.safestring import mark_safe


from . import extensions

SUMMARY_LENGTH = 200

class OLMarkdownBase(models.Model):

    class Meta:
        abstract = True

    olmarkdown_rendered = models.TextField(blank=True,
            help_text=_("HTML for rendered OL Markdown"))

    olmarkdown_summary = models.TextField(blank=True,
            help_text=_("Text-only suffix of rendered, for rendered OL Markdown"))

    olmarkdown_rendered_date = models.DateTimeField(blank=True, null=True)

    def get_olmarkdown_source(self):
        raise NotImplemented("Anything that subclasses OLMarkdownBase should "
                            "implement get_olmarkdown_source!")

    def fetch_olmarkdown_context_object(self):
        raise NotImplemented("Anything that subclasses OLMarkdownBase should "
                            "implement fetch_olmarkdown_context_object!")

    def regenerate_markdown(self, context_object=None):
        """
        Regenerates the OL Markdown field for this object.

        (May cause DB Queries to fetch info about related objects.)
        """

        if not context_object:
            context_object = self.fetch_olmarkdown_context_object()

        source = self.get_olmarkdown_source()
        result = extensions.markdown_for_object(source, context_object)
        self.olmarkdown_rendered = result
        self.olmarkdown_rendered_date = datetime.now()
        summary = strip_tags(result)
        if len(summary) > 197:
            summary = summary[:197] + "..."
        self.olmarkdown_summary = summary

    @property
    def rendered_markdown(self):
        if not self.olmarkdown_rendered:
            # Was viewed before it was ready, generate on the fly, shouldn't
            # happen ever though once we get everything in place
            # XXX logging
            self.regenerate_markdown()
        return mark_safe(self.olmarkdown_rendered)

    @property
    def rendered_summary(self):
        if not self.olmarkdown_summary:
            # Was viewed before it was ready, generate on the fly, shouldn't
            # happen though once we get everything in place
            self.regenerate_markdown()
        return self.olmarkdown_summary

    @staticmethod
    def _all_subclasses():
        classes = OLMarkdownBase.__subclasses__()
        return classes


