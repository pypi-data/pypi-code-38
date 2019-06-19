"""
Created on Tue May 16 15:14:13 2017

@author: me
"""
import re
from argparse import ArgumentParser

from requests import Session
from getpass import getpass

DEFAULT_HOST = "envipath.org"
ANONYMOUS = "anonymous"

JSONHEADERS = {"Accept": "application/json"}
TEXTHEADERS = {'Accept': 'text/plain'}


class WrongParameter(Exception): pass
class E400(Exception): pass
class E500(Exception): pass


class EnviPathClient(object):
    def __init__(self, host, username=ANONYMOUS, password=None, verify=True, secure=False):
        self.host = host
        self.secure = secure
        self.hosturl = "http{}://{}".format(("s" if self.secure else ""), self.host)
        self.verify = verify
        self.session = login(self.hosturl, username, password, self.verify, secure=self.secure)

    def close(self):
        logout(self.session, self.hosturl, verify=self.verify, secure=self.secure)

    def delete(self, url):
        if self.secure:
            url = url.replace("http://", "https://")
        r = self.session.delete(url, verify=self.verify)
        if r.status_code > 299:
            raise Exception("Failed with status code {}, text:\n{}".format(r.status_code, r.text.decode()))

    def get(self, url):
        return getjson(self.session, url, self.verify, secure=self.secure)

    def post(self, url, data):
        return post(self.session, url, data, self.verify, secure=self.secure)

    def importpackage(self, jsonfile):
        importpackage(self.session, hosturl=self.hosturl, jsonfile=jsonfile,
                      verify=self.verify, secure=self.secure)

    def exportpackage(self, packageurl=None, packagename=None, jsonfile=None):
        return exportpackage(
            self.session,
            packageurl=(packageurl or self.findpackage(packagename)),
            outfile=jsonfile,
            verify=self.verify,
            secure=self.secure)

    def findpackage(self, packagename):
        return findpackage(self.session, hosturl=self.hosturl,
                           packagename=packagename, verify=self.verify, secure=self.secure)

    def rename(self, url, newname):
        rename(self.session, object=url, newname=newname,
               verify=self.verify, secure=self.secure)

    def runrule(self, ruleurl, smiles):
        return runRule(self.session, ruleurl=ruleurl, smiles=smiles,
                       verify=self.verify, secure=self.secure)

    def addscenario(self, objecturl, scenariourl):
        return addScenario(session=self.session, url=objecturl,
                           scenario=scenariourl, verify=self.verify, secure=self.secure)

    def updatescenario(self, scenariourl,
                       soilsource=None, soiltexture1=None, soiltexture2=None,
                       soilclassificationsystem=None, redox=None, acidity=None, temperature=None,
                       waterstoragecapacity=None, humidity=None, omcontent=None, cec=None, bulkdens=None,
                       biomass=None, spikecompoundsmiles=None, spikeconcentration=None, halflife=None,
                       minormajor=None, proposedintermediate=None, confidencelevel=None,
                       referringscenario=None, enzyme=None,
                       infotypes=[], infodata={}):
        return updateScenario(self.session, scenario=scenariourl,
                              soilsource=soilsource, soiltexture1=soiltexture1, soiltexture2=soiltexture2,
                              soilclassificationsystem=soilclassificationsystem, redox=redox, acidity=acidity,
                              temperature=temperature, waterstoragecapacity=waterstoragecapacity, humidity=humidity,
                              omcontent=omcontent, cec=cec, bulkdens=bulkdens, biomass=biomass,
                              spikecompoundsmiles=spikecompoundsmiles, spikeconcentration=spikeconcentration,
                              halflife=halflife, minormajor=minormajor, proposedintermediate=proposedintermediate,
                              confidencelevel=confidencelevel, referringscenario=referringscenario, enzyme=enzyme,
                              addInfoTypes=infotypes, addInfoInput=infodata,
                              verify=self.verify, secure=self.secure)

    def createrule(self, packageurl,
            ruletype='SIMPLE',
            smirks=None,
            name=None,
            description=None,
            compositerule=None,
            simplerules=None,
            aerobiclikelihood=None,
            immediaterule=False,
            productfiltersmarts=None,
            reactantfiltersmarts=None,
            ):
        return createRule(self.session, packageurl=packageurl, ruletype=ruletype,
                          smirks=smirks, name=name, description=description,
                          compositerule=compositerule, simplerules=simplerules,
                          aerobiclikelihood=aerobiclikelihood, immediaterule=immediaterule,
                          productfiltersmarts=productfiltersmarts, reactantfiltersmarts=reactantfiltersmarts,
                          secure=self.secure, verify=self.verify)

    def updaterule(self, simplerule,
            smirks=None,
            name=None,
            description=None):
        return updateRule(self.session, ruleurl=simplerule,
                          smirks=smirks, name=name, description=description,
                          secure=self.secure, verify=self.verify)

    def combinerules(self, simplerule, compositerule):
        return combineRules(self.session, simplerule=simplerule, compositerule=compositerule,
                            secure=self.secure, verify=self.verify)

    def separaterules(self, simplerule, compositerule):
        return separateRules(self.session, simplerule=simplerule, compositerule=compositerule,
                             secure=self.secure, verify=self.verify)

    def separaterule(self, simplerule):
        return separateRule(self.session, simplerule=simplerule,
                            secure=self.secure, verify=self.verify)

    def createcompound(self, packageurl, smiles, name=None,
                       description=None):
        return createCompound(self.session, packageurl, smiles, name=name,
            description=description, secure=self.secure, verify=self.verify)

    def createpathway(self, packageurl, smiles, name=None, description=None):
        return createPathway(self.session, packageurl, smiles, name=name,
            description=description, secure=self.secure, verify=self.verify)

    def predictpathway(self, packageurl, smiles, settingsurl=None, hangon=True):
        return predictPathway(self.session, packageurl, smiles, settings_url=settingsurl, hangon=hangon,
                              verify=self.verify, secure=self.secure)

    def addcompoundtopathway(self, pathwayurl, smiles):
        return addCompoundToPathway(self.session, pathwayurl, smiles,
                                    secure=self.secure, verify=self.verify)

    def createscenario(self, packageurl,
            plainname=None,
            description=None,
            studydate=None,
            scenariotype=None,
            soilsource=None,
            soiltexture1=None,
            soiltexture2=None,
            soilclassificationsystem=None,
            redox=None,
            acidity=None,
            temperature=None,
            waterstoragecapacity=None,
            humidity=None,
            omcontent=None,
            cec=None,
            bulkdens=None,
            biomass=None,
            spikecompoundsmiles=None,
            spikeconcentration=None,
            halflife=None,
            minormajor=None,
            proposedintermediate=None,
            confidencelevel=None,
            referringscenario=None,
            enzyme=None):
        return createScenario(self.session, packageurl,
            plainname=plainname,
            description=description,
            studydate=studydate,
            scenariotype=scenariotype,
            soilsource=soilsource,
            soiltexture1=soiltexture1,
            soiltexture2=soiltexture2,
            soilclassificationsystem=soilclassificationsystem,
            redox=redox,
            acidity=acidity,
            temperature=temperature,
            waterstoragecapacity=waterstoragecapacity,
            humidity=humidity,
            omcontent=omcontent,
            cec=cec,
            bulkdens=bulkdens,
            biomass=biomass,
            spikecompoundsmiles=spikecompoundsmiles,
            spikeconcentration=spikeconcentration,
            minormajor=minormajor,
            proposedintermediate=proposedintermediate,
            confidencelevel=confidencelevel,
            halflife=halflife,
            referringscenario=referringscenario,
            enzyme=enzyme,
            verify=self.verify,
            secure=self.secure)

    def remove_ec_number(self, eclink_url):
        return remove_ec_number(self.session, eclink_url, verify=self.verify, secure=self.secure)

    def update_ec_number(self, eclink_url,
            ec_number=None,
            name=None,
            linking_method=None,
            evidence=[],
            description=None):
        return update_ec_number(self.session, eclink_url,
            ec_number=ec_number,
            name=name,
            linking_method=linking_method,
            evidence=evidence,
            description=description,
            verify=self.verify, secure=self.secure)

    def add_ec_number(self, rule_url,
            ec_number,
            name=None,
            linking_method=None,
            evidence=[],
            description=None):
        return add_ec_number(self.session, rule_url,
            ec_number,
            name=name,
            linking_method=linking_method,
            evidence=evidence,
            description=description,
            verify=self.verify, secure=self.secure)


