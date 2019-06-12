from AccessControl.SecurityManagement import newSecurityManager
from ftw.contacts.contents.contact import IContactSchema
from ftw.contacts.interfaces import IContact, IContactsSettings
from ftw.contacts.interfaces import ILDAPAttributeMapper
from ftw.contacts.interfaces import ILDAPCustomUpdater
from ftw.contacts.interfaces import ILDAPSearch
from ftw.contacts.sync.mapper import DefaultLDAPAttributeMapper
from plone.app.blob.interfaces import IBlobWrapper
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import iterSchemata
from plone.dexterity.utils import createContent
from plone.namedfile import NamedBlobImage
from plone.namedfile.interfaces import INamedImageField
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zExceptions import BadRequest
from zope.component import getAdapters
from zope.component import getUtility
from zope.component import queryUtility
from zope.container.interfaces import INameChooser
from zope.event import notify
from zope.lifecycleevent import ObjectAddedEvent
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema import getFieldsInOrder
from zope.site.hooks import setSite
import argparse
import json
import ldif
import logging
import sys
import transaction


logger = logging.getLogger('ftw.contacts.sync')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', dest='plone_site', default=None,
                        help='Absolute path to the Plone site')
    parser.add_argument('-c', dest='config_file_path', default=None,
                        help='Absolute path to the config file')
    parser.add_argument('-b', dest='base_dn', default=None,
                        help='Base DN for contacts')
    parser.add_argument('-f', dest='filter', default='(objectClass=*)',
                        help='LDAP Filter, defaults to (objectClass=*)')
    parser.add_argument('-l', dest='ldif_file', type=str,
                        help='Import records from the given LDIF file')
    parser.add_argument('-v', dest='verbose', action='store_true',
                        help='Verbose')
    parser.add_argument('-n', dest='dry_run', action='store_true',
                        help='Dry run')
    parser.add_argument('-q', dest='quiet', action='store_true',
                        help='Quiet')

    if sys.argv == ['']:
        options = parser.parse_args([])
    else:
        options = parser.parse_args(sys.argv)

    # Setup logging
    log_handler = logging.StreamHandler()
    log_formatter = logging.Formatter("%(message)s")
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)
    if options.verbose:
        logger.setLevel(logging.DEBUG)

    # If no plone site was provided by the command line, try to find one.
    if options.plone_site is None:
        sites = get_plone_sites(app)
        if len(sites) == 1:
            portal = sites[0]
        elif len(sites) > 1:
            sys.exit("Multiple Plone sites found. Please specify which Plone "
                     "site should be used.")
        else:
            sys.exit("No Plone site found.")
    else:
        portal = app.unrestrictedTraverse(options.plone_site, None)
    if not portal:
        sys.exit("Plone site not found at %s" % options.plone_site)

    user = portal.getOwner()
    newSecurityManager(app, user)

    setSite(portal)

    # get the contact folder
    contacts_path = api.portal.get_registry_record(
        name='contacts_path', interface=IContactsSettings)
    if not contacts_path:
        sys.exit("Contacts path not set. Please configure the path to the "
                 "folder containing contacts in the configuration registry.")
    contacts_folder = portal.unrestrictedTraverse(
        contacts_path.lstrip('/').encode('utf-8'), None)

    if contacts_folder is None:
        sys.exit("Contacts folder not found at %s.")

    # collect config
    config = []
    # read the config from the provided file
    if options.config_file_path:
        with open(options.config_file_path) as config_file:
            config = json.load(config_file)
            # validate
            for entry in config:
                if not entry.get('ldap_plugin_id', False):
                    sys.exit("Please provide the ldap_plugin_id"
                             "in the config file.")

    # or use registry and command line parameter
    else:
        config.append({
            'ldap_plugin_id': api.portal.get_registry_record(
                name='ldap_plugin_id', interface=IContactsSettings),
            'base_dn': options.base_dn,
            'filter': options.filter
        })

    # Read records from an LDIF file
    if options.ldif_file:
        rlist = ldif.LDIFRecordList(open(options.ldif_file, 'rb'))
        rlist.parse()
        ldap_records = rlist.all_records

    # Get records from LDAP
    else:
        ldap = getUtility(ILDAPSearch)
        ldap_records = []

        for ldap_config in config:
            plugin_records = ldap.search(
                plugin_id=ldap_config.get('ldap_plugin_id'),
                base_dn=ldap_config.get('base_dn'),
                filter=ldap_config.get('filter'),
                attrs=get_ldap_attribute_mapper().mapping().keys(),
            )

            # prepend the prefix to avoid id collisions
            if ldap_config.get('userid_prefix'):
                for dn, entry in plugin_records:
                    if not dn:
                        continue
                    id_arr = entry.get(get_ldap_attribute_mapper().id())
                    if id_arr:
                        id_arr[0] = ldap_config.get('userid_prefix').encode('ascii') + id_arr[0]

            ldap_records += plugin_records

    stats = sync_contacts(contacts_folder, ldap_records)

    if not options.dry_run:
        transaction.commit()

    if not options.quiet:
        print "Created: %s" % stats['created']
        print "Modified: %s" % stats['modified']
        print "Unchanged: %s" % stats['unchanged']
        print "Skipped: %s" % stats['skipped']
        print "Failed: %s" % stats['failed']
        print "Total: %s" % stats['total']
        print "Deleted contacts: %s" % stats['deleted']


def get_ldap_attribute_mapper():
    mapper = queryUtility(ILDAPAttributeMapper)
    if mapper is None:
        mapper = DefaultLDAPAttributeMapper()
    return mapper


