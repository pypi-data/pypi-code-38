# aws.py - Automation code for Amazon Web Services
#
# Copyright 2019 Gregory Szorc <gregory.szorc@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

# no-check-code because Python 3 native.

import contextlib
import copy
import hashlib
import json
import os
import pathlib
import subprocess
import time

import boto3
import botocore.exceptions

from .winrm import (
    run_powershell,
    wait_for_winrm,
)


SOURCE_ROOT = pathlib.Path(os.path.abspath(__file__)).parent.parent.parent.parent

INSTALL_WINDOWS_DEPENDENCIES = (SOURCE_ROOT / 'contrib' /
                                'install-windows-dependencies.ps1')


KEY_PAIRS = {
    'automation',
}


SECURITY_GROUPS = {
    'windows-dev-1': {
        'description': 'Mercurial Windows instances that perform build automation',
        'ingress': [
            {
                'FromPort': 22,
                'ToPort': 22,
                'IpProtocol': 'tcp',
                'IpRanges': [
                    {
                        'CidrIp': '0.0.0.0/0',
                        'Description': 'SSH from entire Internet',
                    },
                ],
            },
            {
                'FromPort': 3389,
                'ToPort': 3389,
                'IpProtocol': 'tcp',
                'IpRanges': [
                    {
                        'CidrIp': '0.0.0.0/0',
                        'Description': 'RDP from entire Internet',
                    },
                ],

            },
            {
                'FromPort': 5985,
                'ToPort': 5986,
                'IpProtocol': 'tcp',
                'IpRanges': [
                    {
                        'CidrIp': '0.0.0.0/0',
                        'Description': 'PowerShell Remoting (Windows Remote Management)',
                    },
                ],
            }
        ],
    },
}


IAM_ROLES = {
    'ephemeral-ec2-role-1': {
        'description': 'Mercurial temporary EC2 instances',
        'policy_arns': [
            'arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM',
        ],
    },
}


ASSUME_ROLE_POLICY_DOCUMENT = '''
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
'''.strip()


IAM_INSTANCE_PROFILES = {
    'ephemeral-ec2-1': {
        'roles': [
            'ephemeral-ec2-role-1',
        ],
    }
}


# User Data for Windows EC2 instance. Mainly used to set the password
# and configure WinRM.
# Inspired by the User Data script used by Packer
# (from https://www.packer.io/intro/getting-started/build-image.html).
WINDOWS_USER_DATA = r'''
<powershell>

# TODO enable this once we figure out what is failing.
#$ErrorActionPreference = "stop"

# Set administrator password
net user Administrator "%s"
wmic useraccount where "name='Administrator'" set PasswordExpires=FALSE

# First, make sure WinRM can't be connected to
netsh advfirewall firewall set rule name="Windows Remote Management (HTTP-In)" new enable=yes action=block

# Delete any existing WinRM listeners
winrm delete winrm/config/listener?Address=*+Transport=HTTP  2>$Null
winrm delete winrm/config/listener?Address=*+Transport=HTTPS 2>$Null

# Create a new WinRM listener and configure
winrm create winrm/config/listener?Address=*+Transport=HTTP
winrm set winrm/config/winrs '@{MaxMemoryPerShellMB="0"}'
winrm set winrm/config '@{MaxTimeoutms="7200000"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
winrm set winrm/config/service '@{MaxConcurrentOperationsPerUser="12000"}'
winrm set winrm/config/service/auth '@{Basic="true"}'
winrm set winrm/config/client/auth '@{Basic="true"}'

# Configure UAC to allow privilege elevation in remote shells
$Key = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System'
$Setting = 'LocalAccountTokenFilterPolicy'
Set-ItemProperty -Path $Key -Name $Setting -Value 1 -Force

# Configure and restart the WinRM Service; Enable the required firewall exception
Stop-Service -Name WinRM
Set-Service -Name WinRM -StartupType Automatic
netsh advfirewall firewall set rule name="Windows Remote Management (HTTP-In)" new action=allow localip=any remoteip=any
Start-Service -Name WinRM

# Disable firewall on private network interfaces so prompts don't appear.
Set-NetFirewallProfile -Name private -Enabled false
</powershell>
'''.lstrip()


