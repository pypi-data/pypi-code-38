import xmltodict
import json

# TODO: resolve need to always align elements > 0,0 in camunda modeler

# this module reads from a given bpmn/xml file and completes a given skeleton template by initialized blocks and their order


def Parse_BPMN(BPMNPATH, JSONPATH, TEMPLATEPATH, MODELPATH):
    ##########################################################################################################
    # prepare as json-formatted dict and save json for quick manual analysis if needed

    with open(BPMNPATH, 'rb') as f:
        bpmn = xmltodict.parse(f)
        bpmn = json.loads(json.dumps(bpmn, indent=4))

    with open(JSONPATH, 'w+') as f:
        json.dump(bpmn, f, indent=4)

    ##########################################################################################################
    # bpmn parsing

    mapping = {
        "dataStoreReference": "resources",
        "startEvent": "sources",
        "endEvent": "sinks",
        "task": "tasks",
        "exclusiveGateway": "xGateways",
        "sequenceFlow": "connectors",
        "textAnnotation": "textAnnotations",
        "association": "associations"
    }

    elements = {
        value: getElements(bpmn, key) for key, value in mapping.items()
    }

    insertions = []
    # resources
    """
    for resource in elements["resources"]:
        names = resource["@name"].split(":")
        names = [n.strip() for n in names]
        className = names[0]
        idName = names[1]
        insertions.append("self.%s = %s(self.env, '%s', c)\n\n" % (idName,
                                                                   className, idName))
        resource["idName"] = idName
    """

    # components
    components = elements["sources"] + elements["sinks"] + \
        elements["tasks"] + elements["xGateways"]

    for comp in elements["resources"] + components:
        names = comp["@name"].split(":")
        # add removal of possibly leading/trailing blanks
        names = [n.strip() for n in names]
        comp["className"] = names[0]
        comp["idName"] = names[1]

    for comp in elements["resources"] + components:
        className = comp["className"]
        idName = comp["idName"]

        xy = get_shape_xy(comp["@id"], bpmn)

        resName = getRelatedResourceIDName(comp, elements)

        if resName is None:
            insertions.append("self.%s = %s(self.env, '%s', xy=%s" % (idName,
                                                                      className, idName, xy))
        else:
            insertions.append("self.%s = %s(self.env, '%s', self.%s, xy=%s" % (
                idName, className, idName, resName, xy))

        insertions[-1] += getRelatedTextAnnotations(comp, elements)

        insertions[-1] += ", ways=" + \
            str(getWaysToSuccessors(comp, bpmn, elements, components))

        # close bracket and 2x newline
        insertions[-1] += ")\n\n"

    mC = "self.modelComponents = {" + ", ".join(
        ["'" + comp["idName"] + "': self." + comp["idName"] for comp in components]) + "}"

    modelGraphNames = {
        comp["idName"]: getSuccessorNamesList(comp, elements, components) for comp in components if not (getSuccessorNamesList(comp, elements, components) is None)
    }

    ##########################################################################################################
    # file writing

    # read template file
    with open(TEMPLATEPATH, 'r') as f:
        template = f.readlines()

    # find resources+components insertion space
    for idx, line in enumerate(template):
        if "#!resources+components" in line:
            loc = idx + 1
            template.insert(loc, "\n")
            break

    for iLine in insertions:
        loc += 1
        template.insert(loc, "".join([" " for _ in range(8)]) + iLine)

    # find #!model insertion space
    for idx, line in enumerate(template):
        if "#!model" in line:
            loc = idx
            break

    loc += 1
    template.insert(loc, "\n" + "".join([" " for _ in range(8)]) + mC)
    loc += 1
    template.insert(loc, "\n\n" + "".join([" " for _ in range(8)])
                    + "self.modelGraphNames = " + json.dumps(modelGraphNames))

    with open(MODELPATH, 'w+') as f:
        f.writelines(template)

    print("\nBPMN parsed.\n")


""" BPMN parsed """


