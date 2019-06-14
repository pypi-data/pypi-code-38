# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# GNU General Public License (GPL)
# ------------------------------------------------------------------------------
'''This module, borrowed from Products.PloneMeeting, defines helper methods
   to ease migration process.'''

from imio.helpers.catalog import removeColumns
from imio.helpers.catalog import removeIndexes
from imio.helpers.content import disable_link_integrity_checks
from imio.helpers.content import restore_link_integrity_checks
from plone import api
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.utils import base_hasattr
from Products.GenericSetup.upgrade import normalize_version
from Products.ZCatalog.ProgressHandler import ZLogHandler
from zope.component import getUtility

import logging
import time


logger = logging.getLogger('imio.migrator')
CURRENTLY_MIGRATING_REQ_VALUE = 'imio_migrator_currently_migrating'


class Migrator(object):
    '''Abstract class for creating a migrator.'''
    def __init__(self, context, disable_linkintegrity_checks=False):
        self.context = context
        self.portal = context.portal_url.getPortalObject()
        self.request = self.portal.REQUEST
        self.ps = self.portal.portal_setup
        self.wfTool = self.portal.portal_workflow
        self.registry = getUtility(IRegistry)
        self.catalog = api.portal.get_tool('portal_catalog')
        self.startTime = time.time()
        self.warnings = []
        self.request.set(CURRENTLY_MIGRATING_REQ_VALUE, True)
        self.disable_linkintegrity_checks = disable_linkintegrity_checks
        if disable_linkintegrity_checks:
            self.original_link_integrity = disable_link_integrity_checks()

    def run(self):
        '''Must be overridden. This method does the migration job.'''
        raise 'You should have overridden me darling.'

    def warn(self, logger, warning_msg):
        '''Manage warning messages, into logger and saved into self.warnings.'''
        logger.warn(warning_msg)
        self.warnings.append(warning_msg)

    def finish(self):
        '''At the end of the migration, you can call this method to log its
           duration in minutes.'''
        if self.disable_linkintegrity_checks:
            restore_link_integrity_checks(self.original_link_integrity)
        self.request.set(CURRENTLY_MIGRATING_REQ_VALUE, False)
        seconds = time.time() - self.startTime
        if self.warnings:
            logger.info('Here are warning messages generated during the migration : \n{0}'.format(
                '\n'.join(self.warnings))
            )
        logger.info('Migration finished in %d minute(s).' % (seconds / 60))

    def refreshDatabase(self,
                        catalogs=True,
                        catalogsToRebuild=['portal_catalog'],
                        workflows=False,
                        workflowsToUpdate=[]):
        '''After the migration script has been executed, it can be necessary to
           update the Plone catalogs and/or the workflow settings on every
           database object if workflow definitions have changed. We can pass
           catalog ids we want to 'clear and rebuild' using
           p_catalogsToRebuild.'''
        if catalogs:
            # Manage the catalogs we want to clear and rebuild
            # We have to call another method as clear=1 passed to refreshCatalog
            # does not seem to work as expected...
            for catalog in catalogsToRebuild:
                logger.info('Recataloging %s...' % catalog)
                catalogObj = getattr(self.portal, catalog)
                if base_hasattr(catalogObj, 'clearFindAndRebuild'):
                    catalogObj.clearFindAndRebuild()
                else:
                    # special case for the uid_catalog
                    catalogObj.manage_rebuildCatalog()
            catalogIds = ('portal_catalog', 'reference_catalog', 'uid_catalog')
            for catalogId in catalogIds:
                if catalogId not in catalogsToRebuild:
                    catalogObj = getattr(self.portal, catalogId)
                    pghandler = ZLogHandler()
                    catalogObj.refreshCatalog(clear=0, pghandler=pghandler)
        if workflows:
            logger.info('Refresh workflow-related information on every object of the database...')
            if not workflowsToUpdate:
                count = self.wfTool.updateRoleMappings()
            wfs = {}
            for wf_id in workflowsToUpdate:
                wf = self.wfTool.getWorkflowById(wf_id)
                wfs[wf] = wf
            count = self.wfTool._recursiveUpdateRoleMappings(self.portal, wfs)
            logger.info('{0} object(s) updated.'.format(count))

    def cleanRegistries(self, registries=('portal_javascripts', 'portal_css', 'portal_setup')):
        '''
          Clean p_registries, remove not found elements.
        '''
        logger.info('Cleaning registries...')
        if 'portal_javascripts' in registries:
            jstool = self.portal.portal_javascripts
            for script in jstool.getResources():
                scriptId = script.getId()
                resourceExists = script.isExternal or self.portal.restrictedTraverse(scriptId, False) and True
                if not resourceExists:
                    # we found a notFound resource, remove it
                    logger.info('Removing %s from portal_javascripts' % scriptId)
                    jstool.unregisterResource(scriptId)
            jstool.cookResources()
            logger.info('portal_javascripts has been cleaned!')

        if 'portal_css' in registries:
            csstool = self.portal.portal_css
            for sheet in csstool.getResources():
                sheetId = sheet.getId()
                resourceExists = sheet.isExternal or self.portal.restrictedTraverse(sheetId, False) and True
                if not resourceExists:
                    # we found a notFound resource, remove it
                    logger.info('Removing %s from portal_css' % sheetId)
                    csstool.unregisterResource(sheetId)
            csstool.cookResources()
            logger.info('portal_css has been cleaned!')

        if 'portal_setup' in registries:
            # clean portal_setup
            for stepId in self.ps.getSortedImportSteps():
                stepMetadata = self.ps.getImportStepMetadata(stepId)
                # remove invalid steps
                if stepMetadata['invalid']:
                    logger.info('Removing %s step from portal_setup' % stepId)
                    self.ps._import_registry.unregisterStep(stepId)
            logger.info('portal_setup has been cleaned!')
        logger.info('Registries have been cleaned!')

    def removeUnusedIndexes(self, indexes=[]):
        """ Remove unused catalog indexes. """
        logger.info('Removing no more used catalog indexes...')
        removeIndexes(self.portal, indexes=indexes)
        logger.info('Done.')

    def removeUnusedColumns(self, columns=[]):
        """ Remove unused catalog columns. """
        logger.info('Removing no more used catalog columns...')
        removeColumns(self.portal, columns=columns)
        logger.info('Done.')

    def removeUnusedPortalTypes(self, portal_types=[]):
        """ Remove unused portal_types from portal_types and portal_factory."""
        logger.info('Removing no more used {0} portal_types...'.format(', '.join(portal_types)))
        # remove from portal_types
        types = self.portal.portal_types
        to_remove = [portal_type for portal_type in portal_types if portal_type in types]
        if to_remove:
            types.manage_delObjects(ids=to_remove)
        # remove from portal_factory
        portal_factory = api.portal.get_tool('portal_factory')
        registeredFactoryTypes = [portal_type for portal_type in portal_factory.getFactoryTypes().keys()
                                  if portal_type not in portal_types]
        portal_factory.manage_setPortalFactoryTypes(listOfTypeIds=registeredFactoryTypes)
        logger.info('Done.')

    def install(self, products):
        """ Allows to install a series of products """
        qi = api.portal.get_tool('portal_quickinstaller')
        for product in products:
            logger.info("Install product '{}'".format(product))
            logger.info(qi.installProduct(product, forceProfile=True))  # don't reinstall

    def reinstall(self, profiles, ignore_dependencies=False, dependency_strategy=None):
        """ Allows to reinstall a series of p_profiles. """
        logger.info('Reinstalling product(s) %s...' % ', '.join([profile.startswith('profile-') and profile[8:] or
                                                                 profile for profile in profiles]))
        for profile in profiles:
            if not profile.startswith('profile-'):
                profile = 'profile-%s' % profile
            try:
                self.ps.runAllImportStepsFromProfile(profile,
                                                     ignore_dependencies=ignore_dependencies,
                                                     dependency_strategy=dependency_strategy)
            except KeyError:
                logger.error('Profile %s not found!' % profile)
        logger.info('Done.')

    def upgradeProfile(self, profile, olds=[]):
        """ Get upgrade steps and run it. olds can contain a list of dest upgrades to run. """

        def run_upgrade_step(step, source, dest):
            logger.info('Running upgrade step %s (%s -> %s): %s' % (profile, source, dest, step.title))
            step.doStep(self.ps)

        # if olds, we get all steps.
        upgrades = self.ps.listUpgrades(profile, show_old=bool(olds))
        applied_dests = []
        for container in upgrades:
            if isinstance(container, dict):
                if not olds or container['sdest'] in olds:
                    applied_dests.append((normalize_version(container['sdest']), container['sdest']))
                    run_upgrade_step(container['step'], container['ssource'], container['sdest'])
            elif isinstance(container, list):
                for dic in container:
                    if not olds or dic['sdest'] in olds:
                        applied_dests.append((normalize_version(dic['sdest']), dic['sdest']))
                        run_upgrade_step(dic['step'], dic['ssource'], dic['sdest'])
        if applied_dests:
            current_version = normalize_version(self.ps.getLastVersionForProfile(profile))
            highest_version, dest = sorted(applied_dests)[-1]
            # check if highest applied version is higher than current version
            if highest_version > current_version:
                self.ps.setLastVersionForProfile(profile, dest)
                # we update portal_quickinstaller version
                pqi = self.portal.portal_quickinstaller
                try:
                    product = profile.split(':')[0]
                    prod = pqi.get(product)
                    setattr(prod, 'installedversion', pqi.getProductVersion(product))
                except IndexError, e:
                    logger.error("Cannot extract product from profile '%s': %s" % (profile, e))
                except AttributeError, e:
                    logger.error("Cannot get product '%s' from portal_quickinstaller: %s" % (product, e))

    def upgradeAll(self, omit=[]):
        """ Upgrade all upgrade profiles except those in omit parameter list """
        if self.portal.REQUEST.get('profile_id'):
            omit.append(self.portal.REQUEST.get('profile_id'))
        for profile in self.ps.listProfilesWithUpgrades():
            # make sure the profile isn't the current (or must be avoided) and
            # the profile is well installed
            if profile not in omit and self.ps.getLastVersionForProfile(profile) != 'unknown':
                self.upgradeProfile(profile)

    def runProfileSteps(self, product, steps=[], profile='default'):
        """ Run given steps of a product profile (default is 'default' profile) """
        for step_id in steps:
            logger.info("Running profile step '%s:%s' => %s" % (product, profile, step_id))
            self.ps.runImportStepFromProfile('profile-%s:%s' % (product, profile), step_id)