def login(hosturl, username, password, verify=True, secure=False):
    session = Session()
    data = {
        'hiddenMethod': 'login',
        'loginusername': username
    }
    if username != ANONYMOUS:
        data['loginpassword'] = (password or getpass())

    if secure:
        hosturl = hosturl.replace("http://", "https://")

    response = session.post(hosturl, data=data, headers=TEXTHEADERS, allow_redirects=True,
                            verify=verify)
    #print(response)
    return session


# does not seem to have any effect
# probably all wrong
def logout(session, hosturl, verify=True, secure=False):
    data = {
        'hiddenMethod': 'logout',
    }
    if secure:
        hosturl = hosturl.replace("http://", "https://")
    response = session.post(hosturl, data=data, headers=TEXTHEADERS, allow_redirects=True,
                            verify=verify)
    return response


def findpackage(session, hosturl, packagename, verify=True, secure=False):
    url = "{0}/package".format(hosturl)
    if secure:
        url = url.replace("http://", "https://")
    r = session.get(url, headers=JSONHEADERS, verify=verify)
    for p in r.json()['package']:
        if packagename == p['name']:
            return p['id']
    raise Exception("no package found in {0} with name {1}".format(hosturl, packagename))


def commonparser(prog, description):
    parser = ArgumentParser(prog=prog, description=description)
    parser.add_argument('--host', dest='host', action='store', default=DEFAULT_HOST,
                        help='host url other than https://enviPath.org')
    parser.add_argument('--user', dest='user', action='store', default=ANONYMOUS,
                        help='login user name')
    parser.add_argument('--password', dest='password', action='store',
                        help='login password')
    parser.add_argument('--verify-not', dest='verify', action='store_false',
                        help='skip signature verification')
    parser.add_argument('--package', dest='package', action='store', default=ANONYMOUS,
                        help='package name')
    parser.add_argument('--name', dest='name', action='store',
                        help='object name')
    return parser


