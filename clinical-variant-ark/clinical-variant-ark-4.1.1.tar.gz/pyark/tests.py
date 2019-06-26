import logging
import os
import random
import uuid
from unittest import TestCase

import pandas as pd
from mock import patch
from protocols.protocol_7_2.cva import Assembly, PedigreeInjectRD, CancerParticipantInject, \
    EvidenceEntryAndVariants, EvidenceEntry, Property, EvidenceSource, Actions, Therapy, DrugResponse, GenomicFeature, \
    FeatureTypes, VariantCoordinates, VariantsCoordinates, Penetrance, DrugResponseClassification, Transaction, \
    TransactionStatus
from protocols.protocol_7_2.reports import Program
from protocols.util import dependency_manager
from protocols.util.factories.avro_factory import GenericFactoryAvro
from requests import ConnectionError

from pyark.cva_client import CvaClient
from pyark.errors import CvaClientError, CvaServerError
from pyark.models.wrappers import ReportEventEntryWrapper, VariantWrapper


class TestPyArk (TestCase):
    # credentials
    CVA_URL_BASE = os.getenv("CVA_URL")
    GEL_USER = os.getenv("CVA_USER")
    GEL_PASSWORD = os.getenv("CVA_PASSWORD")

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG)
        if cls.GEL_PASSWORD is None:
            cls.GEL_PASSWORD = ""
        if not cls.CVA_URL_BASE or not cls.GEL_USER:
            logging.error("Please set the configuration environment variables: CVA_URL, GEL_USER, GEL_PASSWORD")
            raise ValueError("Missing config")
        logging.info("Running tests against {}".format(cls.CVA_URL_BASE))
        cls.cva = CvaClient(cls.CVA_URL_BASE, user=cls.GEL_USER, password=cls.GEL_PASSWORD, retries=10)
        cls.report_events = cls.cva.report_events()
        cls.entities = cls.cva.entities()
        cls.cases = cls.cva.cases()
        cls.pedigrees = cls.cva.pedigrees()
        cls.variants = cls.cva.variants()
        cls.data_intake = cls.cva.data_intake()
        # fetch 50 cases to run tests on
        cls.random_cases = list(cls.cases.get_cases(
            max_results=50, program=Program.rare_disease, assembly=Assembly.GRCh38,
            filter='countInterpretationServices.exomiser gt 0 and countTiered gt 100',
            hasClinicalData=True))

    def _get_random_case_id_and_version(self):
        case = self._get_random_case()
        return case['identifier'], case['version']

    def _get_random_case(self):
        return random.choice(self.random_cases)

    def _get_random_panel(self):
        return random.choice(self._get_random_case()['reportEventsAnalysisPanels'])['panelName']

    def _get_random_gene(self):
        return random.choice(self._get_random_case()['genes'])

    def _get_random_variant_ids(self, n=1):
        return random.sample(self._get_random_case()['allVariants'], n)


class TestReportEvents(TestPyArk):

    def test_get_report_events(self):
        random_case = self._get_random_case()
        page_size = 2
        maximum = 5
        report_events_iterator = self.report_events.get_report_events(
            limit=page_size, max_results=maximum, caseId=random_case['identifier'], caseVersion=random_case['version'])
        re_count = 0
        for re in report_events_iterator:
            self.assertIsNotNone(re)
            self.assertTrue(type(re) == ReportEventEntryWrapper)
            re_count += 1
        self.assertEqual(re_count, maximum)

    def test_count_report_events(self):
        random_case = self._get_random_case()
        count = self.report_events.count(caseId=random_case['identifier'], caseVersion=random_case['version'])
        self.assertIsInstance(count, int)

    def test_variant_summary_by_ids(self):
        variant_ids = self._get_random_variant_ids(n=10)
        results = self.report_events.get_variant_summary_by_ids(variant_ids=variant_ids)
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) == 10)
        for r in results:
            self.assertTrue(r['countCases'] > 0)
            self.assertTrue(r['countCasesClassifiedByAcmg'] is not None)
            self.assertTrue(r['variantId'] in variant_ids)
            self.assertTrue(r['variantCoordinatesGRCh38'] is not None)
            self.assertTrue(r.get('countCasesRareDisease', None) is None)

        results2 = self.report_events.get_variant_summary_by_ids(variant_ids=variant_ids, minimal=True)
        for r in results2:
            self.assertTrue(r['countCases'] > 0)
            self.assertTrue(r['countCasesClassifiedByAcmg'] is not None)
            self.assertTrue(r['variantId'] in variant_ids)
            self.assertTrue(r['variantCoordinatesGRCh38'] is not None)
            self.assertTrue(r.get('countCasesRareDisease', None) is None)

        results3 = self.report_events.get_variant_summary_by_ids(variant_ids=variant_ids, minimal=False)
        for r in results3:
            self.assertTrue(r['countCases'] > 0)
            self.assertTrue(r['countCasesClassifiedByAcmg'] is not None)
            self.assertTrue(r['variantId'] in variant_ids)
            self.assertTrue(r['variantCoordinatesGRCh38'] is not None)
            self.assertTrue(r['countCasesRareDisease'] > 0)

    def test_variant_summary_by_coordinates(self):
        variant_ids = self._get_random_variant_ids(n=10)
        results_by_ids = self.report_events.get_variant_summary_by_ids(variant_ids=variant_ids)
        variant_coordinates = [c.toJsonDict() for c in self.variants.variant_ids_to_coordinates(variant_ids)]
        results_by_coordinates = self.report_events.get_variant_summary_by_coordinates(
            variant_coordinates=variant_coordinates)
        variant_ids_1 = set([r['variantId'] for r in results_by_ids])
        variant_ids_2 = set([r['variantId'] for r in results_by_coordinates])
        self.assertEqual(len(variant_ids_1), len(variant_ids_1.intersection(variant_ids_2)))


