#!/usr/bin/python3

"""
moiety_modeling.model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides the :class:`~moiety_modeling.model.Moiety` class, the :class:`~moiety_modeling.model.Molecule`
class, the :class:`~moiety_modeling.model.Relationship` class, and the :class:`~moiety_modeling.model.Model`
class to construct moiety model.

"""

import sys
import itertools
import collections

__all__ = ['Moiety', 'Relationship', 'Molecule', 'Model']


class Moiety:

    """Moiety class describes the :class:`~moiety_modeling.model.Moiety` entity in the moiety model."""

    def __init__(self, name, maxIsotopeNum, isotopeStates, nickname=' ', ranking=0):
        """Moiety initializer.

        :param str name: the name of the moiety.
        :param dict maxIsotopeNum: the dictionary of the labeling isotopes and the corresponding number in the moiety. eg: {'13C': 5, '15N': 3}
        :param dict isotopeStates: the dictionary of the labeling isotopes and the corresponding states in the moiety. eg: {'13C': [0, 2, 5], '15N': [2, 3]}
        :param str nickname: the nickname of the moiety.
        :param int ranking: the ranking of the moiety.
        """
        self.name = name
        self.maxIsotopeNum = dict(maxIsotopeNum)
        self.isotopeStates = dict(isotopeStates)
        self.nickname = nickname
        self.ranking = ranking
        self.states = self._createStates()

    def _createStates(self):

        """
        To calculate the states of moiety. The combinations of each isotope and its state.
        :return: the list of states of the moiety. eg: ['13C0.15N2', '13C2.15N3']
        """

        states = []
        isotopes = sorted(self.isotopeStates)
        for moietyStateComposition in itertools.product(*[self.isotopeStates[isotope] for isotope in isotopes]):
            states.append('.'.join([isotopes[i] + str(moietyStateComposition[i]) for i in range(len(isotopes))]))
        return states

    def __str__(self):

        """Convert the moiety object into string representation.
        :return: the string representation.
        """

        isotopes = sorted(self.isotopeStates)
        string = "Moiety: {0}({1}) \tIsotopes: {2} \tIsotopeStates: ".format(self.name, self.nickname, ','.join(["{0}({1})".format(isotope, self.maxIsotopeNum[isotope]) for isotope in isotopes]))
        for isotope in isotopes:
            string += "{0}[{1}]  ".format(isotope, ', '.join(str(i) for i in self.isotopeStates[isotope]))
        string += "\nMoietyStates: [{0}]".format(', '.join(self.states))
        return string


class Relationship:

    """Relationship class describes the relationship between moiety states in the moiety model."""

    def __init__(self, moiety, moietyState, equivalentMoiety, equivalentMoietyState, operator=None, coefficient=None):
        """Relationship initializer.

        :param moiety: the :class:`~moiety_modeling.model.Moiety` in the relationship.
        :type moiety: :class:`~moiety_modeling.model.Moiety`
        :param str moietyState: the state of the moiety (eg: '13C0.15N1').
        :param equivalentMoiety: :class:`~moiety_modeling.model.Moiety` in the relationship.
        :type equivalentMoiety: :class:`~moiety_modeling.model.Moiety`
        :param str equivalentMoietyState: the state of the equivalentMoiety (eg: '13C0.15N1').
        :param str operator: the operator of the relationship ('*', '/').
        :param double coefficient: the coefficient of the relationship.
        """

        self.moiety = moiety
        self.moietyState = moietyState
        self.equivalentMoiety = equivalentMoiety
        self.equivalentMoietyState = equivalentMoietyState
        self.varName = '{0}[{1}]'.format(self.moiety.name, self.moietyState)
        self.equivalentVarName = '{0}[{1}]'.format(self.equivalentMoiety.name, self.equivalentMoietyState)

        if operator == "/" and coefficient == 0:
            sys.exit("Division by zero in relationship")
        if operator == "*":
            self.multiplier = coefficient
        elif operator == "/":
            self.multiplier = 1/coefficient
        else:
            self.multiplier = 1

    def __str__(self):

        """Converts the relationship to a string representation.
        :return: the string representation.
        """

        if self.multiplier == 1:
            return "Relationship: {0} = {1}".format(self.varName, self.equivalentVarName)
        else:
            return "Relationship: {0} = {1} * {2}".format(self.varName, self.equivalentVarName, self.multiplier)


