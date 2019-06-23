# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

from io import StringIO
from subprocess import CalledProcessError, check_output, STDOUT

from django.contrib import admin
from django.template.response import TemplateResponse
from mezzanine.conf import settings

from mezzanine_sync_pages.models import MezzanineSyncPages
from mezzanine_sync_pages.sync_pages import SyncPagesController


@admin.register(MezzanineSyncPages)
class MezzanineSyncPagesAdmin(admin.ModelAdmin):

    # ----------------------------------------------------------------------
    def has_add_permission(self, request):
        """A fake model should not be added"""
        return False

    # ----------------------------------------------------------------------
    def has_delete_permission(self, request, obj=None):
        """A fake model should not be added"""
        return False

    # ----------------------------------------------------------------------
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or dict()
        extra_context['title'] = 'Sync Pages'

        if request.POST:
            git_pull_requested = self._git_pull_requested(request)
            output = self._sync_pages(git_pull_requested)
            extra_context['output'] = output
            extra_context['exec_git_pull'] = git_pull_requested

        return TemplateResponse(request, 'admin/mezzanine_sync_pages.html', extra_context)

    # ----------------------------------------------------------------------
    def _git_pull_requested(self, request):
        return 'exec_git_pull' in request.POST

    # ----------------------------------------------------------------------
    def _sync_pages(self, git_pull_requested):
        with StringIO() as output:
            try:
                # git pull
                if git_pull_requested:
                    git_pull_output = self._git_pull()
                    output.write(git_pull_output)
                    output.write('\n')
                # sync pages
                controller = SyncPagesController(
                    settings.MEZZANINE_SYNC_PAGES_DESTINATION_PATH,
                    stdout=output,
                    stderr=output,
                    verbosity=2)
                controller.sync()
            except CalledProcessError as exc:
                output.write(str(exc))
                output.write('\n')
                output.write(exc.output.decode('utf-8'))
            except Exception as exc:
                output.write(str(exc))

            return output.getvalue()

    # ----------------------------------------------------------------------
    def _git_pull(self):
        output_bytes = check_output(
            ['git', 'pull'],
            cwd=settings.MEZZANINE_SYNC_PAGES_DESTINATION_PATH,
            stderr=STDOUT)
        return output_bytes.decode('utf-8')
