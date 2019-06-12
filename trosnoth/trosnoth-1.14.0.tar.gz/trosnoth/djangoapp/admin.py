from django import forms
from django import urls
from django.contrib import admin
from django.db import models

from trosnoth.djangoapp.models import (
    TrosnothUser, AchievementProgress, GameRecord, GamePlayer, PlayerKills,
    TrosnothServerSettings, UpgradesUsedInGameRecord, TrosnothArena,
    Tournament,
)

DEFAULT_OVERRIDES = {
    models.TextField: {'widget': admin.widgets.AdminTextInputWidget},
}


@admin.register(TrosnothServerSettings)
class TrosnothServerSettingsAdmin(admin.ModelAdmin):
    formfield_overrides = DEFAULT_OVERRIDES

    def has_add_permission(self, request):
        # if there's already an entry, do not allow adding
        count = TrosnothServerSettings.objects.all().count()
        if count == 0:
            return True

        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    filter_horizontal = ('matches',)


@admin.register(TrosnothArena)
class TrosnothArenaAdmin(admin.ModelAdmin):
    pass


class AchievementProgressInline(admin.TabularInline):
    model = AchievementProgress
    formfield_overrides = DEFAULT_OVERRIDES


@admin.register(TrosnothUser)
class TrosnothUserAdmin(admin.ModelAdmin):
    inlines = [
        AchievementProgressInline,
    ]


class GamePlayerInline(admin.TabularInline):
    model = GamePlayer
    formfield_overrides = DEFAULT_OVERRIDES
    fields = ('user', 'botName', 'team', 'detailLink')
    readonly_fields = ('detailLink',)

    def detailLink(self, instance):
        if not instance.id:
            return ''

        changeform_url = urls.reverse(
            'admin:trosnoth_gameplayer_change', args=(instance.id,)
        )
        return '<a href="%s">Details</a>' % changeform_url
    detailLink.allow_tags = True
    detailLink.short_description = ''


@admin.register(GameRecord)
class GameRecordAdmin(admin.ModelAdmin):
    formfield_overrides = DEFAULT_OVERRIDES
    inlines = [
        GamePlayerInline,
    ]


class UpgradesUsedInGameRecordAdmin(admin.TabularInline):
    model = UpgradesUsedInGameRecord
    formfield_overrides = DEFAULT_OVERRIDES


class PlayerKillsInline(admin.TabularInline):
    model = PlayerKills
    fk_name = 'killee'
    formfield_overrides = DEFAULT_OVERRIDES


@admin.register(GamePlayer)
class GamePlayerAdmin(admin.ModelAdmin):
    model = GamePlayer
    formfield_overrides = DEFAULT_OVERRIDES
    inlines = [
        UpgradesUsedInGameRecordAdmin,
        PlayerKillsInline,
    ]


