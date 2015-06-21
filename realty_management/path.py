from geopy.geocoders import Nominatim
from geopy.distance import vincenty
geolocator = Nominatim()

class Location(object):
    def __init__(self, address):
        self.address = address
        loc = geolocator.geocode(address)
        self.lat = loc.latitude
        self.long = loc.longitude

def shortest_route(properties, start, end):
    locations = list()
    path = list()
    for p in properties:
        locations.append(Location(p.address))

    curr = Location(start)
    path.append(curr.address.replace(" ", "+"))
    while len(locations) > 1:
        nearest = find_nearest(curr, locations)
        if curr in locations:
            locations.remove(curr)
        curr = nearest
        path.append(curr.address.replace(" ", "+"))
    path.pop(0)
    #path.append(locations[0].address.replace(" ", "+"))
    path.append(Location(end).address.replace(" ", "+"))
    return path

def find_nearest(curr, locations):
    min_dist = -1
    nearest = None
    for l in locations:
        if l is not curr:
            dist = vincenty((curr.lat, curr.long), (l.lat, l.long))
            if min_dist == -1 or dist < min_dist:
                min_dist = dist
                nearest = l
    return nearest