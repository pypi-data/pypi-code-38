from random import randint

def mongoLocationToGeojson(locations):

    geojson = []

    for p in locations:

        feature = {
            "type": "Feature",
            "geometry": p["location"],
            "properties": {}
        }

        props = p
        props.pop('location', None)
        feature['properties'].update(props)

        geojson.append(feature)

    return geojson

def randomLatLng():

    points = [
        {
            "latitude1": "16°39′51″S",
            "latitude2": -16.66408139,
            "longitude1": "49°15′53″W",
            "longitude2": -49.26466941
        },
        {
            "latitude1": "16°41′14″S",
            "latitude2": -16.6873471,
            "longitude1": "49°12′26″W",
            "longitude2": -49.20708972
        },
        {
            "latitude1": "16°44′30″S",
            "latitude2": -16.74153538,
            "longitude1": "49°19′20″W",
            "longitude2": -49.32221339
        },
        {
            "latitude1": "16°43′30″S",
            "latitude2": -16.72504467,
            "longitude1": "49°19′09″W",
            "longitude2": -49.31922614
        },
        {
            "latitude1": "16°43′45″S",
            "latitude2": -16.72917,
            "longitude1": "49°11′03″W",
            "longitude2": -49.18415634
        },
        {
            "latitude1": "16°46′06″S",
            "latitude2": -16.76825283,
            "longitude1": "49°16′08″W",
            "longitude2": -49.26884882
        },
        {
            "latitude1": "16°36′55″S",
            "latitude2": -16.61536917,
            "longitude1": "49°18′24″W",
            "longitude2": -49.30675615
        },
        {
            "latitude1": "16°41′06″S",
            "latitude2": -16.68509174,
            "longitude1": "49°16′14″W",
            "longitude2": -49.27050391
        },
        {
            "latitude1": "16°35′58″S",
            "latitude2": -16.59934883,
            "longitude1": "49°14′57″W",
            "longitude2": -49.24920109
        },
        {
            "latitude1": "16°37′37″S",
            "latitude2": -16.62685504,
            "longitude1": "49°17′07″W",
            "longitude2": -49.2851527
        },
        {
            "latitude1": "16°40′48″S",
            "latitude2": -16.67994781,
            "longitude1": "49°20′03″W",
            "longitude2": -49.33429783
        },
        {
            "latitude1": "16°45′50″S",
            "latitude2": -16.76390267,
            "longitude1": "49°14′54″W",
            "longitude2": -49.24829498
        },
        {
            "latitude1": "16°39′49″S",
            "latitude2": -16.6636606,
            "longitude1": "49°18′48″W",
            "longitude2": -49.31333064
        },
        {
            "latitude1": "16°38′10″S",
            "latitude2": -16.63621587,
            "longitude1": "49°15′06″W",
            "longitude2": -49.25156257
        },
        {
            "latitude1": "16°37′40″S",
            "latitude2": -16.62774609,
            "longitude1": "49°12′44″W",
            "longitude2": -49.21231692
        },
        {
            "latitude1": "16°44′04″S",
            "latitude2": -16.73457704,
            "longitude1": "49°10′54″W",
            "longitude2": -49.18166302
        },
        {
            "latitude1": "16°41′10″S",
            "latitude2": -16.68614755,
            "longitude1": "49°10′20″W",
            "longitude2": -49.17217846
        },
        {
            "latitude1": "16°38′58″S",
            "latitude2": -16.64956964,
            "longitude1": "49°17′50″W",
            "longitude2": -49.29719894
        },
        {
            "latitude1": "16°40′52″S",
            "latitude2": -16.68105345,
            "longitude1": "49°18′20″W",
            "longitude2": -49.30554375
        },
        {
            "latitude1": "16°44′42″S",
            "latitude2": -16.74509493,
            "longitude1": "49°16′16″W",
            "longitude2": -49.27106716
        },
        {
            "latitude1": "16°36′58″S",
            "latitude2": -16.61611454,
            "longitude1": "49°16′27″W",
            "longitude2": -49.27410939
        },
        {
            "latitude1": "16°38′30″S",
            "latitude2": -16.64171088,
            "longitude1": "49°16′29″W",
            "longitude2": -49.27466199
        },
        {
            "latitude1": "16°35′35″S",
            "latitude2": -16.59303877,
            "longitude1": "49°14′43″W",
            "longitude2": -49.24535145
        },
        {
            "latitude1": "16°39′05″S",
            "latitude2": -16.65133402,
            "longitude1": "49°16′48″W",
            "longitude2": -49.27992911
        },
        {
            "latitude1": "16°39′08″S",
            "latitude2": -16.65225273,
            "longitude1": "49°16′20″W",
            "longitude2": -49.27227925
        },
        {
            "latitude1": "16°44′09″S",
            "latitude2": -16.73596134,
            "longitude1": "49°18′25″W",
            "longitude2": -49.3068541
        },
        {
            "latitude1": "16°46′12″S",
            "latitude2": -16.77013302,
            "longitude1": "49°15′30″W",
            "longitude2": -49.25836367
        },
        {
            "latitude1": "16°39′08″S",
            "latitude2": -16.65219946,
            "longitude1": "49°18′50″W",
            "longitude2": -49.31381932
        },
        {
            "latitude1": "16°38′01″S",
            "latitude2": -16.63364979,
            "longitude1": "49°11′23″W",
            "longitude2": -49.18960931
        },
        {
            "latitude1": "16°41′04″S",
            "latitude2": -16.68436635,
            "longitude1": "49°10′14″W",
            "longitude2": -49.1706065
        },
        {
            "latitude1": "16°45′45″S",
            "latitude2": -16.76251747,
            "longitude1": "49°14′15″W",
            "longitude2": -49.23763283
        },
        {
            "latitude1": "16°37′16″S",
            "latitude2": -16.62119744,
            "longitude1": "49°11′57″W",
            "longitude2": -49.19906393
        },
        {
            "latitude1": "16°37′14″S",
            "latitude2": -16.620636,
            "longitude1": "49°19′25″W",
            "longitude2": -49.32371839
        },
        {
            "latitude1": "16°43′04″S",
            "latitude2": -16.71769304,
            "longitude1": "49°12′54″W",
            "longitude2": -49.21503622
        },
        {
            "latitude1": "16°40′38″S",
            "latitude2": -16.67734898,
            "longitude1": "49°15′45″W",
            "longitude2": -49.26243974
        },
        {
            "latitude1": "16°39′36″S",
            "latitude2": -16.66007187,
            "longitude1": "49°15′05″W",
            "longitude2": -49.25135043
        },
        {
            "latitude1": "16°44′44″S",
            "latitude2": -16.74554536,
            "longitude1": "49°12′34″W",
            "longitude2": -49.20944928
        },
        {
            "latitude1": "16°37′59″S",
            "latitude2": -16.63331477,
            "longitude1": "49°14′07″W",
            "longitude2": -49.23523107
        },
        {
            "latitude1": "16°42′59″S",
            "latitude2": -16.71675657,
            "longitude1": "49°11′16″W",
            "longitude2": -49.18773645
        },
        {
            "latitude1": "16°38′57″S",
            "latitude2": -16.64917912,
            "longitude1": "49°14′26″W",
            "longitude2": -49.24061074
        },
        {
            "latitude1": "16°44′17″S",
            "latitude2": -16.73802757,
            "longitude1": "49°14′00″W",
            "longitude2": -49.23346117
        },
        {
            "latitude1": "16°43′54″S",
            "latitude2": -16.73168034,
            "longitude1": "49°18′05″W",
            "longitude2": -49.30148189
        },
        {
            "latitude1": "16°42′10″S",
            "latitude2": -16.70267425,
            "longitude1": "49°16′49″W",
            "longitude2": -49.28020132
        },
        {
            "latitude1": "16°37′36″S",
            "latitude2": -16.62656398,
            "longitude1": "49°18′14″W",
            "longitude2": -49.30399029
        },
        {
            "latitude1": "16°35′46″S",
            "latitude2": -16.59617731,
            "longitude1": "49°16′51″W",
            "longitude2": -49.28080341
        },
        {
            "latitude1": "16°42′48″S",
            "latitude2": -16.71344826,
            "longitude1": "49°14′00″W",
            "longitude2": -49.23324296
        },
        {
            "latitude1": "16°40′11″S",
            "latitude2": -16.66972318,
            "longitude1": "49°11′37″W",
            "longitude2": -49.19371937
        },
        {
            "latitude1": "16°41′59″S",
            "latitude2": -16.69988468,
            "longitude1": "49°09′56″W",
            "longitude2": -49.1655871
        },
        {
            "latitude1": "16°42′22″S",
            "latitude2": -16.70618425,
            "longitude1": "49°16′43″W",
            "longitude2": -49.27852544
        },
        {
            "latitude1": "16°38′20″S",
            "latitude2": -16.63902526,
            "longitude1": "49°12′22″W",
            "longitude2": -49.2061201
        },
        {
            "latitude1": "16°40′06″S",
            "latitude2": -16.66840743,
            "longitude1": "49°15′21″W",
            "longitude2": -49.25596177
        },
        {
            "latitude1": "16°42′16″S",
            "latitude2": -16.70439771,
            "longitude1": "49°12′46″W",
            "longitude2": -49.2127238
        },
        {
            "latitude1": "16°43′07″S",
            "latitude2": -16.71858907,
            "longitude1": "49°15′56″W",
            "longitude2": -49.26552988
        },
        {
            "latitude1": "16°40′42″S",
            "latitude2": -16.67823939,
            "longitude1": "49°13′24″W",
            "longitude2": -49.22328674
        },
        {
            "latitude1": "16°40′02″S",
            "latitude2": -16.66734207,
            "longitude1": "49°20′06″W",
            "longitude2": -49.33489986
        },
        {
            "latitude1": "16°41′06″S",
            "latitude2": -16.68507724,
            "longitude1": "49°18′56″W",
            "longitude2": -49.31568916
        },
        {
            "latitude1": "16°36′22″S",
            "latitude2": -16.60621089,
            "longitude1": "49°18′22″W",
            "longitude2": -49.30617465
        },
        {
            "latitude1": "16°40′49″S",
            "latitude2": -16.68034563,
            "longitude1": "49°17′06″W",
            "longitude2": -49.285067
        },
        {
            "latitude1": "16°43′41″S",
            "latitude2": -16.72802857,
            "longitude1": "49°12′35″W",
            "longitude2": -49.20977278
        },
        {
            "latitude1": "16°37′01″S",
            "latitude2": -16.61703902,
            "longitude1": "49°12′38″W",
            "longitude2": -49.21068215
        },
        {
            "latitude1": "16°45′44″S",
            "latitude2": -16.76224371,
            "longitude1": "49°17′25″W",
            "longitude2": -49.29028852
        },
        {
            "latitude1": "16°37′51″S",
            "latitude2": -16.63092711,
            "longitude1": "49°11′12″W",
            "longitude2": -49.18671936
        },
        {
            "latitude1": "16°37′33″S",
            "latitude2": -16.62579446,
            "longitude1": "49°19′44″W",
            "longitude2": -49.32887204
        },
        {
            "latitude1": "16°41′03″S",
            "latitude2": -16.68409471,
            "longitude1": "49°13′42″W",
            "longitude2": -49.22824249
        },
        {
            "latitude1": "16°45′16″S",
            "latitude2": -16.75433097,
            "longitude1": "49°13′49″W",
            "longitude2": -49.23040504
        },
        {
            "latitude1": "16°36′18″S",
            "latitude2": -16.60493711,
            "longitude1": "49°17′31″W",
            "longitude2": -49.29187444
        },
        {
            "latitude1": "16°40′32″S",
            "latitude2": -16.67542476,
            "longitude1": "49°19′25″W",
            "longitude2": -49.32349337
        },
        {
            "latitude1": "16°37′31″S",
            "latitude2": -16.62529785,
            "longitude1": "49°13′17″W",
            "longitude2": -49.22143047
        },
        {
            "latitude1": "16°42′48″S",
            "latitude2": -16.71320661,
            "longitude1": "49°17′45″W",
            "longitude2": -49.29595755
        },
        {
            "latitude1": "16°37′13″S",
            "latitude2": -16.6203255,
            "longitude1": "49°15′39″W",
            "longitude2": -49.26074123
        },
        {
            "latitude1": "16°41′45″S",
            "latitude2": -16.69585594,
            "longitude1": "49°20′21″W",
            "longitude2": -49.33905245
        },
        {
            "latitude1": "16°38′10″S",
            "latitude2": -16.63610231,
            "longitude1": "49°11′25″W",
            "longitude2": -49.19021059
        },
        {
            "latitude1": "16°44′05″S",
            "latitude2": -16.7346966,
            "longitude1": "49°18′17″W",
            "longitude2": -49.30485223
        },
        {
            "latitude1": "16°38′54″S",
            "latitude2": -16.64846336,
            "longitude1": "49°17′35″W",
            "longitude2": -49.29294114
        },
        {
            "latitude1": "16°42′12″S",
            "latitude2": -16.70346781,
            "longitude1": "49°20′08″W",
            "longitude2": -49.33559556
        },
        {
            "latitude1": "16°38′47″S",
            "latitude2": -16.64627469,
            "longitude1": "49°10′24″W",
            "longitude2": -49.1733119
        },
        {
            "latitude1": "16°42′51″S",
            "latitude2": -16.71423661,
            "longitude1": "49°16′29″W",
            "longitude2": -49.27479729
        },
        {
            "latitude1": "16°35′54″S",
            "latitude2": -16.59833608,
            "longitude1": "49°15′15″W",
            "longitude2": -49.25403847
        },
        {
            "latitude1": "16°43′10″S",
            "latitude2": -16.71937022,
            "longitude1": "49°12′18″W",
            "longitude2": -49.20504928
        },
        {
            "latitude1": "16°39′59″S",
            "latitude2": -16.66636399,
            "longitude1": "49°15′26″W",
            "longitude2": -49.25734527
        },
        {
            "latitude1": "16°37′43″S",
            "latitude2": -16.62870562,
            "longitude1": "49°15′16″W",
            "longitude2": -49.25434084
        },
        {
            "latitude1": "16°44′06″S",
            "latitude2": -16.73494636,
            "longitude1": "49°14′03″W",
            "longitude2": -49.23426236
        },
        {
            "latitude1": "16°41′56″S",
            "latitude2": -16.69881242,
            "longitude1": "49°18′44″W",
            "longitude2": -49.3123422
        },
        {
            "latitude1": "16°44′43″S",
            "latitude2": -16.74535562,
            "longitude1": "49°16′59″W",
            "longitude2": -49.2831708
        },
        {
            "latitude1": "16°42′43″S",
            "latitude2": -16.71188038,
            "longitude1": "49°19′11″W",
            "longitude2": -49.31979765
        },
        {
            "latitude1": "16°43′48″S",
            "latitude2": -16.73012721,
            "longitude1": "49°15′25″W",
            "longitude2": -49.25699908
        },
        {
            "latitude1": "16°38′39″S",
            "latitude2": -16.64428463,
            "longitude1": "49°19′12″W",
            "longitude2": -49.32003698
        },
        {
            "latitude1": "16°44′19″S",
            "latitude2": -16.73857884,
            "longitude1": "49°16′20″W",
            "longitude2": -49.27212167
        },
        {
            "latitude1": "16°39′44″S",
            "latitude2": -16.66234972,
            "longitude1": "49°17′39″W",
            "longitude2": -49.29416878
        },
        {
            "latitude1": "16°42′50″S",
            "latitude2": -16.71380386,
            "longitude1": "49°19′02″W",
            "longitude2": -49.31722745
        },
        {
            "latitude1": "16°43′31″S",
            "latitude2": -16.72516883,
            "longitude1": "49°14′18″W",
            "longitude2": -49.23824239
        },
        {
            "latitude1": "16°38′39″S",
            "latitude2": -16.64420217,
            "longitude1": "49°13′28″W",
            "longitude2": -49.22431545
        },
        {
            "latitude1": "16°41′22″S",
            "latitude2": -16.68954124,
            "longitude1": "49°10′25″W",
            "longitude2": -49.17354157
        },
        {
            "latitude1": "16°40′03″S",
            "latitude2": -16.66749122,
            "longitude1": "49°16′57″W",
            "longitude2": -49.28252091
        },
        {
            "latitude1": "16°38′05″S",
            "latitude2": -16.63483649,
            "longitude1": "49°11′24″W",
            "longitude2": -49.18994962
        },
        {
            "latitude1": "16°35′40″S",
            "latitude2": -16.59442191,
            "longitude1": "49°15′02″W",
            "longitude2": -49.25061499
        },
        {
            "latitude1": "16°39′34″S",
            "latitude2": -16.65945333,
            "longitude1": "49°12′52″W",
            "longitude2": -49.21449793
        },
        {
            "latitude1": "16°36′12″S",
            "latitude2": -16.60330517,
            "longitude1": "49°16′32″W",
            "longitude2": -49.27542966
        },
        {
            "latitude1": "16°39′32″S",
            "latitude2": -16.65888001,
            "longitude1": "49°17′58″W",
            "longitude2": -49.29940388
        },
        {
            "latitude1": "16°38′16″S",
            "latitude2": -16.63784058,
            "longitude1": "49°18′57″W",
            "longitude2": -49.3157598
        },
        {
            "latitude1": "16°43′56″S",
            "latitude2": -16.73228294,
            "longitude1": "49°16′14″W",
            "longitude2": -49.27066271
        },
        {
            "latitude1": "16°38′08″S",
            "latitude2": -16.63559231,
            "longitude1": "49°13′20″W",
            "longitude2": -49.22220337
        },
        {
            "latitude1": "16°41′25″S",
            "latitude2": -16.69026981,
            "longitude1": "49°16′16″W",
            "longitude2": -49.27104939
        },
        {
            "latitude1": "16°41′30″S",
            "latitude2": -16.69161111,
            "longitude1": "49°16′08″W",
            "longitude2": -49.26885521
        },
        {
            "latitude1": "16°40′31″S",
            "latitude2": -16.67529913,
            "longitude1": "49°16′55″W",
            "longitude2": -49.28196422
        },
        {
            "latitude1": "16°42′25″S",
            "latitude2": -16.70690567,
            "longitude1": "49°12′59″W",
            "longitude2": -49.21651264
        },
        {
            "latitude1": "16°37′57″S",
            "latitude2": -16.63253226,
            "longitude1": "49°12′27″W",
            "longitude2": -49.2075546
        },
        {
            "latitude1": "16°41′24″S",
            "latitude2": -16.69009382,
            "longitude1": "49°18′03″W",
            "longitude2": -49.30091994
        },
        {
            "latitude1": "16°40′11″S",
            "latitude2": -16.6696026,
            "longitude1": "49°11′37″W",
            "longitude2": -49.19354632
        },
        {
            "latitude1": "16°42′33″S",
            "latitude2": -16.70930402,
            "longitude1": "49°19′54″W",
            "longitude2": -49.3316794
        },
        {
            "latitude1": "16°43′40″S",
            "latitude2": -16.72789656,
            "longitude1": "49°12′04″W",
            "longitude2": -49.20106912
        },
        {
            "latitude1": "16°36′06″S",
            "latitude2": -16.60179068,
            "longitude1": "49°13′40″W",
            "longitude2": -49.22780634
        },
        {
            "latitude1": "16°37′04″S",
            "latitude2": -16.61785627,
            "longitude1": "49°17′35″W",
            "longitude2": -49.29296358
        },
        {
            "latitude1": "16°35′43″S",
            "latitude2": -16.59533983,
            "longitude1": "49°13′43″W",
            "longitude2": -49.22868623
        },
        {
            "latitude1": "16°40′54″S",
            "latitude2": -16.68180418,
            "longitude1": "49°16′31″W",
            "longitude2": -49.27538316
        },
        {
            "latitude1": "16°36′46″S",
            "latitude2": -16.61287697,
            "longitude1": "49°18′34″W",
            "longitude2": -49.30934692
        },
        {
            "latitude1": "16°44′03″S",
            "latitude2": -16.73426688,
            "longitude1": "49°13′15″W",
            "longitude2": -49.22090629
        },
        {
            "latitude1": "16°36′51″S",
            "latitude2": -16.61422256,
            "longitude1": "49°13′06″W",
            "longitude2": -49.2184582
        },
        {
            "latitude1": "16°45′21″S",
            "latitude2": -16.75583684,
            "longitude1": "49°17′07″W",
            "longitude2": -49.28529323
        },
        {
            "latitude1": "16°39′31″S",
            "latitude2": -16.65871999,
            "longitude1": "49°15′57″W",
            "longitude2": -49.26576474
        },
        {
            "latitude1": "16°36′09″S",
            "latitude2": -16.60262281,
            "longitude1": "49°18′08″W",
            "longitude2": -49.30231996
        },
        {
            "latitude1": "16°40′25″S",
            "latitude2": -16.67352968,
            "longitude1": "49°14′28″W",
            "longitude2": -49.24120349
        },
        {
            "latitude1": "16°39′48″S",
            "latitude2": -16.66336933,
            "longitude1": "49°19′06″W",
            "longitude2": -49.31835147
        },
        {
            "latitude1": "16°43′02″S",
            "latitude2": -16.71714456,
            "longitude1": "49°11′22″W",
            "longitude2": -49.18955192
        },
        {
            "latitude1": "16°38′49″S",
            "latitude2": -16.64685895,
            "longitude1": "49°15′11″W",
            "longitude2": -49.2530489
        },
        {
            "latitude1": "16°41′37″S",
            "latitude2": -16.69350201,
            "longitude1": "49°13′59″W",
            "longitude2": -49.23314999
        },
        {
            "latitude1": "16°43′40″S",
            "latitude2": -16.72769449,
            "longitude1": "49°13′42″W",
            "longitude2": -49.22843039
        },
        {
            "latitude1": "16°42′20″S",
            "latitude2": -16.70552192,
            "longitude1": "49°13′17″W",
            "longitude2": -49.2213285
        },
        {
            "latitude1": "16°37′59″S",
            "latitude2": -16.63316679,
            "longitude1": "49°11′08″W",
            "longitude2": -49.18553948
        },
        {
            "latitude1": "16°44′17″S",
            "latitude2": -16.73802496,
            "longitude1": "49°11′14″W",
            "longitude2": -49.18712977
        },
        {
            "latitude1": "16°40′20″S",
            "latitude2": -16.67215561,
            "longitude1": "49°14′10″W",
            "longitude2": -49.23619445
        },
        {
            "latitude1": "16°42′20″S",
            "latitude2": -16.70546619,
            "longitude1": "49°12′50″W",
            "longitude2": -49.21376969
        },
        {
            "latitude1": "16°38′55″S",
            "latitude2": -16.64860964,
            "longitude1": "49°19′00″W",
            "longitude2": -49.31671395
        },
        {
            "latitude1": "16°39′23″S",
            "latitude2": -16.65627135,
            "longitude1": "49°20′30″W",
            "longitude2": -49.34171899
        },
        {
            "latitude1": "16°39′35″S",
            "latitude2": -16.65968913,
            "longitude1": "49°14′22″W",
            "longitude2": -49.23939151
        },
        {
            "latitude1": "16°42′39″S",
            "latitude2": -16.71069651,
            "longitude1": "49°13′52″W",
            "longitude2": -49.23115419
        },
        {
            "latitude1": "16°41′42″S",
            "latitude2": -16.69508221,
            "longitude1": "49°14′49″W",
            "longitude2": -49.24705094
        },
        {
            "latitude1": "16°38′08″S",
            "latitude2": -16.63568297,
            "longitude1": "49°18′35″W",
            "longitude2": -49.30975971
        },
        {
            "latitude1": "16°36′06″S",
            "latitude2": -16.60162321,
            "longitude1": "49°14′40″W",
            "longitude2": -49.24439561
        },
        {
            "latitude1": "16°39′57″S",
            "latitude2": -16.66587306,
            "longitude1": "49°13′06″W",
            "longitude2": -49.21824208
        },
        {
            "latitude1": "16°39′37″S",
            "latitude2": -16.66041213,
            "longitude1": "49°14′32″W",
            "longitude2": -49.24208533
        },
        {
            "latitude1": "16°35′52″S",
            "latitude2": -16.59788419,
            "longitude1": "49°14′32″W",
            "longitude2": -49.24211458
        },
        {
            "latitude1": "16°37′26″S",
            "latitude2": -16.62395033,
            "longitude1": "49°13′44″W",
            "longitude2": -49.22898349
        },
        {
            "latitude1": "16°36′38″S",
            "latitude2": -16.61056959,
            "longitude1": "49°17′34″W",
            "longitude2": -49.29279915
        },
        {
            "latitude1": "16°40′21″S",
            "latitude2": -16.67241435,
            "longitude1": "49°17′32″W",
            "longitude2": -49.29234407
        },
        {
            "latitude1": "16°39′23″S",
            "latitude2": -16.65652204,
            "longitude1": "49°15′32″W",
            "longitude2": -49.25888668
        },
        {
            "latitude1": "16°43′05″S",
            "latitude2": -16.71814618,
            "longitude1": "49°10′29″W",
            "longitude2": -49.17481293
        },
        {
            "latitude1": "16°38′16″S",
            "latitude2": -16.63785038,
            "longitude1": "49°20′13″W",
            "longitude2": -49.33696171
        },
        {
            "latitude1": "16°40′43″S",
            "latitude2": -16.67865793,
            "longitude1": "49°10′07″W",
            "longitude2": -49.16850157
        },
        {
            "latitude1": "16°43′26″S",
            "latitude2": -16.72384821,
            "longitude1": "49°18′43″W",
            "longitude2": -49.3118388
        },
        {
            "latitude1": "16°44′31″S",
            "latitude2": -16.74205918,
            "longitude1": "49°11′45″W",
            "longitude2": -49.19573876
        },
        {
            "latitude1": "16°43′37″S",
            "latitude2": -16.72701903,
            "longitude1": "49°17′30″W",
            "longitude2": -49.29154677
        },
        {
            "latitude1": "16°35′38″S",
            "latitude2": -16.59381405,
            "longitude1": "49°16′32″W",
            "longitude2": -49.2755451
        },
        {
            "latitude1": "16°36′55″S",
            "latitude2": -16.61528996,
            "longitude1": "49°14′39″W",
            "longitude2": -49.24426488
        },
        {
            "latitude1": "16°44′06″S",
            "latitude2": -16.7349388,
            "longitude1": "49°13′44″W",
            "longitude2": -49.22896665
        },
        {
            "latitude1": "16°37′26″S",
            "latitude2": -16.62395343,
            "longitude1": "49°17′08″W",
            "longitude2": -49.28562873
        },
        {
            "latitude1": "16°37′20″S",
            "latitude2": -16.62234327,
            "longitude1": "49°15′33″W",
            "longitude2": -49.25915141
        },
        {
            "latitude1": "16°39′27″S",
            "latitude2": -16.6575704,
            "longitude1": "49°10′52″W",
            "longitude2": -49.18120557
        },
        {
            "latitude1": "16°43′28″S",
            "latitude2": -16.72432109,
            "longitude1": "49°19′22″W",
            "longitude2": -49.3227537
        },
        {
            "latitude1": "16°36′51″S",
            "latitude2": -16.61420723,
            "longitude1": "49°18′28″W",
            "longitude2": -49.30770946
        },
        {
            "latitude1": "16°36′24″S",
            "latitude2": -16.60653355,
            "longitude1": "49°17′17″W",
            "longitude2": -49.28808949
        },
        {
            "latitude1": "16°37′23″S",
            "latitude2": -16.62293292,
            "longitude1": "49°18′37″W",
            "longitude2": -49.31040396
        },
        {
            "latitude1": "16°44′36″S",
            "latitude2": -16.74334086,
            "longitude1": "49°15′36″W",
            "longitude2": -49.25995692
        },
        {
            "latitude1": "16°37′06″S",
            "latitude2": -16.61835375,
            "longitude1": "49°16′55″W",
            "longitude2": -49.28181719
        },
        {
            "latitude1": "16°37′30″S",
            "latitude2": -16.62487524,
            "longitude1": "49°13′54″W",
            "longitude2": -49.23174911
        },
        {
            "latitude1": "16°38′59″S",
            "latitude2": -16.64972834,
            "longitude1": "49°15′51″W",
            "longitude2": -49.2641759
        },
        {
            "latitude1": "16°44′44″S",
            "latitude2": -16.74546183,
            "longitude1": "49°13′03″W",
            "longitude2": -49.21761916
        },
        {
            "latitude1": "16°44′57″S",
            "latitude2": -16.74926803,
            "longitude1": "49°12′27″W",
            "longitude2": -49.20750609
        },
        {
            "latitude1": "16°41′56″S",
            "latitude2": -16.69888107,
            "longitude1": "49°15′31″W",
            "longitude2": -49.25848739
        },
        {
            "latitude1": "16°41′27″S",
            "latitude2": -16.69091546,
            "longitude1": "49°19′29″W",
            "longitude2": -49.32475477
        },
        {
            "latitude1": "16°37′18″S",
            "latitude2": -16.62162888,
            "longitude1": "49°13′34″W",
            "longitude2": -49.22613055
        },
        {
            "latitude1": "16°43′13″S",
            "latitude2": -16.72040524,
            "longitude1": "49°15′49″W",
            "longitude2": -49.26363996
        },
        {
            "latitude1": "16°40′34″S",
            "latitude2": -16.67604827,
            "longitude1": "49°10′14″W",
            "longitude2": -49.17057584
        },
        {
            "latitude1": "16°39′51″S",
            "latitude2": -16.66415297,
            "longitude1": "49°17′34″W",
            "longitude2": -49.29274813
        },
        {
            "latitude1": "16°43′39″S",
            "latitude2": -16.72755422,
            "longitude1": "49°14′02″W",
            "longitude2": -49.23391676
        },
        {
            "latitude1": "16°38′40″S",
            "latitude2": -16.6443933,
            "longitude1": "49°14′32″W",
            "longitude2": -49.24211337
        },
        {
            "latitude1": "16°40′03″S",
            "latitude2": -16.66738371,
            "longitude1": "49°16′30″W",
            "longitude2": -49.27491794
        },
        {
            "latitude1": "16°40′02″S",
            "latitude2": -16.6672344,
            "longitude1": "49°13′05″W",
            "longitude2": -49.21808406
        },
        {
            "latitude1": "16°44′05″S",
            "latitude2": -16.73479236,
            "longitude1": "49°11′45″W",
            "longitude2": -49.19588627
        },
        {
            "latitude1": "16°42′32″S",
            "latitude2": -16.70890751,
            "longitude1": "49°19′31″W",
            "longitude2": -49.32520186
        },
        {
            "latitude1": "16°40′09″S",
            "latitude2": -16.66915414,
            "longitude1": "49°10′57″W",
            "longitude2": -49.18246031
        },
        {
            "latitude1": "16°39′07″S",
            "latitude2": -16.65206634,
            "longitude1": "49°14′54″W",
            "longitude2": -49.24839942
        },
        {
            "latitude1": "16°44′09″S",
            "latitude2": -16.7359082,
            "longitude1": "49°15′20″W",
            "longitude2": -49.2555886
        },
        {
            "latitude1": "16°40′07″S",
            "latitude2": -16.66851431,
            "longitude1": "49°10′45″W",
            "longitude2": -49.1790294
        },
        {
            "latitude1": "16°36′33″S",
            "latitude2": -16.60930045,
            "longitude1": "49°16′25″W",
            "longitude2": -49.2735273
        },
        {
            "latitude1": "16°38′39″S",
            "latitude2": -16.64426785,
            "longitude1": "49°15′39″W",
            "longitude2": -49.26090862
        },
        {
            "latitude1": "16°41′05″S",
            "latitude2": -16.68461545,
            "longitude1": "49°16′16″W",
            "longitude2": -49.27121498
        },
        {
            "latitude1": "16°37′11″S",
            "latitude2": -16.6198157,
            "longitude1": "49°18′16″W",
            "longitude2": -49.3043769
        },
        {
            "latitude1": "16°42′42″S",
            "latitude2": -16.71175566,
            "longitude1": "49°17′30″W",
            "longitude2": -49.29176502
        },
        {
            "latitude1": "16°37′36″S",
            "latitude2": -16.62663657,
            "longitude1": "49°18′12″W",
            "longitude2": -49.30342489
        },
        {
            "latitude1": "16°42′43″S",
            "latitude2": -16.71182046,
            "longitude1": "49°16′25″W",
            "longitude2": -49.27363121
        },
        {
            "latitude1": "16°45′57″S",
            "latitude2": -16.76596559,
            "longitude1": "49°14′44″W",
            "longitude2": -49.24554575
        },
        {
            "latitude1": "16°42′54″S",
            "latitude2": -16.7149385,
            "longitude1": "49°11′05″W",
            "longitude2": -49.18480993
        },
        {
            "latitude1": "16°45′36″S",
            "latitude2": -16.76012644,
            "longitude1": "49°17′53″W",
            "longitude2": -49.29791945
        },
        {
            "latitude1": "16°41′56″S",
            "latitude2": -16.69878387,
            "longitude1": "49°19′17″W",
            "longitude2": -49.32137079
        },
        {
            "latitude1": "16°36′15″S",
            "latitude2": -16.60429944,
            "longitude1": "49°12′27″W",
            "longitude2": -49.20763296
        },
        {
            "latitude1": "16°41′37″S",
            "latitude2": -16.69348353,
            "longitude1": "49°16′41″W",
            "longitude2": -49.27810077
        },
        {
            "latitude1": "16°39′23″S",
            "latitude2": -16.6564013,
            "longitude1": "49°18′54″W",
            "longitude2": -49.31486647
        },
        {
            "latitude1": "16°36′51″S",
            "latitude2": -16.61404957,
            "longitude1": "49°14′13″W",
            "longitude2": -49.23700638
        },
        {
            "latitude1": "16°42′35″S",
            "latitude2": -16.70975912,
            "longitude1": "49°10′59″W",
            "longitude2": -49.18327425
        },
        {
            "latitude1": "16°42′36″S",
            "latitude2": -16.71005403,
            "longitude1": "49°16′36″W",
            "longitude2": -49.27653436
        },
        {
            "latitude1": "16°39′19″S",
            "latitude2": -16.65532787,
            "longitude1": "49°13′44″W",
            "longitude2": -49.22886047
        },
        {
            "latitude1": "16°40′38″S",
            "latitude2": -16.67731133,
            "longitude1": "49°18′29″W",
            "longitude2": -49.30799678
        },
        {
            "latitude1": "16°38′59″S",
            "latitude2": -16.64989447,
            "longitude1": "49°12′36″W",
            "longitude2": -49.21009276
        },
        {
            "latitude1": "16°41′13″S",
            "latitude2": -16.6870815,
            "longitude1": "49°16′12″W",
            "longitude2": -49.26987827
        },
        {
            "latitude1": "16°39′54″S",
            "latitude2": -16.66509725,
            "longitude1": "49°14′10″W",
            "longitude2": -49.23606593
        },
        {
            "latitude1": "16°39′39″S",
            "latitude2": -16.66089296,
            "longitude1": "49°13′49″W",
            "longitude2": -49.23026012
        },
        {
            "latitude1": "16°36′54″S",
            "latitude2": -16.61504646,
            "longitude1": "49°14′47″W",
            "longitude2": -49.24641713
        },
        {
            "latitude1": "16°40′16″S",
            "latitude2": -16.67124584,
            "longitude1": "49°16′11″W",
            "longitude2": -49.26983543
        },
        {
            "latitude1": "16°39′12″S",
            "latitude2": -16.65325197,
            "longitude1": "49°10′52″W",
            "longitude2": -49.18122829
        },
        {
            "latitude1": "16°38′34″S",
            "latitude2": -16.64291582,
            "longitude1": "49°12′38″W",
            "longitude2": -49.21044762
        },
        {
            "latitude1": "16°43′28″S",
            "latitude2": -16.72454296,
            "longitude1": "49°12′32″W",
            "longitude2": -49.20879611
        },
        {
            "latitude1": "16°43′08″S",
            "latitude2": -16.71886331,
            "longitude1": "49°10′24″W",
            "longitude2": -49.1732806
        },
        {
            "latitude1": "16°39′07″S",
            "latitude2": -16.65204882,
            "longitude1": "49°14′18″W",
            "longitude2": -49.2382345
        },
        {
            "latitude1": "16°41′13″S",
            "latitude2": -16.68702594,
            "longitude1": "49°20′04″W",
            "longitude2": -49.33456849
        },
        {
            "latitude1": "16°45′53″S",
            "latitude2": -16.7645899,
            "longitude1": "49°16′41″W",
            "longitude2": -49.27802188
        },
        {
            "latitude1": "16°39′06″S",
            "latitude2": -16.65173009,
            "longitude1": "49°19′24″W",
            "longitude2": -49.32332669
        },
        {
            "latitude1": "16°38′58″S",
            "latitude2": -16.64934504,
            "longitude1": "49°11′46″W",
            "longitude2": -49.19599098
        },
        {
            "latitude1": "16°42′47″S",
            "latitude2": -16.71317899,
            "longitude1": "49°17′01″W",
            "longitude2": -49.28366797
        },
        {
            "latitude1": "16°41′42″S",
            "latitude2": -16.69490485,
            "longitude1": "49°16′56″W",
            "longitude2": -49.2822485
        },
        {
            "latitude1": "16°39′04″S",
            "latitude2": -16.65119508,
            "longitude1": "49°15′49″W",
            "longitude2": -49.26358981
        },
        {
            "latitude1": "16°37′18″S",
            "latitude2": -16.62179603,
            "longitude1": "49°16′23″W",
            "longitude2": -49.27308021
        },
        {
            "latitude1": "16°39′56″S",
            "latitude2": -16.66557177,
            "longitude1": "49°19′43″W",
            "longitude2": -49.32855249
        },
        {
            "latitude1": "16°45′47″S",
            "latitude2": -16.76292616,
            "longitude1": "49°15′44″W",
            "longitude2": -49.26224535
        },
        {
            "latitude1": "16°41′30″S",
            "latitude2": -16.69167151,
            "longitude1": "49°17′07″W",
            "longitude2": -49.28540414
        },
        {
            "latitude1": "16°37′11″S",
            "latitude2": -16.61959674,
            "longitude1": "49°14′21″W",
            "longitude2": -49.23918023
        },
        {
            "latitude1": "16°41′41″S",
            "latitude2": -16.69469931,
            "longitude1": "49°18′11″W",
            "longitude2": -49.30310043
        },
        {
            "latitude1": "16°41′45″S",
            "latitude2": -16.69588382,
            "longitude1": "49°12′31″W",
            "longitude2": -49.20858555
        },
        {
            "latitude1": "16°42′45″S",
            "latitude2": -16.71251861,
            "longitude1": "49°20′18″W",
            "longitude2": -49.33839097
        },
        {
            "latitude1": "16°41′41″S",
            "latitude2": -16.69476828,
            "longitude1": "49°10′45″W",
            "longitude2": -49.17924398
        },
        {
            "latitude1": "16°40′17″S",
            "latitude2": -16.67126755,
            "longitude1": "49°17′33″W",
            "longitude2": -49.29259366
        },
        {
            "latitude1": "16°42′55″S",
            "latitude2": -16.71528203,
            "longitude1": "49°15′19″W",
            "longitude2": -49.25537736
        },
        {
            "latitude1": "16°38′38″S",
            "latitude2": -16.64380049,
            "longitude1": "49°11′56″W",
            "longitude2": -49.1989884
        },
        {
            "latitude1": "16°46′01″S",
            "latitude2": -16.76683807,
            "longitude1": "49°14′47″W",
            "longitude2": -49.24651211
        },
        {
            "latitude1": "16°36′57″S",
            "latitude2": -16.61579988,
            "longitude1": "49°14′40″W",
            "longitude2": -49.24438263
        },
        {
            "latitude1": "16°41′24″S",
            "latitude2": -16.68997762,
            "longitude1": "49°15′19″W",
            "longitude2": -49.25518404
        },
        {
            "latitude1": "16°44′22″S",
            "latitude2": -16.73941845,
            "longitude1": "49°15′54″W",
            "longitude2": -49.26504129
        },
        {
            "latitude1": "16°41′35″S",
            "latitude2": -16.69306928,
            "longitude1": "49°13′57″W",
            "longitude2": -49.23241142
        },
        {
            "latitude1": "16°39′07″S",
            "latitude2": -16.65196604,
            "longitude1": "49°13′00″W",
            "longitude2": -49.21668643
        },
        {
            "latitude1": "16°37′15″S",
            "latitude2": -16.62089673,
            "longitude1": "49°18′22″W",
            "longitude2": -49.30608787
        },
        {
            "latitude1": "16°41′24″S",
            "latitude2": -16.68995558,
            "longitude1": "49°15′48″W",
            "longitude2": -49.26333049
        },
        {
            "latitude1": "16°36′26″S",
            "latitude2": -16.60728425,
            "longitude1": "49°16′03″W",
            "longitude2": -49.26747215
        },
        {
            "latitude1": "16°40′49″S",
            "latitude2": -16.68035231,
            "longitude1": "49°16′41″W",
            "longitude2": -49.27819011
        },
        {
            "latitude1": "16°39′45″S",
            "latitude2": -16.66254721,
            "longitude1": "49°20′11″W",
            "longitude2": -49.33626438
        },
        {
            "latitude1": "16°43′42″S",
            "latitude2": -16.72847013,
            "longitude1": "49°18′41″W",
            "longitude2": -49.31141478
        },
        {
            "latitude1": "16°39′11″S",
            "latitude2": -16.65300081,
            "longitude1": "49°10′52″W",
            "longitude2": -49.18101436
        },
        {
            "latitude1": "16°38′36″S",
            "latitude2": -16.64338355,
            "longitude1": "49°14′48″W",
            "longitude2": -49.24661548
        },
        {
            "latitude1": "16°39′01″S",
            "latitude2": -16.65025866,
            "longitude1": "49°14′25″W",
            "longitude2": -49.24024318
        },
        {
            "latitude1": "16°42′07″S",
            "latitude2": -16.7020036,
            "longitude1": "49°10′27″W",
            "longitude2": -49.17411813
        },
        {
            "latitude1": "16°37′56″S",
            "latitude2": -16.63228669,
            "longitude1": "49°11′49″W",
            "longitude2": -49.19690569
        },
        {
            "latitude1": "16°42′43″S",
            "latitude2": -16.71197376,
            "longitude1": "49°19′03″W",
            "longitude2": -49.31749759
        },
        {
            "latitude1": "16°46′05″S",
            "latitude2": -16.76818356,
            "longitude1": "49°14′49″W",
            "longitude2": -49.24683071
        },
        {
            "latitude1": "16°44′21″S",
            "latitude2": -16.73925244,
            "longitude1": "49°14′19″W",
            "longitude2": -49.23857937
        },
        {
            "latitude1": "16°37′52″S",
            "latitude2": -16.63108443,
            "longitude1": "49°16′43″W",
            "longitude2": -49.27862224
        },
        {
            "latitude1": "16°40′48″S",
            "latitude2": -16.6798891,
            "longitude1": "49°18′26″W",
            "longitude2": -49.30712689
        },
        {
            "latitude1": "16°41′56″S",
            "latitude2": -16.69875297,
            "longitude1": "49°16′18″W",
            "longitude2": -49.27176855
        },
        {
            "latitude1": "16°43′36″S",
            "latitude2": -16.72656255,
            "longitude1": "49°11′18″W",
            "longitude2": -49.18825765
        },
        {
            "latitude1": "16°36′29″S",
            "latitude2": -16.608016,
            "longitude1": "49°13′51″W",
            "longitude2": -49.23075343
        },
        {
            "latitude1": "16°39′34″S",
            "latitude2": -16.65951712,
            "longitude1": "49°13′48″W",
            "longitude2": -49.22994238
        },
        {
            "latitude1": "16°35′42″S",
            "latitude2": -16.5948752,
            "longitude1": "49°15′05″W",
            "longitude2": -49.25127492
        },
        {
            "latitude1": "16°43′29″S",
            "latitude2": -16.72460134,
            "longitude1": "49°14′16″W",
            "longitude2": -49.2377087
        },
        {
            "latitude1": "16°43′04″S",
            "latitude2": -16.71782245,
            "longitude1": "49°11′09″W",
            "longitude2": -49.18583671
        },
        {
            "latitude1": "16°43′52″S",
            "latitude2": -16.73097953,
            "longitude1": "49°11′37″W",
            "longitude2": -49.19357656
        },
        {
            "latitude1": "16°36′49″S",
            "latitude2": -16.6136079,
            "longitude1": "49°14′33″W",
            "longitude2": -49.24256196
        },
        {
            "latitude1": "16°38′03″S",
            "latitude2": -16.6342696,
            "longitude1": "49°17′33″W",
            "longitude2": -49.29254878
        },
        {
            "latitude1": "16°43′45″S",
            "latitude2": -16.72904893,
            "longitude1": "49°13′19″W",
            "longitude2": -49.22205411
        },
        {
            "latitude1": "16°43′48″S",
            "latitude2": -16.73002052,
            "longitude1": "49°17′15″W",
            "longitude2": -49.28749853
        },
        {
            "latitude1": "16°41′04″S",
            "latitude2": -16.68440659,
            "longitude1": "49°15′32″W",
            "longitude2": -49.25892604
        },
        {
            "latitude1": "16°38′13″S",
            "latitude2": -16.63683373,
            "longitude1": "49°16′18″W",
            "longitude2": -49.27159397
        },
        {
            "latitude1": "16°37′42″S",
            "latitude2": -16.62828477,
            "longitude1": "49°15′16″W",
            "longitude2": -49.2545272
        },
        {
            "latitude1": "16°41′07″S",
            "latitude2": -16.68531544,
            "longitude1": "49°16′31″W",
            "longitude2": -49.27527831
        },
        {
            "latitude1": "16°44′09″S",
            "latitude2": -16.73576853,
            "longitude1": "49°14′58″W",
            "longitude2": -49.24932929
        },
        {
            "latitude1": "16°44′52″S",
            "latitude2": -16.74764389,
            "longitude1": "49°12′15″W",
            "longitude2": -49.20425065
        },
        {
            "latitude1": "16°38′21″S",
            "latitude2": -16.63912096,
            "longitude1": "49°16′01″W",
            "longitude2": -49.26705842
        },
        {
            "latitude1": "16°43′42″S",
            "latitude2": -16.72844627,
            "longitude1": "49°18′01″W",
            "longitude2": -49.30025364
        },
        {
            "latitude1": "16°45′10″S",
            "latitude2": -16.75283557,
            "longitude1": "49°12′19″W",
            "longitude2": -49.2053433
        },
        {
            "latitude1": "16°37′29″S",
            "latitude2": -16.62475296,
            "longitude1": "49°14′13″W",
            "longitude2": -49.23698573
        },
        {
            "latitude1": "16°43′10″S",
            "latitude2": -16.7194155,
            "longitude1": "49°16′41″W",
            "longitude2": -49.27794866
        },
        {
            "latitude1": "16°43′47″S",
            "latitude2": -16.72964623,
            "longitude1": "49°14′13″W",
            "longitude2": -49.23681449
        },
        {
            "latitude1": "16°41′13″S",
            "latitude2": -16.68697086,
            "longitude1": "49°17′38″W",
            "longitude2": -49.29401206
        },
        {
            "latitude1": "16°37′56″S",
            "latitude2": -16.63209532,
            "longitude1": "49°11′15″W",
            "longitude2": -49.18751484
        },
        {
            "latitude1": "16°41′47″S",
            "latitude2": -16.69629019,
            "longitude1": "49°17′17″W",
            "longitude2": -49.28806774
        },
        {
            "latitude1": "16°37′04″S",
            "latitude2": -16.61772904,
            "longitude1": "49°17′28″W",
            "longitude2": -49.29105883
        },
        {
            "latitude1": "16°42′30″S",
            "latitude2": -16.70844,
            "longitude1": "49°10′49″W",
            "longitude2": -49.18032342
        },
        {
            "latitude1": "16°44′38″S",
            "latitude2": -16.74387188,
            "longitude1": "49°11′40″W",
            "longitude2": -49.19431362
        },
        {
            "latitude1": "16°41′22″S",
            "latitude2": -16.68933733,
            "longitude1": "49°18′20″W",
            "longitude2": -49.30548964
        },
        {
            "latitude1": "16°37′50″S",
            "latitude2": -16.63042126,
            "longitude1": "49°11′04″W",
            "longitude2": -49.18457286
        },
        {
            "latitude1": "16°38′36″S",
            "latitude2": -16.64343227,
            "longitude1": "49°15′40″W",
            "longitude2": -49.2610197
        },
        {
            "latitude1": "16°44′38″S",
            "latitude2": -16.74381183,
            "longitude1": "49°17′24″W",
            "longitude2": -49.28992593
        },
        {
            "latitude1": "16°41′57″S",
            "latitude2": -16.69922665,
            "longitude1": "49°14′27″W",
            "longitude2": -49.24094187
        },
        {
            "latitude1": "16°42′52″S",
            "latitude2": -16.7144151,
            "longitude1": "49°10′15″W",
            "longitude2": -49.17092629
        },
        {
            "latitude1": "16°41′15″S",
            "latitude2": -16.68745933,
            "longitude1": "49°19′00″W",
            "longitude2": -49.31656061
        },
        {
            "latitude1": "16°44′05″S",
            "latitude2": -16.73464806,
            "longitude1": "49°19′31″W",
            "longitude2": -49.3253657
        },
        {
            "latitude1": "16°41′39″S",
            "latitude2": -16.694167,
            "longitude1": "49°11′45″W",
            "longitude2": -49.19595129
        },
        {
            "latitude1": "16°39′32″S",
            "latitude2": -16.658871,
            "longitude1": "49°16′10″W",
            "longitude2": -49.26942384
        },
        {
            "latitude1": "16°44′30″S",
            "latitude2": -16.74153698,
            "longitude1": "49°16′57″W",
            "longitude2": -49.28238122
        },
        {
            "latitude1": "16°40′54″S",
            "latitude2": -16.68164087,
            "longitude1": "49°13′17″W",
            "longitude2": -49.22148295
        },
        {
            "latitude1": "16°37′41″S",
            "latitude2": -16.62799593,
            "longitude1": "49°19′33″W",
            "longitude2": -49.32586817
        },
        {
            "latitude1": "16°43′28″S",
            "latitude2": -16.72449638,
            "longitude1": "49°10′34″W",
            "longitude2": -49.17616695
        },
        {
            "latitude1": "16°38′24″S",
            "latitude2": -16.63996115,
            "longitude1": "49°14′14″W",
            "longitude2": -49.23735678
        },
        {
            "latitude1": "16°39′10″S",
            "latitude2": -16.65283097,
            "longitude1": "49°16′51″W",
            "longitude2": -49.28090585
        },
        {
            "latitude1": "16°41′06″S",
            "latitude2": -16.68499356,
            "longitude1": "49°10′38″W",
            "longitude2": -49.17716694
        },
        {
            "latitude1": "16°36′35″S",
            "latitude2": -16.60976906,
            "longitude1": "49°17′20″W",
            "longitude2": -49.28875319
        },
        {
            "latitude1": "16°38′30″S",
            "latitude2": -16.64174528,
            "longitude1": "49°11′24″W",
            "longitude2": -49.18989173
        },
        {
            "latitude1": "16°38′42″S",
            "latitude2": -16.64501219,
            "longitude1": "49°18′11″W",
            "longitude2": -49.30306051
        },
        {
            "latitude1": "16°39′26″S",
            "latitude2": -16.65728843,
            "longitude1": "49°13′16″W",
            "longitude2": -49.22117317
        },
        {
            "latitude1": "16°42′53″S",
            "latitude2": -16.7147605,
            "longitude1": "49°17′24″W",
            "longitude2": -49.29003359
        },
        {
            "latitude1": "16°36′12″S",
            "latitude2": -16.60337795,
            "longitude1": "49°16′39″W",
            "longitude2": -49.27736667
        },
        {
            "latitude1": "16°43′57″S",
            "latitude2": -16.73248265,
            "longitude1": "49°17′36″W",
            "longitude2": -49.29320669
        },
        {
            "latitude1": "16°41′52″S",
            "latitude2": -16.69779411,
            "longitude1": "49°19′20″W",
            "longitude2": -49.32214982
        },
        {
            "latitude1": "16°42′54″S",
            "latitude2": -16.71510733,
            "longitude1": "49°18′47″W",
            "longitude2": -49.31291856
        },
        {
            "latitude1": "16°43′17″S",
            "latitude2": -16.72126792,
            "longitude1": "49°10′58″W",
            "longitude2": -49.18278059
        },
        {
            "latitude1": "16°39′56″S",
            "latitude2": -16.6656495,
            "longitude1": "49°17′51″W",
            "longitude2": -49.29758737
        },
        {
            "latitude1": "16°37′00″S",
            "latitude2": -16.61654939,
            "longitude1": "49°11′42″W",
            "longitude2": -49.19510954
        },
        {
            "latitude1": "16°42′10″S",
            "latitude2": -16.70275041,
            "longitude1": "49°17′03″W",
            "longitude2": -49.28412199
        },
        {
            "latitude1": "16°39′51″S",
            "latitude2": -16.66429205,
            "longitude1": "49°16′04″W",
            "longitude2": -49.26782433
        },
        {
            "latitude1": "16°41′09″S",
            "latitude2": -16.68590504,
            "longitude1": "49°14′25″W",
            "longitude2": -49.24018099
        },
        {
            "latitude1": "16°37′20″S",
            "latitude2": -16.62226292,
            "longitude1": "49°16′45″W",
            "longitude2": -49.27908162
        },
        {
            "latitude1": "16°38′11″S",
            "latitude2": -16.63632648,
            "longitude1": "49°15′12″W",
            "longitude2": -49.25342023
        },
        {
            "latitude1": "16°43′26″S",
            "latitude2": -16.72392824,
            "longitude1": "49°17′01″W",
            "longitude2": -49.28349639
        },
        {
            "latitude1": "16°35′54″S",
            "latitude2": -16.59825479,
            "longitude1": "49°14′07″W",
            "longitude2": -49.23520381
        },
        {
            "latitude1": "16°36′28″S",
            "latitude2": -16.607886,
            "longitude1": "49°14′38″W",
            "longitude2": -49.24389782
        },
        {
            "latitude1": "16°44′34″S",
            "latitude2": -16.74267252,
            "longitude1": "49°12′56″W",
            "longitude2": -49.21555736
        },
        {
            "latitude1": "16°39′27″S",
            "latitude2": -16.65763807,
            "longitude1": "49°20′04″W",
            "longitude2": -49.33433287
        },
        {
            "latitude1": "16°37′40″S",
            "latitude2": -16.6277411,
            "longitude1": "49°14′58″W",
            "longitude2": -49.24950415
        },
        {
            "latitude1": "16°40′30″S",
            "latitude2": -16.67512449,
            "longitude1": "49°15′42″W",
            "longitude2": -49.261747
        },
        {
            "latitude1": "16°43′19″S",
            "latitude2": -16.72203208,
            "longitude1": "49°16′51″W",
            "longitude2": -49.28089988
        },
        {
            "latitude1": "16°37′58″S",
            "latitude2": -16.63267676,
            "longitude1": "49°20′08″W",
            "longitude2": -49.33560637
        },
        {
            "latitude1": "16°42′04″S",
            "latitude2": -16.70116473,
            "longitude1": "49°14′30″W",
            "longitude2": -49.24153611
        },
        {
            "latitude1": "16°38′19″S",
            "latitude2": -16.63852593,
            "longitude1": "49°12′07″W",
            "longitude2": -49.20206923
        },
        {
            "latitude1": "16°39′11″S",
            "latitude2": -16.65308134,
            "longitude1": "49°15′10″W",
            "longitude2": -49.25276619
        },
        {
            "latitude1": "16°43′34″S",
            "latitude2": -16.72612385,
            "longitude1": "49°19′58″W",
            "longitude2": -49.3327738
        },
        {
            "latitude1": "16°40′32″S",
            "latitude2": -16.67551828,
            "longitude1": "49°11′13″W",
            "longitude2": -49.18704017
        },
        {
            "latitude1": "16°42′05″S",
            "latitude2": -16.70132718,
            "longitude1": "49°12′04″W",
            "longitude2": -49.20107844
        },
        {
            "latitude1": "16°43′31″S",
            "latitude2": -16.72533461,
            "longitude1": "49°17′34″W",
            "longitude2": -49.29274899
        },
        {
            "latitude1": "16°42′06″S",
            "latitude2": -16.7015896,
            "longitude1": "49°16′45″W",
            "longitude2": -49.27911435
        },
        {
            "latitude1": "16°45′43″S",
            "latitude2": -16.76196668,
            "longitude1": "49°14′24″W",
            "longitude2": -49.2399355
        },
        {
            "latitude1": "16°38′15″S",
            "latitude2": -16.63754969,
            "longitude1": "49°14′58″W",
            "longitude2": -49.24951325
        },
        {
            "latitude1": "16°39′55″S",
            "latitude2": -16.66524667,
            "longitude1": "49°18′22″W",
            "longitude2": -49.30606892
        },
        {
            "latitude1": "16°43′49″S",
            "latitude2": -16.73036639,
            "longitude1": "49°16′47″W",
            "longitude2": -49.27958972
        },
        {
            "latitude1": "16°43′30″S",
            "latitude2": -16.72501392,
            "longitude1": "49°18′22″W",
            "longitude2": -49.30600329
        },
        {
            "latitude1": "16°43′03″S",
            "latitude2": -16.71738491,
            "longitude1": "49°19′02″W",
            "longitude2": -49.31721347
        },
        {
            "latitude1": "16°38′45″S",
            "latitude2": -16.64592337,
            "longitude1": "49°19′59″W",
            "longitude2": -49.33297192
        },
        {
            "latitude1": "16°41′49″S",
            "latitude2": -16.69693614,
            "longitude1": "49°18′51″W",
            "longitude2": -49.31409826
        },
        {
            "latitude1": "16°41′05″S",
            "latitude2": -16.68478225,
            "longitude1": "49°18′16″W",
            "longitude2": -49.30453886
        },
        {
            "latitude1": "16°41′36″S",
            "latitude2": -16.69336748,
            "longitude1": "49°14′38″W",
            "longitude2": -49.24378466
        },
        {
            "latitude1": "16°43′47″S",
            "latitude2": -16.729725,
            "longitude1": "49°17′07″W",
            "longitude2": -49.28515609
        },
        {
            "latitude1": "16°41′01″S",
            "latitude2": -16.68350809,
            "longitude1": "49°12′26″W",
            "longitude2": -49.20709369
        },
        {
            "latitude1": "16°40′43″S",
            "latitude2": -16.67874005,
            "longitude1": "49°19′44″W",
            "longitude2": -49.32877056
        },
        {
            "latitude1": "16°37′26″S",
            "latitude2": -16.62378721,
            "longitude1": "49°17′43″W",
            "longitude2": -49.2951571
        },
        {
            "latitude1": "16°35′47″S",
            "latitude2": -16.59646195,
            "longitude1": "49°16′43″W",
            "longitude2": -49.27866083
        },
        {
            "latitude1": "16°42′03″S",
            "latitude2": -16.70095906,
            "longitude1": "49°10′47″W",
            "longitude2": -49.17958585
        },
        {
            "latitude1": "16°40′01″S",
            "latitude2": -16.66688424,
            "longitude1": "49°14′15″W",
            "longitude2": -49.23744441
        },
        {
            "latitude1": "16°42′28″S",
            "latitude2": -16.70772945,
            "longitude1": "49°18′34″W",
            "longitude2": -49.30951671
        },
        {
            "latitude1": "16°37′49″S",
            "latitude2": -16.63022486,
            "longitude1": "49°17′56″W",
            "longitude2": -49.29890033
        },
        {
            "latitude1": "16°36′28″S",
            "latitude2": -16.60776542,
            "longitude1": "49°17′50″W",
            "longitude2": -49.29722735
        },
        {
            "latitude1": "16°39′35″S",
            "latitude2": -16.65983599,
            "longitude1": "49°18′47″W",
            "longitude2": -49.31308071
        },
        {
            "latitude1": "16°40′18″S",
            "latitude2": -16.67161237,
            "longitude1": "49°12′21″W",
            "longitude2": -49.20577353
        },
        {
            "latitude1": "16°42′04″S",
            "latitude2": -16.70101521,
            "longitude1": "49°19′01″W",
            "longitude2": -49.31701616
        },
        {
            "latitude1": "16°45′30″S",
            "latitude2": -16.75836774,
            "longitude1": "49°14′00″W",
            "longitude2": -49.23321497
        },
        {
            "latitude1": "16°45′07″S",
            "latitude2": -16.75182339,
            "longitude1": "49°13′35″W",
            "longitude2": -49.22651334
        },
        {
            "latitude1": "16°37′03″S",
            "latitude2": -16.61750577,
            "longitude1": "49°14′42″W",
            "longitude2": -49.24498311
        },
        {
            "latitude1": "16°43′41″S",
            "latitude2": -16.72815648,
            "longitude1": "49°19′22″W",
            "longitude2": -49.32277898
        },
        {
            "latitude1": "16°41′34″S",
            "latitude2": -16.69285364,
            "longitude1": "49°13′56″W",
            "longitude2": -49.23217743
        },
        {
            "latitude1": "16°36′05″S",
            "latitude2": -16.60150882,
            "longitude1": "49°13′45″W",
            "longitude2": -49.2292552
        },
        {
            "latitude1": "16°44′10″S",
            "latitude2": -16.73597563,
            "longitude1": "49°12′47″W",
            "longitude2": -49.21291734
        },
        {
            "latitude1": "16°41′25″S",
            "latitude2": -16.69036855,
            "longitude1": "49°17′27″W",
            "longitude2": -49.29094849
        },
        {
            "latitude1": "16°40′36″S",
            "latitude2": -16.67658839,
            "longitude1": "49°12′56″W",
            "longitude2": -49.21552681
        },
        {
            "latitude1": "16°41′19″S",
            "latitude2": -16.68856382,
            "longitude1": "49°16′30″W",
            "longitude2": -49.27507547
        },
        {
            "latitude1": "16°44′09″S",
            "latitude2": -16.73589817,
            "longitude1": "49°11′51″W",
            "longitude2": -49.19757629
        },
        {
            "latitude1": "16°41′27″S",
            "latitude2": -16.69096163,
            "longitude1": "49°18′54″W",
            "longitude2": -49.31491329
        },
        {
            "latitude1": "16°36′45″S",
            "latitude2": -16.61237455,
            "longitude1": "49°14′56″W",
            "longitude2": -49.24877517
        },
        {
            "latitude1": "16°39′25″S",
            "latitude2": -16.65705051,
            "longitude1": "49°17′59″W",
            "longitude2": -49.29967944
        },
        {
            "latitude1": "16°41′23″S",
            "latitude2": -16.68981171,
            "longitude1": "49°12′06″W",
            "longitude2": -49.20155957
        },
        {
            "latitude1": "16°35′44″S",
            "latitude2": -16.59553248,
            "longitude1": "49°16′46″W",
            "longitude2": -49.27953399
        },
        {
            "latitude1": "16°44′57″S",
            "latitude2": -16.749266,
            "longitude1": "49°18′44″W",
            "longitude2": -49.31224721
        },
        {
            "latitude1": "16°44′48″S",
            "latitude2": -16.74660943,
            "longitude1": "49°17′54″W",
            "longitude2": -49.2982394
        },
        {
            "latitude1": "16°41′26″S",
            "latitude2": -16.69061895,
            "longitude1": "49°16′17″W",
            "longitude2": -49.27149607
        },
        {
            "latitude1": "16°45′45″S",
            "latitude2": -16.76239515,
            "longitude1": "49°14′35″W",
            "longitude2": -49.24302283
        },
        {
            "latitude1": "16°38′05″S",
            "latitude2": -16.63472084,
            "longitude1": "49°17′59″W",
            "longitude2": -49.29963733
        },
        {
            "latitude1": "16°41′14″S",
            "latitude2": -16.68732256,
            "longitude1": "49°12′15″W",
            "longitude2": -49.2041862
        },
        {
            "latitude1": "16°38′19″S",
            "latitude2": -16.63852275,
            "longitude1": "49°12′54″W",
            "longitude2": -49.21495959
        },
        {
            "latitude1": "16°37′49″S",
            "latitude2": -16.63016199,
            "longitude1": "49°18′38″W",
            "longitude2": -49.31046774
        },
        {
            "latitude1": "16°42′20″S",
            "latitude2": -16.70541927,
            "longitude1": "49°13′28″W",
            "longitude2": -49.2243449
        },
        {
            "latitude1": "16°39′36″S",
            "latitude2": -16.65990778,
            "longitude1": "49°13′39″W",
            "longitude2": -49.22757619
        },
        {
            "latitude1": "16°39′23″S",
            "latitude2": -16.65648791,
            "longitude1": "49°20′09″W",
            "longitude2": -49.33578446
        },
        {
            "latitude1": "16°39′18″S",
            "latitude2": -16.65496684,
            "longitude1": "49°13′42″W",
            "longitude2": -49.22828946
        },
        {
            "latitude1": "16°40′19″S",
            "latitude2": -16.67183296,
            "longitude1": "49°17′48″W",
            "longitude2": -49.29673362
        },
        {
            "latitude1": "16°43′58″S",
            "latitude2": -16.73285735,
            "longitude1": "49°15′52″W",
            "longitude2": -49.26452778
        },
        {
            "latitude1": "16°42′34″S",
            "latitude2": -16.70957763,
            "longitude1": "49°13′19″W",
            "longitude2": -49.22193338
        },
        {
            "latitude1": "16°45′36″S",
            "latitude2": -16.76011915,
            "longitude1": "49°13′51″W",
            "longitude2": -49.23089382
        },
        {
            "latitude1": "16°40′29″S",
            "latitude2": -16.67485639,
            "longitude1": "49°19′24″W",
            "longitude2": -49.32334203
        },
        {
            "latitude1": "16°42′36″S",
            "latitude2": -16.71004001,
            "longitude1": "49°18′08″W",
            "longitude2": -49.30218123
        },
        {
            "latitude1": "16°40′21″S",
            "latitude2": -16.67250707,
            "longitude1": "49°18′52″W",
            "longitude2": -49.31433378
        },
        {
            "latitude1": "16°35′49″S",
            "latitude2": -16.59688897,
            "longitude1": "49°13′32″W",
            "longitude2": -49.22544934
        },
        {
            "latitude1": "16°40′51″S",
            "latitude2": -16.68085337,
            "longitude1": "49°10′12″W",
            "longitude2": -49.17012454
        },
        {
            "latitude1": "16°43′23″S",
            "latitude2": -16.72296883,
            "longitude1": "49°18′20″W",
            "longitude2": -49.30567616
        },
        {
            "latitude1": "16°39′29″S",
            "latitude2": -16.6579397,
            "longitude1": "49°13′56″W",
            "longitude2": -49.2323548
        },
        {
            "latitude1": "16°42′40″S",
            "latitude2": -16.71119091,
            "longitude1": "49°19′07″W",
            "longitude2": -49.31864965
        },
        {
            "latitude1": "16°39′24″S",
            "latitude2": -16.6565967,
            "longitude1": "49°10′45″W",
            "longitude2": -49.17922322
        },
        {
            "latitude1": "16°42′42″S",
            "latitude2": -16.71164756,
            "longitude1": "49°12′30″W",
            "longitude2": -49.20844603
        },
        {
            "latitude1": "16°38′14″S",
            "latitude2": -16.63725098,
            "longitude1": "49°20′06″W",
            "longitude2": -49.33504429
        },
        {
            "latitude1": "16°36′53″S",
            "latitude2": -16.61484737,
            "longitude1": "49°15′03″W",
            "longitude2": -49.25088767
        },
        {
            "latitude1": "16°38′16″S",
            "latitude2": -16.63768324,
            "longitude1": "49°17′51″W",
            "longitude2": -49.29758441
        },
        {
            "latitude1": "16°43′11″S",
            "latitude2": -16.71965751,
            "longitude1": "49°14′14″W",
            "longitude2": -49.23732013
        },
        {
            "latitude1": "16°39′23″S",
            "latitude2": -16.65633262,
            "longitude1": "49°17′10″W",
            "longitude2": -49.28621076
        },
        {
            "latitude1": "16°37′57″S",
            "latitude2": -16.63251208,
            "longitude1": "49°11′40″W",
            "longitude2": -49.1944032
        },
        {
            "latitude1": "16°42′47″S",
            "latitude2": -16.71306917,
            "longitude1": "49°18′02″W",
            "longitude2": -49.30053654
        },
        {
            "latitude1": "16°43′11″S",
            "latitude2": -16.71960609,
            "longitude1": "49°15′32″W",
            "longitude2": -49.25902304
        },
        {
            "latitude1": "16°42′43″S",
            "latitude2": -16.71188548,
            "longitude1": "49°13′41″W",
            "longitude2": -49.22797423
        },
        {
            "latitude1": "16°40′49″S",
            "latitude2": -16.68033556,
            "longitude1": "49°18′56″W",
            "longitude2": -49.31559717
        },
        {
            "latitude1": "16°44′28″S",
            "latitude2": -16.74121892,
            "longitude1": "49°15′04″W",
            "longitude2": -49.25112331
        },
        {
            "latitude1": "16°41′59″S",
            "latitude2": -16.69978955,
            "longitude1": "49°20′38″W",
            "longitude2": -49.34397086
        },
        {
            "latitude1": "16°38′32″S",
            "latitude2": -16.64209359,
            "longitude1": "49°17′40″W",
            "longitude2": -49.29443646
        },
        {
            "latitude1": "16°39′40″S",
            "latitude2": -16.6610842,
            "longitude1": "49°14′06″W",
            "longitude2": -49.23502325
        },
        {
            "latitude1": "16°39′47″S",
            "latitude2": -16.66308773,
            "longitude1": "49°13′29″W",
            "longitude2": -49.22478284
        },
        {
            "latitude1": "16°41′13″S",
            "latitude2": -16.68701297,
            "longitude1": "49°20′08″W",
            "longitude2": -49.33547601
        },
        {
            "latitude1": "16°44′07″S",
            "latitude2": -16.73533442,
            "longitude1": "49°13′04″W",
            "longitude2": -49.2177108
        },
        {
            "latitude1": "16°35′55″S",
            "latitude2": -16.59853706,
            "longitude1": "49°17′30″W",
            "longitude2": -49.29163649
        },
        {
            "latitude1": "16°42′11″S",
            "latitude2": -16.70296538,
            "longitude1": "49°14′43″W",
            "longitude2": -49.2451808
        },
        {
            "latitude1": "16°44′04″S",
            "latitude2": -16.73453903,
            "longitude1": "49°16′44″W",
            "longitude2": -49.27892177
        },
        {
            "latitude1": "16°37′30″S",
            "latitude2": -16.62503638,
            "longitude1": "49°19′17″W",
            "longitude2": -49.32133826
        },
        {
            "latitude1": "16°39′04″S",
            "latitude2": -16.65119532,
            "longitude1": "49°18′47″W",
            "longitude2": -49.31302302
        },
        {
            "latitude1": "16°38′29″S",
            "latitude2": -16.64126448,
            "longitude1": "49°19′37″W",
            "longitude2": -49.32681659
        },
        {
            "latitude1": "16°39′54″S",
            "latitude2": -16.66488215,
            "longitude1": "49°19′06″W",
            "longitude2": -49.31829647
        },
        {
            "latitude1": "16°41′08″S",
            "latitude2": -16.68564718,
            "longitude1": "49°18′17″W",
            "longitude2": -49.30482007
        },
        {
            "latitude1": "16°39′44″S",
            "latitude2": -16.66218677,
            "longitude1": "49°12′28″W",
            "longitude2": -49.20766533
        },
        {
            "latitude1": "16°39′38″S",
            "latitude2": -16.66066356,
            "longitude1": "49°15′21″W",
            "longitude2": -49.25592554
        },
        {
            "latitude1": "16°37′57″S",
            "latitude2": -16.63260265,
            "longitude1": "49°18′54″W",
            "longitude2": -49.31492171
        },
        {
            "latitude1": "16°39′49″S",
            "latitude2": -16.66349531,
            "longitude1": "49°10′34″W",
            "longitude2": -49.17609828
        },
        {
            "latitude1": "16°38′45″S",
            "latitude2": -16.645898,
            "longitude1": "49°10′59″W",
            "longitude2": -49.1833842
        },
        {
            "latitude1": "16°45′17″S",
            "latitude2": -16.75480586,
            "longitude1": "49°17′38″W",
            "longitude2": -49.2939291
        },
        {
            "latitude1": "16°44′38″S",
            "latitude2": -16.74385342,
            "longitude1": "49°17′35″W",
            "longitude2": -49.29299694
        },
        {
            "latitude1": "16°46′01″S",
            "latitude2": -16.76689539,
            "longitude1": "49°16′20″W",
            "longitude2": -49.27230279
        },
        {
            "latitude1": "16°36′15″S",
            "latitude2": -16.60412754,
            "longitude1": "49°16′16″W",
            "longitude2": -49.27105128
        },
        {
            "latitude1": "16°40′59″S",
            "latitude2": -16.68305637,
            "longitude1": "49°14′14″W",
            "longitude2": -49.23720485
        },
        {
            "latitude1": "16°43′50″S",
            "latitude2": -16.73053727,
            "longitude1": "49°18′41″W",
            "longitude2": -49.3113738
        },
        {
            "latitude1": "16°44′11″S",
            "latitude2": -16.73629047,
            "longitude1": "49°14′55″W",
            "longitude2": -49.24853698
        },
        {
            "latitude1": "16°45′54″S",
            "latitude2": -16.76507701,
            "longitude1": "49°14′55″W",
            "longitude2": -49.2485643
        },
        {
            "latitude1": "16°40′39″S",
            "latitude2": -16.67753086,
            "longitude1": "49°10′23″W",
            "longitude2": -49.1731571
        },
        {
            "latitude1": "16°42′34″S",
            "latitude2": -16.70941194,
            "longitude1": "49°16′13″W",
            "longitude2": -49.27033555
        },
        {
            "latitude1": "16°42′19″S",
            "latitude2": -16.70532722,
            "longitude1": "49°20′26″W",
            "longitude2": -49.34051884
        },
        {
            "latitude1": "16°42′18″S",
            "latitude2": -16.70492726,
            "longitude1": "49°16′53″W",
            "longitude2": -49.28138448
        },
        {
            "latitude1": "16°43′09″S",
            "latitude2": -16.71908672,
            "longitude1": "49°14′40″W",
            "longitude2": -49.24450363
        },
        {
            "latitude1": "16°42′53″S",
            "latitude2": -16.71472725,
            "longitude1": "49°12′44″W",
            "longitude2": -49.21217892
        },
        {
            "latitude1": "16°44′20″S",
            "latitude2": -16.73895888,
            "longitude1": "49°12′04″W",
            "longitude2": -49.20109959
        },
        {
            "latitude1": "16°41′49″S",
            "latitude2": -16.69706488,
            "longitude1": "49°15′47″W",
            "longitude2": -49.26295091
        },
        {
            "latitude1": "16°38′06″S",
            "latitude2": -16.63511555,
            "longitude1": "49°14′40″W",
            "longitude2": -49.24434969
        },
        {
            "latitude1": "16°36′04″S",
            "latitude2": -16.60113111,
            "longitude1": "49°12′45″W",
            "longitude2": -49.21262644
        },
        {
            "latitude1": "16°43′37″S",
            "latitude2": -16.72688748,
            "longitude1": "49°14′49″W",
            "longitude2": -49.2469664
        },
        {
            "latitude1": "16°37′24″S",
            "latitude2": -16.62334538,
            "longitude1": "49°18′48″W",
            "longitude2": -49.31330751
        },
        {
            "latitude1": "16°37′28″S",
            "latitude2": -16.62437285,
            "longitude1": "49°13′07″W",
            "longitude2": -49.21861483
        },
        {
            "latitude1": "16°39′47″S",
            "latitude2": -16.66305584,
            "longitude1": "49°12′40″W",
            "longitude2": -49.21120349
        },
        {
            "latitude1": "16°43′43″S",
            "latitude2": -16.72872407,
            "longitude1": "49°15′58″W",
            "longitude2": -49.26610415
        },
        {
            "latitude1": "16°42′47″S",
            "latitude2": -16.71310871,
            "longitude1": "49°11′53″W",
            "longitude2": -49.19815226
        },
        {
            "latitude1": "16°43′02″S",
            "latitude2": -16.71710666,
            "longitude1": "49°17′56″W",
            "longitude2": -49.29898404
        },
        {
            "latitude1": "16°40′35″S",
            "latitude2": -16.6762571,
            "longitude1": "49°10′41″W",
            "longitude2": -49.17809032
        },
        {
            "latitude1": "16°42′52″S",
            "latitude2": -16.71455893,
            "longitude1": "49°18′06″W",
            "longitude2": -49.30172432
        },
        {
            "latitude1": "16°40′58″S",
            "latitude2": -16.6828455,
            "longitude1": "49°19′35″W",
            "longitude2": -49.32638184
        },
        {
            "latitude1": "16°42′47″S",
            "latitude2": -16.71298298,
            "longitude1": "49°13′02″W",
            "longitude2": -49.21709118
        },
        {
            "latitude1": "16°45′22″S",
            "latitude2": -16.75615452,
            "longitude1": "49°16′26″W",
            "longitude2": -49.27397605
        },
        {
            "latitude1": "16°38′30″S",
            "latitude2": -16.64161541,
            "longitude1": "49°11′31″W",
            "longitude2": -49.19189387
        },
        {
            "latitude1": "16°39′13″S",
            "latitude2": -16.65353535,
            "longitude1": "49°12′38″W",
            "longitude2": -49.21064039
        },
        {
            "latitude1": "16°41′24″S",
            "latitude2": -16.69012099,
            "longitude1": "49°12′22″W",
            "longitude2": -49.20607818
        },
        {
            "latitude1": "16°39′21″S",
            "latitude2": -16.65593654,
            "longitude1": "49°11′26″W",
            "longitude2": -49.19058922
        },
        {
            "latitude1": "16°38′45″S",
            "latitude2": -16.64572245,
            "longitude1": "49°15′02″W",
            "longitude2": -49.25052483
        },
        {
            "latitude1": "16°38′22″S",
            "latitude2": -16.63953641,
            "longitude1": "49°17′30″W",
            "longitude2": -49.2915471
        },
        {
            "latitude1": "16°37′08″S",
            "latitude2": -16.61876173,
            "longitude1": "49°18′25″W",
            "longitude2": -49.30691622
        },
        {
            "latitude1": "16°37′20″S",
            "latitude2": -16.62212975,
            "longitude1": "49°13′07″W",
            "longitude2": -49.21859321
        },
        {
            "latitude1": "16°42′43″S",
            "latitude2": -16.7120111,
            "longitude1": "49°20′22″W",
            "longitude2": -49.33934943
        },
        {
            "latitude1": "16°37′31″S",
            "latitude2": -16.62538937,
            "longitude1": "49°19′03″W",
            "longitude2": -49.31750731
        },
        {
            "latitude1": "16°42′57″S",
            "latitude2": -16.7157883,
            "longitude1": "49°18′01″W",
            "longitude2": -49.30034494
        },
        {
            "latitude1": "16°36′18″S",
            "latitude2": -16.60512965,
            "longitude1": "49°16′46″W",
            "longitude2": -49.27943971
        },
        {
            "latitude1": "16°35′32″S",
            "latitude2": -16.59235023,
            "longitude1": "49°15′55″W",
            "longitude2": -49.26537183
        },
        {
            "latitude1": "16°37′07″S",
            "latitude2": -16.6186314,
            "longitude1": "49°13′14″W",
            "longitude2": -49.22055549
        },
        {
            "latitude1": "16°46′03″S",
            "latitude2": -16.76749938,
            "longitude1": "49°15′12″W",
            "longitude2": -49.25329208
        },
        {
            "latitude1": "16°36′30″S",
            "latitude2": -16.60828955,
            "longitude1": "49°14′45″W",
            "longitude2": -49.24576392
        },
        {
            "latitude1": "16°40′19″S",
            "latitude2": -16.67186744,
            "longitude1": "49°16′50″W",
            "longitude2": -49.28057213
        },
        {
            "latitude1": "16°37′54″S",
            "latitude2": -16.63169297,
            "longitude1": "49°12′46″W",
            "longitude2": -49.21284887
        },
        {
            "latitude1": "16°41′27″S",
            "latitude2": -16.69096598,
            "longitude1": "49°16′59″W",
            "longitude2": -49.2833634
        },
        {
            "latitude1": "16°38′45″S",
            "latitude2": -16.64586495,
            "longitude1": "49°17′54″W",
            "longitude2": -49.29835239
        },
        {
            "latitude1": "16°42′48″S",
            "latitude2": -16.71338463,
            "longitude1": "49°11′29″W",
            "longitude2": -49.19144163
        },
        {
            "latitude1": "16°39′36″S",
            "latitude2": -16.6600132,
            "longitude1": "49°15′47″W",
            "longitude2": -49.26301364
        },
        {
            "latitude1": "16°37′16″S",
            "latitude2": -16.62107847,
            "longitude1": "49°18′37″W",
            "longitude2": -49.31037625
        },
        {
            "latitude1": "16°43′07″S",
            "latitude2": -16.71852343,
            "longitude1": "49°20′24″W",
            "longitude2": -49.33991996
        },
        {
            "latitude1": "16°36′39″S",
            "latitude2": -16.61072642,
            "longitude1": "49°16′02″W",
            "longitude2": -49.2672929
        },
        {
            "latitude1": "16°38′38″S",
            "latitude2": -16.64387081,
            "longitude1": "49°10′30″W",
            "longitude2": -49.17496125
        },
        {
            "latitude1": "16°42′42″S",
            "latitude2": -16.7117185,
            "longitude1": "49°14′11″W",
            "longitude2": -49.23632815
        },
        {
            "latitude1": "16°40′41″S",
            "latitude2": -16.67810509,
            "longitude1": "49°12′33″W",
            "longitude2": -49.20903432
        },
        {
            "latitude1": "16°42′38″S",
            "latitude2": -16.71052412,
            "longitude1": "49°10′19″W",
            "longitude2": -49.17188257
        },
        {
            "latitude1": "16°45′59″S",
            "latitude2": -16.76665516,
            "longitude1": "49°15′25″W",
            "longitude2": -49.25698589
        },
        {
            "latitude1": "16°42′44″S",
            "latitude2": -16.71208509,
            "longitude1": "49°16′43″W",
            "longitude2": -49.27872498
        },
        {
            "latitude1": "16°35′51″S",
            "latitude2": -16.5976295,
            "longitude1": "49°15′17″W",
            "longitude2": -49.25471148
        },
        {
            "latitude1": "16°42′39″S",
            "latitude2": -16.71082428,
            "longitude1": "49°10′49″W",
            "longitude2": -49.18014074
        },
        {
            "latitude1": "16°40′40″S",
            "latitude2": -16.67780218,
            "longitude1": "49°11′47″W",
            "longitude2": -49.19632559
        },
        {
            "latitude1": "16°44′28″S",
            "latitude2": -16.74099551,
            "longitude1": "49°17′22″W",
            "longitude2": -49.28932358
        },
        {
            "latitude1": "16°40′20″S",
            "latitude2": -16.67219757,
            "longitude1": "49°19′54″W",
            "longitude2": -49.33168317
        },
        {
            "latitude1": "16°39′47″S",
            "latitude2": -16.663055,
            "longitude1": "49°12′34″W",
            "longitude2": -49.20957786
        },
        {
            "latitude1": "16°41′33″S",
            "latitude2": -16.69256774,
            "longitude1": "49°12′32″W",
            "longitude2": -49.20895097
        },
        {
            "latitude1": "16°39′22″S",
            "latitude2": -16.65597807,
            "longitude1": "49°15′10″W",
            "longitude2": -49.25290708
        }
        ]

    size = len(points) - 1

    idx = randint(0, size)

    return (points[idx]['latitude2'], points[idx]['longitude2'])
