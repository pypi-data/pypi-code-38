import logging

logger = logging.getLogger('main')


def search_automata(session, instance, client, category, name):
    params = {'page': 0, 'size': 50, 'sortField': 'name', 'sortDirection': 'ASC', 'clientId': client['id'],
              'taskId': None, 'categoryId': None, 'name': name, 'deleted': False}
    search_result = session.get('{}/api/automata/search'.format(instance), params=params)
    logger.debug(search_result.text)
    return search_result.json()


def automaton_exists(session, instance, client, name):
    search_response = search_automata(session, instance, client, None, name)
    if search_response['total'] == 0:
        return None

    automata_list = search_response['content']
    for automaton in automata_list:
        if name == automaton['name']:
            return automaton

    return None


def get_automaton_list_for_client(session, instance, client):
    logger.info('>>Getting automata for client: {}'.format(client['name']))
    automata_list = session.get('{}/api/automata/client/{}'.format(instance, client['id']))
    logger.debug('Get automata list for client %s Response: %s', client['name'], automata_list.status_code)
    return automata_list.json()


# expects category as a Category object
def get_automaton_list_for_category(session, instance, category):
    """

    :param session: session object
    :param instance: instance URL
    :param category: category is a Node here because it is used in preorder_traversal_cat
    :return: list of automata for a category
    """
    logger.debug('Getting automata for category: {}'.format(category.name))
    response = session.get('{}/api/automata/category/{}'.format(instance, category.id))
    logger.debug('Response: %s', response.status_code)
    if response.ok:
        return response.json()
    else:
        logger.error('Failed to get automata list: %s', response.reason)
        return []


def get_automaton(session, instance, automaton_id):
    automaton_response = session.get('{}/api/automata/{}'.format(instance, automaton_id))
    logger.debug('Get automaton %s Response: %s', automaton_id, automaton_response.status_code)
    return automaton_response.json()


def get_automaton_version_latest(session, instance, automaton):
    version_response = session.get('{}/api/automata/{}/versions/latest'.format(instance, automaton['id']))
    logger.debug('get_automaton_version_latest response: %s', version_response.status_code)
    logger.debug(version_response.json())
    return version_response.json()


def get_automaton_version(session, instance, version_id):
    pass


def get_automaton_versions(session, instance, automaton):
    pass


def get_automaton_approved_versions(session, instance, automaton):
    pass


def update_automaton(session, instance, automaton):
    headers = {'Content-Type': 'application/json;charset=UTF-8',
               'Accept': 'application/json, text/plain, */*', 'Accept-Encoding': 'gzip, deflate, br'}
    params = {'newVersion': True}
    update_response = session.put('{}/api/automata/'.format(instance), data=automaton, headers=headers)
    logger.debug('Update automaton response: %s', update_response.status_code)
    logger.debug(update_response.text)
    return update_response.json()


def save_automaton(session, instance, automation):
    headers = {'Content-Type': 'application/json;charset=UTF-8',
               'Accept': 'application/json, text/plain, */*', 'Accept-Encoding': 'gzip, deflate, br'}
    rpc_action = {'action': 'automataController', 'method': 'saveAutomaton', 'type': 'rpc', 'tid': 0,
                  'data': automation.json()}
    save_response = session.post('{}/IPautomata/router'.format(instance), headers=headers, json=rpc_action)
    logger.debug('Save automaton response: %s', save_response.status_code)
    return save_response.json()


def delete_automata(session, instance, automata):
    logger.debug("!!Deleting automata {}".format(automata['name']))
    delete_response = session.delete('{}/api/automata/{}'.format(instance, automata['id']))
    logger.debug('Delete automata %s Response: %s', automata['name'], delete_response.status_code)


def export_automata(session, instance, automaton):
    logger.debug('>Exporting automata {} | {}'.format(automaton['id'], automaton['name']))
    automaton_response = session.get('{}/api/automaton-import-export/export/{}'.format(instance, automaton['id']))
    logger.debug('Response: {}'.format(automaton_response.status_code))

    if automaton_response.ok:
        return automaton_response.json()
    else:
        logger.error('Failed to export automaton: {}'.format(automaton['name']))
        return None


def import_automaton(session, instance, category, automaton_name, automata_dto):
    headers = {'Content-Type': 'application/json;charset=UTF-8',
               'Accept': 'application/json, text/plain, */*', 'Accept-Encoding': 'gzip, deflate, br'}
    import_command = dict(clientId=category['clientId'], categoryId=category['id'],
                          exportedAutomatonDto=automata_dto, automatonName=automaton_name,
                          relinkExisting=True, importCategoryStructure=False,
                          tags=[], linkedImportCommands=[], automatonConnectionGroups=[])
    response = session.post('{}/api/automaton-import-export/import'.format(instance), headers=headers,
                            json=import_command)
    logger.debug('Response: {}'.format(response.status_code))

    if response.ok:
        return response.json()
    else:
        logger.error('Failed to import automaton: {}'.format(automaton_name))
        logger.error(response.text)
        return None


def submit_automaton_for_approval(session, instance, version):
    version['live'] = True
    headers = {'Content-Type': 'application/json;charset=UTF-8',
               'Accept': 'application/json, text/plain, */*', 'Accept-Encoding': 'gzip, deflate, br'}
    params = {'note': 'Submitted on import with clicmod', 'submitterId': version['creatorId']}
    response = session.put(
        '{}/api/automaton-approval/versions/{}/actions/submit'.format(instance, version['versionId']),
        headers=headers, params=params)
    logger.debug('Response: %s', response.status_code)
    if response.ok:
        return response.json()
    else:
        return None


def approve_automaton(session, instance, version):
    headers = {'Content-Type': 'application/json;charset=UTF-8',
               'Accept': 'application/json, text/plain, */*', 'Accept-Encoding': 'gzip, deflate, br'}
    params = {'note': 'Approved on import with clicmod', 'reviewerId': version['submitterId']}
    response = session.put(
        '{}/api/automaton-approval/versions/{}/actions/approve'.format(instance, version['versionId']),
        headers=headers, params=params)
    logger.debug('Response: %s', response.status_code)
    return response.ok
