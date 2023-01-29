import lucene
import json
from java.io import File
from org.apache.lucene import analysis, document, index, queryparser, search, store
from lupyne import engine

assert lucene.getVMEnv() or lucene.initVM()

from datetime import date
# Using readlines()
file1 = open('lucene-test/sep.txt', 'r')
Lines = file1.readlines()
  
geometries = []
for line in Lines[1:5]:
    feature = json.loads(line.strip())
    geometries.append(feature['geometry'])

docs = [
    {
        'city': 'San Francisco',
        'state': 'CA',
        'population': 808976,
        'location': geometries[0]['coordinates'][0]
    },
    {
        'city': 'Los Angeles',
        'state': 'CA',
        # 'incorporated': '1850-04-04',
        'population': 3849378,
        'location': geometries[1]['coordinates'][0]
    },
    {
        'city': 'Portland',
        'state': 'OR',
        # 'incorporated': '1851-02-08',
        'population': 575930,
        'location': geometries[2]['coordinates'][0]
    },
]

indexer = engine.Indexer('tempIndex')
indexer.set('city', stored=True)
indexer.set('state', stored=True)
# set method supports custom field types inheriting their default settings
indexer.set('population', dimensions=1, stored=True)
indexer.set('point', engine.SpatialField, stored=True)
indexer.set('poly', engine.SpatialField, stored=True)
# assigned fields can have a different key from their underlying field name
indexer.fields['location'] = engine.NestedField('state.city')

for doc in docs:
    point = doc.pop('longitude'), doc.pop('latitude')
    poly = [(x[0], x[1]) for x in doc['location']]
    location = doc['state'] + '.' + doc['city']
    indexer.add(doc, location=location, point=[point], poly=poly)
indexer.commit()

query = indexer.fields['poly'].within(34.458433, 31.5029, distance=100.0)
print([hit for hit in indexer.search(query)])