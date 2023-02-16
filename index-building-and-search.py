import lucene
import json
from java.io import File
from org.apache.lucene import analysis, document, index, queryparser, search, store, geo
from lupyne.lupyne import engine
from shapely import Polygon

assert lucene.initVM()

from datetime import date
# Using readlines()
file1 = open('lupyne-example/sep.txt', 'r')
Lines = file1.readlines()
  
geometries = []
features = []
for line in Lines[1:5]:
    feature = json.loads(line.strip())
    geometries.append(feature['geometry'])
    features.append(feature)
    

docs = [
    {
        'city': 'San Francisco',
        'state': 'CA',
        'population': 808976,
        'location': geometries[0]['coordinates'][0],
        'feature': features[0]
    },
    {
        'city': 'Los Angeles',
        'state': 'CA',
        # 'incorporated': '1850-04-04',
        'population': 3849378,
        'location': geometries[1]['coordinates'][0],
        'feature': features[1]
    },
    {
        'city': 'Portland',
        'state': 'OR',
        # 'incorporated': '1851-02-08',
        'population': 575930,
        'location': geometries[2]['coordinates'][0],
        'feature': features[2]
    },
]

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