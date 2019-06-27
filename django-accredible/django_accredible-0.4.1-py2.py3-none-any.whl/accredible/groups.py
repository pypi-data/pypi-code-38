import requests
import logging

from django.conf import settings

from pyaccredible.client import AccredibleWrapper

logger = logging.getLogger('accredible')


def create_group(group, issued_on=None, course_name=None, design_id=None):
    client = AccredibleWrapper(
        key=settings.ACCREDIBLE_API_KEY,
        server=settings.ACCREDIBLE_SERVER_URL)
    design_id = settings.ACCREDIBLE_DESIGN.get(group._type) if not design_id else design_id

    if design_id:
        group_name = group.name
        if issued_on:
            group_name = '{} - {}'.format(group_name, issued_on.strftime('%d %B, %Y'))

        logger.info('GROUP: {} - {}'.format(group_name, design_id))

        response = client.group_create(
            name=group_name,
            course_name=course_name,
            course_description=group.description,
            design_id=design_id,
            attach_pdf=True,
        )

        if response.status_code == requests.codes.ok:
            group.design_id = design_id
            group.accredible_id = response.json()['group']['id']
            group.save(update_fields=['design_id', 'accredible_id', 'modified'])
        else:
            logger.error('Accredible.create_group: {}'.format(response))
            response.raise_for_status()

    else:
        logger.error('Accredible.create_group Not design: {} - {}'.format(group.name, design_id))

    return group


def delete_group(group):
    client = AccredibleWrapper(
        key=settings.ACCREDIBLE_API_KEY,
        server=settings.ACCREDIBLE_SERVER_URL)
    client.group_credentials_delete(group_id=group.accredible_id)


def update_group(group, issued_on=None, course_name=None):
    client = AccredibleWrapper(
        key=settings.ACCREDIBLE_API_KEY,
        server=settings.ACCREDIBLE_SERVER_URL)
    group_name = group.name
    if issued_on:
        group_name = '{} - {}'.format(group_name, issued_on.strftime('%d %B, %Y'))

    logger.info('GROUP: {} - {}'.format(group_name, group.accredible_id))

    response = client.group_update(
        group.accredible_id,
        name=group_name,
        course_name=course_name,
        course_description=group.description,
    )

    if response.status_code != requests.codes.ok:
        logger.error('Accredible.update_group: {}'.format(response))
        response.raise_for_status()
