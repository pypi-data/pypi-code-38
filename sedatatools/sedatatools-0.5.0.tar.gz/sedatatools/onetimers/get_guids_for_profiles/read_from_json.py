from lxml import etree as et
import pandas as pd

# OLD GUIDS
config_tables = {
    'ACS2015': [
        '2a29cffe-6656-4ddc-99a8-4ad5db68e5c4',
        'c04ca1ac-9d5b-4ebb-9a99-074a7047c86b',
        '31410f16-7100-4070-81f5-213b9360579b',
        'c18f83fe-9d70-40bc-9624-acae77360bc3',
        '92f7e028-52fa-4c6f-aff8-9d28d2378abe',
        '47fc9025-1a95-4e01-8ddb-3b740eda3b61',
        '4492bf0b-a78b-4a60-99cf-b7eb7c6cc250',
        '3ba9d346-4114-4c92-a35c-5bf5d9513360',
        '400111e7-10f9-4fda-b5af-9bf22dc1257a',
        '575e3883-03cf-466f-9522-c96a72b53ce6',
        '84629471-9b8b-4707-ac9d-9038ada24c87',
        '517c632f-39af-451b-89b4-bf88c6960375',
        '2f5b61be-a47e-4683-8aa5-5334cc2dd8db',
        '86e64799-9158-4abf-9e64-9e471ef83cf0',
        'b2d61871-6402-46cf-996c-2e3dc4b4d82f',
        '47718433-3846-458c-9202-c10e2fed9503',
        'fb046c40-f48a-4b06-afa4-8cd655928ba2',
        'd9bc9e3d-cb4c-426e-b983-f3f22ed46db9',
        '8758220e-4feb-4fa5-9728-ded5edef0550',
        'b7eb6d97-e1a4-4f97-906a-5498ad571ff6',
        '969f1f2d-e89b-4b6b-864f-ee1b396641ec',
        'f488d319-41a6-416c-9bab-ac71fe05ade4',
        '7b1ed455-0a55-404d-9611-4f69e75610f8',
        '240fa75e-43ef-41b0-b6c9-f98c262bbfb1',
        'fc6bacf9-733d-4713-b9fb-81357cb8b759',
        '44982b19-74e8-42ed-990e-fa8ec3f4bf1d',
        'e7287220-fc04-4d34-8e9d-a0fe9f59744a',
        '1d69923d-6dc4-4837-b143-7cc53146685c',
        '9795cfc5-02af-4a6c-a37b-3bf3a6ea0241',
        '0c21ae2d-9403-468e-8ee5-362a468de971',
        '49167a24-f805-48f7-a922-055e16e69e80',
        '85c26358-a374-4149-85f7-e497a471cad6',
        '252e01df-5c32-4229-806d-bbc28dcb613f',
        'c22046b5-bf0c-4ca3-ae8b-e2d1f4fc4ccd',
        '60e7f16b-311e-42a5-9f0f-9421257478ea',
        '6e934296-5f26-406b-a9d4-20a447f93859',
        'fbbc2f71-ac70-42fe-abc2-f32435fb1d1e',
        '561f9596-0a31-4726-aeab-17798ad0d1f7',
        'fa9d55c9-c907-47f3-8782-2f016a52d699',
        '01274d46-c971-41aa-b6e0-0979204f496a',
        'dab80faf-77c8-4944-b3ea-d0c5ad6953c7',
        '1a604fad-5da6-4132-bd76-559dcf25170a',
        'e26c8c41-3464-4d25-a17e-18c20b08e6b4',
        '18a81aa6-5631-4e55-ab9a-074e4c2194b2',
        '4b6b8bb3-a0b0-4b6d-aab6-6b99de126cd9',
        '49f04fdd-73af-4d1e-a2c4-8da3181a461a',
        '39d99f84-898e-45ba-9698-08c67bacedc1',
    ],
    'ACS2015_5yr': [
        '96eb2223-e810-4ca0-b9cc-dd4a1e88e30f',
        '8b30b65f-d59e-4417-ac9c-8fc402b4575f',
        '519f4b4c-a0b2-46e2-ab42-b124289aa97e',
        '6cdc39a6-3422-492c-ba3c-b31c82b456c9',
        'fede459c-08a5-4236-857f-894479da7c7e',
        'cc6fbcb0-7537-47ea-b9f7-249561b1b4d9',
        'd716db57-2495-4cd2-8962-05165c1a0160',
        'fa88c694-987f-4d92-9baa-83c0a0bc32e3',
        'eb5fd437-7a1e-453d-af9b-60cad6d3286b',
        '4e7eaabd-7cb7-4a5b-ac96-54d19343b0c2',
        '35c8bc09-43ad-48b7-a58e-4e5680899ea4',
        '627a01b4-961a-4831-96c3-6c200d6b1ea7',
        '4b771bb8-ae87-42a3-9629-9b09f8ceff22',
        '2c5bc3b5-3be2-4a0e-abb3-cd0a880fd671',
        '6de7b366-ae63-42ef-9875-d70773ce7eb9',
        '3611b970-5c61-43ce-9698-335ca7c327ea',
        '08ed17e8-2bb2-4d30-b099-4aed4213fade',
        '4795b9c3-0a8a-47a0-a29f-03ccdefbc558',
        '5dc59223-1749-4ef7-b6bd-9f1a0a3ac2ad',
        '76576388-7b6b-4592-a5fc-ce21a6d1ff53',
        '25915be9-502e-4d7d-9045-8141be9853bf',
        'ec6fef32-a756-403a-b85a-002cdab72c92',
        'bfd54142-767d-4e2b-82c8-2c50f616078f',
        'f7b4cf4f-9445-4b90-b3c7-8cc9f9f54bb1',
        '6e767c7e-7c8c-4b30-9912-e2e76c6f24f4',
        'a486ae9d-6bf4-496b-b64e-1adc2c8808bb',
        '3f5c12dd-695d-485b-ad99-69c7f2caba87',
        'f7c86254-67ce-400e-a526-24f7fb37d12f',
        '29d92c05-adff-43c3-a70a-ceb130cf19ab',
        'b310e5af-8014-45e7-b5a3-73f4ad4c011f',
        '9305336d-2c1c-4767-827b-5ae40d176471',
        'dfff68f9-5665-496c-a51e-95d5ed820693',
        '7ae747e4-cb42-4481-a4ce-4a56bf5cabbd',
        'e3e80603-cd15-4955-9528-cf3ff17ff4dd',
        'ea4246e9-3ce5-4e3a-81e6-ce38a1fe2317',
        '030eee36-92e5-41d7-8674-95d1eaf89bc3',
        '45c2f4a1-5c00-4c42-b491-28fc4de8f39b',
        '76506e74-d3da-44b2-9801-1a7eaf2b368e',
        'b6abb891-4f77-4c0e-beef-6a5fc5565524',
        '076f3420-2c36-41d0-9d32-401d7c034447',
        'dc025dae-f4ae-4953-8950-d6d21ee36813',
        'dcd71975-07ce-480f-8b9f-1d951f97973f',
        'c759b4c7-ebce-49c5-b1d7-6125a1898f4e',
        '0f99c223-1d73-4af1-8132-0b4259f73d90',
        '683ae166-39c1-44a8-8473-36ae9d79d398',
        '0525fe23-bc4c-48cb-a146-8b311e1e9a37',
        '7358fbf1-3bcf-4e03-ac80-17bd72c9e5f0',
        'cd6e72fe-7233-47bf-a9c0-cdffaaa691f3',
        'b9aadec7-9a30-4faa-86dc-429e65e63099',
    ],
}

