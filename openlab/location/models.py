import math

from django.db import models
from django.utils.translation import ugettext as _

from cities_light.models import Country, Region, City




def degrees_to_tile_numbers(lat_deg, lon_deg, zoom):
    """
    Converts lat and lon degrees to OpenStreetMap tile-system.

    Taken from OpenStreetMap Wiki
    """
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) +
                (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)



# The satelite Map Quest direct tile access URL was discontinued in 2016
# Replacing for now with (other) direct tile access URL for openstreetmaps
# "humanitarian" graphical layer (not nearly as good, but for now okay)
# Humanitarian example (open street map): http://tile-a.openstreetmap.fr/hot/15/9639/15963.png

#MAP_QUEST_URL = "http://otile2.mqcdn.com/tiles/1.0.0/%(tileset)s/%(zoom)i/%(x)i/%(y)i.jpg"
STAMEN_WATER_COLOR_URL = "http://a.tile.stamen.com/watercolor/%(zoom)i/%(x)i/%(y)i.jpg"
STAMEN_TERRAIN_URL = "http://a.tile.stamen.com/terrain-background/%(zoom)i/%(x)i/%(y)i.jpg"
TILESET = STAMEN_WATER_COLOR_URL
# TILESET = STAMEN_TERRAIN_URL

def image_url(lat_deg, lon_deg, zoom):
    """
    Returns a URL to a JPG of a Stamen tile
    """
    x, y = degrees_to_tile_numbers(lat_deg, lon_deg, zoom)
    return TILESET % {'x': x, 'y': y, 'zoom': zoom}


class LocatableBaseModel(models.Model):
    class Meta:
        abstract = True

    country = models.ForeignKey(Country, null=True, blank=True)
    region  = models.ForeignKey(Region, null=True, blank=True)
    city    = models.ForeignKey(City, null=True, blank=True)

    # Longitude, latitude, and street address

    street_address = models.TextField(
                blank=True, default="",
                help_text=_("Street address for the project."))

    longitude = models.DecimalField(max_digits=8, decimal_places=5,
                blank=True, null=True,
                help_text=_("Longitude for the project"))

    latitude = models.DecimalField(max_digits=8, decimal_places=5,
                blank=True, null=True,
                help_text=_("Latitude for the project"))

    def set_city(self, city):
        self.city = city
        self.region = city.region
        self.country = city.country

        if not self.longitude or not self.latitude:
            self.longitude = city.longitude
            self.latitude = city.latitude

    def set_region(self, region):
        self.city = None
        self.region = region
        self.country = region.country

    def set_country(self, country):
        self.city = None
        self.region = None
        self.country = country

    def copy_location_from(self, other):
        # Copies location from another LocatableBaseModel
        self.country = other.country
        self.region = other.region
        self.ciy = other.city
        self.longitude = other.longitude
        self.latitude = other.latitude
        self.street_address = other.street_address

    def location_name(self):
        # Gives the best info we have about location 
        return self.city or self.region or self.country or "Planet Earth"

    def get_location_image_url(self):
        if self.longitude:
            lon_deg = float(self.longitude)
            lat_deg = float(self.latitude)
            #lon_deg = float(self.city.longitude)
            #lat_deg = float(self.city.latitude)
            zoom = 11

            #if self.city.population:
            #    # Adjust zoom based on city population
            #    pass

            # Sadly only cities have long / lat coordinates presently
            url = image_url(lat_deg, lon_deg, zoom)
            return url

        return None

    @property
    def longitude_as_percent(self):
        lon = self.longitude
        if not lon:
            return None
        p = ((float(lon)+180.0) / 360.0)*100.0
        return p


    @property
    def latitude_as_percent(self):
        # for graphing on projections
        lat = self.latitude
        if not lat:
            return None
        p = ((float(lat)+90.0) / 180.0)*100.0 # - 14.0
        return p

    def latitude_as_percent_of_max_longitude(self):
        # Useful for getting around CSS limitations
        return self.latitude_as_percent
        return (self.latitude_as_percent - 10.0)


