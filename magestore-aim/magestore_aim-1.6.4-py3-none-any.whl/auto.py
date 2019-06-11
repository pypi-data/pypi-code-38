# -*- coding: utf-8 -*-

import calendar
import os
import time
from fabric import Connection, Config
import json
from packaging import version
from invoke import UnexpectedExit

MAGENTO_VERSION = ''
MAGENTO_TYPE = ''
PHP_VERSION = ''
SAMPLE_DATA = False
PERFORMANCE_TEST = False
PERFORMANCE_TEST_PROFILE = ''
VALID_PERFORMANCE_TEST_PROFILES = ['small', 'medium', 'medium_msite', 'large', 'extra_large']

IP_ADDRESS = ''
USER = ''
PASSWORD = ''
KEY_PATH = ''
SOURCE_PATH = ''
ENV_PATH = ''
CONNECTION = ''

ENV_FOLDER_PATH = ''
ENV_FOLDER_NAME_WITH_TIMESTAMP = ''
DEFAULT_PORT_RANGE = ''
WEB_PORT = ''
DB_PORT = ''
PHPMYADMIN_PORT = ''


def get_connection(ip, user, su_pass='', key_path=''):
    try:
        if key_path:
            c = Connection(ip, user, connect_kwargs={'key_filename': key_path})
        else:
            config = Config(overrides={'sudo': {'password': su_pass, "prompt": "[sudo] password: \n"}})
            c = Connection(ip, user, connect_kwargs={"password": su_pass}, config=config)
        return c
    except Exception as e:
        print("Can't create connection for %s@%s" % (user, ip))
        print(e)
        return False


def get_absolute_path(relative_path):
    """
    :param relative_path: relative path of the file to the current directory of auto.py file
    :return:
    """
    # current directory path that contain this file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return "{0}/{1}".format(dir_path, relative_path)


def check_valid_magento_php_version(m_version, p_version, m_type='ce'):
    with open(get_absolute_path('data/magento_versions.json')) as mf:
        magento_versions_info = json.load(mf)
    with open(get_absolute_path('data/php_versions.json')) as pf:
        php_versions = json.load(pf)

    magento_versions = [(m.get('magento_version'), m.get('magento_type')) for m in magento_versions_info]
    if (m_version, m_type) not in magento_versions:
        raise ValueError('Invalid magento version %s-%s' % (m_version, m_type))
    if p_version not in php_versions:
        raise ValueError('Invalid php version')

    magento_versions_info = [m for m in magento_versions_info if m.get('magento_version') == m_version][0]
    php_version_condition = magento_versions_info.get('php_version_condition')
    if eval(php_version_condition.format(php_version=p_version)):
        return True
    raise ValueError('Magento %s-%s is not compatible with PHP %s' % (m_version, m_type, p_version))


def prepare_environment_variables(env_params, server_params, gitlab_access_token):
    global MAGENTO_VERSION, PHP_VERSION, SAMPLE_DATA, PERFORMANCE_TEST, PERFORMANCE_TEST_PROFILE, MAGENTO_TYPE
    global IP_ADDRESS, USER, PASSWORD, KEY_PATH, SOURCE_PATH, ENV_PATH, CONNECTION
    global ENV_FOLDER_PATH, ENV_FOLDER_NAME_WITH_TIMESTAMP, DEFAULT_PORT_RANGE

    MAGENTO_VERSION = env_params.get('magento_version') or ''
    PHP_VERSION = env_params.get('php_version') or '7.1.25'
    MAGENTO_TYPE = env_params.get('magento_type') or 'ce'
    check_valid_magento_php_version(MAGENTO_VERSION, PHP_VERSION, MAGENTO_TYPE)

    SAMPLE_DATA = env_params.get('sample_data', False)
    if type(SAMPLE_DATA) is not bool:
        raise TypeError('sample_data key must be the boolean type')
    elif not SAMPLE_DATA:
        PERFORMANCE_TEST = env_params.get('performance_test', False)
        if type(PERFORMANCE_TEST) is not bool:
            raise TypeError('performance_test key must be the boolean type')
        elif PERFORMANCE_TEST:
            PERFORMANCE_TEST_PROFILE = env_params.get('performance_test_profile', VALID_PERFORMANCE_TEST_PROFILES[0])
            if PERFORMANCE_TEST_PROFILE not in VALID_PERFORMANCE_TEST_PROFILES:
                raise ValueError('performance_test_profile has invalid value. It\'s value can be %s' % (
                    ', '.join(VALID_PERFORMANCE_TEST_PROFILES)))

    IP_ADDRESS = server_params.get('ip')
    USER = server_params.get('user')
    PASSWORD = server_params.get('password')
    KEY_PATH = server_params.get('key_path')
    SOURCE_PATH = '/home/%s/magento/sources' % USER
    ENV_PATH = '/home/%s/magento/docker' % USER
    CONNECTION = get_connection(IP_ADDRESS, USER, PASSWORD, KEY_PATH)
    if not CONNECTION:
        raise Exception('Invalid server information, please check it again!')

    ENV_FOLDER_PATH, ENV_FOLDER_NAME_WITH_TIMESTAMP = create_docker_compose_folder(gitlab_access_token)
    DEFAULT_PORT_RANGE = [80, 9101, 9102]


