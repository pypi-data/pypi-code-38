class BaseObject(object):

    def __init__(self, object):
        self.id = object['id']
        self.name = object['name']


class Category(BaseObject):

    def __init__(self, category):
        super().__init__(category)
        self.client_id = category['clientId']
        self.parent_id = category['parentId']
        self.deleted = category['deleted']

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'parentId': self.parent_id,
            'clientId': self.client_id,
            'deleted': self.deleted
        }


class Automaton(BaseObject):

    def __init__(self, automaton):
        super().__init__(automaton)
        self.categoryId = automaton['categoryId']
        self.clientId = automaton['clientId']
        self.deleted = automaton['deleted']
        self.template = automaton['template']
        self.archived = automaton['archived']
        self.latestAutomatonVersion = automaton['latestAutomatonVersion']
        self.automatonVersion = automaton['automatonVersion']
        self.wrappedAutomatonIds = automaton['wrappedAutomatonIds']

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'categoryId': self.categoryId,
            'clientId': self.clientId,
            'template': self.template,
            'deleted': self.deleted,
            'archived': self.archived,
            'latestAutomatonVersion': self.latestAutomatonVersion,
            'automatonVersion': self.automatonVersion,
            'wrappedAutomatonIds': self.wrappedAutomatonIds
        }


class AutomatonVersion(object):

    def __init__(self, version):
        self.approvalStatus = version['approvalStatus']
        self.archived = version['archived']
        self.archivedDate = version['archivedDate']
        self.automaton = version['automaton']
        self.comments = version['comments']
        self.connectionGroups = version['connectionGroups']
        self.createdDate = version['createdDate']
        self.creatorId = version['creatorId']
        self.creatorName = version['creatorName']
        self.designerDiagram = version['designerDiagram']
        self.equivalentEngineerTime = version['equivalentEngineerTime']
        self.equivalentEngineerTimeString = version['equivalentEngineerTimeString']
        self.executionGroupId = version['executionGroupId']
        self.executionMode = version['executionMode']
        self.flow = version['flow']
        self.live = version['live']
        self.matcherDsl = version['matcherDsl']
        self.newExecutionThrottleCount = version['newExecutionThrottleCount']
        self.newExecutionThrottlePeriodSeconds = version['newExecutionThrottlePeriodSeconds']
        self.notes = version['notes']
        self.purpose = version['purpose']
        self.serializedFlow = version['serializedFlow']
        self.signedAutomaton = version['signedAutomaton']
        self.tags = version['tags']
        self.versionId = version['versionId']
        self.versionNumber = version['versionNumber']

    def json(self):
        return {
            'approvalStatus': self.approvalStatus,
            'archived': self.archived,
            'archivedDate': self.archivedDate,
            'automaton': self.automaton,
            'comments': self.comments,
            'connectionGroups': self.connectionGroups,
            'createdDate': self.createdDate,
            'creatorId': self.creatorId,
            'creatorName': self.creatorName,
            'designerDiagram': self.designerDiagram,
            'equivalentEngineerTime': self.equivalentEngineerTime,
            'equivalentEngineerTimeString': self.equivalentEngineerTimeString,
            'executionGroupId': self.executionGroupId,
            'executionMode': self.executionMode,
            'flow': self.flow,
            'live': self.live,
            'matcherDsl': self.matcherDsl,
            'newExecutionThrottleCount': self.newExecutionThrottleCount,
            'newExecutionThrottlePeriodSeconds': self.newExecutionThrottlePeriodSeconds,
            'notes': self.notes,
            'purpose': self.purpose,
            'serializedFlow': self.serializedFlow,
            'signedAutomaton': self.signedAutomaton,
            'tags': self.tags,
            'versionId': self.versionId,
            'versionNumber': self.versionNumber
        }


class ExportedAutomaton(BaseObject):

    def __init__(self, automaton):
        super().__init__(automaton)
        self.automatonConnectionGroups = automaton['automatonConnectionGroups']
        self.automatonFlow = automaton['automatonFlow']
        self.categoryPath = automaton['categoryPath']
        self.clientCode = automaton['clientCode']
        self.creatorId = automaton['creatorId']
        self.creatorName = automaton['creatorName']
        self.designerDiagram = automaton['designerDiagram']
        self.equivalentEngineerTime = automaton['equivalentEngineerTime']
        self.executionMode = automaton['executionMode']
        self.linkedAutomatons = automaton['linkedAutomatons']
        self.matcherDsl = automaton['matcherDsl']
        self.newExecutionThrottleCount = automaton['newExecutionThrottleCount']
        self.newExecutionThrottlePeriodSeconds = automaton['newExecutionThrottlePeriodSeconds']
        self.notes = automaton['notes']
        self.purpose = automaton['purpose']
        self.tags = automaton['tags']
        self.template = automaton['template']
        self.versionId = automaton['versionId']
        self.versionNumber = automaton['versionNumber']

    def json(self):
        return {
            'automatonConnectionGroups': self.automatonConnectionGroups,
            'automatonFlow': self.automatonFlow,
            'categoryPath': self.categoryPath,
            'clientCode': self.clientCode,
            'creatorId': self.creatorId,
            'creatorName': self.creatorName,
            'designerDiagram': self.designerDiagram,
            'equivalentEngineerTime': self.equivalentEngineerTime,
            'executionMode': self.executionMode,
            'linkedAutomatons': self.linkedAutomatons,
            'matcherDsl': self.matcherDsl,
            'newExecutionThrottleCount': self.newExecutionThrottleCount,
            'newExecutionThrottlePeriodSeconds': self.newExecutionThrottlePeriodSeconds,
            'notes': self.notes,
            'purpose': self.purpose,
            'tags': self.tags,
            'template': self.template,
            'versionId': self.versionId,
            'versionNumber': self.versionNumber,
        }


# Node Structure for N-ary Tree
class Node:
    parent = None
    children = []
    path = ''

    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.children = []
        self.parent = None
        self.path = ''
