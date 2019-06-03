def create_master(args):
    print('Enter repo ssh key, end with EOF (Ctrl-D):')
    repo_ssh_key = sys.stdin.read()
    repo_secret = getpass.getpass('Enter repo secret token: ')

    ssh_canary = base64.b64encode(os.urandom(30)).decode('utf-8')
    cloud_init_template = get_cloud_init_template('cloud-init-master.sh')
    cloud_init = cloud_init_template.render(**{
        'minion_id': args.minion_id,
        'roles': args.roles,
        'ssh_canary': ssh_canary,
        'debian_version': DEBIAN_VERSIONS[args.debian_codename],
        'debian_codename': args.debian_codename,
        'environment': args.environment,
    })
    key_name = build_ssh_key_name(args.minion_id)
    with create_temp_ssh_key(args.provider, key_name) as ssh_key:
        key_fingerprint = binary_to_fingerprint(ssh_key.get_fingerprint())
        droplet = None
        try:
            droplet = create_droplet(cloud_init,
                args.minion_id,
                key_fingerprint,
                args.tags,
                args.debian_codename,
                args.region,
                args.size,
                args.private_networking,
            )
            print('Droplet running at %s' % droplet.ip_address)
            master_secret_setup(args.minion_id, droplet.ip_address, ssh_key, ssh_canary, repo_ssh_key, repo_secret)
            print('Salt master completely configured at %s' % droplet.ip_address)
        except:
            traceback.print_exc()
            if droplet:
                sys.stderr.write('Destroying droplet since it failed initialization\n')
                droplet.destroy()


def master_secret_setup(minion_id, ip, ssh_key, canary, repo_ssh_key, repo_secret):
    '''
    Do setup that requires secrets that shouldn't be managed by cloud-init.

    Requires at least the following to be done by cloud-init:
        - Install git and salt-master/salt-minion
        - Create a user named 'saltmaster'
    '''
    with get_verified_ssh_client(ip, ssh_key, canary) as client:
        wait_for_cloud_init(client)

        # Remove our temp ssh key
        ssh_run_command(client, 'rm /root/.ssh/authorized_keys', timeout=2)

        configure_ssh(client, repo_ssh_key)

        # The server might not have sudo installed yet, thus fixing the
        # permissions in retrospect instead of running with the correct user in
        # the first place
        ssh_run_command(client, '''
            GIT_SSH_COMMAND='ssh -i /etc/salt/.ssh/id_rsa -o UserKnownHostsFile=/etc/salt/.ssh/known_hosts' git clone ssh://git@github.com/megacool/onboard /opt/onboard --depth 1
            chown saltmaster:saltmaster -R /opt/onboard
            ln -s /opt/onboard/salt /srv/salt
            ln -s /opt/onboard/pillar /srv/pillar
        ''', timeout=120)

        ssh_run_command(client, '''
            # -md md5 needed since openssl changed the default in 1.1.0
            # ref https://github.com/fastlane/fastlane/issues/9542
            openssl aes-256-cbc -md md5 -d -in /opt/onboard/salt/salt/gpgkeys.tar.gz.enc -k %s \
                | tar xzC /etc/salt/
        ''' % repo_secret, sensitive=True)

        ssh_run_command(client, '''
            set -e

            # Fix permissions to gpg keys
            # Newer versions of gpg needs write access since the db formats
            # needs to be upgraded from what is stored in the repo (1.4 does not need it)
            chown -R root:saltmaster /etc/salt/gpgkeys
            chmod 770 /etc/salt/gpgkeys
            chmod -R 660 /etc/salt/gpgkeys/*

            # Now the salt-master setup should be valid, connect the minion to the master
            service salt-master restart

            salt-call test.ping || echo 'test.ping completed.'

            salt-key -a %s -y
        ''' % minion_id, timeout=120)

        ssh_run_command(client, 'salt-call state.highstate -l info --force-color', timeout=600)


def configure_ssh(client, ssh_key):
    saltmaster_gid = int(ssh_run_command(client, 'id -g saltmaster'))
    saltmaster_uid = int(ssh_run_command(client, 'id -u saltmaster'))
    sftp_client = client.open_sftp()
    sftp_client.mkdir('/etc/salt/.ssh', mode=0o700)
    sftp_client.chown('/etc/salt/.ssh', saltmaster_uid, saltmaster_gid)
    with sftp_client.open('/etc/salt/.ssh/id_rsa', 'wb') as sftp_file:
        # Set mode after open since I couldn't figure out how to set the
        # umask before creation with paramiko. Since the dir is 700 there
        # shouldn't be any race conditions.
        sftp_file.chmod(0o400)
        sftp_file.chown(saltmaster_uid, saltmaster_gid)
        sftp_file.write(ssh_key.encode('utf-8'))

    with sftp_client.open('/etc/salt/.ssh/known_hosts', 'wb') as sftp_file:
        sftp_file.write('github.com ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ==\n')
        sftp_file.chown(saltmaster_uid, saltmaster_gid)

    sftp_client.close()

    # Ensure there is a pubkey available too, otherwise the saltmaster fails to start
    ssh_run_command(client, 'ssh-keygen -y -f /etc/salt/.ssh/id_rsa > /etc/salt/.ssh/id_rsa.pub')