def current_timestamp():
    return calendar.timegm(time.gmtime())


def docker_components_installed():
    try:
        CONNECTION.sudo('docker --version', hide='both')
        CONNECTION.sudo('docker-compose --version', hide='both')
        return True
    except Exception:
        return False


def install_docker_components():
    global CONNECTION
    if not docker_components_installed():
        CONNECTION.sudo('apt-get update', hide='both')
        try:
            CONNECTION.sudo('apt-get remove --purge -y docker docker-engine docker.io containerd runc', hide='both')
        except Exception:
            pass

        CONNECTION.sudo('apt-get install -y apt-transport-https ca-certificates curl gnupg2 software-properties-common',
                        hide='both')
        CONNECTION.sudo('touch $HOME/add-docker-repo.sh', hide='both')
        CONNECTION.sudo('chmod 777 $HOME/add-docker-repo.sh', hide='both')
        CONNECTION.sudo(
            'echo "curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -" > $HOME/add-docker-repo.sh',
            hide='both')
        CONNECTION.sudo('$HOME/add-docker-repo.sh', hide='both')
        CONNECTION.sudo('rm -rf $HOME/add-docker-repo.sh', hide='both')
        CONNECTION.sudo('apt-key fingerprint 0EBFCD88', hide='both')
        CONNECTION.sudo(
            'add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"',
            hide='both')
        CONNECTION.sudo('apt-get update', hide='both')
        CONNECTION.sudo('apt-get install docker-ce -y', hide='both')
        CONNECTION.sudo(
            'curl -L "https://github.com/docker/compose/releases/download/1.23.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose',
            hide='both')
        CONNECTION.sudo('chmod +x /usr/local/bin/docker-compose', hide='both')
        CONNECTION.sudo('usermod -aG docker %s' % USER, hide='both')

        # reset connection to get new $USER permission (docker)
        CONNECTION = get_connection(IP_ADDRESS, USER, PASSWORD, KEY_PATH)


def check_file_exist(file_path):
    try:
        CONNECTION.run('[ -f %s ]' % file_path, hide='both')
        return True
    except UnexpectedExit:
        return False


def get_source_url():
    if SAMPLE_DATA:
        source_name = '{magento_version}_sample_data.tar.gz'.format(magento_version=MAGENTO_VERSION)
    else:
        source_name = '{magento_version}.tar.gz'.format(magento_version=MAGENTO_VERSION)

    if MAGENTO_TYPE == 'ee':
        source_name = '{magento_version}_sample_data_ee.tar.gz'.format(magento_version=MAGENTO_VERSION)
    source_url = "https://github.com/mars-trueplus/public-resource/releases/download/magento_sources/{source_name}".format(
        source_name=source_name
    )
    return source_url


def get_source_file():
    source_url = get_source_url()

    if SAMPLE_DATA:
        source_file_name = '{magento_version}_sample_data.tar.gz'.format(magento_version=MAGENTO_VERSION)
    else:
        source_file_name = '{magento_version}.tar.gz'.format(magento_version=MAGENTO_VERSION)
    # We don't have Magento EE - no sample data source
    if MAGENTO_TYPE == 'ee':
        source_file_name = '{magento_version}_sample_data_ee.tar.gz'.format(magento_version=MAGENTO_VERSION)
    source_file_path = SOURCE_PATH + '/' + source_file_name

    if not check_file_exist(source_file_path):
        CONNECTION.run('mkdir -p %s' % SOURCE_PATH, hide='both')
        CONNECTION.run('wget -O {source_file_path} {source_url}'.format(
            source_file_path=source_file_path,
            source_url=source_url
        ), hide='both')

    return source_file_path


