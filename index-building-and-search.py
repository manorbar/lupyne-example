import lucene
from datetime import date
import json

import java
from java.io import File
# from org.apache.lucene.geo import Polygon, Point
from org.apache.lucene import analysis, document, index, queryparser, search, store, geo
# from jarray import array
from lupyne import engine
from shapely import Polygon
from org.apache.lucene.document import LatLonPoint

from org.apache.lucene.spatial3d.geom import GeoPolygonFactory, GeoPoint, GeoPolygon, PlanetModel, XYZBounds
from org.apache.lucene.geo import XYPolygon


lucene.initVM()


# Using readlines()
file1 = open('/home/sep.txt', 'r')
Lines = file1.readlines()
  
geometries = []
features = []
try:
    # POLYGON((30 10, 40 40, 20 40, 10 20, 30 10))
    for line in Lines:
        feature = json.loads(line.strip())
        geometries.append(feature['geometry'])
        poly = Polygon([[p[0], p[1]] for p in feature['geometry']['coordinates'][0]])
        poly2 = geo.Polygon([p[0] for p in feature['geometry']['coordinates'][0]], [p[1] for p in feature['geometry']['coordinates'][0]])
        # Convert the polygon to a GeoShape
        # geo_points = [GeoPoint(PlanetModel.WGS84, point[0], point[1]) for point in poly.exterior.coords[:-1]]
        geo_points = [GeoPoint(PlanetModel.WGS84, p[0], p[1], p[2]) for p in feature['geometry']['coordinates'][0]]
        geo_polygon = GeoPolygonFactory.makeGeoPolygon(PlanetModel.WGS84, geo_points)
        geo_points = [GeoPoint(p[0], p[1], p[2]) for p in feature['geometry']['coordinates'][0]]
        # geo_points.append(GeoPoint(feature['geometry']['coordinates'][0][-1][0], feature['geometry']['coordinates'][0][-1][1], feature['geometry']['coordinates'][0][-1][2]))
        # poly = XYPolygon([30, 40, 20, 10, 30], [10, 40, 40, 20, 10])
        
        polygon = GeoPolygonFactory.makeGeoPolygon(PlanetModel.WGS84, geo_points)
        # polygon = GeoPolygonFactory.makeGeoPolygon(feature['geometry']['coordinates'][0])
        # poly = XYPolygon([p[0] for p in feature['geometry']['coordinates'][0]], [p[1] for p in feature['geometry']['coordinates'][0]])
        # Create a list of GeoPoints from your list of points
        point_list = [(x[0], x[1], x[2]) for x in feature['geometry']['coordinates'][0]]
        points = [GeoPoint.fromRadians(p[0], p[1]) for p in point_list]

        # Create a GeoPolygon from the list of GeoPoints
        polygon = GeoPolygonFactory.makeGeoPolygon(PlanetModel.WGS84, points)
        features.append(feature)
except BaseException as e:
    print(e)
indexer = engine.Indexer('tempIndex')
indexer.set('city', stored=True)
indexer.set('state', stored=True)
# set method supports custom field types inheriting their default settings
indexer.set('population', dimensions=1, stored=True)
indexer.set('poly', engine.ShapeField)
indexer.set('centroid', engine.ShapeField)
# assigned fields can have a different key from their underlying field name
indexer.fields['location'] = engine.NestedField('state.city')

for doc in docs:
    lats = [*[point[0] for point in doc['location']], doc['location'][0][0]]
    lons = [*[point[1] for point in doc['location']], doc['location'][0][1]]
    poly = Polygon([lats[i], lons[i]] for i, p in enumerate(lons))
    print(poly.is_closed)
    centroid = geo.Point(doc['location'][0][0], doc['location'][0][1])
    points = [geo.Point(lats[i], lons[i]) for i, p in enumerate(lats)]
    poly = geo.Polygon(lats, lons)
    location = doc['state'] + '.' + doc['city']
    indexer.add(doc, location=location, centroid=centroid)
indexer.commit()

query = indexer.fields['poly'].within(34.458433, 31.5029, distance=100.0)
print([hit for hit in indexer.search(query)])