from django.apps import AppConfig
from django.conf import settings


class DbbackupGitConfig(AppConfig):
    def ready(self):
        assert hasattr(settings, 'DBBACKUP_GIT'), '`dbbackup_git` app requires the `DBBACKUP_GIT` setting.'
        assert settings.DBBACKUP_GIT.get('DATABASE_BACKUP_FILENAME', None), \
            "`dbbackup_git` app requires the `DBBACKUP_GIT['DATABASE_BACKUP_FILENAME']` setting."