def create_docker_compose_folder(gitlab_access_token):
    """
    Clone env folder
    :return: local env folder path
    """
    if not os.path.isdir(ENV_PATH):
        CONNECTION.run('mkdir -p %s' % ENV_PATH, hide='both')
    env_folder_name = 'Apache2-Mysql5.7-PHP%s' % PHP_VERSION
    env_folder_name_with_timestamp = '%s-%s' % (env_folder_name, current_timestamp())
    env_folder_path = ('%s/%s' % (ENV_PATH, env_folder_name_with_timestamp))
    clone_command = 'git clone https://gitlab-ci-token:{gitlab_access_token}@gitlab.com/general-oil/infrastructure.git --depth 1 -b master {env_folder_path}'.format(
        gitlab_access_token=gitlab_access_token,
        env_folder_path=env_folder_path)

    CONNECTION.run(clone_command, hide='both')
    CONNECTION.run(
        'cd %s && git filter-branch --prune-empty --subdirectory-filter Environment/Magento/DemoPortalApache/%s HEAD' % (
            env_folder_path, env_folder_name), hide='both')

    return env_folder_path, env_folder_name_with_timestamp


def prepare_source_folder():
    source_file_path = get_source_file()
    src_folder_path = '%s/%s' % (ENV_FOLDER_PATH, 'src')

    CONNECTION.run('mkdir -p {src_folder_path}'.format(src_folder_path=src_folder_path), hide='both')
    CONNECTION.run('tar -xf %s -C %s ' % (source_file_path, src_folder_path), hide='both')
    CONNECTION.sudo('chown -R 1000:1000 %s' % src_folder_path, hide='both')
    CONNECTION.sudo('chmod +x %s/bin/magento' % src_folder_path, hide='both')

    return src_folder_path


def check_available_port_range(list_ports):
    try:
        command = 'netstat -tupln| grep LISTEN | grep -c ' + ' '.join(['-e :' + str(x) for x in list_ports])
        CONNECTION.sudo(command, hide='both')
        return False
    except (UnexpectedExit, Exception):
        return True


def get_port_range():
    ports = [DEFAULT_PORT_RANGE[0], DEFAULT_PORT_RANGE[1], DEFAULT_PORT_RANGE[2]]
    for x in range(DEFAULT_PORT_RANGE[1], 65535, 3):
        if check_available_port_range(ports):
            return ports
        else:
            ports = [x, x + 1, x + 2]
    return []


def update_docker_compose_ports():
    """
    Update available ports in docker-compose file
    :return: web port - magento access port
    """
    global WEB_PORT, DB_PORT, PHPMYADMIN_PORT
    ports = get_port_range()
    WEB_PORT = ports[0]
    DB_PORT = ports[1]
    PHPMYADMIN_PORT = ports[2]
    docker_compose_path = (ENV_FOLDER_PATH + '/' + 'docker-compose.yml')
    docker_compose_content = CONNECTION.run(
        'cat {docker_compose_path}'.format(docker_compose_path=docker_compose_path), hide='both').stdout
    # replace correct ports
    correct_ports = {'"9102:80"': '"{}:80"'.format(PHPMYADMIN_PORT),
                     '"9101:3306"': '"{}:3306"'.format(DB_PORT),
                     '"80:80"': '"{}:80"'.format(WEB_PORT)}
    for key in correct_ports:
        docker_compose_content = docker_compose_content.replace(key, str(correct_ports[key]))
    CONNECTION.run("echo '{docker_compose_content}' > {docker_compose_path}".format(
        docker_compose_content=docker_compose_content,
        docker_compose_path=docker_compose_path
    ), hide='both')


def update_env_docker_compose_params():
    update_docker_compose_ports()
    res = []
    env_file_path = (ENV_FOLDER_PATH + '/' + 'env')
    env_content = CONNECTION.run('cat {env_file_path}'.format(env_file_path=env_file_path), hide='both').stdout
    env_content_lines = env_content.split('\n')
    for line in env_content_lines:
        if 'MAGENTO_URL' in line:
            if WEB_PORT == 80 or WEB_PORT == '80':
                line = 'MAGENTO_URL=http://%s\n' % (IP_ADDRESS)
            else:
                line = 'MAGENTO_URL=http://%s:%s\n' % (IP_ADDRESS, WEB_PORT)
        res.append(line)
    env_content = '\n'.join(res)
    CONNECTION.run("echo '{env_content}' > {env_file_path}".format(
        env_content=env_content,
        env_file_path=env_file_path
    ), hide='both')


def docker_compose_up():
    update_env_docker_compose_params()
    compose_file = '%s/docker-compose.yml' % ENV_FOLDER_PATH
    CONNECTION.sudo('docker-compose -f %s up -d' % compose_file, hide='both')