config_variables = {
    'ACS2015': [
        'fa5eec81-2604-4bbd-b01e-aa5164a34527',
        '0a9f3d2d-5612-4e63-91c4-39b14038d815',
        'b0b9dbec-8960-438a-af83-4a06fb378827',
        'b9f616e1-d135-4be5-8edc-62e303487d54',
        'e6f1cbb0-5e0c-41e6-a863-df919c6e9ca1',
        'bc84d06c-a2e0-40f6-8563-f70bc6c2b90b',
        '2722e9ea-5b3f-417e-b0f0-14801ca2280b',
        'a65ccc31-c108-48df-9269-9937a41c1133',
        '8959ee97-67a7-4dcf-8c43-7e6d3789b779',
        '403bbf45-9f9d-4383-be25-453fc01fffec',
        '25243edf-c12d-4f20-819b-0fa949b8f396',
        'a3f7b233-aa3e-4172-842c-9426db548339',
        '0627dcff-d3a5-4a0f-a858-6d084aad0b92',
        'de3ab82e-7a50-4c37-b2f8-60a8f9cc2999',
        'a5895cd1-16f5-4c72-a050-4ced84bdb78e',
        '5604a14c-a036-4b0b-9922-34f9f6be3f72',
        '39832e2a-b50c-4793-93c4-16055703887b',
        '7f9c7c95-85fe-4523-9f72-46e4846d5f54',
        '37ef41f4-0491-461a-a063-52b7a754e4f9',
        '6b8f2c28-af51-4907-8ba4-b7821d55f2ef',
        'c7a57711-634f-48f8-9cb5-c4d214414908',
        'c106e2ae-e061-46b3-b169-6e69f6ee1635',
        'deac90de-e502-4867-9816-5f5ee2fffc68',
        '1bf893de-927b-4308-995f-7637d27fe430',
        '75aa3d65-7fd8-4ab4-abb9-d8dbcd140fe7',
        '200a157f-a39b-4c76-99f2-b6ba5c7184b5',
        '2caea4f0-53a5-43f9-b0e0-c82ce10dd594',
        '04886715-3e59-4259-b384-443d3db84df1',
        '96378cea-4629-444c-a323-ae2c15444510',
        '18eaef57-1720-4c97-9fcf-975d53e03124',
        '0e556fbc-0ead-4dc1-9f13-b612d327a361',
        'e13d4272-b629-4a99-900c-f5fa8ce5ae15',
        '11e85b7c-4cc0-4b4e-99d3-ecdce6e70af2',
        '0df41cc1-62a4-4bbc-83b9-38d18bb69604',
        'b31f07b8-c1d2-4f55-9d08-a87d67ba8fcd',
        '110b51d0-01e2-4b8a-8584-f250eac7365c',
        'f432e26f-e265-4d22-ad21-782cf62f807a',
        'd6aa9cf2-c51d-4464-bc8a-974135964d17',
        '9471e972-112c-4011-8e48-34ba5f797e39',
        'bbd06e18-382f-4bbe-8e5d-78f21240192a',
        'aae2e68f-33a1-4f1f-81f5-060ce8fec7d5',
        '3c59406a-0e73-4779-8097-764c5de53938',
        'd06b593f-26a6-4c91-ae10-d403777d1f0f',
        'cb8867b9-56bf-4642-b0f4-c982759aa5a3',
        '8168e5e8-96ea-4952-876e-19db79124e28',
        '573a2abd-0c57-45d1-8a09-a7f31fc67771',
        '75c659b9-4ac3-4d5f-96bf-7ae0bf8b5c46',
        'a0d782f2-978d-480b-9fd1-09a19452cdd2',
        'e6b40653-df2f-4ee8-bfb5-9eb45b415db0',
        'b54b3b74-c0a4-4543-afcf-a5d63ee9c28b',
        '43087cd2-d5e4-4e5f-8b32-1d9cd4b0070d',
        '70e6a4f0-f0bf-452a-8fe2-9a85616c9eed',
        'f22f7fee-a6fa-48ed-b971-76bd1b4077bf',
        'dfcb4b84-2d1c-43a3-a436-3ce548c347d1',
        'dae27a1c-07ff-4af2-a434-1da12e92ccd1',
        'a6873e23-cd4d-4f0d-ae99-18308eca65e0',
        '26690934-3e7b-4905-b48f-2a92176aa914',
        '633e1f4e-c3d7-4fbd-94e0-1bb8f72665cd',
        '4889943d-729a-40e8-8d68-2889e744a4ba',
        'fcf36a10-6270-46d0-b38f-ac70fcea6afc',
        'c537d227-600c-4e9c-8415-02f8bb731438',
        '0ef4affc-5165-483b-94a5-4b1fa7b583d6',
        '8405b9ca-2cd9-4478-8dd8-6084b0d795bd',
        'f74458c0-4cad-4d46-9737-87ec33f29593',
        '46c27442-85d5-4065-807f-f3e016ad179f',
        '84fbc255-bc42-4d1b-ab25-d4c4f88deb80',
        '9dd3c940-62ac-4669-9222-6fce6052c105',
        '6c526548-723a-48a4-b9ce-e5c0b8e72a2c',
        '878d9e20-0af3-4374-beea-5924f9df6b4f',
        '1fe56fd9-bdd4-4a37-8301-ab4187c538cb',
        '3f0d7c97-b64c-42d5-a375-54be1d6912a7',
        '16ecd98c-85ef-439a-a0ab-0f9d04029543',
        '08a6f91b-10f5-4986-b5aa-541041fe1306',
        'e83d5178-329a-41c2-bd21-5b3db892f272',
        '2ffa83e4-a06d-42ae-8e13-2d2269c306f1',
        '4c1b3c3c-dc7b-4dfa-8ded-15b481f8469d',
        '5e8c2dac-8aa6-44ce-8067-55aa761e8cc8',
        '2dedae77-78eb-4a6f-aba9-c4fa296e5363',
        '8aca2bb5-c084-43cd-8d3b-fa82b2b4c5fb',
        '545bde7a-e6a6-405c-98a0-4f929e2a246b',
        'bdf8033c-df2f-48e1-8032-51abdc76e3ef',
        'b808ed0d-2c2d-415b-bac1-51d4489f5a54',
        'e6b8bd3b-d2ed-446d-8f4d-705d20f95316',
        '8b028e3a-84c2-4c77-ba13-234580504703',
        'bd71c5f1-49f6-460c-a364-23ac4af1bea3',
        'b14512bb-dc84-4cb9-8372-d9d5a5f08210',
        '47cf2b82-e286-410b-838d-d2efcbe8f301',
        '53197b3c-cb4f-4a31-bef2-e231bc47583e',
        '7e884e0f-e700-4ea0-97da-0e122a43a301',
        'f65b491d-3364-4e27-957a-ed3aa8890f9b',
        '42879689-eddb-4d59-8e74-f843f19b1d57',
        '882966f8-459a-4cff-8dd7-2ab87f31f7d8',
        '0b236659-682f-41e1-b1f6-b15de8cbf1d6',
        '273e48b7-91fc-4b80-baff-262ffa6fd389',
        '4256ef1a-10a6-4229-8e03-7916db6a65ee',
        'e403ccb4-66af-4028-b7f1-e217c9be8828',
        'cec91c1a-7eae-49eb-8b0e-f5b5ec36ff28',
        'aa570558-186c-473e-b5c4-91434f9891f0',
        'c33dd5ef-45dd-4833-8b50-21c8eb0cca26',
        'eafc2132-0b99-435b-8ef8-f7085405169d',
        '77606a9c-31c2-4f77-bdc6-aa46f8fa0a86',
        'e73b6fc5-6a40-4b97-809a-eacb494a6246',
        '5dfbd005-311c-4c4c-90ec-11fc87b72a72',
        '2ab5978d-c103-4ba3-ad2d-34e2c869c8d1',
        '668aef26-9c47-441d-af70-febb651d2831',
        '3e4a2e01-c816-4bdb-b7c5-3486dd2874b7',
        '1272885f-ede7-40c6-b7d5-613d19a33ed1',
        'bb098c2a-3368-444b-8021-ce2b50c11133',
        '20183dee-9245-4d44-8f69-a47434e0870c',
        'c1480fb1-edeb-4a64-af51-ca617125350e',
        '912ce952-4fe3-4b72-8d5e-0d3b58f66db4',
        'b630c537-4b1e-4d13-bdf7-1fc4c0d9b935',
        'ff09d942-30bd-49d6-84e0-1d99bfecebfb',
        'ee3bceaf-68be-454c-a241-6da09e438edf',
        '0f369b17-841b-459b-a7e1-e32cc01e07cd',
        'e429b7bb-f8c7-4aa6-85a3-5a762564ed90',
        'f71ae11b-0587-4a86-b14d-f541a99e39d4',
        'cb07d888-8ce9-49ec-8a6e-bed51db8aa76',
        'df097593-199b-47c1-8311-73dc5dc22191',
        '9508431d-5179-4fda-86cf-6fbf0dea0d6a',
        'ce918380-4040-42fe-9ed6-61f4ad446a33',
        '7a9aaf48-966c-4c77-ac47-20ae1502182d',
        '464eadfc-0acd-4576-8780-dcf274fa65fd',
        'ea233db2-410f-4a4c-8644-61939ca32d58',
        '4637b743-0323-4fa6-a324-d02ddcc019e3',
        'df62441e-f640-49d0-be14-c675a76a437d',
        'fe243f6a-be01-44a1-9943-caae6d0799cf',
        'a28d9aa6-d8b6-4e2c-92ce-a2da1c73a971',
        '9d9f78e1-fca5-4057-8898-27c204ca1a64',
        '77b2d0de-9316-4b63-8e15-444ff7f57b7b',
        '2741c5a5-ba81-4ef4-a696-175ff8a827ad',
        '5306c210-718e-463c-a3eb-a264b9f78110',
        '7c31d0c6-8082-44f2-954f-f6dad6148426',
        'fb0fb5ff-d8f1-45f5-8c68-166541a558f1',
        '592b9d1a-f4af-4f6a-b5b7-d14a74c1d81b',
        'f0bb3730-3443-4a92-bf2c-3dc1a745877e',
        '9aa01a82-77aa-49f5-9a6b-aa173598fc39',
        '648d5d95-58e1-4aa4-a1bf-414f496161eb',
        '0bd0d8cb-2596-4d5e-bb3c-eb6f67ef1287',
        'abdf0345-f35c-4765-aeb8-5ff7419476de',
        '84806a84-2364-4011-aeb8-b3bdf6b5ae6d',
        'adcb1248-6101-413f-8810-5ab11ab5726d',
        '77d5371a-8e05-4b23-8e06-9084807b7198',
        'cb9fc254-e188-40f4-a9df-9a11f67d55fd',
        'b3db1004-10f0-4554-870f-b0794641d1f7',
        'ee284862-7856-4972-8e62-7fd68643e787',
        '43276893-9561-4a99-88ee-f81843b4a5aa',
        '77e611f0-6723-44b0-a043-32bd2d257fb4',
        '12dfc1c9-d083-4669-a5e3-b33b6639fd3f',
        '8192bb0f-bc96-4c7b-922b-95dc275fc028',
        '3a3a717e-02ba-4091-82ad-6a04d6ac0531',
        '943dc6d0-687d-4d31-b761-4a38ab27074b',
        'dfc9ba15-a03b-43ba-9437-e1080d696c4a',
        '3b5ba0b6-d09e-408a-a6dc-d61ee409cacf',
        '3e0510c1-ed66-452f-8138-bca36db6ddf6',
        '21cfe8b8-fb14-4542-ab3b-c391cd26c2fe',
        '1ed63017-6bad-4f4f-b345-4dfd005a3f6f',
        'c9d4c8c4-813b-4e95-b61c-2a18f83b8e8e',
        'b5f42b91-d34b-4b88-9ba7-cc5cd42c85c2',
        '02f29521-1ea0-4dcb-ad3f-7b0ba3ad30ec',
        'daa9531b-fc2e-431d-b46d-3194b9951c29',
        '7de603ed-1f10-4f87-8995-aace9705905c',
        'b2357d3a-d6a6-44da-a3fd-96c17586dc49',
        'c5f9b34c-4f4b-45c0-8bda-2fc54dec7195',
        '7f67a71b-9be8-4059-b78e-a037178c4db5',
        '5b840068-baea-46a6-943b-7acf5d74b2aa',
        '03b9b993-caad-4abf-9c65-8969a898496c',
        '74cfa131-cea3-4b11-b8b6-a91663aff15e',
        '15166999-6204-4c09-a6c9-28857b2a1551',
        'd5fde4d0-ed11-4eda-a2fd-1fc8362ef19e',
        'ab527e74-84e1-47db-8463-a3d66699ba64',
        '33bb2caa-f834-495f-9d24-073244871261',
        '0311200f-b96c-464b-a1a2-7d03a9b39ae6',
        '23635f6d-19ac-4a0a-94fb-abad544f2f03',
        'd9f6bb7f-fac3-4eba-9694-ab46ce04dd86',
        'b3a55de2-b77f-4d60-80f7-5c0abd8373e5',
        '5ef5b608-5fcf-4c2f-b631-e56d8f932e76',
        '456784ce-b745-4980-99be-173a40cdef5e',
        'c8d51134-00b8-4b53-859f-27727e6582b2',
        '75528fdf-85b4-4dcb-8281-b43154cfacca',
        '84a90161-b81a-4c16-8a0f-cdd1a4763ec8',
        '0066f8d7-d2aa-4485-9497-325532c77c11',
        '1e52b4f9-1d11-48ea-b172-2d7485a20791',
        '2ff65956-60d8-495f-af0f-3704482b4c39',
        '9968a436-2e07-49e9-9ff7-ff113022687f',
        'de2fa13e-bbea-4361-8fab-43b43e5b365d',
        '38140a20-60d9-439f-b83f-d4b017c4fa1d',
        '93b72a1f-8c63-49f8-acbb-dfeec67f2358',
        '81550b51-fb02-466c-b289-e7059a6609d1',
        '0e0aece6-7a95-440b-8cd6-361975613e0e',
        'e3f8660d-69cc-4c6e-a056-8a0373c75a69',
        'bb8b8283-f9a0-47ec-94ae-38bf975753be',
        '8df17a32-3899-46c5-b5fa-42c0ea67d61f',
        '',
        '1ef50374-e395-45c9-a067-96a06c37036c',
        '343a00ff-c030-420f-9457-0566df0e17b2',
        '3b2667a1-ce8f-4f2b-853c-595cf3cf22ff',
        '15044ee8-fb1f-414a-a642-0a4bad8ff55d',
        '960e98b5-2db5-4249-a717-5b9b93671386',
        '6c080e8f-4adf-4ee3-94b7-add201f57292',
        'efd1c3d9-1f88-4813-b3b3-ec4e320bd73a',
        '9f9fd5de-b936-4705-a44d-ea4c3a453f65',
        'f803d559-c89b-4a50-8e51-d15e50449341',
        '2fb9a595-998f-45ed-a00c-3eb67b21eeed',
        '7d23e87c-e5ad-4f8a-9641-dbcda617a999',
        'd1b6f21d-ff56-4434-83a0-ee0db160410f',
        'f8b9e3cf-9392-495e-81df-554384a396fd',
        '736c89e3-82b0-415a-beaa-ecd9ab35ca70',
        '508960c5-4666-4a95-8c91-a1680564b26d',
        'aadabd02-91bc-4b38-9daf-6184adf509c3',
        'e0778327-c258-4fe4-9675-b6e4b7f84237',
        'dafcd288-f9ca-4a21-ab1e-a6b128ea3f66',
        '63185e9d-368f-418d-b345-4b11587780b9',
        '4a40c9cf-6737-4e17-b353-b7e9be960c1e',
        '2851b34d-a168-4753-b001-c6a9c4a0b55e',
        '5d06736f-d7b4-409a-842a-0c49674d674d',
    ],
    'ACS2015_5yr': [
        '1ef50374-e395-45c9-a067-96a06c37036c',
        '343a00ff-c030-420f-9457-0566df0e17b2',
        '3b2667a1-ce8f-4f2b-853c-595cf3cf22ff',
        '15044ee8-fb1f-414a-a642-0a4bad8ff55d',
        '960e98b5-2db5-4249-a717-5b9b93671386',
        '6c080e8f-4adf-4ee3-94b7-add201f57292',
        'efd1c3d9-1f88-4813-b3b3-ec4e320bd73a',
        '9f9fd5de-b936-4705-a44d-ea4c3a453f65',
        'f803d559-c89b-4a50-8e51-d15e50449341',
        '2fb9a595-998f-45ed-a00c-3eb67b21eeed',
        '7d23e87c-e5ad-4f8a-9641-dbcda617a999',
        'd1b6f21d-ff56-4434-83a0-ee0db160410f',
        'f8b9e3cf-9392-495e-81df-554384a396fd',
        '736c89e3-82b0-415a-beaa-ecd9ab35ca70',
        '508960c5-4666-4a95-8c91-a1680564b26d',
        'aadabd02-91bc-4b38-9daf-6184adf509c3',
        'e0778327-c258-4fe4-9675-b6e4b7f84237',
        'dafcd288-f9ca-4a21-ab1e-a6b128ea3f66',
        '63185e9d-368f-418d-b345-4b11587780b9',
        '4a40c9cf-6737-4e17-b353-b7e9be960c1e',
        '2851b34d-a168-4753-b001-c6a9c4a0b55e',
        '5d06736f-d7b4-409a-842a-0c49674d674d',
    ],
}

