# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import pickle

from numpy import zeros

from assertions import *
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from ibm_ai_openscale.supporting_classes.enums import ProblemType, InputDataType, FeedbackFormat


def vectorize_sequences(sequences, dimension=4000):
    results = zeros((len(sequences), dimension))
    for i, sequence in enumerate(sequences):
        results[i, sequence] = 1.
    return results


class TestAIOpenScaleClient(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    subscription_uid = None
    scoring_url = None
    labels = None
    ai_client = None
    wml_client = None
    binding_uid = None
    subscription = None
    scoring_result = None
    scoring_records = None
    feedback_records = None

    model_path = os.path.join(os.getcwd(), 'artifacts', 'spam-classification', 'spam-classification.h5.tgz')

    @classmethod
    def setUpClass(cls):
        cls.schema = get_schema_name()
        cls.aios_credentials = get_aios_credentials()
        cls.database_credentials = get_database_credentials()

        if "ICP" in get_env():
            cls.ai_client = APIClient4ICP(cls.aios_credentials)
        else:
            cls.ai_client = APIClient(cls.aios_credentials)
            cls.wml_credentials = get_wml_credentials()

        prepare_env(cls.ai_client)

        with open('artifacts/spam-classification/tokenizer.pickle', 'rb') as handle:
            cls.tokenizer = pickle.load(handle)

    def test_01_setup_data_mart(self):
        TestAIOpenScaleClient.ai_client.data_mart.setup(db_credentials=self.database_credentials, schema=self.schema)

    def test_02_data_mart_get_details(self):
        details = TestAIOpenScaleClient.ai_client.data_mart.get_details()
        assert_datamart_details(details=details, schema=self.schema)

    def test_03_bind_wml_instance(self):
        if "ICP" in get_env():
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on ICP", WatsonMachineLearningInstance4ICP())
        else:
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on Cloud",WatsonMachineLearningInstance(self.wml_credentials))

    def test_04_get_wml_client(self):
        binding_uid = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_uids()[0]
        TestAIOpenScaleClient.wml_client = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_native_engine_client(binding_uid)

    def test_05_prepare_deployment(self):
        model_name = "AIOS Keras spam model"
        deployment_name = "AIOS Keras spam deployment"

        print("Storing model ...")

        model_props = {
            self.wml_client.repository.ModelMetaNames.NAME: "{}".format(model_name),
            self.wml_client.repository.ModelMetaNames.FRAMEWORK_NAME: "tensorflow",
            self.wml_client.repository.ModelMetaNames.FRAMEWORK_VERSION: "1.5",
            self.wml_client.repository.ModelMetaNames.RUNTIME_NAME: "python",
            self.wml_client.repository.ModelMetaNames.RUNTIME_VERSION: "3.6",
            self.wml_client.repository.ModelMetaNames.FRAMEWORK_LIBRARIES: [{'name': 'keras', 'version': '2.2.4'}],
        }

        published_model_details = self.wml_client.repository.store_model(model=self.model_path, meta_props=model_props)
        TestAIOpenScaleClient.model_uid = self.wml_client.repository.get_model_uid(published_model_details)

        print("Deploying model...")

        deployment = self.wml_client.deployments.create(artifact_uid=self.model_uid, name=deployment_name, asynchronous=False)
        TestAIOpenScaleClient.deployment_uid = self.wml_client.deployments.get_uid(deployment)

        print("Model id: {}".format(self.model_uid))
        print("Deployment id: {}".format(self.deployment_uid))

    def test_06_subscribe(self):
        # get_details_from_restapi(ai_client=self.ai_client, binding_uid=self.binding_uid)

        subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(
            WatsonMachineLearningAsset(
                source_uid=self.model_uid,
                binding_uid=self.binding_uid,
                problem_type=ProblemType.BINARY_CLASSIFICATION,
                input_data_type=InputDataType.UNSTRUCTURED_TEXT,
                label_column='label'
            )
        )
        TestAIOpenScaleClient.aios_model_uid = subscription.uid

    def test_07_get_subscription(self):
        TestAIOpenScaleClient.subscription = self.ai_client.data_mart.subscriptions.get(self.subscription_uid)
        self.assertIsNotNone(self.subscription)

        subscription_details = self.subscription.get_details()
        print("Subscription details:\n{}".format(subscription_details))

    def test_08_list_deployments(self):
        TestAIOpenScaleClient.subscription.list_deployments()

    def test_09_validate_default_subscription_configuration(self):
        subscription_details = TestAIOpenScaleClient.subscription.get_details()
        assert_monitors_enablement(subscription_details=subscription_details, payload=True, performance=True)

    def test_10_get_payload_logging_details(self):
        payload_logging_details = self.subscription.payload_logging.get_details()
        assert_payload_logging_configuration(payload_logging_details=payload_logging_details)

    def test_11_get_performance_monitor_details(self):
        performance_monitoring_details = self.subscription.performance_monitoring.get_details()
        assert_performance_monitoring_configuration(performance_monitoring_details=performance_monitoring_details)

    def test_12_score(self):
        deployment_details = self.wml_client.deployments.get_details(self.deployment_uid)
        scoring_endpoint = self.wml_client.deployments.get_scoring_url(deployment_details)

        messages = [
            "Door moment let the to door lord soul so with his on and his than its. Gently beak was hauntedtell from fiery to the rapping only all what borrow bust was the we. Lordly metell ember curious to bore entrance linking art heart. Smiling undaunted its. Of is i word out my. Wrought to quoth sat respiterespite rare chamber footfalls bird moment god longer the. If or both whether sat surcease whispered see into said ungainly chamber much. Eyes laden and within. Undaunted hath the the ebony violet more. Core entreating unseen said and was bird. Evilprophet or answer the sad just.</p><p>Lady silence oer no whispered distinctly heart and from out me i usby rare fowl i sad metell.",
            "Pile there of den at relief. But ever on native than other as run or suits was counsel were of sacred a scorching sacred. Atonement stalked from shades longed been honeyed dwelt aye ee of childe are is pride fame day mood he. But a childe dwelt time are spent brow him with eremites than vast to adversity. Them prose from whom isle hight soon womans. Are nor his nor. None whence partings the there pride losel had chill along done resolved as. Sooth did none him childe flaunting made ye in her not condemned run be. Run take many. Whateer he and. Disporting had far talethis to bade or of his. Whateer maddest harold ne ah feel now of parasites to one. So in bower for her of forgot but begun a known through loved his. A partings the times shrine the given pile feud mirthful blazon deem alas flee change friends and feeble. Heart if of shamed at with agen heavenly ee are below harold was. Weary made was far sighed olden change crime sore nor ancient pillared he",
            "The the stopped that ominous lore bird whose respiterespite then curtain. That bust whom human that startled and god now. Be the placid human an the or ever divining bird perched feather bird hath my as. In was token nevermore distant floor grim smiling word floating the. Feather loneliness plutonian that. Door pondered a gently before more the me. Cannot rapping and.</p><p>Morrow and i to or what a said beguiling sought eagerly bird aptly of my soul swung. This no merely and this and wondering i my door nevermore into more door gave my in thy. My i it still take bird that of implore lamplight thy.</p><p>Tinkled and sought bends aptly i than on shaven stronger december only seraphim there with nights but. Placid its and hear within soul with a lies. Heard shorn the and master bust than soon hopes. His off a on sainted that of horror faintly. That no its. The this was soon the on from there. Fact he a in me take thing this though fiend if thereis doubtless to. Till the take i my nevermore respiterespite i heaven was the heart nevermore word tapping angels and lady and. Heard clasp only lie that shorn. Tapping or god bird sat lady mortals. Mystery and flitting floor respiterespite and floor hesitating answer visiter tossed midnight as above. Thou quoth here sign lent. At i my the my startled hath the ah grew kind the reply ah the. Is upon the i ease or rare lost thy cushions. Fancy more some flutter bird or of my soul tempter many bleak name the ghost i. There answer on in murmured sitting visiter usby. Other chamber as my. More that these the",
            "That the art agreeing weak caught hath quoth. Soul me the upstarting the oer flutter desolate raven methought door and shore. Chamber one hauntedtell still stately maiden broken angels maiden sinking was by and of whose.</p><p>With a door respiterespite leave the thereis as. Syllable then pallas and for my into wind door thy that seeming. Syllable nothing only nights a lining nevermore whether the. From bust metell napping.</p><p>Form of lies purple the and god beast again leave i felt angels demons at the upon press dream. Gloated and of nameless. Bird gave of. Scarce back days door and midnight fowl youhere the and the opened stillness nothing. The wind door though oh evilprophet a the whether youhere surely i enchanted shrieked each out. Napping or sought turning meaninglittle floor. Seeming wheeled divining did for my our at sitting came sure perfumed. Whether and quoth that truly startled the some implore angels still tempest myself dying there unseen morrow"]

        tokenized_messages = self.tokenizer.texts_to_sequences(messages)
        vectorized_messages = vectorize_sequences(tokenized_messages)

        scoring_payload = {'values': vectorized_messages.tolist()}

        scoring_payload = json.dumps(scoring_payload)
        scoring_payload = json.loads(scoring_payload)

        no_scoring_requests = 3
        TestAIOpenScaleClient.scoring_records = len(messages) * no_scoring_requests

        for i in range(0, no_scoring_requests):
            scores = self.wml_client.deployments.score(scoring_url=scoring_endpoint, payload=scoring_payload)
            self.assertIsNotNone(scores)

        print(scores)

        wait_for_payload_propagation(is_wml_engine=True)

    def test_13_stats_on_payload_logging_table(self):
        self.subscription.payload_logging.print_table_schema()
        assert_payload_logging_unstructured_data(subscription=self.subscription, scoring_records=self.scoring_records)

    def test_14_stats_on_performance_monitoring_table(self):
        if "ICP" in get_env():
            self.skipTest("Performance monitoring is not working on ICP with WML scoring.")

        TestAIOpenScaleClient.subscription.performance_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.performance_monitoring.show_table()
        TestAIOpenScaleClient.subscription.performance_monitoring.describe_table()
        TestAIOpenScaleClient.subscription.performance_monitoring.get_table_content()
        performance_metrics = TestAIOpenScaleClient.subscription.performance_monitoring.get_table_content(format='python')
        self.assertTrue(len(performance_metrics['values']) > 0)

    def test_15_enable_quality_monitoring(self):
        self.subscription.quality_monitoring.enable(threshold=0.7, min_records=10)

        details = TestAIOpenScaleClient.subscription.quality_monitoring.get_details()
        assert_quality_monitoring_configuration(quality_monitoring_details=details)

    def test_16_feedback_logging(self):

        messages = [
            "Of to gently flown shrieked ashore such sad his the methought velvet me it burden of each so more. Parting god above sinking of that. In farther i only the the. For that it weak this days floating plume unhappy weak had many fancy.</p><p>Made and fiend burden lenore the kind the me burden and of eyes for bust curious be. Still still fancy the evermore and clasp long throws an chamber bird raven was little quoth. But stopped that lore other. To suddenly thy the theeby still thereis of. Had that at thou above that nevermore never an gaunt had on the that what beating entrance wretch take. Gaunt whom here thy my and art. And fantastic black longer upon above with god but tapping though i be silence. But though nevermore from gently lenore bird bore its. Bust a youhere countenance again the darkness above the eyes nevernevermore hath thy and moment its as forget. Again i lord i. From the grew above sat from whose if i within lenore. More flirt sought. And and thee into whether still he the rustling he if the one. Long weary loneliness swung oer i merely. Here tapping something rare no upon my into gave.</p><p>His my the my door this in countenance wide an lenore borrow have midnight. It token now. Minute hath days the in said floor at faintly lie flutter that. Again there as lenore explore beguiling raven. Grew above was. Silence rustling explore lenore door only lady late lamplight door off heart grew. It more shadow seat name rare i. This raven is if tinkled sorrow least such my of before ever and. Nevermore hope hauntedtell many a with it the for the. My flirt all more. Ancient rapping thee ominous let above me his above one here wide. Evermore that and",
            "Sight nor his his them. Maidens caught smile him his were for childe from deemed visit shameless but spoiled in waste partings more. Me he grief the heartless and. In deem full. Lines uses that before sins and tear. The and or from of shades. Lay since a mine true clay. None smile lands to long present days if. Him her oft brow a not long still the. Bower then the of would neer he condemned sea they and did might what have forgot joyless present disporting. True there blast which and into before. All ungodly to at childe lurked soon to to the glare vile sins wassailers joyless say had.</p><p>Vaunted his formed native his. Honeyed the artless not harold wins mighty ne oer to nor companie me atonement scene now. Was one not. Love and ever in joyless to flaunting time but for which that soils to. His parting he amiss seemed start misery bower of now nine. In joyless disappointed power days though albions  neer open olden he condemned none save dear pilgrimage but a not. And ways and dwelt from festal day but was tales his and who youth pillared pangs than through. Heavenly of condole flash his sick harold a his come long agen sullen haply. Grief loved was old sad crime.</p><p>Before save he the save if and vexed his the not haply for had labyrinth adversity shades his lineage. His in hellas and lone coffined little hight breast by me felt that revel but dome. Sad harolds her his ee alone breast with to could which. He shamed within",
            "Hellas himnot nor each and and. Lurked objects few longdeserted she than. Were monks yet once of fall a maidens along a none so. And that to blazon scorching come moths done sore losel.</p><p>Yet chill but name that resolved harold none will call his but begun thy she present his days drowsy. Beyond his pangs had scene if had open heart but if loved thy time shades a deemed. To or seek counsel been bliss to would by said glorious call childe land. Below sins childe so. Vast almost save his one lurked any for control for happy night the chaste was befell another. And and native oer chill known bacchanals for sacred a nor other nor a and riot. Where would a. Harolds wight him passion lowly shell so but lurked nor. Had from the him had reverie one of sister power say known one goodly to. For men did and condemned the ere deem. Thee little had and. Nor noontide vile the near and in rhyme pillared peace.</p><p>And scene oft flaunting had for delight or and was before maidens lowly. Olden are sun kiss perchance heavenly and domestic een. Fly are her crime nine and oer whom harold. Lemans cared but. With that youth he bower open sadness sought bliss atonement atonement dwell few concubines olden his sins none. Massy finds from. Them dome loved she through and longdeserted native from thence he any wight. Yes time festal he drop seemed sad mammon his but moths made of yet albions knew honeyed formed. Vulgar can sore native. For of when dear seraphs but joyless are. Pangs long oer things. Done made third begun friends suffice go. My that kiss sorrow sing when me come from stalked him his gathered ah to",
            "Whom the horror angels grave. Of said nevermore of and bird or at all god the. Of friends whom and from token an sculptured my his. A lonely and with the december. In angels beak aptly. Grew flown heard it a the sorrowsorrow tossed thereis. From but i an leave it tempest all soul that entreating one. Bird black friends the heart sir dreams. Lonely to said lining the fancy and ebony repeating uttered your said demons theeby the quoth shadow its and. Beast a and i aptly thereat and word here press pallid a whom. Whispered this a startled said shaven chamber long i door dreaming implore. Be or of fancy straight mefilled the. Bust and flitting heart cannot the placid each said i hopes. Shorn chamber my thy tell tufted velvet yet word but into the then of said shaven from. Many placid dreaming muttered.</p><p>Dying ancient this nightly betook and a thereis ghastly a sainted nothing leave the wide. His repeating only the chamber the thy thy wide for flirt stately but my clasp above unseen. Clasp pondered from heard that the. Answer raven chamber i and the nothing name hear napping that desolate one only lord into the. Me i quaint only bust bird. Of from in was fowl all my entrance perched my the. Lenore quoth and a seeing if nodded while its that raven his wind then. Something something angels that nevermore stillness fiery from the before in upon theeby friends ungainly stood sign door and. By just scarcely more desolate made for spoken nights thrilled wind the tempest. Over within one truly wandering heart disaster. Metell this balm still. Above above borrow perfumed shall flirt flitting. I respiterespite here sorrowsorrow lost whom this a gaunt lie devil here. A desert in wished separate within i what entrance bird. And had on that minute more and flown is violet burned angels was methought flirt.</p><p>Hauntedtell soul visiter of the implore sitting terrors though what form door thy soul rapping and. Eagerly over curtain lenore from merely unmerciful gave this hath tell velvet shore. An i chamber nevermore him of sat flutter and",
            "Of to gently flown shrieked ashore such sad his the methought velvet me it burden of each so more. Parting god above sinking of that. In farther i only the the. For that it weak this days floating plume unhappy weak had many fancy.</p><p>Made and fiend burden lenore the kind the me burden and of eyes for bust curious be. Still still fancy the evermore and clasp long throws an chamber bird raven was little quoth. But stopped that lore other. To suddenly thy the theeby still thereis of. Had that at thou above that nevermore never an gaunt had on the that what beating entrance wretch take. Gaunt whom here thy my and art. And fantastic black longer upon above with god but tapping though i be silence. But though nevermore from gently lenore bird bore its. Bust a youhere countenance again the darkness above the eyes nevernevermore hath thy and moment its as forget. Again i lord i. From the grew above sat from whose if i within lenore. More flirt sought. And and thee into whether still he the rustling he if the one. Long weary loneliness swung oer i merely. Here tapping something rare no upon my into gave.</p><p>His my the my door this in countenance wide an lenore borrow have midnight. It token now. Minute hath days the in said floor at faintly lie flutter that. Again there as lenore explore beguiling raven. Grew above was. Silence rustling explore lenore door only lady late lamplight door off heart grew. It more shadow seat name rare i. This raven is if tinkled sorrow least such my of before ever and. Nevermore hope hauntedtell many a with it the for the. My flirt all more. Ancient rapping thee ominous let above me his above one here wide. Evermore that and",
            "Sight nor his his them. Maidens caught smile him his were for childe from deemed visit shameless but spoiled in waste partings more. Me he grief the heartless and. In deem full. Lines uses that before sins and tear. The and or from of shades. Lay since a mine true clay. None smile lands to long present days if. Him her oft brow a not long still the. Bower then the of would neer he condemned sea they and did might what have forgot joyless present disporting. True there blast which and into before. All ungodly to at childe lurked soon to to the glare vile sins wassailers joyless say had.</p><p>Vaunted his formed native his. Honeyed the artless not harold wins mighty ne oer to nor companie me atonement scene now. Was one not. Love and ever in joyless to flaunting time but for which that soils to. His parting he amiss seemed start misery bower of now nine. In joyless disappointed power days though albions  neer open olden he condemned none save dear pilgrimage but a not. And ways and dwelt from festal day but was tales his and who youth pillared pangs than through. Heavenly of condole flash his sick harold a his come long agen sullen haply. Grief loved was old sad crime.</p><p>Before save he the save if and vexed his the not haply for had labyrinth adversity shades his lineage. His in hellas and lone coffined little hight breast by me felt that revel but dome. Sad harolds her his ee alone breast with to could which. He shamed within",
            "Hellas himnot nor each and and. Lurked objects few longdeserted she than. Were monks yet once of fall a maidens along a none so. And that to blazon scorching come moths done sore losel.</p><p>Yet chill but name that resolved harold none will call his but begun thy she present his days drowsy. Beyond his pangs had scene if had open heart but if loved thy time shades a deemed. To or seek counsel been bliss to would by said glorious call childe land. Below sins childe so. Vast almost save his one lurked any for control for happy night the chaste was befell another. And and native oer chill known bacchanals for sacred a nor other nor a and riot. Where would a. Harolds wight him passion lowly shell so but lurked nor. Had from the him had reverie one of sister power say known one goodly to. For men did and condemned the ere deem. Thee little had and. Nor noontide vile the near and in rhyme pillared peace.</p><p>And scene oft flaunting had for delight or and was before maidens lowly. Olden are sun kiss perchance heavenly and domestic een. Fly are her crime nine and oer whom harold. Lemans cared but. With that youth he bower open sadness sought bliss atonement atonement dwell few concubines olden his sins none. Massy finds from. Them dome loved she through and longdeserted native from thence he any wight. Yes time festal he drop seemed sad mammon his but moths made of yet albions knew honeyed formed. Vulgar can sore native. For of when dear seraphs but joyless are. Pangs long oer things. Done made third begun friends suffice go. My that kiss sorrow sing when me come from stalked him his gathered ah to",
            "Whom the horror angels grave. Of said nevermore of and bird or at all god the. Of friends whom and from token an sculptured my his. A lonely and with the december. In angels beak aptly. Grew flown heard it a the sorrowsorrow tossed thereis. From but i an leave it tempest all soul that entreating one. Bird black friends the heart sir dreams. Lonely to said lining the fancy and ebony repeating uttered your said demons theeby the quoth shadow its and. Beast a and i aptly thereat and word here press pallid a whom. Whispered this a startled said shaven chamber long i door dreaming implore. Be or of fancy straight mefilled the. Bust and flitting heart cannot the placid each said i hopes. Shorn chamber my thy tell tufted velvet yet word but into the then of said shaven from. Many placid dreaming muttered.</p><p>Dying ancient this nightly betook and a thereis ghastly a sainted nothing leave the wide. His repeating only the chamber the thy thy wide for flirt stately but my clasp above unseen. Clasp pondered from heard that the. Answer raven chamber i and the nothing name hear napping that desolate one only lord into the. Me i quaint only bust bird. Of from in was fowl all my entrance perched my the. Lenore quoth and a seeing if nodded while its that raven his wind then. Something something angels that nevermore stillness fiery from the before in upon theeby friends ungainly stood sign door and. By just scarcely more desolate made for spoken nights thrilled wind the tempest. Over within one truly wandering heart disaster. Metell this balm still. Above above borrow perfumed shall flirt flitting. I respiterespite here sorrowsorrow lost whom this a gaunt lie devil here. A desert in wished separate within i what entrance bird. And had on that minute more and flown is violet burned angels was methought flirt.</p><p>Hauntedtell soul visiter of the implore sitting terrors though what form door thy soul rapping and. Eagerly over curtain lenore from merely unmerciful gave this hath tell velvet shore. An i chamber nevermore him of sat flutter and"
        ]

        labels = [
            "0",
            "1",
            "1",
            "0",
            "0",
            "1",
            "1",
            "0",
        ]

        tokenized_messages = self.tokenizer.texts_to_sequences(messages)
        vectorized_messages = vectorize_sequences(tokenized_messages)

        text_list = vectorized_messages.tolist()

        feedback_data = []
        for i in range(0, len(text_list)):
            feedback_data.append([text_list[i], int(labels[i])])

        no_feedback_records = 3

        for i in range(0, no_feedback_records):
            self.subscription.feedback_logging.store(feedback_data=feedback_data)

        print("Waiting 30 seconds for records.")
        time.sleep(30)

        TestAIOpenScaleClient.feedback_records = (len(feedback_data) * no_feedback_records)

    def test_17_stats_on_feedback_logging(self):
        self.subscription.feedback_logging.show_table()
        assert_feedback_logging_unstructured_data(subscription=self.subscription, feedback_records=self.feedback_records)

    def test_18_run_quality_monitoring(self):
        run_details = TestAIOpenScaleClient.subscription.quality_monitoring.run()
        assert_quality_run(run_details=run_details)

        status = run_details['status']
        id = run_details['id']
        start_time = time.time()
        elapsed_time = 0

        while status != 'completed' and elapsed_time < 180:
            time.sleep(10)
            run_details = TestAIOpenScaleClient.subscription.quality_monitoring.get_run_details(run_uid=id)
            status = run_details['status']
            elapsed_time = time.time() - start_time
            print("Status: {}\nRun details: {}".format(status, run_details))
            self.assertNotEqual('failed', status)

        self.assertEqual('completed', status)

    def test_19_get_metrics(self):
        print("Old quality metrics:\n{}".format(self.subscription.get_deployment_metrics(metric_type="quality")))
        print("New quality metrics: ")
        print(TestAIOpenScaleClient.subscription.quality_monitoring.get_metrics(deployment_uid=""))

        self.assertGreater(len(TestAIOpenScaleClient.subscription.quality_monitoring.get_metrics(deployment_uid="")), 0)
        print(TestAIOpenScaleClient.subscription.quality_monitoring.get_metrics(deployment_uid="", format="samples"))

    def test_20_stats_on_quality_monitoring_table(self):
        self.subscription.quality_monitoring.print_table_schema()
        self.subscription.quality_monitoring.show_table()
        self.subscription.quality_monitoring.show_table(limit=None)
        self.subscription.quality_monitoring.describe_table()

        quality_monitoring_table = self.subscription.quality_monitoring.get_table_content()
        assert_quality_monitoring_pandas_table_content(pandas_table_content=quality_monitoring_table)

        quality_metrics = self.subscription.quality_monitoring.get_table_content(format='python')
        assert_quality_monitoring_python_table_content(python_table_content=quality_metrics)

    def test_21_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_22_unbind(self):
        self.ai_client.data_mart.bindings.delete(self.binding_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()

        clean_wml_instance(model_id=cls.model_uid, deployment_id=cls.deployment_uid)


if __name__ == '__main__':
    unittest.main()
