import os
from codecs import open

import setuptools


path = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(path, 'README.md')) as fd:
    long_desc = fd.read()

setuptools.setup(
    name='probator',
    use_scm_version=True,
    python_requires='~=3.7',

    entry_points={
        'console_scripts': [
            'probator = probator.cli:cli'
        ],

        'probator.plugins.auth': [
            'auth_local = probator.plugins.auth.local:LocalAuth'
        ],

        'probator.plugins.collectors': [
            'collector_aws_amis = probator.plugins.collectors.aws.region:AWSAMICollector',
            'collector_aws_beanstalks = probator.plugins.collectors.aws.region:AWSBeanStalkCollector',
            'collector_aws_classic_lb = probator.plugins.collectors.aws.region:AWSClassicLoadBalancerCollector',
            'collector_aws_cloudfront = probator.plugins.collectors.aws.account:AWSCloudFrontCollector',
            'collector_aws_ebs_snapshots = probator.plugins.collectors.aws.region:AWSEBSSnapshotCollector',
            'collector_aws_ebs_volumes = probator.plugins.collectors.aws.region:AWSEBSVolumeCollector',
            'collector_aws_eks_clusters = probator.plugins.collectors.aws.region:AWSEKSCollector',
            'collector_aws_eni = probator.plugins.collectors.aws.region:AWSENICollector',
            'collector_aws_instances = probator.plugins.collectors.aws.region:AWSEC2InstanceCollector',
            'collector_aws_lb = probator.plugins.collectors.aws.region:AWSLoadBalancerCollector',
            'collector_aws_rds = probator.plugins.collectors.aws.region:AWSRDSCollector',
            'collector_aws_route53 = probator.plugins.collectors.aws.account:AWSRoute53Collector',
            'collector_aws_s3 = probator.plugins.collectors.aws.account:AWSS3Collector',
            'collector_aws_vpc = probator.plugins.collectors.aws.region:AWSVPCCollector',
        ],

        'probator.plugins.commands': [
            'auth = probator.plugins.commands.auth:Auth',
            'list_plugins = probator.plugins.commands.plugins:ListPlugins',
            'scheduler = probator.plugins.commands.scheduler:Scheduler',
            'setup = probator.plugins.commands.setup:Setup',
            'userdata = probator.plugins.commands.userdata:UserData',
            'worker = probator.plugins.commands.scheduler:Worker',
        ],

        'probator.plugins.notifiers': [
            'email_notify = probator.plugins.notifiers.email:EmailNotifier',
            'slack_notify = probator.plugins.notifiers.slack:SlackNotifier',
        ],

        'probator.plugins.types': [
            'aws_access_key = probator.plugins.types.resources:AccessKey',
            'aws_ami = probator.plugins.types.resources:AMI',
            'aws_beanstalk = probator.plugins.types.resources:BeanStalk',
            'aws_cloudfront_dist = probator.plugins.types.resources:CloudFrontDist',
            'aws_ebs_snapshot = probator.plugins.types.resources:EBSSnapshot',
            'aws_ebs_volume = probator.plugins.types.resources:EBSVolume',
            'aws_ec2_instance = probator.plugins.types.resources:EC2Instance',
            'aws_eni = probator.plugins.types.resources:ENI',
            'aws_eks_cluster = probator.plugins.types.resources:EKSCluster',
            'aws_elb = probator.plugins.types.resources:ELB',
            'aws_iam_user = probator.plugins.types.resources:IAMUser',
            'aws_lb = probator.plugins.types.resources:LoadBalancer',
            'aws_rds_instance = probator.plugins.types.resources:RDSInstance',
            'aws_s3_bucket = probator.plugins.types.resources:S3Bucket',
            'aws_vpc = probator.plugins.types.resources:VPC',
            'dns_record = probator.plugins.types.resources:DNSRecord',
            'dns_zone = probator.plugins.types.resources:DNSZone',
        ],

        'probator.plugins.types.issues': [
            'domain_hijacking = probator.plugins.types.issues:DomainHijackIssue',
        ],

        'probator.plugins.types.accounts': [
            'AWS = probator.plugins.types.accounts:AWSAccount',
            'DNS: AXFR = probator.plugins.types.accounts:AXFRAccount',
            'DNS: CloudFlare = probator.plugins.types.accounts:CloudFlareAccount',
        ],

        'probator.plugins.schedulers': [
            'scheduler_standalone = probator.plugins.schedulers.standalone:StandaloneScheduler'
        ],

        'probator.plugins.views': [
            'account_details = probator.plugins.views.accounts:AccountDetail',
            'account_imex = probator.plugins.views.accounts:AccountImportExport',
            'account_list = probator.plugins.views.accounts:AccountList',
            'auditlog_get = probator.plugins.views.auditlog:AuditLogGet',
            'auditlog_list = probator.plugins.views.auditlog:AuditLogList',
            'config = probator.plugins.views.config:ConfigGet',
            'config_import_export = probator.plugins.views.config:ConfigImportExport',
            'config_list = probator.plugins.views.config:ConfigList',
            'config_namespace_get = probator.plugins.views.config:NamespaceGet',
            'config_namespace_list = probator.plugins.views.config:Namespaces',
            'dashboard = probator.plugins.views.dashboard:Dashboard',
            'email = probator.plugins.views.emails:EmailGet',
            'email_list = probator.plugins.views.emails:EmailList',
            'health = probator.plugins.views.health:Health',
            'issues_list = probator.plugins.views.issues:IssueList',
            'issue_get = probator.plugins.views.issues:IssueGet',
            'log = probator.plugins.views.logs:Logs',
            'log_details = probator.plugins.views.logs:LogDetails',
            'metadata = probator.plugins.views.metadata:MetaData',
            'password_reset = probator.plugins.views.users:PasswordReset',
            'resource_children = probator.plugins.views.resources:ResourceGetChildren',
            'resource_get = probator.plugins.views.resources:ResourceGet',
            'resource_list = probator.plugins.views.resources:ResourceList',
            'role_get = probator.plugins.views.roles:RoleGet',
            'role_list = probator.plugins.views.roles:RoleList',
            'template_get = probator.plugins.views.templates:TemplateGet',
            'template_list = probator.plugins.views.templates:TemplateList',
            'user_details = probator.plugins.views.users:UserDetails',
            'user_list = probator.plugins.views.users:UserList',
            'version = probator.plugins.views.health:Version',
        ]
    },

    packages=setuptools.find_packages(
        exclude=[
            '*.tests',
            '*.tests.*',
            'tests.*',
            'tests'
        ]
    ),
    include_package_data=True,
    zip_safe=False,

    # Requirements for setup and installation
    setup_requires=['setuptools_scm'],
    install_requires=[
        'APScheduler~=3.3',
        'Flask-Compress~=1.4',
        'Flask-Migrate~=2.1',
        'Flask-RESTful~=0.3',
        'Flask-Script~=2.0',
        'Flask~=1.0.2',
        'Jinja2~=2.9',
        'MarkupSafe~=1.0',
        'PyJWT~=1.5',
        'SQLAlchemy~=1.1',
        'argon2-cffi~=19.1',
        'boto3~=1.9',
        'click~=7.0',
        'flake8-comprehensions~=2.0',
        'flake8-deprecated~=1.2',
        'flake8-pep3101~=1.1',
        'flake8-quotes~=1.0',
        'flake8~=3.3',
        'gunicorn~=19.7',
        'hvac~=0.7',
        'ipython~=7.2',
        'more-itertools~=6.0',
        'munch~=2.1',
        'mysqlclient~=1.3',
        'pyexcel-io~=0.5.11',
        'pyexcel-xlsx~=0.5.6',
        'pyexcel~=0.5.10',
        'rainbow-logging-handler~=2.2',
        'requests~=2.19',
        'slackclient~=1.0',
        'sqlservice~=1.1.3',
    ],

    extras_require={
        'test': [
            'pytest-cov~=2.5',
            'pytest~=4.1.0',
        ]
    },

    # Metadata
    description='Tool to enforce ownership and data security within cloud environments',
    long_description=long_desc,
    long_description_content_type='text/markdown',
    author='Asbjorn Kjaer',
    author_email='bunjiboys+probator@gmail.com',
    url='https://github.com/bunjiboys/probator',
    license='Apache 2.0',
    classifiers=[
        # Current project status
        'Development Status :: 4 - Beta',

        # Audience
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',

        # License information
        'License :: OSI Approved :: Apache Software License',

        # Supported python versions
        'Programming Language :: Python :: 3.7',

        # Frameworks used
        'Framework :: Flask',

        # Supported OS's
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',

        # Extra metadata
        'Environment :: Console',
        'Natural Language :: English',
        'Topic :: Security',
        'Topic :: Utilities',
    ],
    keywords='cloud security',
)