config_percs = {
    'ACS2015': [
        '8a1a9717-27f8-4a88-8a9b-246f24c35097',
        'c2584895-691b-4f1e-a2b9-171ba87fadf4',
        '33d083b2-779f-4674-b35a-cd24221ead2c',
        'fbee5219-17bb-4806-9d0c-892fe2a8e1ef',
        '7263197e-e8e1-454f-b22b-a777485ddade',
        '6261dc86-2d43-42f5-9f8c-113603a7edf7',
        'f1b5e36f-649c-4b92-965d-6a4532003b40',
        '71794589-d10f-4f32-b467-da462d624340',
        '6318dffe-c071-4018-9165-8e3cc6675dcc',
        '851089f5-84de-417f-b82f-804dbe288749',
        'a3f541e7-48cc-41d9-864a-8d1c24715e38',
        '79f80919-43ac-456a-9fa0-f8c3ac2aff9c',
        '917edccf-3858-4fd6-afba-5c6bee28e5f6',
        'bf90910b-4404-4865-ad9a-e98f7e39e827',
        '7905f320-20f7-4d17-b52a-f0fd00b1f647',
        '4144a5cb-b12a-409c-89d0-f589c0c4126c',
        'dbb3b38b-306b-4706-9600-15eeb3873dbe',
        '3d166dc5-9f22-4136-bd22-0ac85bd03e64',
        'c5169671-edea-4147-b2e6-1d51235a127c',
        '97f459e0-0f6a-4c18-962b-022a2b78acba',
        'a5caf1d9-b94e-4ef7-8d9e-e735c858ecb4',
        '386a3902-97e9-4769-be7b-c765d59b02f9',
        'aa34a35e-c88b-4d35-bb09-6a6254489389',
        '83efff36-5f00-429d-8a60-ecf767720099',
        '372281bd-99fb-4503-b885-6696fa52496e',
        '5948dff8-14e3-47a1-8d1b-63840a6617c8',
        'b12313a0-b219-4a05-a8f8-625ba054b0f3',
        '4b641934-0f62-42e0-a931-120514f98990',
        '24c71763-0a5d-4f84-aeac-d82e185071a8',
        'cf36392b-e9df-4721-8b86-cffbb630bd52',
        '32830fa6-8c0d-4bd0-a038-44affcc06e00',
        'acbfab6d-bac9-430a-ab3b-acd50afd9b58',
        '392ce81c-7e52-429b-9551-f00aeb988e99',
        'fd01fdd7-6d57-46ba-897b-28ba41c6f44a',
        'b18cd1b0-cb94-4698-8ddb-d07ee3e2e939',
        '92f3e3fb-7dc2-453c-a5e7-0c910d52c7c8',
        '14bf8194-d7b4-4de0-9505-683b8dc80fa4',
        '33ad1318-8413-49eb-ae24-5f3480bcf024',
        '335775ea-edce-4a40-ad7b-c7fab2cee7ca',
    ]
}