WINDOWS_BOOTSTRAP_POWERSHELL = '''
Write-Output "installing PowerShell dependencies"
Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force
Set-PSRepository -Name PSGallery -InstallationPolicy Trusted
Install-Module -Name OpenSSHUtils -RequiredVersion 0.0.2.0

Write-Output "installing OpenSSL server"
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
# Various tools will attempt to use older versions of .NET. So we enable
# the feature that provides them so it doesn't have to be auto-enabled
# later.
Write-Output "enabling .NET Framework feature"
Install-WindowsFeature -Name Net-Framework-Core
'''


class AWSConnection:
    """Manages the state of a connection with AWS."""

    def __init__(self, automation, region: str):
        self.automation = automation
        self.local_state_path = automation.state_path

        self.prefix = 'hg-'

        self.session = boto3.session.Session(region_name=region)
        self.ec2client = self.session.client('ec2')
        self.ec2resource = self.session.resource('ec2')
        self.iamclient = self.session.client('iam')
        self.iamresource = self.session.resource('iam')

        ensure_key_pairs(automation.state_path, self.ec2resource)

        self.security_groups = ensure_security_groups(self.ec2resource)
        ensure_iam_state(self.iamresource)

    def key_pair_path_private(self, name):
        """Path to a key pair private key file."""
        return self.local_state_path / 'keys' / ('keypair-%s' % name)

    def key_pair_path_public(self, name):
        return self.local_state_path / 'keys' / ('keypair-%s.pub' % name)


def rsa_key_fingerprint(p: pathlib.Path):
    """Compute the fingerprint of an RSA private key."""

    # TODO use rsa package.
    res = subprocess.run(
        ['openssl', 'pkcs8', '-in', str(p), '-nocrypt', '-topk8',
         '-outform', 'DER'],
        capture_output=True,
        check=True)

    sha1 = hashlib.sha1(res.stdout).hexdigest()
    return ':'.join(a + b for a, b in zip(sha1[::2], sha1[1::2]))


def ensure_key_pairs(state_path: pathlib.Path, ec2resource, prefix='hg-'):
    remote_existing = {}

    for kpi in ec2resource.key_pairs.all():
        if kpi.name.startswith(prefix):
            remote_existing[kpi.name[len(prefix):]] = kpi.key_fingerprint

    # Validate that we have these keys locally.
    key_path = state_path / 'keys'
    key_path.mkdir(exist_ok=True, mode=0o700)

    def remove_remote(name):
        print('deleting key pair %s' % name)
        key = ec2resource.KeyPair(name)
        key.delete()

    def remove_local(name):
        pub_full = key_path / ('keypair-%s.pub' % name)
        priv_full = key_path / ('keypair-%s' % name)

        print('removing %s' % pub_full)
        pub_full.unlink()
        print('removing %s' % priv_full)
        priv_full.unlink()

    local_existing = {}

    for f in sorted(os.listdir(key_path)):
        if not f.startswith('keypair-') or not f.endswith('.pub'):
            continue

        name = f[len('keypair-'):-len('.pub')]

        pub_full = key_path / f
        priv_full = key_path / ('keypair-%s' % name)

        with open(pub_full, 'r', encoding='ascii') as fh:
            data = fh.read()

        if not data.startswith('ssh-rsa '):
            print('unexpected format for key pair file: %s; removing' %
                  pub_full)
            pub_full.unlink()
            priv_full.unlink()
            continue

        local_existing[name] = rsa_key_fingerprint(priv_full)

    for name in sorted(set(remote_existing) | set(local_existing)):
        if name not in local_existing:
            actual = '%s%s' % (prefix, name)
            print('remote key %s does not exist locally' % name)
            remove_remote(actual)
            del remote_existing[name]

        elif name not in remote_existing:
            print('local key %s does not exist remotely' % name)
            remove_local(name)
            del local_existing[name]

        elif remote_existing[name] != local_existing[name]:
            print('key fingerprint mismatch for %s; '
                  'removing from local and remote' % name)
            remove_local(name)
            remove_remote('%s%s' % (prefix, name))
            del local_existing[name]
            del remote_existing[name]

    missing = KEY_PAIRS - set(remote_existing)

    for name in sorted(missing):
        actual = '%s%s' % (prefix, name)
        print('creating key pair %s' % actual)

        priv_full = key_path / ('keypair-%s' % name)
        pub_full = key_path / ('keypair-%s.pub' % name)

        kp = ec2resource.create_key_pair(KeyName=actual)

        with priv_full.open('w', encoding='ascii') as fh:
            fh.write(kp.key_material)
            fh.write('\n')

        priv_full.chmod(0o0600)

        # SSH public key can be extracted via `ssh-keygen`.
        with pub_full.open('w', encoding='ascii') as fh:
            subprocess.run(
                ['ssh-keygen', '-y', '-f', str(priv_full)],
                stdout=fh,
                check=True)

        pub_full.chmod(0o0600)


