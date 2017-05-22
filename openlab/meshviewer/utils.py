import subprocess
import json
import os.path

from django.conf import settings
from django.template.loader import render_to_string
import os
import sys
import re
import uuid

from core import util

_appdir = os.path.dirname(os.path.abspath(__file__))
PJS_SCRIPT = os.path.join(_appdir, "phantomjs_rasterize.js")
JS_PATH = os.path.join(_appdir, "static", "meshviewer", "js", "jsc3d", "jsc3d.min.js")

def phantomjs_rasterize(**kwds):
    args = json.dumps(kwds)
    return subprocess.check_call(["phantomjs", PJS_SCRIPT, args])

def render_to_png(path, output_path):
    """
    Renders the given STL or OBJ file path to the given output path
    """

    # NOTE Unix only here
    html_path = os.path.join("/tmp", "django_meshviewer", "%s.html" % str(uuid.uuid4()))

    # Build out directories
    util.makedirs_to_path(html_path)

    js3d_text = open(JS_PATH).read()
    full_in_path = 'file://' + path

    # Render & write preview HTML
    html = render_to_string("meshviewer/render/jsc3d_stl_render.html", {
            'jsc3d_js': js3d_text,
            'STATIC_URL': '',
            #'path': full_in_path,
            'url_stl': full_in_path,
        })

    open(html_path, "w+").write(html)

    # Use PhantomJS to rasterize (ie screencap) it 
    phantomjs_rasterize(output=output_path, input=html_path)


def test_main():
    test_path = os.path.join(_appdir, 'static', 'meshviewer',
                            'stl', 'hotair_retainer_support.stl')
    test_out_path = os.path.join(_appdir, 'out.png')
    render_to_png(test_path, test_out_path)


if __name__ == '__main__':
    test_main()