def get_new_guids_for_tables(acs_guid_elements, acs_old_guid_elements, old_guids):
    old_guids_by_names = {}
    new_guids_by_names = {}
    for guid in old_guids:
        try:
            old_name = acs_old_guid_elements.xpath(f"//table[@GUID='{guid}']/@name")[0]
            old_display_name = acs_old_guid_elements.xpath(f"//table[@GUID='{guid}']/@displayName")[0]
            old_title = acs_old_guid_elements.xpath(f"//table[@GUID='{guid}']/@title")[0]
        except IndexError:
            print(f'Guid not found in xml file: {guid}')
            break
        old_guids_by_names[old_name.lower() + old_display_name.lower() + old_title.lower()] = guid

        # no case insensitive search
        # new_names.append([guid, *acs_guid_elements.xpath(
        #     f"//table[@name='{old_name}' and @displayName='{old_display_name}' and @title='{old_title}']/@GUID")])
    new_guids = acs_guid_elements.xpath("//table/@GUID")
    for nguid in new_guids:
        new_name = acs_guid_elements.xpath(f"//table[@GUID='{str(nguid)}']/@name")[0]
        new_display_name = acs_guid_elements.xpath(f"//table[@GUID='{str(nguid)}']/@displayName")[0]
        new_title = acs_guid_elements.xpath(f"//table[@GUID='{str(nguid)}']/@title")[0]
        new_guids_by_names[new_name.lower() + new_display_name.lower() + new_title.lower()] = \
            [nguid, old_guids_by_names.get(new_name.lower() + new_display_name.lower() + new_title.lower(), 'missing')]

    guid_comp = pd.DataFrame(new_guids_by_names)
    guid_comp = guid_comp.loc[:, guid_comp.iloc[1, :] != 'missing']
    return guid_comp