def delete_instance_profile(profile):
    for role in profile.roles:
        print('removing role %s from instance profile %s' % (role.name,
                                                             profile.name))
        profile.remove_role(RoleName=role.name)

    print('deleting instance profile %s' % profile.name)
    profile.delete()


def ensure_iam_state(iamresource, prefix='hg-'):
    """Ensure IAM state is in sync with our canonical definition."""

    remote_profiles = {}

    for profile in iamresource.instance_profiles.all():
        if profile.name.startswith(prefix):
            remote_profiles[profile.name[len(prefix):]] = profile

    for name in sorted(set(remote_profiles) - set(IAM_INSTANCE_PROFILES)):
        delete_instance_profile(remote_profiles[name])
        del remote_profiles[name]

    remote_roles = {}

    for role in iamresource.roles.all():
        if role.name.startswith(prefix):
            remote_roles[role.name[len(prefix):]] = role

    for name in sorted(set(remote_roles) - set(IAM_ROLES)):
        role = remote_roles[name]

        print('removing role %s' % role.name)
        role.delete()
        del remote_roles[name]

    # We've purged remote state that doesn't belong. Create missing
    # instance profiles and roles.
    for name in sorted(set(IAM_INSTANCE_PROFILES) - set(remote_profiles)):
        actual = '%s%s' % (prefix, name)
        print('creating IAM instance profile %s' % actual)

        profile = iamresource.create_instance_profile(
            InstanceProfileName=actual)
        remote_profiles[name] = profile

    for name in sorted(set(IAM_ROLES) - set(remote_roles)):
        entry = IAM_ROLES[name]

        actual = '%s%s' % (prefix, name)
        print('creating IAM role %s' % actual)

        role = iamresource.create_role(
            RoleName=actual,
            Description=entry['description'],
            AssumeRolePolicyDocument=ASSUME_ROLE_POLICY_DOCUMENT,
        )

        remote_roles[name] = role

        for arn in entry['policy_arns']:
            print('attaching policy %s to %s' % (arn, role.name))
            role.attach_policy(PolicyArn=arn)

    # Now reconcile state of profiles.
    for name, meta in sorted(IAM_INSTANCE_PROFILES.items()):
        profile = remote_profiles[name]
        wanted = {'%s%s' % (prefix, role) for role in meta['roles']}
        have = {role.name for role in profile.roles}

        for role in sorted(have - wanted):
            print('removing role %s from %s' % (role, profile.name))
            profile.remove_role(RoleName=role)

        for role in sorted(wanted - have):
            print('adding role %s to %s' % (role, profile.name))
            profile.add_role(RoleName=role)


def find_windows_server_2019_image(ec2resource):
    """Find the Amazon published Windows Server 2019 base image."""

    images = ec2resource.images.filter(
        Filters=[
            {
                'Name': 'owner-alias',
                'Values': ['amazon'],
            },
            {
                'Name': 'state',
                'Values': ['available'],
            },
            {
                'Name': 'image-type',
                'Values': ['machine'],
            },
            {
                'Name': 'name',
                'Values': ['Windows_Server-2019-English-Full-Base-2019.02.13'],
            },
        ])

    for image in images:
        return image

    raise Exception('unable to find Windows Server 2019 image')


def ensure_security_groups(ec2resource, prefix='hg-'):
    """Ensure all necessary Mercurial security groups are present.

    All security groups are prefixed with ``hg-`` by default. Any security
    groups having this prefix but aren't in our list are deleted.
    """
    existing = {}

    for group in ec2resource.security_groups.all():
        if group.group_name.startswith(prefix):
            existing[group.group_name[len(prefix):]] = group

    purge = set(existing) - set(SECURITY_GROUPS)

    for name in sorted(purge):
        group = existing[name]
        print('removing legacy security group: %s' % group.group_name)
        group.delete()

    security_groups = {}

    for name, group in sorted(SECURITY_GROUPS.items()):
        if name in existing:
            security_groups[name] = existing[name]
            continue

        actual = '%s%s' % (prefix, name)
        print('adding security group %s' % actual)

        group_res = ec2resource.create_security_group(
            Description=group['description'],
            GroupName=actual,
        )

        group_res.authorize_ingress(
            IpPermissions=group['ingress'],
        )

        security_groups[name] = group_res

    return security_groups


