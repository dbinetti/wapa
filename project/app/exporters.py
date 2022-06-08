import json


def export_school(school):
    feature = {
        'type': 'Feature',
        'properties': {
            'name': school.name,
            'capacity': school.capacity,
        },
        'geometry': school.boundary,
    }
    return json.dumps(feature)