def get_new_guids_for_variables(acs_guid_elements, acs_old_guid_elements, old_guids):
    old_guids_by_names = {}
    for guid in old_guids:
        try:
            old_name = acs_old_guid_elements.xpath(f"//variable[@GUID='{guid}']/@name")[0]
            # old_display_name = acs_old_guid_elements.xpath(f"//variable[@GUID='{guid}']/@displayName")[0]
            old_title = acs_old_guid_elements.xpath(f"//variable[@GUID='{guid}']/@label")[0]
            old_guids_by_names[old_name.lower().replace('2015', '').replace('2016', '').replace('<dollaryear>', '') + old_title.lower().replace('2015', '').replace('2016', '').replace('<dollaryear>', '')] = guid
        except IndexError:
            print(f'Guid not found in old xml file: {guid}')
    new_variables = acs_guid_elements.xpath("//variable")
    new_guids_vars = {}
    for el in new_variables:
        key_v = el.attrib['name'].lower().replace('2015', '').replace('2016', '').replace('<dollaryear>', '') + \
                el.attrib['label'].lower().replace('2015', '').replace('2016', '').replace('<dollaryear>', '')
        val_v = [el.attrib['GUID'], old_guids_by_names.get(el.attrib['name'].lower().replace('2015', '').replace('2016', '').replace('<dollaryear>', '') + \
           el.attrib['label'].lower().replace('2015', '').replace('2016', '').replace('<dollaryear>', ''), 'missing').replace('<dollaryear>', '')]
        new_guids_vars[key_v] = val_v
    guid_comp = pd.DataFrame(new_guids_vars)
    guid_comp = guid_comp.loc[:, guid_comp.iloc[1, :] != 'missing']
    return guid_comp


