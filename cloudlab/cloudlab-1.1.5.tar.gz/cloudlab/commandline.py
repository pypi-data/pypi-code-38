import collections
import json
import logging
import os
import os.path
import pkg_resources
import shutil
import stat
import subprocess
import sys
import time
import yaml

COMMANDS = ['mkenv', 'rmenv', 'update', 'help']
config = None  # config is global


def print_help():
    print('Make a new environment:               cloudlab mkenv path/envname')
    print('Update an existing environment:       cloudlab update path/envname')
    print('Destroy an existing environment:      cloudlab rmenv path/envname ')
    print()
    print('A file named "cloudlab_config.yaml" must be present in the current directory.')
    print('See the sample below.')
    print()

    sample = pkg_resources.resource_string('cloudlab', 'cloudlab_config.yaml')
    print(sample.decode('unicode_escape'))


def run():
    global config

    if len(sys.argv) < 3:
        print_help()
        sys.exit(1)

    command = sys.argv[1]
    if command not in COMMANDS:
        sys.exit('Unrecognized command: {0}'.format(command))

    if not os.path.isfile('cloudlab_config.yaml'):
        sys.exit('Exiting because the configuration file is not present. Run "cloudlab help" for details.')

    with open('cloudlab_config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)

    envdir = sys.argv[2]

    logging.basicConfig(format='%(asctime)s:%(message)s', level=logging.DEBUG)

    if command == COMMANDS[0]:
        mkenv(envdir, False)
    elif command == COMMANDS[1]:
        rmenv(envdir)
    elif command == COMMANDS[2]:
        mkenv(envdir, True)
    else:
        print_help()
        sys.exit(0)


def rmenv(envdir):
    if envdir.endswith('/'):
        envdir = envdir[0:-1]

    envname = os.path.basename(envdir)

    runaws('aws cloudformation delete-stack --stack-name={}'.format(envname))
    logging.info("Deleted cloud formation stack: %s", envname)

    runaws('aws ec2 delete-key-pair --key-name={}'.format(envname))
    logging.info('Deleted the AWS key pair named %s.', envname + '.pem')

    shutil.rmtree(envdir, ignore_errors=True)
    logging.info('Removed cloudlab environment: %s.', envdir)


def mkenv(envdir, update):
    global config

    # create the directory
    if envdir.endswith('/'):
        envdir = envdir[0:-1]

    envname = os.path.basename(envdir)

    if update:
        if not os.path.exists(envdir):
            sys.exit('Environment directory does not exist. Exiting.')
        else:
            shutil.rmtree(envdir, ignore_errors=True)
            logging.info('Removed cloudlab environment directory: %s.', envdir)

    else:
        if os.path.exists(envdir):
            sys.exit('Environment directory already exists. Exiting.')

    os.makedirs(envdir)
    logging.info('Created directory %s', envdir)

    # generate the yaml file and save it to the target environment
    config['key_pair_name'] = envname
    with open(os.path.join(envdir, 'tplate.yaml'), 'w') as tplate_config_file:
        yaml.dump(config, tplate_config_file)

    logging.info('Wrote "tplate.yaml" file to %s.', envdir)

    sourcedir = pkg_resources.resource_filename('cloudlab', 'plans/aws_basic')

    tplate_cmd = ['tplate', sourcedir, envdir]
    if update:
        tplate_cmd += ['--update']

    result = subprocess.run(tplate_cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    if result.returncode != 0:
        sys.exit('Template generation failed with the following output: {}'.format(result.stdout))

    logging.info('Generated aws cloud formation template to %s.', envdir)

    # create the key pair
    if not update:
        result = runaws('aws ec2 create-key-pair --key-name={}'.format(envname))

        keyfile_name = os.path.join(envdir, envname + '.pem')
        with open(keyfile_name, 'w') as f:
            f.write(result['KeyMaterial'])

        os.chmod(keyfile_name, stat.S_IRUSR | stat.S_IWUSR)

        logging.info('Created a new key pair and saved the private key to {}.'.format(keyfile_name))

    # deploy to AWS using Cloud Formation
    nowait = False
    if update:
        # first we need to figure out the latest event related to this stack so we can start watching events after that
        result = runaws('aws cloudformation describe-stack-events --stack-name={}'.format(envname))
        last_event_timestamp = result['StackEvents'][0]['Timestamp']


        result = runaws_result('aws cloudformation update-stack --stack-name={} --template-body=file://{}'
               .format(envname, os.path.join(envdir, 'aws-cloud-template.yaml')))

        if result.returncode != 0:
            if 'No updates are to be performed'  in str(result.stdout):
                nowait = True
                logging.info("The Cloudformation stack is already up to date")
            else:
                sys.exit('An error occurred while updating the Cloudformation stack: {}'.format(result.stdout))

        else:
            logging.info('Waiting for stack update to complete.')
    else:
        runaws('aws cloudformation create-stack --stack-name={} --template-body=file://{}'
               .format(envname, os.path.join(envdir, 'aws-cloud-template.yaml')))

        logging.info('Cloud Formation stack created.  Waiting for provisioning to complete.')

    # use aws cloudformation describe-stack-events to follow the progress
    done = nowait
    previously_seen = dict()
    while not done:
        time.sleep(5.0)
        result = runaws('aws cloudformation describe-stack-events --stack-name={}'.format(envname))
        for event in reversed(result['StackEvents']):
            if update and event['Timestamp'] <= last_event_timestamp:
                continue

            if event['EventId'] in previously_seen:
                continue
            else:
                if not event['ResourceStatus'].endswith('IN_PROGRESS'):
                    logging.info('Provisioning event: %s %s',
                                 event['LogicalResourceId'] if event['ResourceType'] != 'AWS::CloudFormation::Stack' else 'CloudLab {}'.format(envname),
                                 event['ResourceStatus'])

                previously_seen[event['EventId']] = event
                if event['ResourceType'] == 'AWS::CloudFormation::Stack' and event['ResourceStatus'].find('COMPLETE') >= 0:
                    done = True

    result = runaws('aws cloudformation describe-stacks --stack-name={}'.format(envname))
    status = result['Stacks'][0]['StackStatus']

    if update:
        if not status.startswith('UPDATE_COMPLETE'):
            sys.exit('There was a failure while updating the CloudFormation stack.')
        else:
            logging.info('Cloud formation stack updated.')

    else:
        if status != 'CREATE_COMPLETE':
            sys.exit('There was a failure while creating the CloudFormation stack.')
        else:
            logging.info('Cloud formation stack created.')

    # we need a map of role to list of public ip addresses but we don't have it yet
    # make role_to_server_num:  a map of role to list of server_num
    # make server_num_to_public_ip: a map of server number to public ip address
    # then use the combination of the two to make the desired map
    role_to_server_num = collections.defaultdict(list)
    server_num_to_public_ip = dict()
    role_to_public_ip = collections.defaultdict(list)

    # build role_to_server_num
    for server_type in config['servers']:
        for server_num in server_type['private_ip_addresses']:
            for role in server_type['roles']:
                role_to_server_num[role].append(server_num)

    # use the outputs section of the describe-stacks result to write an Ansible inventory file.
    invfile = os.path.join(envdir, 'inventory.ini'.format(envname))
    with open(invfile, 'w') as f:
        for server_type in config['servers']:
            for server_num in server_type['private_ip_addresses']:
                public_ip = ''
                private_ip = ''
                dns_name = ''
                for output in result['Stacks'][0]['Outputs']:
                    if output['OutputKey'] == 'Instance{}PublicIpAddress'.format(server_num):
                        public_ip = output['OutputValue']
                    elif output['OutputKey'] == 'Instance{}PrivateIpAddress'.format(server_num):
                        private_ip = output['OutputValue']
                    elif output['OutputKey'] == 'Instance{}PublicDnsName'.format(server_num):
                        dns_name = output['OutputValue']

                    if len(public_ip) > 0 and len(private_ip) > 0 and len(dns_name) > 0:
                        break

                server_num_to_public_ip[server_num] = public_ip
                f.write('{}  private_ip={} dns_name={}\n'.format(public_ip, private_ip, dns_name))

        # now, before closing the file, create the role_to_public_ip map and write out a section for each role
        for role, server_nums in role_to_server_num.items():
            for server_num in server_nums:
                role_to_public_ip[role].append(server_num_to_public_ip[server_num])

        for role in role_to_public_ip:
            f.write('\n')
            f.write('[{}]\n'.format(role))
            for public_ip in role_to_public_ip[role]:
                f.write('{}\n'.format(public_ip))

    logging.info('Wrote inventory to {}'.format(invfile))


# automatically appends --region= --output=json
def runaws(commands):
    cmdarray = commands.split()
    cmdarray += ['--region={}'.format(config['region']), '--output=json']

    result = subprocess.run(cmdarray, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    if result.returncode != 0:
        sys.exit(
            'Exiting because an error occurred while running: {}.  The output was: {}'.format(' '.join(cmdarray),
                                                                                              result.stdout))
    if len(result.stdout) > 0:
        return json.loads(result.stdout)
    else:
        return None

# automatically appends --region= --output=json
def runaws_result(commands):
    cmdarray = commands.split()
    cmdarray += ['--region={}'.format(config['region']), '--output=json']

    return subprocess.run(cmdarray, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