def getjson(session, url, verify=True, secure=False):
    if secure:
        url = url.replace("http://", "https://")
    r = session.get(url, headers=JSONHEADERS, allow_redirects=True,
                    verify=verify)
    return r.json()


def get(session, url, verify=True, secure=False):
    return getjson(session=session, url=url, verify=verify, secure=secure)


def post(session, url, data, verify=True, secure=False):
    if secure:
        url = url.replace("http://", "https://")
    r = session.post(url, data=data, headers=JSONHEADERS, allow_redirects=True,
                     verify=verify)
    return r.json()


def rename(session, object, newname, verify=True, secure=False):
    if secure:
        url = object.replace("http://", "https://")
    else:
        url = object
    data = {"name": newname, "defaultName": "defaultName"}
    r = session.post(url, data=data, headers=JSONHEADERS, allow_redirects=True,
                     verify=verify)
    if r.json().get("name") != newname:
        print(r.json())
        raise Exception("renaming to {} failed for {}".format(newname, object))


def importpackage(session, hosturl, jsonfile, verify=True, secure=False):
    url = "{}/package".format(hosturl)
    if secure:
        url = url.replace("http://", "https://")
    data = {"hiddenMethod": "IMPORTFROMJSON"}
    files = {"file": (jsonfile, open(jsonfile, 'rb'))}
    response = session.post(url, data=data, files=files, headers=JSONHEADERS,
                            allow_redirects=True, verify=verify)
    response.raise_for_status()


def exportpackage(session, packageurl, outfile=None, verify=True, secure=False):
    params = {'exportAsJson': 'true'}
    if secure:
        packageurl = packageurl.replace("http://", "https://")
    response = session.get(packageurl, params=params, headers=JSONHEADERS,
                           stream=(not outfile), verify=verify)

    if not outfile:
        return response.json()

    with open(outfile, 'wb') as handle:
        for block in response.iter_content(1024):
            handle.write(block)

    response.raise_for_status()


def runRule(session, ruleurl, smiles, verify=True, secure=False):
    data = {'hiddenMethod': 'APPLYRULES', 'compound': smiles}
    if secure:
        ruleurl = ruleurl.replace("http://", "https://")
    r = session.post(ruleurl, data=data, headers=JSONHEADERS,
                     verify=verify)
    return r.content.decode().strip().split("\n")