def terminate_ec2_instances(ec2resource, prefix='hg-'):
    """Terminate all EC2 instances managed by us."""
    waiting = []

    for instance in ec2resource.instances.all():
        if instance.state['Name'] == 'terminated':
            continue

        for tag in instance.tags or []:
            if tag['Key'] == 'Name' and tag['Value'].startswith(prefix):
                print('terminating %s' % instance.id)
                instance.terminate()
                waiting.append(instance)

    for instance in waiting:
        instance.wait_until_terminated()


def remove_resources(c, prefix='hg-'):
    """Purge all of our resources in this EC2 region."""
    ec2resource = c.ec2resource
    iamresource = c.iamresource

    terminate_ec2_instances(ec2resource, prefix=prefix)

    for image in ec2resource.images.all():
        if image.name.startswith(prefix):
            remove_ami(ec2resource, image)

    for group in ec2resource.security_groups.all():
        if group.group_name.startswith(prefix):
            print('removing security group %s' % group.group_name)
            group.delete()

    for profile in iamresource.instance_profiles.all():
        if profile.name.startswith(prefix):
            delete_instance_profile(profile)

    for role in iamresource.roles.all():
        if role.name.startswith(prefix):
            print('removing role %s' % role.name)
            role.delete()


def wait_for_ip_addresses(instances):
    """Wait for the public IP addresses of an iterable of instances."""
    for instance in instances:
        while True:
            if not instance.public_ip_address:
                time.sleep(2)
                instance.reload()
                continue

            print('public IP address for %s: %s' % (
                instance.id, instance.public_ip_address))
            break


def remove_ami(ec2resource, image):
    """Remove an AMI and its underlying snapshots."""
    snapshots = []

    for device in image.block_device_mappings:
        if 'Ebs' in device:
            snapshots.append(ec2resource.Snapshot(device['Ebs']['SnapshotId']))

    print('deregistering %s' % image.id)
    image.deregister()

    for snapshot in snapshots:
        print('deleting snapshot %s' % snapshot.id)
        snapshot.delete()


def wait_for_ssm(ssmclient, instances):
    """Wait for SSM to come online for an iterable of instance IDs."""
    while True:
        res = ssmclient.describe_instance_information(
            Filters=[
                {
                    'Key': 'InstanceIds',
                    'Values': [i.id for i in instances],
                },
            ],
        )

        available = len(res['InstanceInformationList'])
        wanted = len(instances)

        print('%d/%d instances available in SSM' % (available, wanted))

        if available == wanted:
            return

        time.sleep(2)


def run_ssm_command(ssmclient, instances, document_name, parameters):
    """Run a PowerShell script on an EC2 instance."""

    res = ssmclient.send_command(
        InstanceIds=[i.id for i in instances],
        DocumentName=document_name,
        Parameters=parameters,
        CloudWatchOutputConfig={
            'CloudWatchOutputEnabled': True,
        },
    )

    command_id = res['Command']['CommandId']

    for instance in instances:
        while True:
            try:
                res = ssmclient.get_command_invocation(
                    CommandId=command_id,
                    InstanceId=instance.id,
                )
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'InvocationDoesNotExist':
                    print('could not find SSM command invocation; waiting')
                    time.sleep(1)
                    continue
                else:
                    raise

            if res['Status'] == 'Success':
                break
            elif res['Status'] in ('Pending', 'InProgress', 'Delayed'):
                time.sleep(2)
            else:
                raise Exception('command failed on %s: %s' % (
                    instance.id, res['Status']))


