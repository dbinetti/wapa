# Standard Libary
import csv
import logging

import geocoder
from dateutil.parser import ParserError
from dateutil.parser import parse
# Django
from django.contrib.gis.geos import Point
from django_rq import job

from .forms import VoterForm
from .models import Voter

log = logging.getLogger(__name__)

GENDER = {
    'M': 10,
    'F': 20,
    'N': 30,
}

def extract_file(filename='voters.csv'):
    with open(filename) as f:
        reader = csv.DictReader(
            f,
            fieldnames=[
                'voter_id',
                'prefix',
                'last_name',
                'first_name',
                'middle_name',
                'suffix',
                'age',
                'gender',
                'phone',
                'street',
                'ResPostDir',
                'city',
                'st',
                'zipcode',
                'ResCountyDesc',
                'MailResAddr1',
                'MailResAddr2',
                'MailResCity',
                'MailresState',
                'MailResZip',
                'MailResCountry',
                'registration',
                'party',
                'precinct',
                'SCHOOLDISTRICT',
                'zone',
                'nov17',
                'apr18',
                'may18',
                'nov18',
                'nov19',
                'may20',
                'aug20',
                'nov20',
            ]
        )
        next(reader)
        rows = list(reader)
    return rows


def transform_data(rows):
    for row in rows:
        row['phone'] = row['phone'].replace(" ", "").replace("(","").replace(")","")
        row['party'] = getattr(Voter.PARTY, str(row['party']).lower().strip(), None)
        row['gender'] = getattr(GENDER, str(row['gender']).strip(), None)
        try:
            row['registration'] = parse(row['registration'].strip())
        except ParserError as e:
            log.error(e)
            row['registration'] = None
            continue
        row['zone'] = int(row['zone'][-1])
        row['age'] = int(row['age'])
        row['voter_id'] = int(row['voter_id'])
        row['prefix'] = row['prefix'].strip()
        row['last_name'] = row['last_name'].strip()
        row['first_name'] = row['first_name'].strip()
        row['middle_name'] = row['middle_name'].strip()
        row['suffix'] = row['suffix'].strip()
        row['street'] = row['street'].strip()
        row['city'] = row['city'].strip()
        row['st'] = row['st'].strip()
        row['zipcode'] = str(row['zipcode']).strip()
        row['precinct'] = int(row['precinct'])

        del row['precinct']
        del row['ResPostDir']
        del row['ResCountyDesc']
        del row['MailResAddr1']
        del row['MailResAddr2']
        del row['MailResCity']
        del row['MailresState']
        del row['MailResZip']
        del row['MailResCountry']
        del row['SCHOOLDISTRICT']
        del row['nov17']
        del row['apr18']
        del row['may18']
        del row['nov18']
        del row['nov19']
        del row['may20']
        del row['aug20']
        del row['nov20']
    return rows


@job
def clean_rows(rows):
    for row in rows:
        form = VoterForm(data=row)
        if not form.is_valid():
            log.info(form.errors.as_json())


@job
def wipe_address(rows):
    voters = Voter.objects.values(
        'voter_id',
        'street',
    )
    vs = list(voters)
    for row in rows:
        for v in vs:
            if v['voter_id'] == row['voter_id'] and v['street'] != row['street']:
                voter = Voter.objects.get(voter_id=v['voter_id'])
                voter.address = ''
                voter.place = ''
                voter.geocode = None
                voter.point = None
                voter.save()
                log.info(voter)
                continue


def load_voters(rows):
    i = 0
    t = len(rows)
    for row in rows:
        i += 1
        log.info(f'{i}/{t}')
        form = VoterForm(data=row)
        if not form.is_valid():
            log.error(form.errors.as_json())
            continue
        voter, created = Voter.objects.update_or_create(
            voter_id=row['voter_id'],
            defaults=row,
        )
    return


@job
def geocode_voter(voter):
    result = geocoder.google(f'{voter.street}, {voter.city}, {voter.st} {voter.zipcode}')
    voter.geocode = result.json
    voter.save()
    return


def check_precision(voter):
    if not voter.geocode:
        return False
    return all([
        voter.geocode['accuracy'] == 'ROOFTOP',
        any([
            voter.geocode['quality'] == 'premise',
            voter.geocode['quality'] == 'subpremise',
            voter.geocode['quality'] == 'street_address',
        ])
    ])


def denormalize_voter(voter):
    names = [
        voter.first_name,
        voter.middle_name,
        voter.last_name,
    ]
    name = ' '.join(filter(None, names))
    voter.name = name
    voter.address = voter.geocode['address']
    point = Point(
        voter.geocode['lng'],
        voter.geocode['lat'],
    )
    voter.point = point
    voter.place = voter.geocode['place']
    voter.is_precise = check_precision(voter)
    try:
        voter.location = f"{voter.geocode['street']}, {voter.geocode['city']}, {voter.geocode['state']}"
    except KeyError:
        pass
    return voter.save()
