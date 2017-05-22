from django.db import models
from django.core.validators import RegexValidator


class LicenseField(models.CharField):
    """
    Field that allows multiple choice licensing.
    """
    def __init__(*a, **k):
        choices = (
                ('pd', 'Public domain'),
                ('cc-by', 'Creative Commons Attribution'),
                ('cc-by-sa', 'Creative Commons Attribution-ShareAlike'),
                ('gpl3', 'GPL 3.0'),
                ('lgpl3', 'LGPL 3.0'),
                ('tapr', 'TAPR Open Hardware'),
                ('cern', 'CERN Open Hardware'),
                #('cc-by-nc', 'Creative Commons Attribution-NonCommercial'),
                #('cc-by-nd', 'Creative Commons Attribution-NoDerivs'),
                #('cc-by-nc-sa', 'Creative Commons Attribution-NonCommercial-ShareAlike'),
                #('cc-by-nc-nd', 'Creative Commons Attribution-NonCommercial-NoDerivs'),
            )
        if 'dont_allow' in k:
            disallowed = lambda c: not any([(s in c) for s in k['dont_allow']])
            choices = filter(lambda c: disallowed(c[0]), choices)
            del k['dont_allow']
        k['choices'] = choices
        k['max_length'] = 24
        models.CharField.__init__(*a, **k)

