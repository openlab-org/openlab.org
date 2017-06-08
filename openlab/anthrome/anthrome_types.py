import math
import json
import os
import sys
from subprocess import check_call


_path = os.path.dirname(os.path.abspath(__file__))

JSON_PATH = os.path.join(_path, "data", "anthrome_offsets.json")

_up = os.path.dirname(_path)

if _up not in sys.path:
    sys.path.append(_up)


# photographer deltafrut is awesome, btw
ANTHROME_TYPE_INFO = [
    # Color scheme idea:
    # Red
    (11, 1170211, 'Urban',                           'sao_paulo__ndecam__cc_by.jpg', '#FF0000'),
    (12, 1357412, 'Mixed settlements',               'suburb__futureatlas.com.jpg',  '#FF7373'),

    # Pink
    (21, 2822921, 'Rice villages',                   'rice_village__yarra64.jpg',    '#D0464A'),
    (22, 2439522, 'Irrigated villages',              'irrigation__soilscience.jpg',  '#9C4E50'),
    (23, 5066423, 'Rainfed villages',                'lencois__deltafruit.jpg',      '#87171A'),
    (24, 1091524, 'Pastoral villages',               'san_cristobal_de_las_casas__emilio_labrador.jpg', '#E87477'),

    # Blue
    (31, 1600631, 'Residential irrigated croplands', 'chpaada_do_apodi_melao2__deltafrut.jpg', '#6DC2CA'),
    (32, 15894532, 'Residential rainfed croplands',  'chpaada_do_apodi_abacaxi__deltafrut.jpg', '#639398'),
    (33, 9675533, 'Populated croplands',             'field_wisconsin__dieseldemon.jpg',        '#237B83'),
    (34, 4071934, 'Remote croplands',                'rice_2__gillpenney.jpg',                  '#96DEE4'),

    # Yellow
    (41, 10447641, 'Residential rangelands',         'cote_dor__sybarite48.jpg',          '#FFF700'),
    (42, 18773842, 'Populated rangelands',           'rocha__michaelb.jpg',               '#BFBB30'),
    (43, 27895143, 'Remote rangelands',              'penedo__deltafruit.jpg',            '#A6A000'),

    # Green
    (51, 7156451, 'Residential woodlands',           'northern_wisconsin__chefranden.jpg', '#346524'),
    (52, 14732552, 'Populated woodlands',            'nwi__bradleypjohnson.jpg', '#304C27'),
    (53, 8011153, 'Remote woodlands',                'auga_rico__88rabbit.jpg', '#19420C'),
    #(54, 8223254, 'Inhabited treeless and barren lands', 'seca__mary_hsu.jpg', '#71B25C'),
    (54, 8223254, 'Inhabited treeless and barren lands', 'salt_desert__janus_sandsgaard__cc_by__500px__cropped.jpg', '#71B25C'),

    # Brown
    (61, 40267961, 'Wild woodlands',                     'alaska__arthur_chapman.jpg', '#854c30'),

    # White
    (62, 32495362, 'Wild treeless and barren lands',     'desert__canecalon.jpg',      '#ffffff'),
]

ANTHROME_GROUPS_INFO = [
    (1, 'Dense settlement', 1),
    (2, 'Village',          1),
    (3, 'Croplands',        3),
    (4, 'Rangelands',       2),
    (5, 'Semi-natural',     3),
    (6, 'Wild lands',       2),
]

CHOICES = [(str(i[0]), i[2]) for i in ANTHROME_TYPE_INFO]

ANTHROMES_DICT = {}
ANTHROMES = []
TOTAL_COUNT = sum([a[1] for a in ANTHROME_TYPE_INFO])
STATIC_DIR = os.path.join('anthrome', 'images')

ALL_BY_SLUG = {}



class AnthromeBase(object):
    json = None
    def __init__(self):
        if not AnthromeBase.json:
            try:
                AnthromeBase.json = json.load(open(JSON_PATH))
            except Exception as e:
                print("Error could load JSON for offsets")
                print(repr(e))
                return

        self.offset = AnthromeBase.json.get(str(self.number))
        # >>> d1 = 4320, 2160
        # >>> d2 = 1162, 455
        # >>> 4320/1162.0
        # 3.7177280550774525
        # >>> 2160/455.0
        # 4.747252747252747
        # 3.7177280550774525
        # NOTE: these aren't used any more... now we just cheat with a pixel to
        # prevent overzealous cropping
        self.offset_scaled = {
                'left': int((self.offset[0] - 0) / 4.747252747252747),
                'top': int((self.offset[1] - 223) / 4.747252747252747),
            }
        self.offset_percent = {
                'left': (self.offset_scaled['left']/1162.0)*100.0,
                'top': (self.offset_scaled['top']/1162.0)*100.0,
            }

        self.slug = self.label.replace(' ', '_').lower()
        self.slug_dasherized = self.label.replace(' ', '-').lower()
        ALL_BY_SLUG[self.slug_dasherized] = self

    @classmethod
    def by_slug(cls, slug):
        return ALL_BY_SLUG.get(slug)