@contextlib.contextmanager
def temporary_ec2_instances(ec2resource, config):
    """Create temporary EC2 instances.

    This is a proxy to ``ec2client.run_instances(**config)`` that takes care of
    managing the lifecycle of the instances.

    When the context manager exits, the instances are terminated.

    The context manager evaluates to the list of data structures
    describing each created instance. The instances may not be available
    for work immediately: it is up to the caller to wait for the instance
    to start responding.
    """

    ids = None

    try:
        res = ec2resource.create_instances(**config)

        ids = [i.id for i in res]
        print('started instances: %s' % ' '.join(ids))

        yield res
    finally:
        if ids:
            print('terminating instances: %s' % ' '.join(ids))
            for instance in res:
                instance.terminate()
            print('terminated %d instances' % len(ids))


@contextlib.contextmanager
def create_temp_windows_ec2_instances(c: AWSConnection, config):
    """Create temporary Windows EC2 instances.

    This is a higher-level wrapper around ``create_temp_ec2_instances()`` that
    configures the Windows instance for Windows Remote Management. The emitted
    instances will have a ``winrm_client`` attribute containing a
    ``pypsrp.client.Client`` instance bound to the instance.
    """
    if 'IamInstanceProfile' in config:
        raise ValueError('IamInstanceProfile cannot be provided in config')
    if 'UserData' in config:
        raise ValueError('UserData cannot be provided in config')

    password = c.automation.default_password()

    config = copy.deepcopy(config)
    config['IamInstanceProfile'] = {
        'Name': 'hg-ephemeral-ec2-1',
    }
    config.setdefault('TagSpecifications', []).append({
        'ResourceType': 'instance',
        'Tags': [{'Key': 'Name', 'Value': 'hg-temp-windows'}],
    })
    config['UserData'] = WINDOWS_USER_DATA % password

    with temporary_ec2_instances(c.ec2resource, config) as instances:
        wait_for_ip_addresses(instances)

        print('waiting for Windows Remote Management service...')

        for instance in instances:
            client = wait_for_winrm(instance.public_ip_address, 'Administrator', password)
            print('established WinRM connection to %s' % instance.id)
            instance.winrm_client = client

        yield instances


