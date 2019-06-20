# -*- coding: utf-8 -*-
from robot.libraries.BuiltIn import BuiltIn


class Library(object):
    """This library provides RobotFramework resources for openMairie based apps."""

    def __init__(self):
        """Init."""
        self.import_library_resources()

    def import_library_resources(self):
        """Import openMairieRobotFramework user keywords."""
        BuiltIn().import_resource('openmairie/robotframework/om_resources.robot')
        #
        BuiltIn().import_resource('openmairie/robotframework/formulaire.robot')
        BuiltIn().import_resource('openmairie/robotframework/menu.robot')
        BuiltIn().import_resource('openmairie/robotframework/module_gen.robot')
        BuiltIn().import_resource('openmairie/robotframework/module_import.robot')
        BuiltIn().import_resource('openmairie/robotframework/module_reqmo.robot')
        BuiltIn().import_resource('openmairie/robotframework/module_sig_interne.robot')
        BuiltIn().import_resource('openmairie/robotframework/navigation.robot')
        BuiltIn().import_resource('openmairie/robotframework/pdf.robot')
        BuiltIn().import_resource('openmairie/robotframework/tableau.robot')
        BuiltIn().import_resource('openmairie/robotframework/utils.robot')
        #
        BuiltIn().import_resource('openmairie/robotframework/om_collectivite.robot')
        BuiltIn().import_resource('openmairie/robotframework/om_droit.robot')
        BuiltIn().import_resource('openmairie/robotframework/om_etat.robot')
        BuiltIn().import_resource('openmairie/robotframework/om_lettretype.robot')
        BuiltIn().import_resource('openmairie/robotframework/om_logo.robot')
        BuiltIn().import_resource('openmairie/robotframework/om_parametre.robot')
        BuiltIn().import_resource('openmairie/robotframework/om_profil.robot')
        BuiltIn().import_resource('openmairie/robotframework/om_requete.robot')
        BuiltIn().import_resource('openmairie/robotframework/om_sousetat.robot')
        BuiltIn().import_resource('openmairie/robotframework/om_utilisateur.robot')
        BuiltIn().import_resource('openmairie/robotframework/om_widget.robot')
