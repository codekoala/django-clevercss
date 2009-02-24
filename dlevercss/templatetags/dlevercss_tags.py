from django import template
from django.conf import settings
from dlevercss.models import Stylesheet
from datetime import datetime
import os
import clevercss

register = template.Library()

# the following tag was borrowed from:
# http://repo.or.cz/w/gitology.git?a=blob;f=src/gitology/d/templatetags/clevercsstag.py
@register.tag(name="clevercss")
def do_clevercss(parser, token):
    nodelist = parser.parse(('endclevercss',))
    parser.delete_first_token()
    return CleverCSSNode(nodelist)

class CleverCSSNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        output = self.nodelist.render(context)
        return clevercss.convert(output)

def get_clever_css(title):
    title = title.strip('"')

    try:
        sheet = Stylesheet.objects.get(title=title)
    except Stylesheet.DoesNotExist:
        raise template.TemplateSyntaxError('%s is an invalid stylesheet' % title)

    parse = False
    modified = None
    path = os.path.join(settings.MEDIA_ROOT, 'clevercss')
    file = '%s.css' % sheet.filename
    output = os.path.join(path, file)

    try:
        os.makedirs(path)
    except OSError:
        pass

    try:
        modified = datetime.fromtimestamp(os.path.getmtime(output))
    except OSError:
        pass

    if not modified or (modified and modified < sheet.date_updated):
        parse = True

    if parse:
        try:
            f = open(output, 'w')
            f.write(clevercss.convert(sheet.ccss))
            f.close()
        except IOError:
            raise template.TemplateSyntaxError('Failed to write %s' % output)
    return '%sclevercss/%s' % (settings.MEDIA_URL, file)
register.simple_tag(get_clever_css)