def ensure_windows_dev_ami(c: AWSConnection, prefix='hg-'):
    """Ensure Windows Development AMI is available and up-to-date.

    If necessary, a modern AMI will be built by starting a temporary EC2
    instance and bootstrapping it.

    Obsolete AMIs will be deleted so there is only a single AMI having the
    desired name.

    Returns an ``ec2.Image`` of either an existing AMI or a newly-built
    one.
    """
    ec2client = c.ec2client
    ec2resource = c.ec2resource
    ssmclient = c.session.client('ssm')

    name = '%s%s' % (prefix, 'windows-dev')

    config = {
        'BlockDeviceMappings': [
            {
                'DeviceName': '/dev/sda1',
                'Ebs': {
                    'DeleteOnTermination': True,
                    'VolumeSize': 32,
                    'VolumeType': 'gp2',
                },
            }
        ],
        'ImageId': find_windows_server_2019_image(ec2resource).id,
        'InstanceInitiatedShutdownBehavior': 'stop',
        'InstanceType': 't3.medium',
        'KeyName': '%sautomation' % prefix,
        'MaxCount': 1,
        'MinCount': 1,
        'SecurityGroupIds': [c.security_groups['windows-dev-1'].id],
    }

    commands = [
        # Need to start the service so sshd_config is generated.
        'Start-Service sshd',
        'Write-Output "modifying sshd_config"',
        r'$content = Get-Content C:\ProgramData\ssh\sshd_config',
        '$content = $content -replace "Match Group administrators","" -replace "AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys",""',
        r'$content | Set-Content C:\ProgramData\ssh\sshd_config',
        'Import-Module OpenSSHUtils',
        r'Repair-SshdConfigPermission C:\ProgramData\ssh\sshd_config -Confirm:$false',
        'Restart-Service sshd',
        'Write-Output "installing OpenSSL client"',
        'Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0',
        'Set-Service -Name sshd -StartupType "Automatic"',
        'Write-Output "OpenSSH server running"',
    ]

    with INSTALL_WINDOWS_DEPENDENCIES.open('r', encoding='utf-8') as fh:
        commands.extend(l.rstrip() for l in fh)

    # Disable Windows Defender when bootstrapping because it just slows
    # things down.
    commands.insert(0, 'Set-MpPreference -DisableRealtimeMonitoring $true')
    commands.append('Set-MpPreference -DisableRealtimeMonitoring $false')

    # Compute a deterministic fingerprint to determine whether image needs
    # to be regenerated.
    fingerprint = {
        'instance_config': config,
        'user_data': WINDOWS_USER_DATA,
        'initial_bootstrap': WINDOWS_BOOTSTRAP_POWERSHELL,
        'bootstrap_commands': commands,
    }

    fingerprint = json.dumps(fingerprint, sort_keys=True)
    fingerprint = hashlib.sha256(fingerprint.encode('utf-8')).hexdigest()

    # Find existing AMIs with this name and delete the ones that are invalid.
    # Store a reference to a good image so it can be returned one the
    # image state is reconciled.
    images = ec2resource.images.filter(
        Filters=[{'Name': 'name', 'Values': [name]}])

    existing_image = None

    for image in images:
        if image.tags is None:
            print('image %s for %s lacks required tags; removing' % (
                image.id, image.name))
            remove_ami(ec2resource, image)
        else:
            tags = {t['Key']: t['Value'] for t in image.tags}

            if tags.get('HGIMAGEFINGERPRINT') == fingerprint:
                existing_image = image
            else:
                print('image %s for %s has wrong fingerprint; removing' % (
                      image.id, image.name))
                remove_ami(ec2resource, image)

    if existing_image:
        return existing_image

    print('no suitable Windows development image found; creating one...')

    with create_temp_windows_ec2_instances(c, config) as instances:
        assert len(instances) == 1
        instance = instances[0]

        wait_for_ssm(ssmclient, [instance])

        # On first boot, install various Windows updates.
        # We would ideally use PowerShell Remoting for this. However, there are
        # trust issues that make it difficult to invoke Windows Update
        # remotely. So we use SSM, which has a mechanism for running Windows
        # Update.
        print('installing Windows features...')
        run_ssm_command(
            ssmclient,
            [instance],
            'AWS-RunPowerShellScript',
            {
                'commands': WINDOWS_BOOTSTRAP_POWERSHELL.split('\n'),
            },
        )

        # Reboot so all updates are fully applied.
        print('rebooting instance %s' % instance.id)
        ec2client.reboot_instances(InstanceIds=[instance.id])

        time.sleep(15)

        print('waiting for Windows Remote Management to come back...')
        client = wait_for_winrm(instance.public_ip_address, 'Administrator',
                                c.automation.default_password())
        print('established WinRM connection to %s' % instance.id)
        instance.winrm_client = client

        print('bootstrapping instance...')
        run_powershell(instance.winrm_client, '\n'.join(commands))

        print('bootstrap completed; stopping %s to create image' % instance.id)
        instance.stop()

        ec2client.get_waiter('instance_stopped').wait(
            InstanceIds=[instance.id],
            WaiterConfig={
                'Delay': 5,
            })
        print('%s is stopped' % instance.id)

        image = instance.create_image(
            Name=name,
            Description='Mercurial Windows development environment',
        )

        image.create_tags(Tags=[
            {
                'Key': 'HGIMAGEFINGERPRINT',
                'Value': fingerprint,
            },
        ])

        print('waiting for image %s' % image.id)

        ec2client.get_waiter('image_available').wait(
            ImageIds=[image.id],
        )

        print('image %s available as %s' % (image.id, image.name))

        return image


@contextlib.contextmanager
def temporary_windows_dev_instances(c: AWSConnection, image, instance_type,
                                    prefix='hg-', disable_antivirus=False):
    """Create a temporary Windows development EC2 instance.

    Context manager resolves to the list of ``EC2.Instance`` that were created.
    """
    config = {
        'BlockDeviceMappings': [
            {
                'DeviceName': '/dev/sda1',
                'Ebs': {
                    'DeleteOnTermination': True,
                    'VolumeSize': 32,
                    'VolumeType': 'gp2',
                },
            }
        ],
        'ImageId': image.id,
        'InstanceInitiatedShutdownBehavior': 'stop',
        'InstanceType': instance_type,
        'KeyName': '%sautomation' % prefix,
        'MaxCount': 1,
        'MinCount': 1,
        'SecurityGroupIds': [c.security_groups['windows-dev-1'].id],
    }

    with create_temp_windows_ec2_instances(c, config) as instances:
        if disable_antivirus:
            for instance in instances:
                run_powershell(
                    instance.winrm_client,
                    'Set-MpPreference -DisableRealtimeMonitoring $true')

        yield instances