class TestCases(TestPyArk):

    def test_get_case(self):

        case_id, case_version = self._get_random_case_id_and_version()

        # gets case
        result = self.cases.get_case(case_id, case_version)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))

        # gets pedigree
        result = self.cases.get_case(case_id, case_version, as_data_frame=True)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, pd.DataFrame))

    def test_get_cases_summary(self):

        summary = self.cases.get_summary(program=Program.rare_disease)
        self.assertIsNotNone(summary)
        self.assertIsInstance(summary, dict)

        summary = self.cases.get_summary(program=Program.rare_disease, as_data_frame=True)
        self.assertIsNotNone(summary)
        self.assertIsInstance(summary, pd.DataFrame)

    def test_get_cases_summary_with_many_queries(self):

        queries = [{'assembly': a} for a in [Assembly.GRCh37, Assembly.GRCh38]]
        summary = self.cases.get_summary(params_list=queries)
        self.assertIsNotNone(summary)
        self.assertIsInstance(summary, list)

        summary = self.cases.get_summary(params_list=queries, as_data_frame=True)
        self.assertIsNotNone(summary)
        self.assertIsInstance(summary, pd.DataFrame)

        try:
            self.cases.get_summary(params_list=queries, program=Program.rare_disease)
            self.assertTrue(False)
        except:
            self.assertTrue(True)

    def test_get_cases(self):

        page_size = 2
        maximum = 5
        cases_iterator = self.cases.get_cases(as_data_frame=False, limit=page_size, max_results=maximum)
        cases_count = 0
        for c in cases_iterator:
            self.assertIsNotNone(c)
            self.assertIsInstance(c, dict)
            cases_count += 1
        self.assertEqual(cases_count, maximum)

    def test_get_cases_as_dataframes(self):

        page_size = 2
        maximum = 5
        cases_iterator = self.cases.get_cases(as_data_frame=True, limit=page_size, max_results=maximum)
        cases_count = 0
        for cases_data_frame in cases_iterator:
            self.assertIsNotNone(cases_data_frame)
            self.assertIsInstance(cases_data_frame, pd.DataFrame)
            cases_count += cases_data_frame.shape[0]
        self.assertEqual(cases_count, maximum)

    def test_get_cases_ids(self):

        page_size = 2
        maximum = 5
        cases_iterator = self.cases.get_cases_ids(as_data_frame=False, limit=page_size, max_results=maximum)
        cases_count = 0
        for c in cases_iterator:
            self.assertIsNotNone(c)
            self.assertIsInstance(c, str)
            cases_count += 1
        self.assertEqual(cases_count, maximum)

    def test_count_cases(self):

        count = self.cases.count()
        self.assertIsInstance(count, int)

    def test_get_similar_cases_by_case(self):

        case_id, case_version = self._get_random_case_id_and_version()

        results = self.cases.get_similar_cases_by_case(case_id=case_id, case_version=case_version)
        if results:
            self.assertIsInstance(results, list)

        results = self.cases.get_similar_cases_by_case(case_id=case_id, case_version=case_version, limit=5)
        if results:
            self.assertIsInstance(results, list)
            self.assertTrue(len(results) <= 5)

    def test_get_similar_cases_by_phenotypes(self):

        phenotypes = ["HP:0000006", "HP:0003186", "HP:0002365"]

        results = self.cases.get_similar_cases_by_phenotypes(phenotypes=phenotypes)
        self.assertIsNotNone(results)
        self.assertIsInstance(results, list)

        results = self.cases.get_similar_cases_by_phenotypes(phenotypes=phenotypes, limit=5)
        self.assertIsNotNone(results)
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) == 5)