def get_new_guids_for_percs(acs_guid_elements, acs_old_guid_elements, old_guids):
    old_guids_by_names = {}
    for guid in old_guids:
        try:
            old_name = acs_old_guid_elements.xpath(f"//variable[@GUID='{guid}']/@name")[0]
            # old_display_name = acs_old_guid_elements.xpath(f"//variable[@GUID='{guid}']/@displayName")[0]
            old_title = acs_old_guid_elements.xpath(f"//variable[@GUID='{guid}']/@label")[0]
            old_guids_by_names[old_name.lower().replace('2015', '').replace('2016', '').replace('<dollaryear>', '') + old_title.lower().replace('2015', '').replace('2016', '').replace('<dollaryear>', '')] = guid
        except IndexError:
            print(f'Guid not found in old xml file: {guid}')
    new_variables = acs_guid_elements.xpath("//variable")
    new_guids_vars = {}
    for el in new_variables:
        key_v = el.attrib['name'].lower().replace('2015', '').replace('2016', '').replace('<dollaryear>', '') + \
                el.attrib['label'].lower().replace('2015', '').replace('2016', '').replace('<dollaryear>', '')
        val_v = [el.attrib['GUID'], old_guids_by_names.get(el.attrib['name'].lower().replace('2015', '').replace('2016', '').replace('<dollaryear>', '') + \
           el.attrib['label'].lower().replace('2015', '').replace('2016', '').replace('<dollaryear>', ''), 'missing').replace('<dollaryear>', '')]
        new_guids_vars[key_v] = val_v
    guid_comp = pd.DataFrame(new_guids_vars)
    guid_comp = guid_comp.loc[:, guid_comp.iloc[1, :] != 'missing']
    return guid_comp