def updateScenario(session, scenario, soilsource=None, soiltexture1=None, soiltexture2=None,
        soilclassificationsystem=None, redox=None, acidity=None, temperature=None,
        waterstoragecapacity=None, humidity=None, omcontent=None, cec=None, bulkdens=None,
        biomass=None, spikecompoundsmiles=None, spikeconcentration=None, halflife=None,
        minormajor=None, proposedintermediate=None, confidencelevel=None, referringscenario=None, enzyme=None,
        addInfoTypes=[], addInfoInput={}, verify=True, secure=False):
    url = scenario
    if secure:
        url = url.replace("http://", "https://")
    data = {"updateScenario": "true"}
    addinfos = collectData(data,
        soilsource=soilsource,
        soiltexture1=soiltexture1,
        soiltexture2=soiltexture2,
        soilclassificationsystem=soilclassificationsystem,
        redox=redox,
        acidity=acidity,
        temperature=temperature,
        waterstoragecapacity=waterstoragecapacity,
        humidity=humidity,
        omcontent=omcontent,
        cec=cec,
        bulkdens=bulkdens,
        biomass=biomass,
        spikecompoundsmiles=spikecompoundsmiles,
        spikeconcentration=spikeconcentration,
        halflife=halflife,
        minormajor=minormajor,
        proposedintermediate=proposedintermediate,
        confidencelevel=confidencelevel,
        referringscenario=referringscenario,
        enzyme=enzyme)
    for k,v in addInfoInput.items():
        data[k] = v
    if addinfos:
        data['adInfoTypes[]'] = ",".join(addinfos+addInfoTypes)

    r = session.post(url, data=data, headers=JSONHEADERS, allow_redirects=True,
                     verify=verify)
    try:
        if r.json().get('status') and r.json().get('status')!=200:
            raise Exception("post failure {} {}".format(r.json().get('status'), r.json().get('message')))
        return r.json()
    except ValueError as ve:
        from sys import stderr
        stderr.write("{} to json failed, message {}, status code {}\n".format(url, str(ve), r.status_code))
        return {}


def addScenario(session, url, scenario, verify=True, secure=False):
    data = {"scenario": scenario}
    # for some obscure reason, rules requires a 'hidden' parameter be set to 'addScen'
    if '-rule/' in url:
        data['hidden'] = 'addScen'
    headers = {"Accept": "application/json", "referer": url}
    if secure:
        url = url.replace("http://", "https://")
    try:
        response = session.post(url, data=data, headers=headers,
                                allow_redirects=True, verify=verify)
    except Exception as e:
        raise
    response.raise_for_status()
    return response


def extractrange(x):
    try:
        min_, max_ = x.split(' - ')
        return min_, max_
    except:
        pass
    try:
        min_, max_ = x
        if min_ is None:
            return max_, max_
        if max_ is None:
            return min_, min_
        return min_, max_
    except:
        pass
    return x, x


def unNone(x, c='-'):
    if x is None:
        return c
    return x


def blankMap(m):
    if not m:
        return True
    for x in m.values():
        if x is not None:
            return False
    return True


def blankList(l):
    if not l:
        return l != 0
    try:
        for x in l:
            if x is not None:
                return False
        return True
    except TypeError:
        return False


def createScenario(
        session, package,
        plainname=None,
        description=None,
        studydate=None,
        scenariotype=None,

        soilsource=None,
        soiltexture1=None,
        soiltexture2=None,
        soilclassificationsystem=None,
        redox=None,
        acidity=None,
        temperature=None,
        waterstoragecapacity=None,
        humidity=None,
        omcontent=None,
        cec=None,
        bulkdens=None,
        biomass=None,
        spikecompoundsmiles=None,
        spikeconcentration=None,

        halflife=None,
        minormajor=None,
        proposedintermediate=None,
        confidencelevel=None,
        referringscenario=None,

        enzyme=None,

        verify=True,
        secure=False):

    url = package+"/scenario"
    if secure:
        url = url.replace("http://", "https://")
    data = {
        #scenario
        'studyname': plainname,
        'studydescription': description,
        'date': studydate,
        'type': scenariotype,
    }
    addinfos = collectData(data=data,
        soilsource=soilsource,
        soiltexture1=soiltexture1,
        soiltexture2=soiltexture2,
        soilclassificationsystem=soilclassificationsystem,
        redox=redox,
        acidity=acidity,
        temperature=temperature,
        waterstoragecapacity=waterstoragecapacity,
        humidity=humidity,
        omcontent=omcontent,
        cec=cec,
        bulkdens=bulkdens,
        biomass=biomass,
        spikecompoundsmiles=spikecompoundsmiles,
        spikeconcentration=spikeconcentration,
        halflife=halflife,
        minormajor=minormajor,
        proposedintermediate=proposedintermediate,
        confidencelevel=confidencelevel,
        referringscenario=referringscenario,
        enzyme=enzyme)

    # count the blessings
    if addinfos:
        data['adInfoTypes[]'] = ",".join(addinfos)
        # not sure about this one.
        # may this be the source of the referring scenario trouble?
        data['fullScenario'] = 'true'
    data['jsonredirect'] = 'true'

    response = session.post(url, data=data, headers=JSONHEADERS,
                            verify=verify)
    return respond_or_raise(response, field='scenarioLocation')


