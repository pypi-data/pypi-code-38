# -*- coding: utf-8 -*-
'''
diacamma.invoice tests package

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2015 sd-libre.fr
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
from shutil import rmtree
from _io import StringIO

from django.utils import six

from lucterios.framework.test import LucteriosTest
from lucterios.framework.filetools import get_user_dir
from lucterios.CORE.models import SavedCriteria
from lucterios.CORE.views import ObjectMerge

from diacamma.accounting.test_tools import initial_thirds_fr, default_compta_fr, default_costaccounting
from diacamma.invoice.models import Article
from diacamma.invoice.test_tools import default_articles, default_categories, default_customize, default_accountPosting
from diacamma.invoice.views_conf import InvoiceConfFinancial, InvoiceConfCommercial, VatAddModify, VatDel, CategoryAddModify, CategoryDel, ArticleImport, StorageAreaDel,\
    StorageAreaAddModify, AccountPostingAddModify, AccountPostingDel, AutomaticReduceAddModify, AutomaticReduceDel
from diacamma.invoice.views import ArticleList, ArticleAddModify, ArticleDel, ArticleShow, ArticleSearch


class ConfigTest(LucteriosTest):

    def setUp(self):
        LucteriosTest.setUp(self)
        default_compta_fr()
        rmtree(get_user_dir(), True)

    def test_vat(self):
        self.factory.xfer = InvoiceConfFinancial()
        self.calljson('/diacamma.invoice/invoiceConfFinancial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfFinancial')
        self.assertTrue('__tab_3' in self.json_data.keys(), self.json_data.keys())
        self.assertFalse('__tab_4' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 2 + 7 + 2 + 2)  # general + parameters + imputation + vat

        self.assert_grid_equal('vat', {'name': "nom", 'rate': "taux", 'account': "compte de TVA", 'isactif': "actif ?"}, 0)

        self.factory.xfer = VatAddModify()
        self.calljson('/diacamma.invoice/vatAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'vatAddModify')
        self.assert_count_equal('', 5)

        self.factory.xfer = VatAddModify()
        self.calljson('/diacamma.invoice/vatAddModify',
                      {'name': 'my vat', 'rate': '11.57', 'account': '4455', 'isactif': 1, 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'vatAddModify')

        self.factory.xfer = InvoiceConfFinancial()
        self.calljson('/diacamma.invoice/invoiceConfFinancial', {}, False)
        self.assert_count_equal('vat', 1)
        self.assert_json_equal('', 'vat/@0/name', 'my vat')
        self.assert_json_equal('', 'vat/@0/rate', '11.57')
        self.assert_json_equal('', 'vat/@0/account', '4455')
        self.assert_json_equal('', 'vat/@0/isactif', '1')

        self.factory.xfer = VatDel()
        self.calljson('/diacamma.invoice/vatDel', {'vat': 1, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'vatDel')

        self.factory.xfer = InvoiceConfFinancial()
        self.calljson('/diacamma.invoice/invoiceConfFinancial', {}, False)
        self.assert_count_equal('vat', 0)

    def test_category(self):
        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfCommercial')
        self.assertTrue('__tab_5' in self.json_data.keys(), self.json_data.keys())
        self.assertFalse('__tab_6' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 3 + 3 + 2 + 2 + 2 + 2)

        self.assert_grid_equal('category', {'name': "nom", 'designation': "désignation"}, 0)

        self.factory.xfer = CategoryAddModify()
        self.calljson('/diacamma.invoice/categoryAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'categoryAddModify')
        self.assert_count_equal('', 3)

        self.factory.xfer = CategoryAddModify()
        self.calljson('/diacamma.invoice/categoryAddModify',
                      {'name': 'my category', 'designation': "bla bla bla", 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'categoryAddModify')

        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_count_equal('category', 1)
        self.assert_json_equal('', 'category/@0/name', 'my category')
        self.assert_json_equal('', 'category/@0/designation', 'bla bla bla')

        self.factory.xfer = CategoryDel()
        self.calljson('/diacamma.invoice/categoryDel', {'category': 1, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'categoryDel')

        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_count_equal('category', 0)

    def test_accountposting(self):
        default_costaccounting()
        self.factory.xfer = InvoiceConfFinancial()
        self.calljson('/diacamma.invoice/invoiceConfFinancial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfFinancial')
        self.assert_grid_equal('accountposting', {'name': "nom", 'sell_account': "compte de vente", 'cost_accounting': 'comptabilité analytique'}, 0)

        self.factory.xfer = AccountPostingAddModify()
        self.calljson('/diacamma.invoice/accountPostingAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'accountPostingAddModify')
        self.assert_count_equal('', 4)
        self.assert_select_equal('sell_account', 3)
        self.assert_select_equal('cost_accounting', {0: None, 2: 'open'})

        self.factory.xfer = AccountPostingAddModify()
        self.calljson('/diacamma.invoice/accountPostingAddModify', {'name': 'aaa', 'sell_account': '601', 'cost_accounting': 2, 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'accountPostingAddModify')

        self.factory.xfer = InvoiceConfFinancial()
        self.calljson('/diacamma.invoice/invoiceConfFinancial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfFinancial')
        self.assert_count_equal('accountposting', 1)

        self.factory.xfer = AccountPostingDel()
        self.calljson('/diacamma.invoice/accountPostingDel', {'accountposting': 1, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'accountPostingDel')

        self.factory.xfer = InvoiceConfFinancial()
        self.calljson('/diacamma.invoice/invoiceConfFinancial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfFinancial')
        self.assert_count_equal('accountposting', 0)

    def test_automaticreduce(self):
        default_categories()
        SavedCriteria.objects.create(name='my filter', modelname='accounting.Third', criteria='azerty')
        SavedCriteria.objects.create(name='other filter', modelname='contacts.EntityLegal', criteria='qwerty')

        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfCommercial')
        self.assert_grid_equal('automaticreduce', {'name': "nom", 'category': "catégorie", 'mode': 'mode', 'amount_txt': 'montant', 'occurency': 'occurence', 'filtercriteria': 'critère de filtrage'}, 0)

        self.factory.xfer = AutomaticReduceAddModify()
        self.calljson('/diacamma.invoice/automaticReduceAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'automaticReduceAddModify')
        self.assert_count_equal('', 7)
        self.assert_select_equal('category', 3)
        self.assert_select_equal('filtercriteria', {0: None, 1: 'my filter'})

        self.factory.xfer = AutomaticReduceAddModify()
        self.calljson('/diacamma.invoice/automaticReduceAddModify', {'name': "abc", 'category': 2, 'mode': 1, 'amount': '10.0', 'filtercriteria': '1', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'automaticReduceAddModify')

        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfCommercial')
        self.assert_count_equal('automaticreduce', 1)

        self.factory.xfer = AutomaticReduceDel()
        self.calljson('/diacamma.invoice/automaticReduceDel', {'automaticreduce': 1, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'automaticReduceDel')

        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfCommercial')
        self.assert_count_equal('automaticreduce', 0)

    def test_customize(self):
        default_customize()
        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfCommercial')
        self.assertTrue('__tab_5' in self.json_data.keys(), self.json_data.keys())
        self.assertFalse('__tab_6' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 3 + 3 + 2 + 2 + 2 + 2)

        self.assert_grid_equal('custom_field', {'name': "nom", 'kind_txt': "type"}, 2)
        self.assert_json_equal('', 'custom_field/@0/name', 'couleur')
        self.assert_json_equal('', 'custom_field/@0/kind_txt', 'Sélection (---,noir,blanc,rouge,bleu,jaune)')
        self.assert_json_equal('', 'custom_field/@1/name', 'taille')
        self.assert_json_equal('', 'custom_field/@1/kind_txt', 'Entier [0;100]')

    def test_storagearea(self):
        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConfCommercial')
        self.assertTrue('__tab_5' in self.json_data.keys(), self.json_data.keys())
        self.assertFalse('__tab_6' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 3 + 3 + 2 + 2 + 2 + 2)

        self.assert_grid_equal('storagearea', {'name': "nom", 'designation': "désignation"}, 0)

        self.factory.xfer = StorageAreaAddModify()
        self.calljson('/diacamma.invoice/storageAreaAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageAreaAddModify')
        self.assert_count_equal('', 3)

        self.factory.xfer = StorageAreaAddModify()
        self.calljson('/diacamma.invoice/storageAreaAddModify',
                      {'name': 'my category', 'designation': "bla bla bla", 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'storageAreaAddModify')

        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_count_equal('storagearea', 1)
        self.assert_json_equal('', 'storagearea/@0/name', 'my category')
        self.assert_json_equal('', 'storagearea/@0/designation', 'bla bla bla')

        self.factory.xfer = StorageAreaDel()
        self.calljson('/diacamma.invoice/storageAreaDel', {'storagearea': 1, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'storageAreaDel')

        self.factory.xfer = InvoiceConfCommercial()
        self.calljson('/diacamma.invoice/invoiceConfCommercial', {}, False)
        self.assert_count_equal('storagearea', 0)

    def test_article(self):
        default_accountPosting()
        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 6)
        self.assert_select_equal('stockable', 4)  # nb=4
        self.assert_grid_equal('article', {'reference': "référence", 'designation': "désignation", 'price_txt': "prix", 'unit': "unité", 'isdisabled': "désactivé ?", 'accountposting': "code d'imputation comptable", 'stockable': "stockable"}, 0)
        self.assert_count_equal('#article/actions', 3)

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleAddModify')
        self.assert_count_equal('', 11)

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify',
                      {'reference': 'ABC001', 'designation': 'My beautiful article', 'price': '43.72', 'accountposting': 4, 'stockable': '1', 'qtyDecimal': '1', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'articleAddModify')

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 1)
        self.assert_json_equal('', 'article/@0/reference', "ABC001")
        self.assert_json_equal('', 'article/@0/designation', "My beautiful article")
        self.assert_json_equal('', 'article/@0/price_txt', "43.72€")
        self.assert_json_equal('', 'article/@0/unit', '')
        self.assert_json_equal('', 'article/@0/isdisabled', "0")
        self.assert_json_equal('', 'article/@0/accountposting', "code4")
        self.assert_json_equal('', 'article/@0/stockable', "stockable")

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 14)
        self.assert_json_equal('', 'qtyDecimal', '1')

        self.factory.xfer = ArticleDel()
        self.calljson('/diacamma.invoice/articleDel',
                      {'article': '1', 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'articleDel')

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 0)

    def test_article_with_cat(self):
        default_categories()
        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_select_equal("cat_filter", 3, True)
        self.assert_grid_equal('article', {"reference": "référence", "designation": "désignation", "price_txt": "prix", "unit": "unité",
                                           "isdisabled": "désactivé ?", "accountposting": "code d'imputation comptable", "stockable": "stockable", "categories": "catégories"}, 0)

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleAddModify')
        self.assert_count_equal('', 13)

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify',
                      {'reference': 'ABC001', 'designation': 'My beautiful article', 'price': '43.72', 'sell_account': '705', 'stockable': '1', 'categories': '2;3', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'articleAddModify')

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 15)
        self.assert_json_equal('', 'qtyDecimal', '0')

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 1)
        self.assert_json_equal('', 'article/@0/categories', "cat 2{[br/]}cat 3")

    def test_article_merge(self):
        default_categories()
        default_articles(with_storage=True)
        default_customize()
        initial_thirds_fr()

        search_field_list = Article.get_search_fields()
        self.assertEqual(9 + 2 + 2 + 2 + 1, len(search_field_list), search_field_list)  # article + art custom + category + provider

        self.factory.xfer = ArticleSearch()
        self.calljson('/diacamma.invoice/articleSearch', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleSearch')
        self.assert_count_equal('article', 5)
        self.assert_json_equal('', 'article/@0/reference', "ABC1")
        self.assert_json_equal('', 'article/@1/reference', "ABC2")
        self.assert_json_equal('', 'article/@2/reference', "ABC3")
        self.assert_json_equal('', 'article/@3/reference', "ABC4")
        self.assert_json_equal('', 'article/@4/reference', "ABC5")
        self.assert_json_equal('', 'article/@0/categories', "cat 1")
        self.assert_json_equal('', 'article/@1/categories', "cat 2")
        self.assert_json_equal('', 'article/@2/categories', "cat 2{[br/]}cat 3")
        self.assert_json_equal('', 'article/@3/categories', "cat 3")
        self.assert_json_equal('', 'article/@4/categories', "cat 1{[br/]}cat 2{[br/]}cat 3")
        self.assert_count_equal('#article/actions', 4)
        self.assert_action_equal('#article/actions/@3', ('Fusion', 'images/clone.png', 'CORE', 'objectMerge', 0, 1, 2,
                                                         {'modelname': 'invoice.Article', 'field_id': 'article'}))

        self.factory.xfer = ObjectMerge()
        self.calljson('/CORE/objectMerge', {'modelname': 'invoice.Article', 'field_id': 'article', 'article': '1;3;5'}, False)
        self.assert_observer('core.custom', 'CORE', 'objectMerge')
        self.assert_count_equal('mrg_object', 3)
        self.assert_json_equal('', 'mrg_object/@0/value', "ABC1")
        self.assert_json_equal('', 'mrg_object/@1/value', "ABC3")
        self.assert_json_equal('', 'mrg_object/@2/value', "ABC5")

        self.factory.xfer = ObjectMerge()
        self.calljson('/CORE/objectMerge', {'modelname': 'invoice.Article', 'field_id': 'article', 'article': '1;3;5', 'CONFIRME': 'YES', 'mrg_object': '3'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'objectMerge')
        self.assert_action_equal(self.response_json['action'], ('Editer', 'images/show.png', 'diacamma.invoice', 'articleShow', 1, 1, 1, {'article': '3'}))

        self.factory.xfer = ArticleSearch()
        self.calljson('/diacamma.invoice/articleSearch', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleSearch')
        self.assert_count_equal('article', 3)
        self.assert_json_equal('', 'article/@0/reference', "ABC2")
        self.assert_json_equal('', 'article/@1/reference', "ABC3")
        self.assert_json_equal('', 'article/@2/reference', "ABC4")
        self.assert_json_equal('', 'article/@0/categories', "cat 2")
        self.assert_json_equal('', 'article/@1/categories', "cat 1{[br/]}cat 2{[br/]}cat 3")
        self.assert_json_equal('', 'article/@2/categories', "cat 3")

    def test_article_filter(self):
        default_categories()
        default_articles(with_storage=True)
        default_customize()
        initial_thirds_fr()

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 4)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 5)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1, 'stockable': 0}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 2)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1, 'stockable': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 2)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1, 'stockable': 2}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 1)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1, 'cat_filter': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 3)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1, 'cat_filter': '2;3'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 2)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1, 'cat_filter': '1;2;3'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 1)

    def test_article_import1(self):
        initial_thirds_fr()
        default_categories()
        default_accountPosting()
        csv_content = """'num','comment','prix','unité','compte','stock?','categorie','fournisseur','ref'
'A123','article N°1','','Kg','code1','stockable','cat 2','Dalton Avrel','POIYT'
'B234','article N°2','23,56','L','code1','stockable','cat 3','',''
'C345','article N°3','45.74','','code2','non stockable','cat 1','Dalton Avrel','MLKJH'
'D456','article N°4','56,89','m','code1','stockable & non vendable','','Maximum','987654'
'A123','article N°1','13.57','Kg','code1','stockable','cat 3','',''
'A123','article N°1','16,95','Kg','code1','stockable','','Maximum','654321'
"""

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 0)

        self.factory.xfer = ArticleImport()
        self.calljson('/diacamma.invoice/articleImport', {'step': 1, 'modelname': 'invoice.Article', 'quotechar': "'",
                                                          'delimiter': ',', 'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'csvcontent': StringIO(csv_content)}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleImport')
        self.assert_count_equal('', 6 + 12)
        self.assert_select_equal('fld_reference', 9)  # nb=9
        self.assert_select_equal('fld_categories', 10)  # nb=10
        self.assert_count_equal('CSV', 6)
        self.assert_count_equal('#CSV/actions', 0)
        self.assertEqual(len(self.json_actions), 3)
        self.assert_action_equal(self.json_actions[0], (six.text_type('Retour'), 'images/left.png', 'diacamma.invoice', 'articleImport', 0, 2, 1, {'step': '0'}))
        self.assert_action_equal(self.json_actions[1], (six.text_type('Ok'), 'images/ok.png', 'diacamma.invoice', 'articleImport', 0, 2, 1, {'step': '2'}))
        self.assertEqual(len(self.json_context), 8)

        self.factory.xfer = ArticleImport()
        self.calljson('/diacamma.invoice/articleImport', {'step': 2, 'modelname': 'invoice.Article', 'quotechar': "'", 'delimiter': ',',
                                                          'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'csvcontent0': csv_content,
                                                          "fld_reference": "num", "fld_designation": "comment", "fld_price": "prix",
                                                          "fld_unit": "unité", "fld_isdisabled": "", "fld_accountposting": "compte",
                                                          "fld_vat": "", "fld_stockable": "stock?", 'fld_categories': 'categorie',
                                                          'fld_provider.third.contact': 'fournisseur', 'fld_provider.reference': 'ref', }, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleImport')
        self.assert_count_equal('', 4)
        self.assert_count_equal('CSV', 6)
        self.assert_count_equal('#CSV/actions', 0)
        self.assertEqual(len(self.json_actions), 3)
        self.assert_action_equal(self.json_actions[1], (six.text_type('Ok'), 'images/ok.png', 'diacamma.invoice', 'articleImport', 0, 2, 1, {'step': '3'}))

        self.factory.xfer = ArticleImport()
        self.calljson('/diacamma.invoice/articleImport', {'step': 3, 'modelname': 'invoice.Article', 'quotechar': "'", 'delimiter': ',',
                                                          'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'csvcontent0': csv_content,
                                                          "fld_reference": "num", "fld_designation": "comment", "fld_price": "prix",
                                                          "fld_unit": "unité", "fld_isdisabled": "", "fld_accountposting": "compte",
                                                          "fld_vat": "", "fld_stockable": "stock?", 'fld_categories': 'categorie',
                                                          'fld_provider.third.contact': 'fournisseur', 'fld_provider.reference': 'ref', }, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleImport')
        self.assert_count_equal('', 2)
        self.assert_json_equal('LABELFORM', 'result', "{[center]}{[i]}4 éléments ont été importés{[/i]}{[/center]}")
        self.assertEqual(len(self.json_actions), 1)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 4)
        self.assert_json_equal('', 'article/@0/reference', "A123")
        self.assert_json_equal('', 'article/@0/designation', "article N°1")
        self.assert_json_equal('', 'article/@0/price_txt', "16.95€")
        self.assert_json_equal('', 'article/@0/unit', 'Kg')
        self.assert_json_equal('', 'article/@0/isdisabled', "0")
        self.assert_json_equal('', 'article/@0/accountposting', "code1")
        self.assert_json_equal('', 'article/@0/stockable', "stockable")
        self.assert_json_equal('', 'article/@0/categories', "cat 2{[br/]}cat 3")

        self.assert_json_equal('', 'article/@1/reference', "B234")
        self.assert_json_equal('', 'article/@1/designation', "article N°2")
        self.assert_json_equal('', 'article/@1/price_txt', "23.56€")
        self.assert_json_equal('', 'article/@1/unit', 'L')
        self.assert_json_equal('', 'article/@1/isdisabled', "0")
        self.assert_json_equal('', 'article/@1/accountposting', "code1")
        self.assert_json_equal('', 'article/@1/stockable', "stockable")
        self.assert_json_equal('', 'article/@1/categories', "cat 3")

        self.assert_json_equal('', 'article/@2/reference', "C345")
        self.assert_json_equal('', 'article/@2/designation', "article N°3")
        self.assert_json_equal('', 'article/@2/price_txt', "45.74€")
        self.assert_json_equal('', 'article/@2/unit', '')
        self.assert_json_equal('', 'article/@2/isdisabled', "0")
        self.assert_json_equal('', 'article/@2/accountposting', "code2")
        self.assert_json_equal('', 'article/@2/stockable', "non stockable")
        self.assert_json_equal('', 'article/@2/categories', "cat 1")

        self.assert_json_equal('', 'article/@3/reference', "D456")
        self.assert_json_equal('', 'article/@3/designation', "article N°4")
        self.assert_json_equal('', 'article/@3/price_txt', "56.89€")
        self.assert_json_equal('', 'article/@3/unit', 'm')
        self.assert_json_equal('', 'article/@3/isdisabled', "0")
        self.assert_json_equal('', 'article/@3/accountposting', "code1")
        self.assert_json_equal('', 'article/@3/stockable', "stockable & non vendable")
        self.assert_json_equal('', 'article/@3/categories', '')

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 17)
        self.assert_json_equal('LABELFORM', 'reference', "A123")
        self.assert_json_equal('LABELFORM', 'categories', "cat 2{[br/]}cat 3")
        self.assert_count_equal('provider', 2)
        self.assert_json_equal('', 'provider/@0/third', "Dalton Avrel")
        self.assert_json_equal('', 'provider/@0/reference', "POIYT")
        self.assert_json_equal('', 'provider/@1/third', "Maximum")
        self.assert_json_equal('', 'provider/@1/reference', "654321")

        self.factory.xfer = ArticleImport()
        self.calljson('/diacamma.invoice/articleImport', {'step': 3, 'modelname': 'invoice.Article', 'quotechar': "'", 'delimiter': ',',
                                                          'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'csvcontent0': csv_content,
                                                          "fld_reference": "num", "fld_designation": "comment", "fld_price": "prix",
                                                          "fld_unit": "unité", "fld_isdisabled": "", "fld_accountposting": "compte",
                                                          "fld_vat": "", "fld_stockable": "stock?", 'fld_categories': 'categorie',
                                                          'fld_provider.third.contact': 'fournisseur', 'fld_provider.reference': 'ref', }, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleImport')
        self.assert_count_equal('', 2)
        self.assert_json_equal('LABELFORM', 'result', "{[center]}{[i]}4 éléments ont été importés{[/i]}{[/center]}")
        self.assertEqual(len(self.json_actions), 1)

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 17)
        self.assert_json_equal('LABELFORM', 'reference', "A123")
        self.assert_json_equal('LABELFORM', 'categories', "cat 2{[br/]}cat 3")
        self.assert_count_equal('provider', 2)
        self.assert_json_equal('', 'provider/@0/third', "Dalton Avrel")
        self.assert_json_equal('', 'provider/@0/reference', "POIYT")
        self.assert_json_equal('', 'provider/@1/third', "Maximum")
        self.assert_json_equal('', 'provider/@1/reference', "654321")

    def test_article_import2(self):
        initial_thirds_fr()
        default_categories()
        default_accountPosting()
        csv_content = """'num','comment','prix','unité','compte','stock?','categorie','fournisseur','ref'
'A123','article N°1','ssdqs','Kg','code1','stockable','cat 2','Avrel','POIYT'
'B234','article N°2','23.56','L','code1','stockable','cat 3','',''
'C345','article N°3','45.74','','code2','non stockable','cat 1','Avrel','MLKJH'
'D456','article N°4','56.89','m','code1','stockable & non vendable','','Maximum','987654'
'A123','article N°1','13.57','Kg','code1','stockable','cat 3','',''
'A123','article N°1','16.95','Kg','code1','stockable','','Maximum','654321'
"""

        self.factory.xfer = ArticleImport()
        self.calljson('/diacamma.invoice/articleImport', {'step': 3, 'modelname': 'invoice.Article', 'quotechar': "'", 'delimiter': ',',
                                                          'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'csvcontent0': csv_content,
                                                          "fld_reference": "num", "fld_designation": "comment", "fld_price": "prix",
                                                          "fld_unit": "unité", "fld_isdisabled": "", "fld_accountposting": "compte",
                                                          "fld_vat": "", "fld_stockable": "stock?", 'fld_categories': '',
                                                          'fld_provider.third.contact': '', 'fld_provider.reference': '', }, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleImport')
        self.assert_count_equal('', 2)
        self.assert_json_equal('LABELFORM', 'result', "{[center]}{[i]}4 éléments ont été importés{[/i]}{[/center]}")
        self.assertEqual(len(self.json_actions), 1)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 4)
        self.assert_json_equal('', 'article/@0/reference', "A123")
        self.assert_json_equal('', 'article/@0/designation', "article N°1")
        self.assert_json_equal('', 'article/@0/price_txt', "16.95€")
        self.assert_json_equal('', 'article/@0/unit', 'Kg')
        self.assert_json_equal('', 'article/@0/isdisabled', "0")
        self.assert_json_equal('', 'article/@0/accountposting', "code1")
        self.assert_json_equal('', 'article/@0/stockable', "stockable")
        self.assert_json_equal('', 'article/@0/categories', '')

        self.assert_json_equal('', 'article/@1/reference', "B234")
        self.assert_json_equal('', 'article/@1/designation', "article N°2")
        self.assert_json_equal('', 'article/@1/price_txt', "23.56€")
        self.assert_json_equal('', 'article/@1/unit', 'L')
        self.assert_json_equal('', 'article/@1/isdisabled', "0")
        self.assert_json_equal('', 'article/@1/accountposting', "code1")
        self.assert_json_equal('', 'article/@1/stockable', "stockable")
        self.assert_json_equal('', 'article/@1/categories', '')

        self.assert_json_equal('', 'article/@2/reference', "C345")
        self.assert_json_equal('', 'article/@2/designation', "article N°3")
        self.assert_json_equal('', 'article/@2/price_txt', "45.74€")
        self.assert_json_equal('', 'article/@2/unit', '')
        self.assert_json_equal('', 'article/@2/isdisabled', "0")
        self.assert_json_equal('', 'article/@2/accountposting', "code2")
        self.assert_json_equal('', 'article/@2/stockable', "non stockable")
        self.assert_json_equal('', 'article/@2/categories', '')

        self.assert_json_equal('', 'article/@3/reference', "D456")
        self.assert_json_equal('', 'article/@3/designation', "article N°4")
        self.assert_json_equal('', 'article/@3/price_txt', "56.89€")
        self.assert_json_equal('', 'article/@3/unit', 'm')
        self.assert_json_equal('', 'article/@3/isdisabled', "0")
        self.assert_json_equal('', 'article/@3/accountposting', "code1")
        self.assert_json_equal('', 'article/@3/stockable', "stockable & non vendable")
        self.assert_json_equal('', 'article/@3/categories', '')

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 17)
        self.assert_json_equal('LABELFORM', 'reference', "A123")
        self.assert_json_equal('LABELFORM', 'categories', '')
        self.assert_count_equal('provider', 0)

    def test_article_import3(self):
        default_customize()
        default_accountPosting()
        csv_content = """'num','comment','prix','unité','compte','stock?','categorie','fournisseur','ref','color','size'
'A123','article N°1','12.45','Kg','code1','stockable','cat 2','Avrel','POIYT','---','10'
'B234','article N°2','23.56','L','code1','stockable','cat 3','','','noir','25'
'C345','article N°3','45.74','','code2','non stockable','cat 1','Avrel','MLKJH','rouge','75'
'D456','article N°4','56.89','m','code1','stockable & non vendable','','Maximum','987654','blanc','1'
'A123','article N°1','13.57','Kg','code1','stockable','cat 3','','','bleu','10'
'A123','article N°1','16.95','Kg','code1','stockable','','Maximum','654321','bleu','15'
"""

        self.factory.xfer = ArticleImport()
        self.calljson('/diacamma.invoice/articleImport', {'step': 3, 'modelname': 'invoice.Article', 'quotechar': "'", 'delimiter': ',',
                                                          'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'csvcontent0': csv_content,
                                                          "fld_reference": "num", "fld_designation": "comment", "fld_price": "prix",
                                                          "fld_unit": "unité", "fld_isdisabled": "", "fld_accountposting": "compte",
                                                          "fld_vat": "", "fld_stockable": "stock?",
                                                          "fld_custom_1": "color", "fld_custom_2": "size", }, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleImport')
        self.assert_count_equal('', 2)
        self.assert_json_equal('LABELFORM', 'result', "{[center]}{[i]}4 éléments ont été importés{[/i]}{[/center]}")
        self.assertEqual(len(self.json_actions), 1)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 4)
        self.assert_json_equal('', 'article/@0/reference', "A123")
        self.assert_json_equal('', 'article/@0/designation', "article N°1")
        self.assert_json_equal('', 'article/@0/price_txt', "16.95€")
        self.assert_json_equal('', 'article/@0/unit', 'Kg')
        self.assert_json_equal('', 'article/@0/isdisabled', "0")
        self.assert_json_equal('', 'article/@0/accountposting', "code1")
        self.assert_json_equal('', 'article/@0/stockable', "stockable")

        self.assert_json_equal('', 'article/@1/reference', "B234")
        self.assert_json_equal('', 'article/@1/designation', "article N°2")
        self.assert_json_equal('', 'article/@1/price_txt', "23.56€")
        self.assert_json_equal('', 'article/@1/unit', 'L')
        self.assert_json_equal('', 'article/@1/isdisabled', "0")
        self.assert_json_equal('', 'article/@1/accountposting', "code1")
        self.assert_json_equal('', 'article/@1/stockable', "stockable")

        self.assert_json_equal('', 'article/@2/reference', "C345")
        self.assert_json_equal('', 'article/@2/designation', "article N°3")
        self.assert_json_equal('', 'article/@2/price_txt', "45.74€")
        self.assert_json_equal('', 'article/@2/unit', '')
        self.assert_json_equal('', 'article/@2/isdisabled', "0")
        self.assert_json_equal('', 'article/@2/accountposting', "code2")
        self.assert_json_equal('', 'article/@2/stockable', "non stockable")

        self.assert_json_equal('', 'article/@3/reference', "D456")
        self.assert_json_equal('', 'article/@3/designation', "article N°4")
        self.assert_json_equal('', 'article/@3/price_txt', "56.89€")
        self.assert_json_equal('', 'article/@3/unit', 'm')
        self.assert_json_equal('', 'article/@3/isdisabled', "0")
        self.assert_json_equal('', 'article/@3/accountposting', "code1")
        self.assert_json_equal('', 'article/@3/stockable', "stockable & non vendable")

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 16)
        self.assert_json_equal('LABELFORM', 'reference', "A123")
        self.assert_json_equal('LABELFORM', 'custom_1', "bleu")
        self.assert_json_equal('LABELFORM', 'custom_2', "15")

    def test_article_same_name(self):
        default_categories()
        default_articles()

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 4)
        self.assert_json_equal('', 'article/@0/reference', "ABC1")
        self.assert_json_equal('', 'article/@0/id', 1)
        self.assert_json_equal('', 'article/@1/reference', "ABC2")
        self.assert_json_equal('', 'article/@2/reference', "ABC3")
        self.assert_json_equal('', 'article/@3/reference', "ABC4")

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleAddModify')
        self.assert_count_equal('', 13)
        self.assert_json_equal('EDIT', 'reference', 'ABC1')

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify',
                      {'article': '1', 'reference': 'ABC1', 'designation': 'Article 01', 'price': '12.34', 'accountposting': 1, 'stockable': '1', 'qtyDecimal': '3', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'articleAddModify')

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify',
                      {'article': '1', 'reference': 'ABC2', 'designation': 'Article 02', 'price': '12.34', 'accountposting': 1, 'stockable': '1', 'qtyDecimal': '3', 'SAVE': 'YES'}, False)
        self.assert_observer('core.exception', 'diacamma.invoice', 'articleAddModify')

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify',
                      {'reference': 'ABC1', 'designation': 'Article 01', 'price': '12.34', 'accountposting': 1, 'stockable': '1', 'qtyDecimal': '3', 'SAVE': 'YES'}, False)
        self.assert_observer('core.exception', 'diacamma.invoice', 'articleAddModify')