def get_container_id(container_pattern):
    prefix_container_name = ENV_FOLDER_NAME_WITH_TIMESTAMP.lower().replace('.', '')
    command = """docker ps --format "table {{.ID}} {{.Names}}" | awk  '{if ($2 ~ "%s%s") {print $1}}'""" % (
        prefix_container_name, container_pattern)
    out = CONNECTION.run(command, hide='both').stdout
    container_id = out.replace('\n', '')
    return container_id


def check_docker_compose_services_status():
    """
    Check status of all services in docker-compose file.
    Only run install-mangento when all services are healthy
    :return: True if all services are healthy, otherwise False
    """
    try:
        web_container_id = get_container_id('_web_')
        db_container_id = get_container_id('_db_')
        command = 'docker ps --filter "health=healthy"|egrep -c "%s|%s"' % (web_container_id, db_container_id)
        result = CONNECTION.sudo(command, hide='both')
        return True if result.stdout.replace('\n', '') == '2' else False
    except (UnexpectedExit, Exception):
        return False


def get_instance_url():
    if WEB_PORT == 80 or WEB_PORT == '80':
        url = 'http://{ip}'.format(ip=IP_ADDRESS)
    else:
        url = 'http://{ip}:{web_port}'.format(ip=IP_ADDRESS, web_port=WEB_PORT)
    return url


def get_phpmyadmin_url():
    url = 'http://{ip}:{phpmyadmin_port}'.format(ip=IP_ADDRESS, phpmyadmin_port=PHPMYADMIN_PORT)
    return url


def magento_instance_info():
    url = get_instance_url()
    phpmyadmin_url = get_phpmyadmin_url()
    src_folder_path = '%s/%s' % (ENV_FOLDER_PATH, 'src')
    db_container_id = get_container_id('_db_')
    web_container_id = get_container_id('_web_')
    phpmyadmin_container_id = get_container_id('_phpmyadmin_')
    res = {
        'magento_version': MAGENTO_VERSION,
        'php_version': PHP_VERSION,
        'ip': IP_ADDRESS,
        'user': USER,
        'password': PASSWORD,
        'key_path': KEY_PATH,
        'compose_folder': ENV_FOLDER_PATH,
        'src_folder': src_folder_path,
        'db_container_id': db_container_id,
        'web_container_id': web_container_id,
        'phpmyadmin_container_id': phpmyadmin_container_id,
        'front_end': url,
        'back_end': url + '/admin',
        'phpmyadmin': phpmyadmin_url,
        'site_user': 'admin',
        'site_password': 'admin123@',
        'db': 'magento',
        'db_user': 'magento',
        'db_password': 'magento'
    }

    return res


def execute_install_command():
    retries = 10
    timeout = 20
    while retries != 0:
        healthy = check_docker_compose_services_status()
        if healthy:
            break
        retries -= 1
        time.sleep(timeout)
    if retries == 0:
        return False
    try:
        web_container_id = get_container_id('_web_')
        CONNECTION.sudo('docker exec -i {web_container_id} install-magento'.format(web_container_id=web_container_id),
                        hide='both')
        if not SAMPLE_DATA and PERFORMANCE_TEST:
            # install magento performance toolkit
            performance_profile_name = '/var/www/html/setup/performance-toolkit/profiles/ce/%s.xml' % PERFORMANCE_TEST_PROFILE

            CONNECTION.sudo(
                'docker exec -u www-data -i {web_container_id} php bin/magento setup:perf:generate-fixtures {performance_profile_name}'.format(
                    web_container_id=web_container_id,
                    performance_profile_name=performance_profile_name
                ), hide='both')

            CONNECTION.sudo('docker exec -u www-data -i {web_container_id} php bin/magento indexer:reindex'.format(
                web_container_id=web_container_id
            ), hide='both')

            CONNECTION.sudo('docker exec -u www-data -i {web_container_id} composer require zendframework/zend-barcode'.format(
                web_container_id=web_container_id
            ), hide='both')

        return True
    except Exception as e:
        print("Can't execute install magento command.")
        print(e)
        return False


def install_magento(env_params, server_params, gitlab_access_token):
    """
    MAIN function.
    Install magento with defined params
    :param env_params: dict params for magento requirements
    :param server_params: dict params for local and backup server info
    :param gitlab_access_token: {str} access_token that have permission to read
     https://gitlab.com/general-oil/infrastructure repo
    """
    prepare_environment_variables(env_params, server_params, gitlab_access_token)
    print('Preparing environment for installation Magento-%s %s ...' % (MAGENTO_TYPE.upper(), MAGENTO_VERSION))
    install_docker_components()
    prepare_source_folder()
    docker_compose_up()
    print('Installing Magento-%s %s ...' % (MAGENTO_TYPE.upper(), MAGENTO_VERSION))
    done = execute_install_command()
    return magento_instance_info() if done else False