class TestVariants(TestPyArk):

    def test_count_variants(self):

        count = self.variants.count()
        self.assertIsInstance(count, int)

    def test_get_variants(self):
        page_size = 2
        maximum = 5
        variants_iterator = self.variants.get_variants(
            limit=page_size, max_results=maximum, genes=[self._get_random_gene()])
        re_count = 0
        for v in variants_iterator:
            self.assertIsNotNone(v)
            self.assertTrue(type(v) == VariantWrapper)
            re_count += 1
        self.assertEqual(re_count, maximum)

    def test_get_variant_by_id(self):

        variant = self.variants.get_variant_by_id(identifier=self._get_random_variant_ids()[0])
        self.assertIsNotNone(variant)
        self.assertIsInstance(variant, VariantWrapper)

    def test_unexisting_variant_by_id(self):
        with self.assertRaises(CvaClientError):
            self.variants.get_variant_by_id(identifier='whatever')

    def test_get_variants_by_id(self):

        identifiers = self._get_random_variant_ids()
        variants = self.variants.get_variants_by_id(identifiers=identifiers)
        self.assertIsNotNone(variants)
        self.assertIsInstance(variants, list)
        for v in variants:
            self.assertIsInstance(v, VariantWrapper)
        self.assertTrue(len(variants) == len(identifiers))

    def test_dont_get_variants_by_id(self):
        non_existing_identifiers = ['whatever', 'this', 'that']
        self.assertRaises(CvaClientError,
                          lambda: self.variants.get_variants_by_id(identifiers=non_existing_identifiers))

    def test_variant_coordinates_to_ids(self):
        expected = self._get_random_variant_ids(n=10)
        variant_coordinates = [c.toJsonDict() for c in self.variants.variant_ids_to_coordinates(expected)]
        observed = self.variants.variant_coordinates_to_ids(variant_coordinates=variant_coordinates)
        self.assertTrue(len(observed) == len(set(observed).intersection(set(expected))))