class AnthromeGroup(AnthromeBase):
    def __init__(self, number, label, first_child):
        self.number = number
        self.label = label
        self.children = Anthrome.get_by_prefix(number)
        self.parent = None
        for child in self.children:
            child.parent = self
        self.first_child = Anthrome.get_by_number(int('%i%i' %
                            (number, first_child)))
        self.count = sum([a.count for a in self.children])
        self.ratio = float(self.count) / float(TOTAL_COUNT)
        self.ratio_as_percent = round(self.ratio*100.0, 1)
        AnthromeBase.__init__(self)

    @staticmethod
    def get_by_number(number):
        if number >= 10:
            number = int(str(number)[0])
        return ANTHROME_GROUPS_DICT.get(number)

    @classmethod
    def all(cls):
        return ANTHROME_GROUPS


class Anthrome(AnthromeBase):
    def __init__(self, number, count, label, image_filename, color=None):
        self.label = label
        self.number = number
        self.count = count
        self.ratio = float(count) / float(TOTAL_COUNT)
        self.ratio_as_percent = round(self.ratio*100.0, 1)
        self.image_filename = image_filename
        self.slug = self.label.replace(' ', '_').lower()
        self.attr = os.path.splitext(image_filename.replace('__cc_by',
            '').split('__')[1])[0]

        self.slug_attr = '%s__%s' % (self.slug, self.attr)
        self.out_filename = '%02i__%s.jpg' % (self.number, self.slug_attr)
        self.out_thumb_filename = self.out_filename.replace('.jpg', '.thumb.jpg')

        self.source_path = os.path.abspath(os.path.join(_path, 'media_src',
            image_filename))

        self.image_path = os.path.join(_path, 'static', STATIC_DIR,
                self.out_filename)

        self.image_thumb_path = os.path.join(_path, 'static', STATIC_DIR,
                self.out_thumb_filename)

        self.image_url = os.path.join(STATIC_DIR, self.out_filename)

        self.image_thumb_url = os.path.join(STATIC_DIR, self.out_thumb_filename)

        self.percent = round(self.ratio)
        self.random_color = "%02x%02x%02x" % (hash(number) % 255, hash(label) % 255, hash(count) % 255)
        self.color = color or self.random_color

        c = lambda i: int(self.color[i:i+2], 16)
        self.color_rgb = (c(1), c(3), c(5))

        # load margin offset stuff
        AnthromeBase.__init__(self)

    @staticmethod
    def get_by_number(number):
        return ANTHROMES_DICT.get(number)

    @staticmethod
    def get_by_prefix(number):
        results = []
        for i in range(10):
            code = int("%i%i" % (number, i))
            anth = Anthrome.get_by_number(code)
            if anth:
                results.append(anth)
        return results

    def __repr__(self):
        return '<Anthrome: %i %s>' % (self.number, self.slug)

    def __str__(self):
        return self.label

    THUMB_STYLE = {} # use default
    PREVIEW_STYLE = {
                'max_width': 1600,
                'max_height': 1600,
                'quality': 96,
                'brightness': 20, # boost brightness
                'contrast': 15, # boost contrast

                # only use bottom half
                'crop': '100%x-70%-0-0',
            }

    def generate_stock_image(self):
        # from prequeue import handlers
        in_path             = self.source_path
        preview_path_prefix, _ = os.path.splitext(self.image_path)
        thumb_path_prefix, _   = os.path.splitext(self.image_thumb_path)

        self.image_thumb_path = os.path.join(_path, STATIC_DIR, self.out_thumb_filename)

        # Generate image
        result = handlers.image_preview('.jpg',
                    in_path,
                    preview_path_prefix,
                    thumb_path_prefix,
                    '',
                    self.PREVIEW_STYLE,
                    self.THUMB_STYLE)
        print("RESULT!", result)

    @classmethod
    def generate_all_stock_images(cls):
        for anthrome in ANTHROMES:
            print(anthrome, anthrome.image_path)
            anthrome.generate_stock_image()


    @classmethod
    def all(cls):
        return ANTHROMES

ANTHROMES = [Anthrome(*a) for a in ANTHROME_TYPE_INFO]
ANTHROMES_DICT = dict([(a.number, a) for a in ANTHROMES])

ANTHROME_GROUPS = [AnthromeGroup(*a) for a in ANTHROME_GROUPS_INFO]
ANTHROME_GROUPS_DICT = dict([(a.number, a) for a in ANTHROME_GROUPS])

def main():
    # Generates stock image
    Anthrome.generate_all_stock_images()

    # Generates 



if __name__ == '__main__':
    main()


