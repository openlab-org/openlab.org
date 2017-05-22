import sys
import json
import os

from . import anthrome_types




try:
    import Image
except ImportError:
    from PIL import Image

_path = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(_path, "data", "anthrome_offsets.json")


_up = os.path.dirname(_path)

if _up not in sys.path:
    sys.path.append(_up)

GEOTIFF_PATH = os.path.join(_path, 'data', 'anthro2_a2000.tif')

GDAL_INFO = '''
Driver: GTiff/GeoTIFF
Files: anthro2_a2000.tif
Size is 4320, 2160
Coordinate System is:
GEOGCS["WGS 84",
    DATUM["WGS_1984",
        SPHEROID["WGS 84",6378137,298.257223563,
            AUTHORITY["EPSG","7030"]],
        AUTHORITY["EPSG","6326"]],
    PRIMEM["Greenwich",0],
    UNIT["degree",0.0174532925199433],
    AUTHORITY["EPSG","4326"]]
Origin = (-180.000000000000000,89.999999999999915)
Pixel Size = (0.083333333333333,-0.083333333333333)
Metadata:
  TIFFTAG_SOFTWARE=IMAGINE TIFF Support
Copyright 1991 - 1999 by ERDAS, Inc. All Rights Reserved
@(#)$RCSfile: etif.c $ $Revision: 1.10.1.9.1.9.2.11 $ $Date: 2004/09/15 18:42:01EDT $
  TIFFTAG_XRESOLUTION=1
  TIFFTAG_YRESOLUTION=1
  TIFFTAG_RESOLUTIONUNIT=1 (unitless)
  AREA_OR_POINT=Area
Image Structure Metadata:
  INTERLEAVE=BAND
Corner Coordinates:
Upper Left  (-180.0000000,  90.0000000) (180d 0'0.00"W, 90d 0'0.00"N)
Lower Left  (-180.0000000, -90.0000000) (180d 0'0.00"W, 90d 0'0.00"S)
Upper Right ( 180.0000000,  90.0000000) (180d 0'0.00"E, 90d 0'0.00"N)
Lower Right ( 180.0000000, -90.0000000) (180d 0'0.00"E, 90d 0'0.00"S)
Center      (  -0.0000000,  -0.0000000) (  0d 0'0.00"W,  0d 0'0.00"S)
Band 1 Block=64x64 Type=Byte, ColorInterp=Gray
'''

