import json

import lucene
from org.apache.lucene import geo
from lupyne.lupyne import engine


lucene.initVM()

# from org.apache.lucene.geo import GeoPolygonFactory, Polygon

# Using readlines()
file1 = open('/home/sep.txt', 'r')
Lines = file1.readlines()
  
features = []
try:
    # POLYGON((30 10, 40 40, 20 40, 10 20, 30 10))
    for i, line in enumerate(Lines[0:5]):
        feature = json.loads(line.strip())
        (pg, ) = geo.Polygon.fromGeoJSON(json.dumps({'type': 'Polygon', 'coordinates': [[(p[1], p[0]) for p in feature['geometry']['coordinates'][0]]]}))
        # poly = Polygon([[p[0], p[1]] for p in feature['geometry']['coordinates'][0]])
        # if not poly.is_valid:
        #     continue

        features.append({
            # 'poly': [(p[0], p[1]) for p in feature['geometry']['coordinates'][0]],
            'poly': pg,
            'name': f'feat_{i}'
        })
        
except BaseException as e:
    print(e)
indexer = engine.Indexer('tempIndex')
indexer.set('poly', engine.documents.ShapeField)
indexer.set('name', engine.Field.Text, stored=True)

for doc in features:
    indexer.add(doc)
indexer.commit()

query = indexer.fields['poly'].intersects(features[0]['poly'])
print([hit for hit in indexer.search(query)])