def get_shape_xy(elid, xmlo):
    for s in xmlo["bpmn:definitions"]["bpmndi:BPMNDiagram"]["bpmndi:BPMNPlane"]["bpmndi:BPMNShape"]:
        if s["@bpmnElement"] == elid:
            x, y = (int(s["dc:Bounds"]["@x"]) + int(int(s["dc:Bounds"]["@width"]) / 2),
                    int(s["dc:Bounds"]["@y"]) + int(int(s["dc:Bounds"]["@height"]) / 2))
            return x, y


def getElements(bpmn, elementType):
    subDict = bpmn['bpmn:definitions']['bpmn:process']
    if 'bpmn:' + elementType in subDict:
        elements = subDict['bpmn:' + elementType]
        return elements if isinstance(elements, list) else [elements]
    else:
        return []


def containsResourceRelation(component):
    if ("bpmn:dataInputAssociation" in component) or ("bpmn:dataOutputAssociation" in component):
        return True
    else:
        return False


def findResIDName(bpmnID, elements):
    for res in elements["resources"]:
        if res["@id"] == bpmnID:
            return res["idName"]


def getRelatedResourceIDName(component, elements):
    if "bpmn:dataInputAssociation" in component:
        bpmnID = component["bpmn:dataInputAssociation"]["bpmn:sourceRef"]
        return findResIDName(bpmnID, elements)
    elif "bpmn:dataOutputAssociation" in component:
        bpmnID = component["bpmn:dataOutputAssociation"]["bpmn:targetRef"]
        return findResIDName(bpmnID, elements)
    else:
        return None


def getRelatedTextAnnotations(component, elements):
    associations = [assoc for assoc in elements["associations"]
                    if assoc["@sourceRef"] == component["@id"]]
    # get corresponding textAnnotations
    annotations = []
    for assoc in associations:
        annotations += [annot for annot in elements["textAnnotations"]
                        if annot["@id"] == assoc["@targetRef"]]
    params = []
    for annot in annotations:
        params += [x.strip() for x in annot["bpmn:text"].split(";")]
    text = ""
    if len(params) > 0:
        text = ", " + ", ".join(params)
    return text


def getOutgoingSFs(comp):
    # get list of outgoing sequence flows
    if "bpmn:outgoing" not in comp:
        return None
    outgoingSFs = comp["bpmn:outgoing"]
    outgoingSFs = [outgoingSFs] if not isinstance(
        outgoingSFs, list) else outgoingSFs
    return outgoingSFs


def getSuccessorNamesList(comp, elements, components):
    outgoingSFs = getOutgoingSFs(comp)
    res = []
    if outgoingSFs is not None:
        for SF in outgoingSFs:
            # find SF element -> find targetRef -> append idName
            for con in elements["connectors"]:
                if con["@id"] == SF:
                    targetID = con["@targetRef"]
                    for targetComp in components:
                        if targetComp["@id"] == targetID:
                            res.append(targetComp["idName"])
                            break
                    break
    return res


def getDiagramWaypointsForSFID(SFID, xmlo):
    waypoints = []
    for s in xmlo["bpmn:definitions"]["bpmndi:BPMNDiagram"]["bpmndi:BPMNPlane"]["bpmndi:BPMNEdge"]:
        if s["@bpmnElement"] == SFID:
            for waypoint in s["di:waypoint"]:
                waypoints.append(
                    (int(waypoint["@x"]),
                     int(waypoint["@y"]))
                )
            return waypoints


def getWaysToSuccessors(comp, xmlo, elements, components):
    results = {}  # {"suc name":[{x: int, y: int}, ...]}
    outgoingSFs = getOutgoingSFs(comp)
    if outgoingSFs is not None:
        for SF in outgoingSFs:
            # find SF element -> find targetRef -> append idName: waypoints
            for con in elements["connectors"]:
                if con["@id"] == SF:
                    targetID = con["@targetRef"]
                    for targetComp in components:
                        if targetComp["@id"] == targetID:
                            waypoints = getDiagramWaypointsForSFID(
                                con["@id"], xmlo)
                            # [{x: int, y: int}]
                            results[targetComp["idName"]] = waypoints
                            break
                    break
    return results