def get_plone_sites(root):
    result = []
    for obj in root.values():
        if obj.meta_type is 'Folder':
            result = result + get_plone_sites(obj)
        elif IPloneSiteRoot.providedBy(obj):
            result.append(obj)
        elif obj.getId() in getattr(root, '_mount_points', {}):
            result.extend(get_plone_sites(obj))
    return result


def sync_contacts(context, ldap_records, set_owner=False):
    """Synchronize the given ldap results """

    # Statistics
    created = 0
    modified = 0
    skipped = 0
    failed = 0
    deleted = 0

    dn_contact_id_mapping = {}

    ct = getToolByName(context, 'portal_catalog')
    mapper = get_ldap_attribute_mapper()
    dummy_contact = createContent('ftw.contacts.Contact')
    dummy_contact_folder = createContent('ftw.contacts.ContactFolder')

    # 1st pass: create or update profiles
    for dn, entry in ldap_records:

        if not dn:
            continue

        dn = dn.decode('unicode_escape').encode('iso8859-1').decode('utf-8')

        # Only entries with a contact id
        contact_id = entry.get(mapper.id(), [None, ])[0]
        if not contact_id:
            skipped += 1
            logger.debug("Skipping entry '%s'. No contact id." % dn)
            continue
        # Get the normalzied name for the contact with the given id. This has
        # to be done on a dummy folder because existing content would influence
        # the resulting id.
        contact_id = INameChooser(dummy_contact_folder).chooseName(
            contact_id, dummy_contact)

        dn_contact_id_mapping[dn] = contact_id

        contact = context.unrestrictedTraverse(contact_id, None)
        changed = False
        is_new_object = False

        # Check if we really got the wanted object.
        if not IContact.providedBy(contact):
            contact = None

        # Create contact
        if contact is None:
            try:
                contact = createContent('ftw.contacts.Contact')
                contact.id = contact_id
                addContentToContainer(context, contact)

                is_new_object = True
            # invalid id
            except BadRequest:
                failed += 1
                logger.warn("Could not create contact '%s' (invalid id)."
                            % contact_id)
                continue

        # Update/set field values
        IContactSchema(contact).ldap_dn = dn
        field_mapping = {}
        for schemata in iterSchemata(contact):
            for name, field in getFieldsInOrder(schemata):
                field_mapping[name] = field
        for ldap_name, field_name in mapper.mapping().items():
            field = field_mapping.get(field_name, None)
            if field is None:
                raise NotImplementedError()

            value = entry.get(ldap_name, [''])[0]

            current_value = field.get(contact)
            if IBlobWrapper.providedBy(current_value):
                current_value = current_value.data

            if current_value != value:
                # Handle images
                if INamedImageField.providedBy(field) and value:
                    value = NamedBlobImage(
                        data=value,
                        contentType='image/jpeg',
                        filename=u'%s.jpg' % contact_id
                    )
                field.set(contact, value)
                changed = True

        # Update/set fields with custom updaters
        custom_updaters = getAdapters((contact, entry),
                                      provided=ILDAPCustomUpdater)
        for name, updater in custom_updaters:
            changed = updater.update()

        if is_new_object:
            if set_owner:
                # Grant owner role to contact
                contact.__ac_local_roles__ = None
                contact.manage_setLocalRoles(contact_id, ['Owner'])
                contact.reindexObjectSecurity()

            aq_contact = context.get(contact_id)
            ct.catalog_object(aq_contact, '/'.join(aq_contact.getPhysicalPath()))

            notify(ObjectAddedEvent(aq_contact))

            created += 1
            logger.debug("Created new contact '%s (%s)'." % (contact_id, dn))

        elif changed:
            contact.reindexObject()
            notify(ObjectModifiedEvent(contact))
            modified += 1
            logger.debug("Modified contact '%s' (%s)." % (contact_id, dn))

    total = len(ldap_records)
    unchanged = total - skipped - modified - created - failed

    # 2nd pass: set references
    # TODO

    # 3rd pass: delete contacts which have an ldap_id but are not in LDAP.
    all_contacts = ct.unrestrictedSearchResults(
        portal_type='ftw.contacts.Contact',
        path=dict(query='/'.join(context.getPhysicalPath()), depth=1))
    to_be_deleted = {}
    for contact in all_contacts:
        obj = contact.getObject()
        ldap_dn = IContactSchema(obj).ldap_dn
        if ldap_dn and ldap_dn not in dn_contact_id_mapping:
            parent_path = '/'.join(obj.getPhysicalPath()[:-1])
            id_ = obj.getPhysicalPath()[-1]
            if parent_path not in to_be_deleted:
                to_be_deleted[parent_path] = []
            to_be_deleted[parent_path].append(id_)
            logger.debug("Deleting contact '%s'" % id_)

    # Disable link integrity check while deleting contacts
    ptool = getToolByName(context, 'portal_properties')
    props = getattr(ptool, 'site_properties')
    old_check = props.getProperty('enable_link_integrity_checks', False)
    props.enable_link_integrity_checks = False

    for parent_path, ids in to_be_deleted.items():
        parent = context.unrestrictedTraverse(parent_path)
        deleted += len(ids)
        parent.manage_delObjects(ids)

    # Reenable previous link integrity setting
    props.enable_link_integrity_checks = old_check

    return dict(
        created=created,
        modified=modified,
        unchanged=unchanged,
        total=total,
        skipped=skipped,
        failed=failed,
        deleted=deleted,
    )


if __name__ == '__main__':
    main()
