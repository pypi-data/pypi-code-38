import re

from django import forms

from crispy_forms.helper import FormHelper


class ContactInformationForm(forms.Form):
    name = forms.CharField(
        label='My name is',
        help_text='This will appear on your name tag, and in public areas of '
                  'this site, e.g. if you submit a talk.',
        max_length=50,
    )
    # TODO: Consider storing the "wallet name" here, and having a separate
    # public name
    # TODO: nametag preview
    nametag_2 = forms.CharField(
        label='Nametag line 2',
        help_text="This could be your company, project, preferred pronoun or "
                  "anything you'd like to say.",
        max_length=50,
        required=False,
    )
    nametag_3 = forms.CharField(
        label='Nametag line 3',
        help_text="This could be your nick, username, or something "
                  "suitably silly.",
        max_length=50,
        required=False,
    )
    email = forms.EmailField(
        label='My e-mail address is',
        help_text="This won't be listed publicly.",
    )
    phone = forms.CharField(
        label='My contact number',
        help_text="The full number, including international dialing codes, "
                  "please. This won't be listed publicly.",
        max_length=16,
        required=False,
    )
    emergency_contact = forms.CharField(
        label='My emergency contact',
        help_text='Please include the name, full international phone number, '
                  'and language spoken (if not English).',
        widget=forms.Textarea(attrs={'rows': 3}),
    )
    # Purposefully left unchecked by default to make this opt-in.
    announce_me = forms.BooleanField(
        label='Announce my arrival',
        help_text='If checked, your name will be announced in the IRC channel '
                  'when you check in to the conference.',
        required=False,
    )
    register_announce = forms.BooleanField(
        label="Subscribe me to the DebConf-announce mailing list",
        help_text='This low-volume mailing list is the primary way for us to '
                  'reach attendees about important conference news and '
                  'information.',
        required=False,
        initial=True,
    )
    register_discuss = forms.BooleanField(
        label='Subscribe me to the DebConf-discuss mailing list',
        help_text='This mailing list is used by attendees and interested '
                  'people for general discussions about the conference.',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not re.match(r'^\+', phone):
            raise forms.ValidationError(
                "If you provide a phone number, please make sure it's in "
                "international dialling format. e.g. +1 234 567 8999")
        return phone
