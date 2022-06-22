import json

from app.models import School


def export_school(school):
    boundary = json.loads(school.boundary.json)
    percentage = round(school.capacity, 2) * 100
    string_capacity = f" {percentage}% Capacity"
    feature = {
        'type': 'Feature',
        'properties': {
            'name': school.name,
            'capacity': school.capacity,
            'string_capacity': string_capacity,
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
