# -*- coding: utf-8 -*-
'''
lucterios.standard tests package

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2018 sd-libre.fr
@license: This file is part of Lucterios.

Lucterios is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Lucterios is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals

from lucterios.framework.test import LucteriosTest, add_user
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.contacts.models import Individual, LegalEntity
from lucterios.CORE.views import get_wizard_step_list

from lucterios.contacts.tests_contacts import change_ourdetail


def create_individual(firstname, lastname):
    empty_contact = Individual()
    empty_contact.firstname = firstname
    empty_contact.lastname = lastname
    empty_contact.address = "rue de la liberté"
    empty_contact.postal_code = "97250"
    empty_contact.city = "LE PRECHEUR"
    empty_contact.country = "MARTINIQUE"
    empty_contact.tel2 = "02-78-45-12-95"
    empty_contact.email = "%s.%s@worldcompany.com" % (firstname, lastname)
    empty_contact.save()
    return empty_contact


def change_legal(name):
    ourdetails = LegalEntity()
    ourdetails.name = name
    ourdetails.address = "Place des cocotiers"
    ourdetails.postal_code = "97200"
    ourdetails.city = "FORT DE FRANCE"
    ourdetails.country = "MARTINIQUE"
    ourdetails.tel1 = "01-23-45-67-89"
    ourdetails.email = "%s@worldcompany.com" % name
    ourdetails.save()


def initial_contacts():
    change_ourdetail()  # contact 1
    create_individual('Avrel', 'Dalton')  # contact 2
    create_individual('William', 'Dalton')  # contact 3
    create_individual('Jack', 'Dalton')  # contact 4
    create_individual('Joe', 'Dalton')  # contact 5
    create_individual('Lucky', 'Luke')  # contact 6
    change_legal("Minimum")  # contact 7
    change_legal("Maximum")  # contact 8


class StandardTest(LucteriosTest):

    def setUp(self):
        initial_contacts()
        LucteriosTest.setUp(self)
        contact = Individual.objects.get(id=5)
        contact.user = add_user('joe')
        contact.save()

    def test_status(self):
        self.calljson('/CORE/authentification', {'username': 'admin', 'password': 'admin'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'OK')

        self.calljson('/CORE/statusMenu', {})
        self.assert_observer('core.custom', 'CORE', 'statusMenu')
        self.assert_count_equal('', 12)

    def test_wizard(self):
        self.calljson('/CORE/authentification', {'username': 'admin', 'password': 'admin'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'OK')

        steplist = get_wizard_step_list()
        self.assertEqual(7, len(steplist.split(';')), steplist)

        self.calljson('/CORE/configurationWizard', {'steplist': steplist})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 8)

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 1})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 18)

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 2})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 17)

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 3})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 8)

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 4})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 9)

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 5})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 10)

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 6})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 13)

    def test_situation(self):
        self.calljson('/CORE/authentification', {'username': 'joe', 'password': 'joe'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'OK')

        self.calljson('/CORE/situationMenu', {})
        self.assert_observer('core.custom', 'CORE', 'situationMenu')
        self.assert_count_equal('', 2)