class Molecule:

    """Molecule class describes the :class:`~moiety_modeling.model.Molecule` entity in the moiety model"""

    def __init__(self, name, moieties):
        """Molecule initializer.

        :param str name: the name of the molecule.
        :param list moieties: the list of :class:`~moiety_modeling.model.Moiety` instances that make up for the :class:`~moiety_modeling.model.Molecule`.
        """

        self.name = name
        self.moieties = list(moieties)
        self.allStates = self._createAllStates()
        self.standardStates = self._createStandardStates()

    def __eq__(self, other):

        return self.name == other.name

    def _createAllStates(self):

        """Calculate all the possible molecule states based on the max isotope number.

        :return: the list of the molecule states. eg: ['13C0.15N0', '13C1.15N0'...]
        """
        # moiety1: {'13C': 6, '15N': 3}, {'13C': [0, 2, 5], '15N': [2, 3]}; moiety2: {'13C': 4, '15N': 5}, {'13C': [1, 3, 4], '15N': [1, 5]}
        # moietyIsotopeNum = [[6, 4], [3, 5]]
        allStates = []
        isotopes = sorted(self.moieties[0].isotopeStates)
        moietyIsotopeNumList = [[moiety.maxIsotopeNum[isotope] for moiety in self.moieties] for isotope in sorted(self.moieties[0].isotopeStates)]
        allStateCompositions = [[i for i in range(sum(isotopeNumList)+1)] for isotopeNumList in moietyIsotopeNumList]
        for moleculeStateComposition in itertools.product(*allStateCompositions):
            allStates.append('.'.join([isotopes[i]+str(moleculeStateComposition[i]) for i in range(len(isotopes))]))
        return allStates

    def _createStandardStates(self):

        """ To calculate the standard molecule states based on the states of each moiety in the molecule.

        :return: the standard molecule states.
        """

        # moietyStates : [[[0, 2, 5], [1, 3, 4]] , [[2, 3], [1, 5]]]
        moleculeStates = collections.defaultdict(list)
        isotopes = sorted(self.moieties[0].isotopeStates)
        moietyStates = [[moiety.isotopeStates[isotope] for moiety in self.moieties] for isotope in sorted(self.moieties[0].isotopeStates)]
        for moleculeStateCompositions in itertools.product(*[itertools.product(*i) for i in moietyStates]):
            isotopeNum = [sum(i) for i in moleculeStateCompositions]
            moleculeComposition = [[] for i in range(len(self.moieties))]
            # example of moleculeStateComposition: [[0 (moiety1), 1 (moiety2)] (13C), [2, 1] (15N))
            for i in range(len(moleculeStateCompositions)):
                for j in range(len(moleculeComposition)):
                    moleculeComposition[j].append(isotopes[i]+str(moleculeStateCompositions[i][j]))
            # example of molecule isotopomer: [g[13C0.15N2], u[13C1.15N1]]
            isotopomer = ['{0}[{1}]'.format(self.moieties[i].name, '.'.join(moleculeComposition[i])) for i in range(len(self.moieties))]
            isotopologue = '.'.join(['{0}{1}'.format(isotopes[i], str(isotopeNum[i])) for i in range(len(isotopeNum))])
            moleculeStates[isotopologue].append(isotopomer)
        return moleculeStates

    def __str__(self):

        """Converts the molecule object into string representation.

        :return: The string representation of the molecule.
        """

        string = "Molecule: {0}\t moieties: {1}\n".format(self.name, ','.join([moiety.name for moiety in self.moieties]))
        for isotopologue in self.standardStates:
            string += " calc[{0}] = {1}\n".format(isotopologue, ' + '.join(['.'.join(isotopomer) for isotopomer in self.standardStates[isotopologue]]))
        return string