def collectData(data,
        soilsource=None,
        soiltexture1=None,
        soiltexture2=None,
        soilclassificationsystem=None,
        redox=None,
        acidity=None,
        temperature=None,
        waterstoragecapacity=None,
        humidity=None,
        omcontent=None,
        cec=None,
        bulkdens=None,
        biomass=None,
        spikecompoundsmiles=None,
        spikeconcentration=None,
        halflife=None,
        minormajor=None,
        proposedintermediate=None,
        confidencelevel=None,
        referringscenario=None,
        enzyme=None):

    addinfos = []

    # SOIL scenario
    if soilsource:
        addinfos.append('soilsource')
        data['soilsourcedata'] = soilsource

    if soiltexture1:
        soiltexture1 = soiltexture1.upper().replace(" ", "_")
        if soiltexture1 not in ['CLAY', 'SANDY_CLAY', 'SILTY_CLAY', 'SANDY_CLAY_LOAM', 'SANDY_LOAM',
                'SILTY_CLAY_LOAM', 'SAND', 'LOAMY_SAND', 'LOAM', 'SILT_LOAM', 'SILT', 'CLAY_LOAM',
                'SILTY_SAND', 'SANDY_SILT_LOAM']:
            raise WrongParameter("soiltexture1 '{}' not allowed".format(soiltexture1))
        addinfos.append('soiltexture1')
        data['soilTextureType'] = soiltexture1

    if not blankMap(soiltexture2):
        addinfos.append('soiltexture2')
        data['sand'] = unNone(soiltexture2['sand'])
        data['silt'] = unNone(soiltexture2['silt'])
        data['clay'] = unNone(soiltexture2['clay'])

    if soilclassificationsystem:
        if soilclassificationsystem not in ["USDA", "UK_ADAS"]:
            raise WrongParameter("soilclassificationsystem '{}' not allowed".format(soilclassificationsystem))
        addinfos.append('soilclassificationsystem')
        data['soilclassificationsystem'] = soilclassificationsystem

    if redox:
        if redox == 'aerobic': redox = 'aerob'
        if redox not in ["aerob", "anaerob", "anaerob: iron-reducing",
                "anaerob: sulftate-reducing", "anaerob: methanogenic conditions",
                "oxic", "nitrate-reducing"]:
            raise WrongParameter("redox '{}' not allowed".format(redox))
        addinfos.append('redox')
        data['redoxType'] = redox

    if not blankMap(acidity):
        addinfos.append('acidity')
        min_, max_ = extractrange(acidity['pH'])
        data['lowPh'] = min_
        data['highPh'] = max_
        if 'method' in acidity and acidity['method']:
            METHOD_MAP = {'H2O':'WATER', 'KCl':'KCL', 'CaCl2':'CACL2'}
            if acidity['method'] not in METHOD_MAP:
                raise WrongParameter("acidity method '{}' not allowed. must be one of {}".format(acidity['method'], METHOD_MAP.keys()))
            data['acidityType'] = METHOD_MAP[acidity['method']]

    if not blankList(temperature):
        addinfos.append('temperature')
        min_, max_ = extractrange(temperature)
        data['temperatureMin'] = min_
        data['temperatureMax'] = max_

    if not blankMap(waterstoragecapacity):
        addinfos.append('waterstoragecapacity')
        data['wst'] = unNone(waterstoragecapacity['capacity'])
        data['wstConditions'] = unNone(waterstoragecapacity['conditions'])
        try:
            data['maximumWaterstoragecapacity'] = waterstoragecapacity['maxCapacity']
        except KeyError:
            pass

    if not blankMap(humidity):
        addinfos.append('humidity')
        data['expHumid'] = humidity['percentage']
        try:
            data['humConditions'] = humidity['conditions']
        except KeyError:
            pass

    if not blankMap(omcontent):
        if omcontent['dimension'] not in ['OM', 'OC']:
            raise WrongParameter("omcontent dimension '{}' not allowed".format(omcontent['dimension']))
        addinfos.append('omcontent')
        omdimmap = {'OM':'omcontentInOM', 'OC':'omcontentINOC'}
        data[omdimmap[omcontent['dimension']]] = unNone(omcontent['content'])

    if cec:
        addinfos.append('cec')
        data['cecdata'] = cec

    if bulkdens:
        addinfos.append('bulkdens')
        data['bulkdensity'] = bulkdens

    if not blankList(biomass):
        addinfos.append('biomass')
        start, end = extractrange(biomass)
        data['biomassStart'] = unNone(start)
        data['biomassEnd'] = unNone(end)

    if spikecompoundsmiles:
        addinfos.append('spikecompound')
        data['spikeCompSmiles'] = spikecompoundsmiles

    if spikeconcentration:
        if spikeconcentration['unit'] not in ['MUG_PER_L', 'MUG_PER_KG_WET', 'MUG_PER_KG_DRY']:
            raise WrongParameter("spikeconcentration unit '{}' not allowed".format(spikeconcentration['unit']))
        addinfos.append('spikeconcentration')
        data['spikeConcentration'] = spikeconcentration['concentration']
        data['spikeconcentrationUnit'] = spikeconcentration['unit']


    # HALFLIFE scenario
    if not blankMap(halflife):
        addinfos.append('halflife')
        data['lower'] = halflife['lower']
        data['upper'] = halflife['upper']
        data['source'] = halflife['source']
        if 'model' in halflife: data['model'] = halflife['model']
        if 'fit' in halflife: data['fit'] = halflife['fit']
        if 'firstOrder' in halflife: data['firstOrder'] = halflife['firstOrder']
        if 'comment' in halflife: data['comment'] = halflife['comment']

    if minormajor:
        addinfos.append('minormajor')
        data['radiomin'] = minormajor

    if proposedintermediate:
        addinfos.append('proposedintermediate')
        data['proposed'] = proposedintermediate

    if confidencelevel:
        addinfos.append('confidencelevel')
        data['radioconfidence'] = confidencelevel

    if referringscenario:
        addinfos.append('referringscenario')
        data['referringscenario'] = referringscenario

    if not blankMap(enzyme):
        addinfos.append('enzyme')
        data['enzymeName'] = enzyme['name']
        data['enzymeECNumber'] = enzyme['ECNumber']

    return addinfos