def main():
    # read xml file
    acs_old_1yr = et.parse('C:\Projects\Website-ASP.NET\pub\ReportData\Metadata\ACS 2015-1yr metadata.xml')
    acs_old_5yr = et.parse('C:\Projects\Website-ASP.NET\pub\ReportData\Metadata\ACS 2015-5yr metadata.xml')

    acs_1yr = et.parse('C:\Projects\Website-ASP.NET\pub\ReportData\Metadata\ACS 2016-1yr metadata.xml')
    acs_5yr = et.parse('C:\Projects\Website-ASP.NET\pub\ReportData\Metadata\ACS 2016-5yr metadata.xml')

    guids_1yr_tables = get_new_guids_for_tables(acs_1yr, acs_old_1yr, config_tables['ACS2015'])
    guids_1yr_tables.to_csv('guids_ACS_1yr_tables.csv', index=False)

    guids_5yr_tables = get_new_guids_for_tables(acs_5yr, acs_old_5yr, config_tables['ACS2015_5yr'])
    guids_5yr_tables.to_csv('guids_ACS_5yr_tables.csv', index=False)

    guids_1yr_variables = get_new_guids_for_variables(acs_1yr, acs_old_1yr, config_variables['ACS2015'])
    guids_1yr_variables.to_csv('guids_ACS_1yr_variables.csv', index=False)

    guids_5yr_variables = get_new_guids_for_variables(acs_5yr, acs_old_5yr, config_variables['ACS2015_5yr'])
    guids_5yr_variables.to_csv('guids_ACS_5yr_variables.csv', index=False)

    guids_1yr_percs = get_new_guids_for_percs(acs_1yr, acs_old_1yr, config_percs['ACS2015'])
    guids_1yr_percs.to_csv('guids_ACS_1yr_perc.csv', index=False)

if __name__ == '__main__':
    main()