class GTiff(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GTiff, cls).__new__(
                    cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.im = Image.open(GEOTIFF_PATH)
        self.width, self.height = self.im.size


    def new(self):
        # creates a new image with the same dimensions as this one
        return Image.new('RGBA', (self.width, self.height))

    def getpixel(self, x, y):
        return self.im.getpixel((x, y))

    def get_type_number(self, x, y):
        return self.im.getpixel((x, y)) or None

    def get_latitude_longitude(self, x, y):
        lat = (y/(self.height/180)-90)/-1
        lng = x/(self.width/360)-180
        return lat, lng

    def get_x_y(self, longitude, latitude):
        # Upper Left  (-180.0000000,  90.0000000) (180d 0'0.00"W, 90d 0'0.00"N)
        # Lower Left  (-180.0000000, -90.0000000) (180d 0'0.00"W, 90d 0'0.00"S)
        # Upper Right ( 180.0000000,  90.0000000) (180d 0'0.00"E, 90d 0'0.00"N)
        # Lower Right ( 180.0000000, -90.0000000) (180d 0'0.00"E, 90d 0'0.00"S)
        # Center      (  -0.0000000,  -0.0000000) (  0d 0'0.00"W,  0d 0'0.00"S)

        #        upper_left
        x = ((longitude  + 90 )/180) * self.width
        y = ((latitude   + 180)/360) * self.height
        return x, y


def get_type_number(longitude, latitude):
    gtiff = GTiff()
    x, y = gtiff.get_x_y(longitude, latitude)
    return gtiff.get_type_number(x, y)


class _maps: pass

STATIC_DIR = os.path.join(_path, 'static', 'anthrome', 'images')
GLOBAL_MAP_PATH_SPECIFIC = os.path.join(STATIC_DIR, 'map_large_specific.png')
GLOBAL_MAP_PATH_EMPTY = os.path.join(STATIC_DIR, 'map_large_empty.png')
GLOBAL_MAP_PATH = os.path.join(STATIC_DIR, 'map_large.png')
ANTHROME_MAP_TEMPLATE = os.path.join(STATIC_DIR, 'map_%02i_large.png')
ANTHROME_GROUP_MAP_TEMPLATE = os.path.join(STATIC_DIR, 'map_%i_group_large.png')

GRAY_CONSTANT = (127, 127, 127)
HILIGHT_CONSTANT = (255, 255, 255)

def generate_maps():
    # this function takes a while to run
    gtiff = GTiff()
    global_map = gtiff.new()
    global_map_specific = gtiff.new()
    global_map_empty = gtiff.new()

    anthrome_offsets = {}

    anthrome_maps = {}
    for anthrome in anthrome_types.Anthrome.all():
        anthrome_maps[anthrome.number] = gtiff.new()

    anthrome_group_maps = {}
    for anthrome_group in anthrome_types.AnthromeGroup.all():
        anthrome_group_maps[anthrome_group.number] = gtiff.new()

    inc = int(gtiff.width / 15)
    global_offset = [10000, 10000] # big numbers
    global_offset_2 = [3000, 1500] # small numbers

    for x in range(gtiff.width):
        for y in range(gtiff.height):
            number = gtiff.get_type_number(x, y)
            if not number:
                # its a blank spot
                continue

            # its an anthrome here
            anthrome = anthrome_types.Anthrome.get_by_number(number)
            anthrome_group = anthrome_types.AnthromeGroup.get_by_number(number)

            # Make the globe based on anthrome_groups
            global_map.putpixel((x, y), anthrome_group.first_child.color_rgb)

            # Make the global map more detailed
            global_map_specific.putpixel((x, y), anthrome.color_rgb)

            # Make the group map more detailed
            anthrome_group_maps[anthrome_group.number].putpixel((x, y), anthrome.color_rgb)

            # Gray empty one
            global_map_empty.putpixel((x, y), GRAY_CONSTANT)

            # do specific maps
            # Instead of using RGB, we just do orange, for a sort of "higlight" effect
            anthrome_maps[number].putpixel((x, y), HILIGHT_CONSTANT)

            # Used to put a white pixel in the upper-left & bottom-right of all
            # maps, as a hack to prevent destructive cropping
            if x < global_offset[0]:
                global_offset[0] = x
            if y < global_offset[1]:
                global_offset[1] = y
            if x > global_offset_2[0]:
                global_offset_2[0] = x
            if y > global_offset_2[1]:
                global_offset_2[1] = y

            # Sets x and y offsets of first pixel encountered (used for
            # calculating margins)
            anthrome_offsets.setdefault(number, (x, y))
            anthrome_offsets.setdefault(anthrome_group.number, (x, y))

        if x % inc == 0:
            print("Progress...", int((float(x) / gtiff.width)*100))

    print("SAVING OFFSETS")
    anthrome_offsets['global_offset'] = global_offset
    anthrome_offsets['global_offset_2'] = global_offset_2
    open(JSON_PATH, 'w+').write(json.dumps(anthrome_offsets, indent=4))

    print("--------------------------------")
    print("SAVING MAPS")
    print("--------------------------------")
    for number, img in list(anthrome_maps.items()):
        print("Anthrome Map - %i " % number)
        img.putpixel(global_offset, (254, 254, 254))
        img.putpixel(global_offset_2, (254, 254, 254))
        img.save(ANTHROME_MAP_TEMPLATE % number)

    for number, img in list(anthrome_group_maps.items()):
        print("Anthrome Group Map - %i " % number)
        img.putpixel(global_offset, (254, 254, 254))
        img.putpixel(global_offset_2, (254, 254, 254))
        img.save(ANTHROME_GROUP_MAP_TEMPLATE % number)

    print("GLOBAL MAPS")
    global_map.save(GLOBAL_MAP_PATH)
    global_map_specific.save(GLOBAL_MAP_PATH_SPECIFIC)
    global_map_empty.save(GLOBAL_MAP_PATH_EMPTY)

    print("--------------------------------")
    print("CONVERTING MAPS VIA PIPELINE    ")
    print("--------------------------------")
    convert_map(GLOBAL_MAP_PATH)

    for number, img in list(anthrome_maps.items()):
        print("Anthrome Map -  %i " % number)
        convert_map(ANTHROME_MAP_TEMPLATE % number, { })


    for number, img in list(anthrome_group_maps.items()):
        print("Anthrome Group Map -  %i " % number)
        convert_map(ANTHROME_GROUP_MAP_TEMPLATE % number)

    print("GLOBAL MAPS")
    convert_map(GLOBAL_MAP_PATH)
    convert_map(GLOBAL_MAP_PATH_SPECIFIC)
    convert_map(GLOBAL_MAP_PATH_EMPTY)


def convert_map(path, preview_override={}):
    from prequeue import handlers
    in_path             = path
    preview_path_prefix = os.path.splitext(path)[0].replace('_large', '')
    thumb_path_prefix   = os.path.splitext(path)[0].replace('_large', '') + ".thumb"

    # Generate image
    result = handlers.image_preview('.png',
                in_path,
                preview_path_prefix,
                thumb_path_prefix,
                '',
                preview_override=preview_override ,
                format_override='.png')

def main():
    generate_maps()

if __name__ == '__main__':
    main()

