import json


def export_school(school):
    boundary = json.loads(school.boundary.json)
    feature = {
        'type': 'Feature',
        'properties': {
            'name': school.name,
            'capacity': school.capacity,
        },
        'geometry': boundary,
    }
    return feature

def export_schools(schools):
    features = []
    for school in schools:
        feature = export_school(school)
        features.append(feature)
    collection = {
        'type': 'FeatureCollection',
        'features': features,
    }
    return collection