class TestOthers(TestPyArk):

    def test_get_pedigree(self):

        case_id, case_version = self._get_random_case_id_and_version()

        # gets pedigree
        result = self.pedigrees.get_pedigree(case_id, case_version)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))

        # gets pedigree
        result = self.pedigrees.get_pedigree(case_id, case_version, as_data_frame=True)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, pd.DataFrame))

    def test_get_all_panels(self):
        panels = self.entities.get_all_panels()
        self.assertIsNotNone(panels)
        self.assertIsInstance(panels, pd.Series)

    def test_get_similarity_matrix(self):

        matrix = self.cases.get_phenosim_matrix(program=Program.rare_disease, specificDiseases='cakut')
        self.assertIsNotNone(matrix)
        self.assertIsInstance(matrix, list)

        matrix = self.cases.get_phenosim_matrix(program=Program.rare_disease, specificDiseases='cakut',
                                                   as_data_frame=True)
        self.assertIsNotNone(matrix)
        self.assertIsInstance(matrix, pd.DataFrame)

    def test_get_panel_summary(self):

        panels = self.entities.get_panels_summary(program=Program.rare_disease)
        self.assertIsNotNone(panels)
        self.assertIsInstance(panels, list)

        panels = self.entities.get_panels_summary(program=Program.cancer, as_data_frame=True)
        self.assertIsNotNone(panels)
        self.assertIsInstance(panels, pd.DataFrame)

    def test_get_disorder_summary(self):

        disorders = self.entities.get_disorders_summary(program=Program.rare_disease)
        self.assertIsNotNone(disorders)
        self.assertIsInstance(disorders, list)

        disorders = self.entities.get_disorders_summary(program=Program.cancer, as_data_frame=True)
        self.assertIsNotNone(disorders)
        self.assertIsInstance(disorders, pd.DataFrame)

    def test_get_gene_summary(self):

        genes = self.entities.get_genes_summary(program=Program.rare_disease)
        self.assertIsNotNone(genes)
        self.assertIsInstance(genes, list)

        genes = self.entities.get_genes_summary(program=Program.cancer, as_data_frame=True)
        self.assertIsNotNone(genes)
        self.assertIsInstance(genes, pd.DataFrame)

    def test_get_phenotypes_summary(self):

        phenotypes = self.entities.get_phenotypes(program=Program.rare_disease)
        self.assertIsNotNone(phenotypes)
        self.assertIsInstance(phenotypes, list)

        phenotypes = self.entities.get_phenotypes(program=Program.cancer, as_data_frame=True)
        self.assertIsNotNone(phenotypes)
        self.assertIsInstance(phenotypes, pd.DataFrame)

    # def test_get_shared_variants_cases(self):
    #     case_id, case_version = self._get_random_case_id_and_version()
    #
    #     results1 = self.cases.get_shared_variants_cases_by_case(
    #         case_id=case_id, case_version=case_version, report_event_type=ReportEventType.genomics_england_tiering)
    #
    #     results2 = self.cases.get_shared_variants_cases_by_case(
    #         case_id=case_id, case_version=case_version, report_event_type=ReportEventType.reported)
    #
    #     results3 = self.cases.get_shared_variants_cases_by_case(
    #         case_id=case_id, case_version=case_version, report_event_type=ReportEventType.questionnaire)
    #
    #     non_null = (r for r in (results1, results2, results3) if r)
    #     self.assertIsNotNone([s for r in non_null for s in r])

    # def test_get_shared_gene_cases(self):
    #     case_id, case_version = self._get_random_case_id_and_version()
    #
    #     results = self.cases.get_shared_genes_cases_by_case(
    #         case_id=case_id, case_version=case_version, report_event_type=ReportEventType.genomics_england_tiering)
    #     self.assertIsNotNone(results)
    #     self.assertIsInstance(results, list)
    #
    #     results = self.cases.get_shared_genes_cases_by_case(
    #         case_id=case_id, case_version=case_version, report_event_type=ReportEventType.reported)
    #     self.assertIsNotNone(results)
    #     self.assertIsInstance(results, list)
    #
    #     results = self.cases.get_shared_genes_cases_by_case(
    #         case_id=case_id, case_version=case_version, report_event_type=ReportEventType.questionnaire)
    #     # NOTE: there are no values
    #     # self.assertIsNotNone(results)
    #     # self.assertIsInstance(results, list)

    def test_get_shared_variants_counts(self):
        case = self._get_random_case()
        all_variants = case['allVariants']
        results = self.cases.get_shared_variants_counts(all_variants)
        for r in results:
            self.assertTrue(r['variantId'] in all_variants)
            self.assertTrue(r['countCases'] >= 1)

    def test_post_pedigree(self):
        transaction = self._test_post(PedigreeInjectRD, self.data_intake.post_pedigree)
        self.assertTrue(isinstance(transaction, Transaction))
        self.assertTrue(transaction.id is not None)
        self.assertTrue(transaction.status == TransactionStatus.PENDING)
        self.assertTrue(transaction.compressedData is None)

    def test_post_participant(self):
        transaction = self._test_post(CancerParticipantInject, self.data_intake.post_participant)
        self.assertTrue(isinstance(transaction, Transaction))
        self.assertTrue(transaction.id is not None)
        self.assertTrue(transaction.status == TransactionStatus.PENDING)
        self.assertTrue(transaction.compressedData is None)

    def test_get_transaction_fails_if_no_results(self):
        # NOTE: this will work when backend returns 404 on this one
        client = self.cva.transactions()
        self.assertRaises(
            CvaClientError,
            lambda: client.get_transaction("notreal")
        )

    def test_errors_if_cva_down(self):
        self.assertRaises(
            ConnectionError,
            lambda: CvaClient("https://nowhere.invalid", user='u', password='p', retries=2).entities().get_all_panels()
        )

    @patch('requests.sessions.Session.get')
    @patch('requests.sessions.Session.post')
    def test_errors_if_4xx(self, post, get):
        self._mock_panels_to_return(get, post, 400)
        self.assertRaises(
            CvaClientError,
            lambda: CvaClient("https://nowhere.invalid", user='u', password='p').entities().get_all_panels()
        )

    @patch('requests.sessions.Session.get')
    @patch('requests.sessions.Session.post')
    def test_errors_if_5xx(self, post, get):
        self._mock_panels_to_return(get, post, 500)
        self.assertRaises(
            CvaServerError,
            lambda: CvaClient("https://nowhere.invalid", user='u', password='p').entities().get_all_panels()
        )

    @patch('requests.sessions.Session.get')
    @patch('requests.sessions.Session.post')
    def test_returns_empty_if_no_results(self, post, get):
        self._mock_panels_to_return(get, post, 200)
        self.assertEqual(0,
                         CvaClient("https://nowhere.invalid", user='u', password='p').entities().get_all_panels().size)

    def test_gets_evidence(self):
        model = create_example_evidence()
        model.evidenceEntry.source.name = str(uuid.uuid1())
        model.evidenceEntry.source.version = str(uuid.uuid1())

        self.cva.evidences().post_evidences(model)

        evidences = self.cva.evidences().get_evidences(
            model.evidenceEntry.source.name,
            version=model.evidenceEntry.source.version
        )
        results = list(evidences)
        self.assertTrue(results, "expected some evidence")

        for item in results:
            self.assertEquals(EvidenceEntryAndVariants, type(item))
            # test random field that has no normalisation against it.
            self.assertEquals(item.evidenceEntry.ethnicity, model.evidenceEntry.ethnicity)

    def test_deleting_case(self):
        transaction = self._test_post(CancerParticipantInject, self.data_intake.post_participant)
        metadata = transaction.transactionDetails.metadata
        caseId = metadata.caseId
        caseVersion = metadata.caseVersion

        transaction = self.cases.delete(caseId, caseVersion)
        self.assertTrue(isinstance(transaction, Transaction))
        self.assertTrue(transaction.id is not None)
        self.assertTrue(transaction.status == TransactionStatus.PENDING)
        self.assertTrue(transaction.compressedData is None)

    @staticmethod
    def _mock_panels_to_return(get, post, status_code):
        auth_response = MockResponse(status_code, {'response': [{'result': [{'token': 'xyz'}]}]})
        post.return_value = auth_response
        response = MockResponse(status_code, {})
        get.return_value = response

    def _test_post(self, clazz, post_function):
        model = GenericFactoryAvro.get_factory_avro(
            clazz=clazz,
            version=dependency_manager.VERSION_70,
            fill_nullables=False,
        ).create()

        response = post_function(model)
        # this is stronger than it looks because post checks for errors
        self.assertIsNotNone(response)
        return response