class Model:

    """
    Model class describes the moiety :class:`~moiety_modeling.model.Model` entity.
    """

    def __init__(self, name, moieties, molecules, relationships=None):
        """Model initializer.

        :param str name: the name of the model.
        :param list moieties: a list of :class:`~moiety_modeling.model.Moiety` instances.
        :param list molecules: a list of :class:`~moiety_modeling.model.Molecule` instances.
        :param list relationships: a list of :class:`~moiety_modeling.model.Relationship` instances.
        """
        self.name = name
        self.molecules = list(molecules)
        self.moieties = list(moieties)
        self.relationships = [] if relationships is None else list(relationships)
        self.orderedMoieties = []
        self.properties = {}
        self.parameterNum = 0
        self._buildModel()

    def _buildModel(self):

        """To build the model properties.

        :return:
        """

        # Check for circular dependencies in relationships
        relationshipDict = {relationship.varName: relationship for relationship in self.relationships}
        for relationship in self.relationships:
            foundVarNames = [relationship.varName]
            testRelationship = relationship
            moietiesVisited = collections.defaultdict(lambda: 0)
            moietiesVisited[relationship.moiety.name] = 1
            while testRelationship and testRelationship.equivalentVarName not in foundVarNames:
                moietiesVisited[testRelationship.equivalentMoiety.name] += 1
                foundVarNames.append(testRelationship.equivalentVarName)
                testRelationship = relationshipDict[testRelationship.equivalentVarName] if testRelationship.equivalentVarName in relationshipDict else None
            if testRelationship:
                # This tests the relationship between the different moieties. There is no circle between moieties. Like g[5] = r[2], r[2] = a[3], a[3] = g[5];
                sys.exit("Circular relationship starting with {0} and ending with {1}".format(relationship.varName, testRelationship.varName))
            if [ value for value in moietiesVisited.values() if value > 2 ]:
                # This test the relationship within the same moiety. Only one relationship between the moiety is allowed. Like g[5] = g[3], g[3] = g[2], g[2] = g[1]; why?
                sys.exit("Relayed Intra moiety relationship starting with {0}".format(relationship.varName))

        # Determine moiety relationships
        # This can cause the problems of ranking, so if there are several relationships between two moieties, we try to put one moiety at one side, another moiety at another side of the equation
        # rather than put them randomly.
        moietyRelationshipDict = {}
        for relationship in self.relationships:
            if relationship.moiety.name != relationship.equivalentMoiety.name:
                if relationship.moiety.name not in moietyRelationshipDict:
                    moietyRelationshipDict[relationship.moiety.name] = {'moiety': relationship.moiety, 'equivalentMoieties': {relationship.equivalentMoiety}}
                else:
                    moietyRelationshipDict[relationship.moiety.name]['equivalentMoieties'].add(relationship.equivalentMoiety)

        for relationship in moietyRelationshipDict.values():
            foundMoieties = {relationship['moiety']}
            testMoieties = relationship['equivalentMoieties']
            while testMoieties and not foundMoieties & testMoieties:
                newTestMoieties = set()
                for moiety in testMoieties:
                    moiety.ranking += 1 # The higher the moiety ranking is, the more likely the moiety is correlated with other moieties.
                    if moiety.name in moietyRelationshipDict:
                        newTestMoieties.update(moietyRelationshipDict[moiety.name]['equivalentMoieties'] - testMoieties)
                foundMoieties.update(testMoieties)
                testMoieties = newTestMoieties
            if testMoieties:
                sys.exit("Circular moiety relationships starting with {0} and ending with {1}".format(relationship.moiety.name, testMoieties[0].name))

        self.orderedMoieties = list(self.moieties)
        self.orderedMoieties.sort(key=lambda moiety: moiety.ranking, reverse=True)

        for moiety in self.orderedMoieties:
            numOfParameters = len(moiety.states) - 1
            preAssignedStates = []
            calculatedStates = []
            postAssignedStates = []
            elements = []
            elementNames = []
            divisors = {state: 1 for state in moiety.states}

            for state in moiety.states:
                varName = '{0}[{1}]'.format(moiety.name, state)
                if varName in relationshipDict and relationshipDict[varName].equivalentMoiety in self.orderedMoieties:
                    numOfParameters -= 1
                    if relationshipDict[varName].moiety.name == relationshipDict[varName].equivalentMoiety.name:
                        # the relationship is appended to the postAssignedStates and preAssignedStates
                        postAssignedStates.append(relationshipDict[varName])
                        divisors[relationshipDict[varName].equivalentMoietyState] += relationshipDict[varName].multiplier
                    else:
                        preAssignedStates.append(relationshipDict[varName])
            for state in moiety.states:
                varName = '{0}[{1}]'.format(moiety.name, state)
                if varName not in relationshipDict or relationshipDict[varName].equivalentMoiety not in self.orderedMoieties:
                    # the states of moiety and its divisor are attached to the calculatedStates.
                    calculatedStates.append([varName, divisors[state]])
            for x in range(numOfParameters):
                self.parameterNum += 1
                elementNames.append('{0}.p{1}'.format(moiety.name, x))
                elements.append(self.parameterNum-1)
            self.properties[moiety.name] = {'preAssignedStates': preAssignedStates, 'postAssignedStates': postAssignedStates, 'calculatedStates': calculatedStates, 'elements': elements, 'elementNames' : elementNames}

    def calculateMoietyState(self, vector):

        """To calculate the value of the all moietyStates.

        :param vector: the list of parameters of the model.
        :param dataset: dataset object.
        :return: the dictionary containing the value of the moietyStates.
        """

        conversionDict = {}
        moietyStates = {}
        for moiety in self.orderedMoieties:
            properties = self.properties[moiety.name]
            if properties['preAssignedStates']:
                for relationship in properties['preAssignedStates']:
                    conversionDict[relationship.varName] = conversionDict[relationship.equivalentVarName] * relationship.multiplier
                conversionDict[moiety.name + 'PreAssignedTotal'] = sum([conversionDict[relationship.varName] for relationship in properties['preAssignedStates']])
                if conversionDict[moiety.name + 'PreAssignedTotal'] > 1:
                    for relationship in properties['preAssignedStates']:
                        conversionDict[relationship.varName] /= conversionDict[moiety.name + 'PreAssignedTotal']
                        conversionDict[moiety.name + 'PreAssignedTotal'] = 1
            else:
                conversionDict[moiety.name + 'PreAssignedTotal'] = 0
            calculatedStates = properties['calculatedStates']
            if properties['elements']:
                conversionDict[moiety.name + 'Parameters'] = [max(0, vector[i]) if vector[i] < 1 else 1 for i in properties['elements'] ]
                conversionDict[moiety.name + 'ParameterMax'] = max(conversionDict[moiety.name + 'Parameters'])
                conversionDict[moiety.name + 'ParametersSum'] = sum(conversionDict[moiety.name + 'Parameters'])
                conversionDict[calculatedStates[0][0]] = (1 - conversionDict[moiety.name + 'ParameterMax']) * (1 - conversionDict[moiety.name + 'PreAssignedTotal']) / calculatedStates[0][1]
                if conversionDict[moiety.name + 'ParametersSum'] == 0:
                    conversionDict[moiety.name + 'ParametersSum'] = 1
                for y in range(len(properties['elements'])):
                    conversionDict[calculatedStates[y + 1][0]] = conversionDict[moiety.name + 'Parameters'][y] / conversionDict[moiety.name + 'ParametersSum'] * conversionDict[moiety.name + 'ParameterMax'] * (1 - conversionDict[moiety.name + 'PreAssignedTotal']) / calculatedStates[y + 1][1]
            elif calculatedStates:
                conversionDict[calculatedStates[0][0]] = (1 - conversionDict[moiety.name + 'PreAssignedTotal']) / calculatedStates[0][1]
            for relationship in properties['postAssignedStates']:
                conversionDict[relationship.varName] = conversionDict[relationship.equivalentVarName] * relationship.multiplier
            for state in moiety.states:
                moietyState = '{0}[{1}]'.format(moiety.name, state)
                moietyStates[moietyState] = conversionDict[moietyState]
        return moietyStates

    def __str__(self):

        """
        String representation of the model.
        :return: string.
        """

        string = "\n#####Conversion and calculation script for model {0}.\n".format(self.name)
        for moiety in self.orderedMoieties:
            properties = self.properties[moiety.name]
            string += "# {0} conversion\n".format(moiety.name)
            if properties['preAssignedStates']:
                for relationship in properties['preAssignedStates']:
                    string += " {0}[{1}] = {2}[{3}]".format(moiety.name, relationship.moietyState, relationship.equivalentMoiety.name, relationship.equivalentMoietyState)
                    string += "" if relationship.multiplier == 1 else " * {0}".format(relationship.multiplier)
                    string += "\n"
                string += " {0}PreAssignedTotal = {1}\n\n".format(moiety.name, " + ".join(["{0}[{1}]".format(moiety.name, relationship.moietyState) for relationship in properties['preAssignedStates']]))
                string += " if {0}PreAssignedTotal > 1:\n".format(moiety.name)
                for relationship in properties['preAssignedStates']:
                    string += "     {0}[{1}] /= {2}PreAssignedTotal\n".format(moiety.name, relationship.moietyState, moiety.name)
                string += "     {0}PreAssignedTotal = 1\n".format(moiety.name)
            else:
                string += " {0}PreAssignedTotal = 0\n".format(moiety.name)
            calculatedStates = properties['calculatedStates']
            if properties['elements']:
                string += " {0}Parameters = [vector[i] for i in {1}]\n".format(moiety.name, properties['elements'])
                string += " {0}ParameterMax = max({1}Parameters)\n".format(moiety.name, moiety.name)
                string += " {0}ParametersSum = 0\n".format(moiety.name)
                string += " for parameter in {0}Parameters:\n".format(moiety.name)
                string += "     {0}ParametersSum += parameter\n".format(moiety.name)
                string += " {0}[{1}] = (1 - {2}ParameterMax) * (1 - {3}PreAssignedTotal)".format(moiety.name, calculatedStates[0][0], moiety.name, moiety.name)
                string += "" if calculatedStates[0][1] == 1 else " / {0}".format(calculatedStates[0][1])
                string += "\n"
                for y in range(len(properties['elements'])):
                    string += " {0}[{1}] = {2}Parameters[{3}] / {4}ParametersSum * {5}ParameterMax * (1 - {6}PreAssignedTotal)".format(moiety.name, calculatedStates[y+1][0], moiety.name, y, moiety.name, moiety.name, moiety.name)
                    string += "" if calculatedStates[y+1][1] == 1 else " / {0}".format(calculatedStates[y+1][1])
                    string += "\n"
            elif calculatedStates:
                string += " {0}[{1}] = (1 - {2}PreAssignedTotal)".format(moiety.name, calculatedStates[0][0], moiety.name)
                string += "" if calculatedStates[0][1] == 1 else " / {0}".format(calculatedStates[0][1])
                string += "\n"
            for relationship in properties['postAssignedStates']:
                string += " {0}[{1}] = {2}[{3}]".format(moiety.name, relationship.moietyState, moiety.name, relationship.equivalentMoietyState)
                string += "" if relationship.multiplier == 1 else " * {0}".format(relationship.multiplier)
                string += "\n"
            string += "\n"
        string += " conversion = {}\n"
        for moiety in self.orderedMoieties:
            string += " conversion['{0}'] = [{1}]\n".format(moiety.name, ','.join(["{0}[{1}]".format(moiety.name, state) for state in moiety.states]))
        return string



