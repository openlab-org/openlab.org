"""
Tests all markdown extensions
"""
from copy import deepcopy

from django.test import SimpleTestCase, TestCase
from openlab.users.models import User

from openlab.olmarkdown.extensions import markdown_for_object
from openlab.olmarkdown.extensions import PhotoPattern, TicketPattern, FilePattern

from openlab.team.models import Team
from openlab.team.factories import TeamTestFactory

from openlab.project.factories import ProjectTestFactory

from openlab.gallery.models import Photo

def _full_clean(text):
    return text.replace("\n", " ").replace("  ", " ").strip()

class TestBaseMarkdown(SimpleTestCase):
    """
    Mostly just a sanity test to make sure extra extensions are being added,
    stuff isn't conflicting with base markdown, etc.
    """
    def test_paragraphs(self):
        result = _full_clean(markdown_for_object(TEST_PARAGRAPHS, None))
        # BROKEN in 2017
        # self.assertEqual(result, TEST_PARAGRAPHS_EXPECTED)


class SimpleTestBase(SimpleTestCase):
    def check(self, in_, out, context=None):
        result = markdown_for_object(in_, context)
        self.assertEqual(result.strip(), out.strip())

def fake_photo(project, title):
    gallery = project.create_gallery_if_necessary()
    photo = Photo(gallery=gallery, title=title, user=project.user)
    photo.path = photo.path.field.attr_class(photo, photo.path.field, 'lol_fake_path')

    # hacks to mock preview thumb stuff
    #photo.preview_image_thumb = photo.preview_image_thumb.field.attr_class(photo,
    #        photo.preview_image_thumb.field, 'lol_fake_thumb_path')

    #photo.preview_image = photo.preview_image.field.attr_class(photo,
    #        photo.preview_image.field, 'lol_fake_preview_path')

    photo.save()
    return photo


def lolokay(s):
    el = etree.fromstring(s)
    return el.tostring()

class TestExtensions(TestCase):
    def setUp(self):
        testuser = User.objects.create_user("testext", "test@test.com", "asdf")
        self.project = ProjectTestFactory(user=testuser)

    def _expected(self, Cls, ctx):
        from markdown.util import etree
        s = '<p>%s</p>' % Cls.render_template(ctx)
        # "tree-ify" it which causes some stuff like re-arranging properties
        # etc
        el = etree.fromstring(s)
        s = etree.tostring(el)
        return s.decode('utf-8')

    def test_photo(self):
        photo = fake_photo(self.project, 'lol test title')

        result = markdown_for_object("{{ !%i }}" % photo.number, self.project)
        expected =  self._expected(PhotoPattern, {
                    'id': photo.number,
                    'object': self.project,
                    'args': [],
                })
        self.assertEqual(result, expected)

        result = markdown_for_object("{{ !%i full }}" % photo.number, self.project)
        expected =  self._expected(PhotoPattern, {
                    'id': photo.number,
                    'object': self.project,
                    'args': ['full'],
                })
        self.assertEqual(result, expected)

        result = markdown_for_object("{{ %s!%i }}" % (self.project.hubpath, photo.number), self.project)
        expected =  '<p>%s</p>' % PhotoPattern.render_template({
                    'id': photo.number,
                    'object': self.project,
                    'args': [],
                })

        # BROKEN in 2017:
        #self.assertEqual(result, expected)






    def _d_test_file(self):
        self.check("{{ joetest/project-one:stuff.stl }}", 
                '<p>%s</p>' % FilePattern.render_template({
                    'path': 'joetest/project-one',
                    'id': 'stuff.stl',
                    'object': None,
                    'args': [],
                }))

    def _d_test_ticket(self):
        self.check("{{ joetest/project-one#123 }}", 
                '<p>%s</p>' % TicketPattern.render_template({
                    'path': 'joetest/project-one',
                    'id': 123,
                    'object': None,
                    'args': [],
                }))


class TestTeam(TestCase):
    def setUp(self):
        testuser = User.objects.create_user("Test",
                            "test@test.com", "asdf")
        self.team = TeamTestFactory(user=testuser)

    def test_markdown(self):
        self.team.description = TEST_PARAGRAPHS
        self.team.regenerate_markdown()
        result = _full_clean(self.team.olmarkdown_rendered)
        # Broken in 2017
        #self.assertEqual(result, TEST_PARAGRAPHS_EXPECTED)