RULEURLSUFFIX = {'SIMPLE': 'rule',
                 'PARALLEL': 'parallel-rule',
                 'SEQUENTIAL': 'sequential-rule'}
def createRule(session, packageurl, ruletype='SIMPLE',
               smirks=None, name=None, description=None,
               compositerule=None,
               simplerules=None,
               aerobiclikelihood=None,
               immediaterule=False,
               productfiltersmarts=None,
               reactantfiltersmarts=None,
               verify=True, secure=False):
    url = "{}/{}".format(packageurl, RULEURLSUFFIX[ruletype])
    if secure:
        url = url.replace("http://", "https://")

    data = {}
    if smirks: data['smirks'] = smirks
    if name: data['name'] = name
    if description: data['description'] = description
    if aerobiclikelihood: data['likelihood'] = aerobiclikelihood
    if immediaterule: data['immediaterule'] = 'true'
    if productfiltersmarts: data['productFilterSmarts'] = productfiltersmarts
    if reactantfiltersmarts: data['reactantFilterSmarts'] = reactantfiltersmarts

    if ruletype != 'SIMPLE' and not simplerules:
        raise WrongParameter("composite rules currently must have non empty simple rules at creation time")
    if simplerules: data['simpleRules[]'] = '{}'.format(
        ",".join([simplerule for simplerule in simplerules]))

    response = session.post(url, data=data, headers=JSONHEADERS,
                            verify=verify)
    rj = respond_or_raise(response)
    if compositerule:
        combineRules(session, rj.get('id'), compositerule,
                     secure=secure, verify=verify)

    if aerobiclikelihood:
        scenario = rj.get('scenarios')[0].get('id')
        scenarioname = rj.get('scenarios')[0].get('name')
        newname = '{} aerobic likelihood'.format(scenarioname)
        try:
            rename(session, scenario,
               newname,
               secure=secure, verify=verify)
        except Exception as e:
            from sys import stderr
            stderr.write("WARNING: failed to rename aerobic likelihood from '{}' to '{}'".format(scenarioname, newname))


    return rj


