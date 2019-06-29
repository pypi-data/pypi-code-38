import json
from collections import OrderedDict

from brokerRPC import VistARPCConnection, RPCLogger
from rpcUtils import toRPCListForm, toFMDateTime, shiftMultiLineString, fillTemplateArguments

"""
purgeAllergies AND VICS DB ...

Allergy:

> db["Allergy"].deleteMany({})
{ "acknowledged" : true, "deletedCount" : 7 }
> db["Allergy"].count()
0

AND 

Assessment:

> db["AllergyAssessment"].count()
5
> db["AllergyAssessment"].deleteMany({})
{ "acknowledged" : true, "deletedCount" : 5 }
> db["AllergyAssessment"].count()
0

    x = json.load(open("ALLERGY_TESTS.json"), object_pairs_hook=OrderedDict)
    json.dump(x, open("ALLERGY_TESTS_N.json", "w"), indent=4)

"""

HOST = "10.2.2.222"
# PORT = 9430
PORT = 9011
ACCESS = "fakedoc1"
VERIFY = "1doc!@#$"

TEMPLATE_SETTINGS = {
    "USERIEN": "63",
    "PATIENTIEN": "25",
    "NOW": toFMDateTime(),
    "CHOCOLATEIEN": "3"
}

def main():

    print
    print "ALLERGY RPCs to {}:{}".format(HOST, PORT)
    print
    # Establishes Login to CPRS (everything else follows)
    connection = VistARPCConnection(HOST, int(PORT), ACCESS, VERIFY, "OR CPRS GUI CHART", RPCLogger())
    log = []
    rpcsSent = OrderedDict()
    rpcSequence = json.load(open("ALLERGY_TESTS.json"))["sequence"]
    flattenAllergyTests = OrderedDict()
    flattenAllergyTests["description"] = json.load(open("ALLERGY_TESTS.json"))["description"]
    flattenAllergyTests["sequence"] = []
    for i, rpcInfo in enumerate(rpcSequence, 1):
        rpcArgs = fillTemplateArguments(rpcInfo["args"], TEMPLATE_SETTINGS)
        rpcArgs = [toRPCListForm(rpcArg) for rpcArg in rpcArgs]
        print "\n{}. Sending {}: {}".format(i, rpcInfo["name"], json.dumps(rpcArgs))
        reply = connection.invokeRPC(rpcInfo["name"], rpcArgs)
        fInfo = OrderedDict([("name", rpcInfo["name"]), ("args", rpcArgs)])
        if "comment" in rpcInfo:
            fInfo["comment"] = rpcInfo["comment"]
        flattenAllergyTests["sequence"].append(fInfo) 
        if rpcInfo["name"] not in rpcsSent:
            rpcsSent[rpcInfo["name"]] = 1
        else:
            rpcsSent[rpcInfo["name"]] += 1
        logInfo = OrderedDict([("rpc", rpcInfo["name"]), ("args", rpcArgs)])
        if "comment" in rpcInfo:
            logInfo["comment"] = rpcInfo["comment"]
        logInfo["reply"] = reply
        log.append(logInfo)
        print "REPLY: {}".format(shiftMultiLineString(reply))
        print
    print
    json.dump(OrderedDict([("endpoint", "{}:{}".format(HOST, PORT)), ("log", log), ("rpcTotals", rpcsSent)]), open("allergyLog.json", "w"), indent=4)
    # FOR USE IN JS until JS does templates
    json.dump(flattenAllergyTests, open("ALLERGY_TEST_FLAT.json", "w"), indent=4)

if __name__ == "__main__":
    main()