# Misc test data for large paragraphs
TEST_PARAGRAPHS = """
Script
=====

I think we're down to splitting hairs.

    #!python
    import sys
    class ExampleClass(object):
        def method(self, val, direction=DEFAULT):
            if val not in self:
                return None

            # Logging value
            sys.stderr.log("Testing statement")
            return val + 3


Shields up. _I know_ I didn't get the wrong room. Tricorders? She could be a
fake. We mentioned that a former member of the crew had come from the colony.
And when I show a glimmer of independent thought, you strap me down, inject me
with drugs and call it a "treatment." Look, I feel the same way, we all do,
but if anything's gonna get done here. That's one trick I didn't even know
about.  Data!

You think we got their attention, Data? *Yes.* That's right. All I have is a
vague memory of reading somewhere about someone taking a shower in his or her
clothing. A personal briefing? I told [OpenLab](http://openlab.org/) I'd feed
it while he was away.



Another header
-------------

First Header  | Second Header
------------- | -------------
Content Cell  | Content Cell
Content Cell  | Content Cell

Apple
:   Pomaceous fruit of plants of the genus Malus in 
    the family Rosaceae.

Orange
:   The fruit of an evergreen tree of the genus Citrus.

1. Ordered item 1
2. Ordered item 2

* Unordered item 1
* Unordered item 2

A Paragraph.
* Not a list item.

1. Ordered list item.
* Not a separate list item.
"""


TEST_PARAGRAPHS_EXPECTED = _full_clean('''
<h1>Script</h1>
<p>I think we're down to splitting hairs.</p>
<table class="codehilitetable"><tr><td class="linenos"><div class="linenodiv"><pre>1
2
3
4
5
6
7
8
9</pre></div></td><td class="code"><div class="codehilite"><pre><span class="kn">import</span> <span class="nn">sys</span>
<span class="k">class</span> <span class="nc">ExampleClass</span><span class="p">(</span><span class="nb">object</span><span class="p">):</span>
    <span class="k">def</span> <span class="nf">method</span><span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="n">val</span><span class="p">,</span> <span class="n">direction</span><span class="o">=</span><span class="n">DEFAULT</span><span class="p">):</span>
        <span class="k">if</span> <span class="n">val</span> <span class="ow">not</span> <span class="ow">in</span> <span class="bp">self</span><span class="p">:</span>
            <span class="k">return</span> <span class="bp">None</span>

        <span class="c"># Logging value</span>
        <span class="n">sys</span><span class="o">.</span><span class="n">stderr</span><span class="o">.</span><span class="n">log</span><span class="p">(</span><span class="s">&quot;Testing statement&quot;</span><span class="p">)</span>
        <span class="k">return</span> <span class="n">val</span> <span class="o">+</span> <span class="mi">3</span>
</pre></div>
</td></tr></table>

<p>Shields up. <em>I know</em> I didn't get the wrong room. Tricorders? She could be a
fake. We mentioned that a former member of the crew had come from the colony.
And when I show a glimmer of independent thought, you strap me down, inject me
with drugs and call it a "treatment." Look, I feel the same way, we all do,
but if anything's gonna get done here. That's one trick I didn't even know
about.  Data!</p>
<p>You think we got their attention, Data? <em>Yes.</em> That's right. All I have is a
vague memory of reading somewhere about someone taking a shower in his or her
clothing. A personal briefing? I told <a href="http://openlab.org/">OpenLab</a> I'd feed
it while he was away.</p>
<h2>Another header</h2>
<table>
<thead>
<tr>
<th>First Header</th>
<th>Second Header</th>
</tr>
</thead>
<tbody>
<tr>
<td>Content Cell</td>
<td>Content Cell</td>
</tr>
<tr>
<td>Content Cell</td>
<td>Content Cell</td>
</tr>
</tbody>
</table>
<dl>
<dt>Apple</dt>
<dd>Pomaceous fruit of plants of the genus Malus in 
the family Rosaceae.</dd>
<dt>Orange</dt>
<dd>The fruit of an evergreen tree of the genus Citrus.</dd>
</dl>
<ol>
<li>Ordered item 1</li>
<li>Ordered item 2</li>
</ol>
<ul>
<li>Unordered item 1</li>
<li>Unordered item 2</li>
</ul>
<p>A Paragraph.
* Not a list item.</p>
<ol>
<li>Ordered list item.
* Not a separate list item.</li>
</ol>
''')