def updateRule(session, ruleurl,
               smirks=None, name=None, description=None,
               verify=True, secure=False):
    if secure:
        ruleurl = ruleurl.replace("http://", "https://")

    data = {}
    if smirks:
        data['smirks'] = smirks
    if name:
        data['name'] = name
    if description:
        data['description'] = description

    r = session.post(ruleurl, data=data,
                     headers=JSONHEADERS, verify=verify)

    try:
        if r.json().get('status') and r.json().get('status')!=200:
            raise Exception("post failure {} {}".format(r.json().get('status'), r.json().get('message')))
        return r.json()
    except ValueError as ve:
        from sys import stderr
        stderr.write("{} to json failed, message {}, status code {}\n".format(ruleurl, str(ve), r.status_code))
        return {}


def combineRules(session, simplerule, compositerule, verify=True, secure=False):
    if secure:
        compositerule = compositerule.replace("http://", "https://")
        simplerule = simplerule.replace("http://", "https://")

    data = {'simpleRule': simplerule}
    response = session.post(compositerule, data=data,
                            headers=JSONHEADERS, verify=verify)
    return respond_or_raise(response)


def separateRules(session, simplerule, compositerule, verify=True, secure=False):
    if secure:
        compositerule = compositerule.replace("http://", "https://")
        simplerule = simplerule.replace("http://", "https://")

    data = {'simpleRule': simplerule, 'hidden': 'delete'}
    response = session.post(compositerule, data=data,
                            headers=JSONHEADERS, verify=verify)
    return respond_or_raise(response)


def separateRule(session, simplerule, verify=True, secure=False):
    if secure:
        simplerule = simplerule.replace("http://", "https://")

    srj = session.get(simplerule, headers=JSONHEADERS, verify=verify).json()
    for compositerule in srj.get('includedInCompositeRule'):
        compositeruleurl = compositerule.get('id')
        if secure: compositeruleurl = compositeruleurl.replace("http://", "https://")
        response = session.post(compositeruleurl, data={'simpleRule': simplerule, 'hidden': 'delete'},
                                headers=JSONHEADERS, verify=verify)
        response.raise_for_status()
    return session.get(simplerule, headers=JSONHEADERS, verify=verify).json()


def createPathway(session, packageurl, smiles, name=None,
                  description=None, verify=True, secure=False):
    properties = {'smilesinput': smiles, 'name': name, 'description': description, 'rootOnly': 'true'}
    return createEntity(session, packageurl, 'pathway', properties=properties, verify=verify, secure=secure)


def predictPathway(session, package_url, root_smiles, settings_url=None, hangon=True, verify=True, secure=False):

    data = {
        "smilesinput": root_smiles,
        "selectedSetting": settings_url
    }
    pw = createEntity(session, package_url, 'pathway', properties=data, verify=verify, secure=secure)
    pwurl = pw["id"]

    while hangon:
        try:
            if pw["completed"].lower() == "true":
                break
        except Exception as ke:
            from sys import stderr
            stderr.write("ERROR: couldnt get completeness ({0}) on {1}\n".format(ke.__class__.__name__, pwurl))
            break
        import time
        time.sleep(5.0)
        pw = getjson(session, pwurl, verify=verify, secure=secure)

    return pw


def addCompoundToPathway(session, pathwayurl, smiles, verify=True, secure=False):
    return createEntity(session, pathwayurl, 'node', properties={'nodeAsSmiles': smiles},
                        secure=secure, verify=verify, headers={"Accept": "application/json", "referer": pathwayurl})


