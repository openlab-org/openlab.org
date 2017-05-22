import re
from . import extensions

USERNAME_MENTIONS = re.compile(r'%s="([^"]+)"' % extensions.UserPattern.CLUE_ATTR)
def get_username_mentions(html):
    return USERNAME_MENTIONS.findall(html)