class MockResponse:
    def __init__(self, status_code, json_dict):
        self.status_code = status_code
        self.json_dict = json_dict
        self.content = str(json_dict)
        self.text = str(json_dict)
        self.headers = {}

    @staticmethod
    def get(key, default):
        return None

    def json(self):
        return self.json_dict


def create_example_evidence():
    coordinates = coordinate()
    marker_coordinates = marker_coordinate()

    genomic_feature = GenomicFeature(
        featureType=FeatureTypes.transcript,
        ensemblId="ENST00000370192.7"
    )

    actions = action()

    source = EvidenceSource(
        date="today",
        name="genomics-england-phamacogenomics",
        version="v1.0"
    )

    pharmgkb_id = Property(
        name="PharmGKB",
        value="PA166153760"
    )

    return EvidenceEntryAndVariants(
        evidenceEntry=EvidenceEntry(
            source=source,
            ethnicity='Z',
            genomicFeatures=[genomic_feature],
            heritable_trait=[],
            penetrance=Penetrance.complete,
            additionalProperties=[pharmgkb_id]
        ),
        variantsCoordinates=VariantsCoordinates(variants=[coordinates]),
        markersCoordinates=VariantsCoordinates(variants=[marker_coordinates]),
        actions=actions
    )


def action():
    return Actions(
        therapies=[
            Therapy(
                drugResponse=[DrugResponse(
                    TreatmentAgent="the drug",
                    drugResponseClassification=DrugResponseClassification.increased_monitoring
                )],
                variantActionable=True,
                referenceUrl="https://something.com/db.html",
                conditions=[]
            )
        ]
    )


def marker_coordinate():
    marker_coordinates = VariantCoordinates(
        assembly=Assembly.GRCh38, reference='G', alternate='T', chromosome='1', position=99450058
    )
    return marker_coordinates


def coordinate():
    coordinates = VariantCoordinates(
        assembly=Assembly.GRCh38, reference='C', alternate='T', chromosome='1', position=97450058
    )
    return coordinates