def createCompound(session, packageurl, smiles, name=None,
                  description=None, verify=True, secure=False):
    properties = {'compoundSmiles': smiles, 'compoundName': name, 'compoundDescription': description}
    return createEntity(session, packageurl, 'compound', properties=properties, secure=secure, verify=verify)


def statusexception(number, message):
    if int(number) > 499 and int(number) < 600:
        raise E500(message)
    if int(number) > 399 and int(number) < 500:
        raise E400(message)
    raise Exception("ERROR {} - {}".format(number, message))


def createEntity(session, packageurl, objectid,
                 properties={}, name=None, description=None,
                 verify=True, secure=False, headers=JSONHEADERS):
    url = "{}/{}".format(packageurl, objectid)
    if secure: url = url.replace("http://", "https://")
    if name: properties['name'] = name
    if description: properties['description'] = description
    response = session.post(url, data=properties, headers=headers, verify=verify)
    return respond_or_raise(response)


def respond_or_raise(response, field=None):
    try:
        response.raise_for_status()
        return response.json().get(field) if field else response.json()
    except Exception as e:
        try:
            ej = response.json()
        except:
            raise e
        statusexception(ej.get('status'),
                        "{}: {}".format(ej.get('type'), ej.get('message')))


def _analyse(url):
    if not url: return {}

    from re import match
    uid_pattern = r'[\dabcdef]{8}-[\dabcdef]{4}-[\dabcdef]{4}-[\dabcdef]{4}-[\dabcdef]{12}$'

    pieces = url.split("/")
    if len(pieces) < 4: return {}
    if pieces[0] not in ['http:', 'https:']: return {}
    if pieces[1] != '': return {}

    urlmap = {}
    urlmap['host'] = pieces[2]
    for i in range(4, len(pieces), 2):
        if not match(uid_pattern, pieces[i]): return {}
        urlmap[pieces[i - 1]] = pieces[i]

    return urlmap


def _check_ec_number(ec_number):
    from re import match
    ec_pattern = r'\d+.(\d+|-).(\d+|-).(\d+|-)$'
    if not match(ec_pattern, ec_number):
        raise ValueError("ec number not according to the rules")


def add_ec_number(session, rule_url, ec_number, name=None, linking_method=None, evidence=[], description=None,
                  verify=True, secure=False):
    _check_ec_number(ec_number)
    if secure: rule_url = rule_url.replace("http://", "https://")

    data = {
        'ecno': ec_number,
        'method': linking_method,
        'name': name
    }

    _post_ec_number(evidence, description, url=rule_url, mut_data=data)

    response = session.post("{}/enzymelink".format(rule_url), data=data, headers=JSONHEADERS, verify=verify)
    return response


def update_ec_number(session, eclink_url, ec_number=None, name=None, linking_method=None, evidence=[], description=None,
                     verify=True, secure=False):
    if secure: eclink_url = eclink_url.replace("http://", "https://")

    data = {}
    if ec_number:
        _check_ec_number(ec_number)
        data['ecno'] = ec_number
    if linking_method: data['method'] = linking_method
    if name: data['name'] = name

    _post_ec_number(evidence, description, url=eclink_url, mut_data=data)

    response = session.post(eclink_url, data=data, headers=JSONHEADERS, verify=verify)
    return response


def _post_ec_number(evidence, description, url, mut_data):

    urlmap = _analyse(url)
    if not 'package' in urlmap:
        raise ValueError("that's not a valid rule url")

    if description:
        mut_data['descr'] = description

    reactions, edges, general = [], [], []
    for e in evidence:
        evidencemap = _analyse(e)
        if 'package' in evidencemap:
            if urlmap['host'] == evidencemap['host']:
                if 'reaction' in evidencemap:
                    reactions.append(e)
                    continue
                if 'edge' in evidencemap:
                    edges.append(e)
                    continue
        general.append(e)

    if reactions:
        mut_data['reac'] = ';'.join(reactions)
    if edges:
        mut_data['edge'] = ';'.join(edges)
    if general:
        mut_data['evidence'] = ';'.join(general)


def remove_ec_number(session, eclink_url, verify=True, secure=False):
    if secure: eclink_url = eclink_url.replace("http://", "https://")
    session.delete(eclink_url, headers=JSONHEADERS, verify=verify)
