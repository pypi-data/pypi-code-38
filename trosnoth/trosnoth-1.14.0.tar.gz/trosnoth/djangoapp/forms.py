from django import forms

from trosnoth.djangoapp.models import (
    TrosnothServerSettings, TrosnothUser, TrosnothArena,
)


class ServerSettingsForm(forms.ModelForm):
    allowed_hosts = forms.CharField(
        required=False,
        help_text='Comma-separated list of host names that are allowed to be '
                  'used to access the server web interface. Used for security '
                  'purposes. Host names will only be permitted if they are '
                  'in this list, or they are known local IP addresses of '
                  'this machine.')
    secret_key = forms.CharField(
        label='Secret key', max_length=100,
        help_text='Used for cryptographic signing. Should be unique and '
                  'unpredictable. Keep this value secret! Changing this '
                  'value will invalidate active web sessions.')
    debug = forms.BooleanField(
        required=False,
        label='Enable debugging',
        help_text='Show detailed error pages. Never turn this on for a '
                  'public server. ')

    class Meta:
        model = TrosnothServerSettings
        fields = (
            'serverName',
            'welcomeText',
            'elephantName',
            'webPort',
            'serverPort',
            'manholePort',
            'manholePassword',
            'trustClientUsernames',
        )
        widgets = {
            'serverName': forms.TextInput,
            'manholePassword': forms.TextInput,
            'elephantName': forms.TextInput,
        }


class ManagePlayerForm(forms.ModelForm):
    active = forms.BooleanField(
        required=False,
        label='Active',
        help_text='Deactivated users cannot log on to this server.',
    )
    superuser = forms.BooleanField(
        required=False,
        label='Superuser',
        help_text='Gives this user full management permissions on this '
                  'server.',
    )

    class Meta:
        model = TrosnothUser
        fields = (
            'nick',
            'ownsElephant',
        )
        widgets = {
            'nick': forms.TextInput,
        }


class ArenaModelForm(forms.ModelForm):
    class Meta:
        model = TrosnothArena
        fields = (
            'name',
            'enabled',
            'autoStartCountDown',
            'gamePort',
            'currentTournament',
            'profileSlowCalls',
        )
        widgets = {
            'name': forms.TextInput,
        }


class ArenaControlForm(forms.Form):
    paused = forms.BooleanField(
        required=False,
        label='Pause game',
    )
    blueShots = forms.BooleanField(
        required=False,
        label='Blue team can shoot',
    )
    blueCaps = forms.BooleanField(
        required=False,
        label='Blue team can capture zones',
    )
    redShots = forms.BooleanField(
        required=False,
        label='Red team can shoot',
    )
    redCaps = forms.BooleanField(
        required=False,
        label='Red team can capture zones',
    )
    action = forms.ChoiceField(
        choices=(
            ('', '------'),
            ('lobby', 'Return to lobby'),
            ('shutdown', 'Restart arena (boots all players)'),
        ),
        required=False,
        help_text='Send a special command to the running game',
    )


class SelectLevelForm(forms.Form):
    scenario = forms.ChoiceField(
        choices=(
            ('standard', 'Trosnoth match'),
            ('trosball', 'Trosball'),
            ('catpigeon', 'Cat among pigeons'),
            ('freeforall', 'Free for all'),
            ('hunted', 'Hunted'),
            ('orbchase', 'Orb chase'),
            ('elephantking', 'Elephant king'),
            ('defencedrill', 'Defence drill (red team cannot cap)'),
            ('positioningdrill', 'Positioning drill (no shooting)'),
        ),
        widget=forms.Select(attrs={
            'onchange': "update_fields();",
        }),
    )
    duration = forms.IntegerField(
        help_text='Duration in minutes. Zero or blank means auto duration.',
        min_value=0,
        required=False,
    )
    teams = forms.ChoiceField(
        required=False,
        choices=(
            ('auto', 'Automatic'),
            ('hvm', 'Humans vs. Machines'),
        ),
    )
    size = forms.ChoiceField(
        required=False,
        choices=(
            ('auto', 'Automatic'),
            ('standard', 'Standard'),
            ('small', 'Small'),
            ('wide', 'Wide'),
            ('large', 'Large'),
            ('custom', 'Custom'),
        ),
        widget=forms.Select(attrs={
            'onchange': "update_fields();",
        }),
    )
    half_width = forms.IntegerField(min_value=1, required=False)
    height = forms.IntegerField(min_value=1, required=False)
