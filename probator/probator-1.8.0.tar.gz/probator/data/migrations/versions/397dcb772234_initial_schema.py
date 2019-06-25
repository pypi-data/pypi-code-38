"""Initial schema

Revision ID: 397dcb772234
Revises: None
Create Date: 2019-01-11 11:01:47.764847

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '397dcb772234'
down_revision = None


def upgrade():
    # Account Types
    op.create_table(
        'account_types',
        sa.Column('account_type_id', mysql.INTEGER(unsigned=True), autoincrement=True, nullable=False),
        sa.Column('account_type', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('account_type_id')
    )
    op.create_index(op.f('ix_account_types_account_type'), 'account_types', ['account_type'], unique=True)

    # Audit Log
    op.create_table(
        'auditlog',
        sa.Column('audit_log_event_id', mysql.INTEGER(unsigned=True), autoincrement=True, nullable=False),
        sa.Column('timestamp', mysql.DATETIME(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('actor', sa.String(length=100), nullable=False),
        sa.Column('event', sa.String(length=50), nullable=False),
        sa.Column('data', mysql.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('audit_log_event_id')
    )
    op.create_index(op.f('ix_auditlog_actor'), 'auditlog', ['actor'], unique=False)
    op.create_index(op.f('ix_auditlog_event'), 'auditlog', ['event'], unique=False)

    # Config Namespaces
    op.create_table(
        'config_namespaces',
        sa.Column('namespace_prefix', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('sort_order', sa.SmallInteger(), server_default='2', nullable=False),
        sa.PrimaryKeyConstraint('namespace_prefix')
    )

    # Emails
    op.create_table(
        'emails',
        sa.Column('email_id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('timestamp', mysql.DATETIME(), nullable=False),
        sa.Column('subsystem', sa.String(length=64), nullable=False),
        sa.Column('subject', sa.String(length=256), nullable=False),
        sa.Column('sender', sa.String(length=256), nullable=False),
        sa.Column('recipients', mysql.JSON(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('message_html', mysql.TEXT(), nullable=True),
        sa.Column('message_text', mysql.TEXT(), nullable=True),
        sa.PrimaryKeyConstraint('email_id')
    )
    op.create_index(op.f('ix_emails_subsystem'), 'emails', ['subsystem'], unique=False)
    op.create_index(op.f('ix_emails_timestamp'), 'emails', ['timestamp'], unique=False)
    op.create_index(op.f('ix_emails_uuid'), 'emails', ['uuid'], unique=False)

    # Issue Types
    op.create_table(
        'issue_types',
        sa.Column('issue_type_id', mysql.INTEGER(unsigned=True), autoincrement=True, nullable=False),
        sa.Column('issue_type', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('issue_type_id')
    )
    op.create_index(op.f('ix_issue_types_issue_type'), 'issue_types', ['issue_type'], unique=False)

    # Issues
    op.create_table(
        'issues',
        sa.Column('issue_id', sa.String(length=256), nullable=False),
        sa.Column('issue_type_id', mysql.INTEGER(unsigned=True), nullable=True),
        sa.PrimaryKeyConstraint('issue_id')
    )
    op.create_index(op.f('ix_issues_issue_type_id'), 'issues', ['issue_type_id'], unique=False)

    # Logs
    op.create_table(
        'logs',
        sa.Column('log_event_id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('level', sa.String(length=10), nullable=False),
        sa.Column('levelno', sa.SmallInteger(), nullable=False),
        sa.Column('timestamp', mysql.DATETIME(), nullable=False),
        sa.Column('message', mysql.TEXT(), nullable=False),
        sa.Column('module', sa.String(length=255), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('lineno', mysql.INTEGER(), nullable=True),
        sa.Column('funcname', sa.String(length=255), nullable=False),
        sa.Column('pathname', mysql.TEXT(), nullable=True),
        sa.Column('process_id', mysql.INTEGER(), nullable=True),
        sa.Column('stacktrace', mysql.TEXT(), nullable=True),
        sa.PrimaryKeyConstraint('log_event_id')
    )
    op.create_index(op.f('ix_logs_level'), 'logs', ['level'], unique=False)
    op.create_index(op.f('ix_logs_levelno'), 'logs', ['levelno'], unique=False)
    op.create_index(op.f('ix_logs_timestamp'), 'logs', ['timestamp'], unique=False)

    # Resource Types
    op.create_table(
        'resource_types',
        sa.Column('resource_type_id', mysql.INTEGER(unsigned=True), autoincrement=True, nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('resource_type_id')
    )
    op.create_index(op.f('ix_resource_types_resource_type'), 'resource_types', ['resource_type'], unique=False)

    # Roles
    op.create_table(
        'roles',
        sa.Column('role_id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(length=7), server_default='#9E9E9E', nullable=False),
        sa.PrimaryKeyConstraint('role_id'),
        sa.UniqueConstraint('name')
    )

    # Scheduler Batches
    op.create_table(
        'scheduler_batches',
        sa.Column('batch_id', sa.String(length=36), nullable=False),
        sa.Column('status', mysql.TINYINT(), nullable=False),
        sa.Column('started', mysql.DATETIME(), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed', mysql.DATETIME(), nullable=True),
        sa.PrimaryKeyConstraint('batch_id')
    )
    op.create_index(op.f('ix_scheduler_batches_status'), 'scheduler_batches', ['status'], unique=False)

    # Templates
    op.create_table(
        'templates',
        sa.Column('template_name', sa.String(length=50), nullable=False),
        sa.Column('template', mysql.TEXT(), nullable=False),
        sa.Column('is_modified', mysql.TINYINT(), nullable=False),
        sa.PrimaryKeyConstraint('template_name')
    )

    # Users
    op.create_table(
        'users',
        sa.Column('user_id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password', sa.String(length=73), nullable=True),
        sa.Column('auth_system', sa.String(length=50), server_default='builtin', nullable=False),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('username', 'auth_system', name='uniq_username_authsys')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)

    # Accounts
    op.create_table(
        'accounts',
        sa.Column('account_id', mysql.INTEGER(unsigned=True), autoincrement=True, nullable=False),
        sa.Column('account_name', sa.String(length=256), nullable=False),
        sa.Column('account_type_id', mysql.INTEGER(unsigned=True), nullable=False),
        sa.Column('contacts', mysql.JSON(), nullable=False),
        sa.Column('enabled', mysql.SMALLINT(unsigned=True), nullable=False),
        sa.Column('required_roles', mysql.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ('account_type_id',),
            ['account_types.account_type_id'],
            name='fk_account_account_type_id',
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('account_id')
    )
    op.create_index(op.f('ix_accounts_account_name'), 'accounts', ['account_name'], unique=True)
    op.create_index(op.f('ix_accounts_account_type_id'), 'accounts', ['account_type_id'], unique=False)

    # Config Items
    op.create_table(
        'config_items',
        sa.Column('config_item_id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('key', sa.String(length=256), nullable=False),
        sa.Column('value', mysql.JSON(), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('namespace_prefix', sa.String(length=100), server_default='default', nullable=False),
        sa.Column('description', sa.String(length=256), nullable=True),
        sa.ForeignKeyConstraint(
            ('namespace_prefix',),
            ['config_namespaces.namespace_prefix'],
            name='fk_config_namespace_prefix',
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('config_item_id'),
        sa.UniqueConstraint('key', 'namespace_prefix', name='uniq_key_namespace')
    )
    op.create_index(op.f('ix_config_items_key'), 'config_items', ['key'], unique=False)

    # Issue Properties
    op.create_table(
        'issue_properties',
        sa.Column('property_id', mysql.INTEGER(unsigned=True), autoincrement=True, nullable=False),
        sa.Column('issue_id', sa.String(length=256), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('value', mysql.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ('issue_id',),
            ['issues.issue_id'],
            name='fk_issue_properties_issue_id',
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('property_id', 'issue_id')
    )
    op.create_index(op.f('ix_issue_properties_issue_id'), 'issue_properties', ['issue_id'], unique=False)
    op.create_index(op.f('ix_issue_properties_name'), 'issue_properties', ['name'], unique=False)

    # Scheduler Jobs
    op.create_table(
        'scheduler_jobs',
        sa.Column('job_id', sa.String(length=36), nullable=False),
        sa.Column('batch_id', sa.String(length=36), nullable=False),
        sa.Column('status', mysql.TINYINT(), nullable=False),
        sa.Column('data', mysql.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ('batch_id',),
            ['scheduler_batches.batch_id'],
            name='fk_scheduler_job_batch_id',
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('job_id')
    )
    op.create_index(op.f('ix_scheduler_jobs_status'), 'scheduler_jobs', ['status'], unique=False)

    # User Roles
    op.create_table(
        'user_roles',
        sa.Column('user_role_id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('user_id', mysql.INTEGER(), nullable=True),
        sa.Column('role_id', mysql.INTEGER(), nullable=True),
        sa.ForeignKeyConstraint(('role_id',), ['roles.role_id'], name='fk_user_role_role', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(('user_id',), ['users.user_id'], name='fk_user_role_user', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_role_id')
    )

    # Account Properties
    op.create_table(
        'account_properties',
        sa.Column('property_id', mysql.INTEGER(unsigned=True), autoincrement=True, nullable=False),
        sa.Column('account_id', mysql.INTEGER(unsigned=True), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('value', mysql.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ('account_id',),
            ['accounts.account_id'],
            name='fk_account_properties_account_id',
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('property_id', 'account_id')
    )
    op.create_index(op.f('ix_account_properties_account_id'), 'account_properties', ['account_id'], unique=False)
    op.create_index(op.f('ix_account_properties_name'), 'account_properties', ['name'], unique=False)

    # Resources
    op.create_table(
        'resources',
        sa.Column('resource_id', sa.String(length=256), nullable=False),
        sa.Column('account_id', mysql.INTEGER(unsigned=True), nullable=True),
        sa.Column('location', sa.String(length=50), nullable=True),
        sa.Column('resource_type_id', mysql.INTEGER(unsigned=True), nullable=True),
        sa.ForeignKeyConstraint(
            ('account_id',),
            ['accounts.account_id'],
            name='fk_resource_account_id',
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ('resource_type_id',),
            ['resource_types.resource_type_id'],
            name='fk_resource_types_resource_type_id',
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('resource_id')
    )
    op.create_index(op.f('ix_resources_account_id'), 'resources', ['account_id'], unique=False)
    op.create_index(op.f('ix_resources_location'), 'resources', ['location'], unique=False)
    op.create_index(op.f('ix_resources_resource_type_id'), 'resources', ['resource_type_id'], unique=False)

    # Resource Mappings
    op.create_table(
        'resource_mappings',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('parent', sa.String(length=256), nullable=False),
        sa.Column('child', sa.String(length=256), nullable=False),
        sa.ForeignKeyConstraint(
            ('child',),
            ['resources.resource_id'],
            name='fk_resource_mapping_child',
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ('parent',),
            ['resources.resource_id'],
            name='fk_resource_mapping_parent',
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resource_mappings_child'), 'resource_mappings', ['child'], unique=False)
    op.create_index(op.f('ix_resource_mappings_parent'), 'resource_mappings', ['parent'], unique=False)

    # Resource Properties
    op.create_table(
        'resource_properties',
        sa.Column('property_id', mysql.INTEGER(unsigned=True), autoincrement=True, nullable=False),
        sa.Column('resource_id', sa.String(length=256), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('value', mysql.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ('resource_id',),
            ['resources.resource_id'],
            name='fk_resource_property_resource_id',
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('property_id', 'resource_id')
    )
    op.create_index(op.f('ix_resource_properties_name'), 'resource_properties', ['name'], unique=False)
    op.create_index(op.f('ix_resource_properties_resource_id'), 'resource_properties', ['resource_id'], unique=False)

    # Tags
    op.create_table(
        'tags',
        sa.Column('tag_id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('resource_id', sa.String(length=256), nullable=False),
        sa.Column('key', sa.String(length=128), nullable=False),
        sa.Column('value', sa.String(length=256), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ('resource_id',),
            ['resources.resource_id'],
            name='fk_tag_resource_id',
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('tag_id', 'resource_id', 'key'),
        sa.UniqueConstraint('tag_id', 'key', 'resource_id', name='uniq_tag_resource_id_key')
    )
    op.create_index(op.f('ix_tags_resource_id'), 'tags', ['resource_id'], unique=False)
    op.create_index(op.f('ix_tags_value'), 'tags', ['value'], unique=False)


def downgrade():
    op.drop_table('tags')
    op.drop_table('resource_properties')
    op.drop_table('resource_mappings')
    op.drop_table('resources')
    op.drop_table('account_properties')
    op.drop_table('user_roles')
    op.drop_table('scheduler_jobs')
    op.drop_table('issue_properties')
    op.drop_table('config_items')
    op.drop_table('accounts')
    op.drop_table('users')
    op.drop_table('templates')
    op.drop_table('scheduler_batches')
    op.drop_table('roles')
    op.drop_table('resource_types')
    op.drop_table('logs')
    op.drop_table('issues')
    op.drop_table('issue_types')
    op.drop_table('enforcements')
    op.drop_table('emails')
    op.drop_table('config_namespaces')
    op.drop_table('auditlog')
    op.drop_table('account_types')
