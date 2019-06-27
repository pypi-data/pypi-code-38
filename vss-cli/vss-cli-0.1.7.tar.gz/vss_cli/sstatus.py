from vss_cli.vssconst import STATUS_PAGE_ID, STATUS_PAGE_SERVICE
import requests
from dateutil import parser as dateutil_parser

components_url = 'https://{page_id}.statuspage.io/' \
                 'api/v2/components.json'.format(page_id=STATUS_PAGE_ID)

upcoming_maints_url = 'https://{page_id}.statuspage.io/' \
                      'api/v2/scheduled-maintenances/' \
                      'upcoming.json'.format(page_id=STATUS_PAGE_ID)


def format_iso8601(s):
    d = dateutil_parser.parse(s)
    return d.strftime("%Y-%m-%d %a %H:%M:%S %z")


def get_component():
    r = requests.get(components_url)
    components = r.json()
    for cmp in components['components']:
        if STATUS_PAGE_SERVICE in cmp['name']:
            return {'created_at': format_iso8601(cmp.get('created_at')),
                    'updated_at': format_iso8601(cmp.get('updated_at')),
                    'name': cmp.get('name'),
                    'description': cmp.get('description'),
                    'status': cmp.get('status')}
    return None


def get_upcoming_maintenance_by_service():
    r = requests.get(upcoming_maints_url)
    maints = r.json()
    maintenances = list()
    for maint in maints['scheduled_maintenances']:
        for cmp in maint['components']:
            if STATUS_PAGE_SERVICE in cmp['name']:
                updates = maint.get('incident_updates')
                created_at = format_iso8601(maint.get('created_at'))
                scheduled_for = format_iso8601(maint.get('scheduled_for'))
                scheduled_until = format_iso8601(maint.get('scheduled_until'))
                maint_dict = {'name': maint.get('name'),
                              'impact': maint.get('impact'),
                              'link': maint.get('shortlink'),
                              'status': maint.get('status'),
                              'created_at': created_at,
                              'scheduled_for': scheduled_for,
                              'scheduled_until': scheduled_until,
                              'description': updates[0].get('body')
                              if updates else None}
                maintenances.append(maint_dict)
    return maintenances


def check_status():
    # Component status
    component = get_component()
    # Component upcoming maintenance
    upcoming_maints = get_upcoming_maintenance_by_service()
    return {'component': component,
            'upcoming_maintenances': upcoming_maints}
