from ftw.contacts.interfaces import IContact
from ftw.contacts.utils import ALPHABET
from ftw.contacts.utils import AlphabeticLetters
from ftw.contacts.utils import normalized_first_letter
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

import json
import re


class ContactFolderView(BrowserView):
    """Contactfolder view
    """


class Letters(BrowserView):
    """View to render the letters-listing
    """
    def __call__(self, brains, current_letter):
        self.letters = AlphabeticLetters().letters(current_letter, brains)
        return super(Letters, self).__call__()


class ContactFolderReload(BrowserView):
    """Returns the nessesary html elements to reload the
    contactlisting per ajax.

    Checks the request for:

    - searchable_text
    - letter
    - index_from
    - index_to

    Contacts:
    This view will be called asynchron to lazy-load the contacts.
    It returns the next few full rendered contacts
    for the contactfolderlisting.

    Letters:
    Returns the letterlisting.
    Puts css-classes on each letter which differs between the
    current letter and letters with contacts.
    """
    def __call__(self):
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        self.request.response.setHeader(
            'Content-Type', 'application/json; charset=utf-8')
        index_from = int(self.request.form.get('index_from', 0))
        index_to = int(self.request.form.get('index_to', 50))
        searchable_text = self.request.form.get('searchable_text', '')
        current_letter = self.request.form.get('letter', None)

        brains = self._contact_brains(SearchableText=searchable_text)
        filtered_brains = self._filter_letter(brains, current_letter)

        # max_contacts: is the length of brains after filtered by
        #               the searchable text and filtered by the letters
        # contacts: are the rendered contacts, sliced with the
        #           index_from and index_to parameter
        # letters: are the rendered letters only filterd by the
        #          searchable_text to get all the possible letters
        return json.dumps({
            'max_contacts': len(filtered_brains),
            'contacts': self.rendered_contacts(
                filtered_brains, index_from, index_to),
            'letters': self.rendered_letters(brains, current_letter)})

    def rendered_contacts(
            self, filtered_brains, index_from, index_to):
        brains = filtered_brains[index_from:index_to]

        return ''.join([brain.getObject().restrictedTraverse(
            '@@contact_summary')() for brain in brains])

    def rendered_letters(self, brains, current_letter):
        view = self.context.restrictedTraverse('@@letters')
        return view(brains, current_letter)

    def _contact_brains(self, **query):
        query = self._build_query(**query)
        self.catalog = getToolByName(self.context, 'portal_catalog')

        return self.catalog(query)

    def _filter_letter(self, brains, current_letter):
        """Compares the title of the brain with the letter and
        filter matching elements
        """
        if not current_letter:
            return brains

        filtered_brains = []
        for brain in brains:
            letter = normalized_first_letter(brain.Title)
            if letter == current_letter:
                filtered_brains.append(brain)
            elif current_letter == '#' and letter not in ALPHABET:
                filtered_brains.append(brain)

        return filtered_brains

    def _build_query(self, **query):
        folder_path = '/'.join(self.context.getPhysicalPath())
        basequery = dict(
            path={'query': folder_path},
            sort_on='sortable_title',
            object_provides=IContact.__identifier__,
            SearchableText='')

        basequery.update(query)
        return self._cleanup_query(basequery)

    def _cleanup_query(self, query):
        text = query.get('SearchableText')

        # Remove unsupported words
        text = re.sub(re.compile(
            r'[^\w\s]', re.UNICODE), r'', text.decode('utf-8')).encode('utf-8')

        text = text.strip()

        if not text:
            query.pop('SearchableText')
            return query

        # Add wildcard
        text = "{0}*".format(text)

        query.update({'SearchableText': text})

        return query
