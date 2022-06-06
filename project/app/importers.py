# Django
import csv
import json

from app.forms import IsatForm
from app.models import Isat
from app.models import School
from app.models import Staff
from django.contrib.gis.geos import GEOSGeometry


def clean_stat(stat):
    try:
        clean = round(float(stat.replace('<','').replace('>','').replace('%', '').strip()),1)
    except ValueError:
        clean = None
    return clean

def clean_note(stat):
    try:
        float(stat)
    except ValueError as e:
        if '<' in stat:
            return '<'
        if '>' in stat:
            return '>'
        if '***' in stat:
            return 'N/A'
        if 'N/A' in stat:
            return 'N/A'
        if 'NSIZE' in stat:
            return 'NSIZE'
        return ''

def import_isat(filename, year):
    with open(filename) as f:
        reader = csv.reader(
            f,
            skipinitialspace=True,
        )
        next(reader)
        rows = [row for row in reader]
        for row in rows:
            subject_reduce = {
                'ELA': 10,
                'Math': 20,
                'Science': 30,
            }
            grade_reduce = {
                'All Grades': 1,
                'Grade 3': 3,
                'Grade 4': 4,
                'Grade 5': 5,
                'Grade 6': 6,
                'Grade 7': 7,
                'Grade 8': 8,
                'High School': 10,
            }
            if row[1] == 'JOINT SCHOOL DISTRICT NO. 2' and row[6].strip() == 'All Students':
                school_id = int(row[2])
                try:
                    school = School.objects.get(
                        school_id=school_id,
                    )
                except School.DoesNotExist:
                    continue
                data = {
                    'subject': subject_reduce[row[4]],
                    'grade': grade_reduce[row[5]],
                    'advanced': clean_stat(row[7]),
                    'proficient': clean_stat(row[8]),
                    'basic': clean_stat(row[9]),
                    'below': clean_stat(row[10]),
                    'advanced_note': clean_note(row[7]),
                    'proficient_note': clean_note(row[8]),
                    'basic_note': clean_note(row[9]),
                    'below_note': clean_note(row[10]),
                    'year': year,
                    'school': school,
                }
                form = IsatForm(data=data)
                if form.is_valid():
                    form.save()
                else:
                    continue
    return


def import_staff(filename):
    with open(filename) as f:
        reader = csv.reader(
            f,
            skipinitialspace=True,
        )
        rows = [row for row in reader]
        for row in rows:
            name = str(row[0]).strip()
            position = str(row[2]).strip()
            school_raw = str(row[1]).strip()
            location_id = int(row[3])
            try:
                school = School.objects.get(
                    location_id=location_id,
                )
            except School.DoesNotExist:
                school = None

            staff = Staff(
                name=name,
                position=position,
                school_raw=school_raw,
                school=school,
            )
            staff.save()
    return


def import_locations(filename):
    with open(filename) as f:
        reader = csv.reader(
            f,
            skipinitialspace=True,
        )
        next(reader)
        rows = [row for row in reader]
        for row in rows:
            location_id = int(row[0])
            name = str(row[1]).strip()
            try:
                school = School.objects.get(
                    location_id=location_id,
                )
            except School.DoesNotExist:
                print(name)
            except School.MultipleObjectsReturned:
                print('Multi', name)
    return


def import_enrollment(filename):
    with open(filename) as f:
        reader = csv.reader(
            f,
            skipinitialspace=True,
        )
        next(reader)
        rows = [row for row in reader]
        miss = []
        for row in rows:
            name = str(row[0]).strip()
            enrollment = int(row[1])
            capacity = int(row[2])
            try:
                school = School.objects.get(
                    full=name,
                )
            except School.DoesNotExist:
                location_id = int(row[4])
                school = School.objects.get(
                    location_id=location_id,
                )
            except School.MultipleObjectsReturned:
                print('Multi', name)
            school.enrollment = enrollment
            school.capacity = capacity
            school.save()
    return


def import_boundary_file(filename):
    with open(filename) as f:
        geojson = json.loads(f.read())
        for feature in geojson['features']:
            school = School.objects.get(name=feature['properties']['Name'])
            geometry = feature['geometry']
            if geometry['type'] == 'Polygon':
                geometry['type'] = 'MultiPolygon'
                geometry['coordinates'] = [geometry['coordinates']]
            geom = GEOSGeometry(str(feature['geometry']))
            school.boundary = geom
            school.save()
    return
