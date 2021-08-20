# Django
import csv

from app.forms import IsatForm
from app.models import Isat
from app.models import School


def clean_stat(stat):
    try:
        clean = float(stat.replace('<','').replace('>',''))
    except ValueError:
        clean = None
    return clean

def import_isat(filename='isat.csv'):
    with open(filename) as f:
        reader = csv.reader(
            f,
            skipinitialspace=True,
        )
        next(reader)
        rows = [row for row in reader]
        for row in rows:
            # print(row)
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
            if row[1] == 'JOINT SCHOOL DISTRICT NO. 2':
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
                    'year': 2021,
                    'school': school,
                }
                form = IsatForm(data=data)
                if form.is_valid():
                    form.save()

    return
