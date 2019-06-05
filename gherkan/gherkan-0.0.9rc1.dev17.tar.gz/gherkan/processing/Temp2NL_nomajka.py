# coding: utf-8

import yaml
import re
from pattern.en import conjugate
import imp
import os

CZ_PROGRAM_YAML_DIR = os.path.join(imp.find_module("gherkan")[1], "utils", "ProgramMeanings_cz.yaml")
EN_PROGRAM_YAML_DIR = os.path.join(imp.find_module("gherkan")[1], "utils", "ProgramMeanings_en.yaml")
GENERAL_YAML_DIR = os.path.join(imp.find_module("gherkan")[1], "utils", "General_phrases.yaml")
SCENARIO = "ProgramNumbers_Scene_2"


class FinetuneLang:

    def conjugate_en(self, word, person, number="singular"):
        if number == "singular":
            self.tag = str(person) + "sg"
            self.declenation = conjugate(word, self.tag)

        elif number == "plural":
            self.tag = str(person) + "pl"
            self.declenation = conjugate(word, self.tag)

        return self.declenation


class FillActions:
    def __init__(self):
        self.finetune = FinetuneLang()

    def ParseMainAction(self, data):
        self.data = data
        if "robot" in self.data[0][0] and "Program" in self.data[3]:
            self.rob_name = "Robot " + self.data[0][0].split('robot')[1]
            if len(self.data[0]) == 2:
                self.rob = self.data[0][0]
                self.prog = self.data[0][1]
                self.action_en = self.MatchActionEN(self.rob, self.prog)
                self.action_cz = self.MatchActionCZ(self.rob, self.prog)
                if "equality" in self.data[1]:
                    self.action_cz = self.rob_name + " " + self.action_cz
                    self.declen_en = self.finetune.conjugate_en(self.action_en.split()[0], 3)
                    self.action_en = self.rob_name + " " + self.action_en.replace(self.action_en.split()[0], self.declen_en)
                elif "equality" not in self.data[1]:
                    self.action_en, self.action_cz = self.ParseBool_Robot(self.data, [self.action_en, self.action_cz])
                    self.action_cz = self.rob_name + " " + self.action_cz
                    self.action_en = self.rob_name + " " + self.action_en
            elif len(self.data[0]) == 1:
                self.action_en, self.action_cz = self.ParseBool_Robot(self.data)
                self.action_cz = self.rob_name + " " + self.action_cz[:-1]
                self.action_en = self.rob_name + " " + self.action_en[:-1]

        elif "AtStation" in self.data[3] or "Destination" in self.data[3]:
            self.actor = re.findall('[a-zA-Z][^A-Z]*', self.data[0][0])
            self.actor_name = self.actor[0] + " " + ''.join(self.actor[1:])
            if "AtStation" in self.data[3]:
                self.matched_en = self.MatchGeneral("AtStation", lang="Phrases_En", key=int(self.data[2]))
                self.matched_cz = self.MatchGeneral("AtStation", lang="Phrases_Cz", key=int(self.data[2]))
            else:
                self.matched_en = self.MatchGeneral("Destination", lang="Phrases_En", key=int(self.data[2]))
                self.matched_cz = self.MatchGeneral("Destination", lang="Phrases_Cz", key=int(self.data[2]))
            self.declen_en = self.finetune.conjugate_en(self.matched_en.split()[0], 3)
            self.action_en = self.actor_name + " " + self.matched_en.replace(self.matched_en.split()[0], self.declen_en) + " " + self.data[0][1]
            self.action_cz = self.MatchGeneral(self.actor[0], lang="Phrases_Cz") + " " + ''.join(self.actor[1:]) + " " + self.matched_cz + " " + self.data[0][1]

        elif "Free" in self.data[3]:
            self.actor = re.findall('[a-zA-Z][^A-Z]*', self.data[0][0])
            self.actor_name = self.actor[0] + " " + ''.join(self.actor[1:])
            self.matched_en = self.MatchGeneral("Free", lang="Phrases_En", key=int(self.data[2]))
            self.matched_cz = self.MatchGeneral("Free", lang="Phrases_Cz", key=int(self.data[2]))
            self.declen_en = self.finetune.conjugate_en(self.matched_en.split()[0], 3)
            self.action_en = self.actor_name + " " + self.matched_en.replace(self.matched_en.split()[0], self.declen_en)
            self.action_cz = self.MatchGeneral(self.actor[0], lang="Phrases_Cz") + " " + ''.join(self.actor[1:]) + " " + self.matched_cz

        elif "Move" in self.data[3]:
            self.actor = re.findall('[a-zA-Z][^A-Z]*', self.data[0][0])
            self.actor_name = self.actor[0] + " " + ''.join(self.actor[1:])
            self.matched_en = self.MatchGeneral("Move", lang="Phrases_En", key=int(self.data[2]))
            self.matched_cz = self.MatchGeneral("Move", lang="Phrases_Cz", key=int(self.data[2]))
            self.declen_en = self.finetune.conjugate_en(self.matched_en.split()[0], 3)
            self.action_en = self.actor_name + " " + self.matched_en.replace(self.matched_en.split()[0], self.declen_en)
            self.action_cz = self.MatchGeneral(self.actor[0], lang="Phrases_Cz") + " " + ''.join(self.actor[1:]) + " " + self.matched_cz

        elif "Full" in self.data[3]:
            self.actor = re.findall('[a-zA-Z][^A-Z]*', self.data[0][0])
            self.actor_name = self.actor[0] + " " + ''.join(self.actor[1:])
            self.matched_en = self.MatchGeneral("Full", lang="Phrases_En", key=int(self.data[2]))
            self.matched_cz = self.MatchGeneral("Full", lang="Phrases_Cz", key=int(self.data[2]))
            self.declen_en = self.finetune.conjugate_en(self.matched_en.split()[0], 3)
            self.action_en = self.actor_name + " " + self.matched_en.replace(self.matched_en.split()[0], self.declen_en)
            self.action_cz = self.MatchGeneral(self.actor[0], lang="Phrases_Cz") + " " + ''.join(self.actor[1:]) + " " + self.matched_cz

        elif "Count" in self.data[3]:
            self.actor = re.findall('[a-zA-Z][^A-Z]*', self.data[0][0])
            self.actor_name = self.actor[0] + " " + ''.join(self.actor[1:])
            if self.data[2] == "0":
                self.action_en = self.actor_name + " is empty"
                self.action_cz = self.MatchGeneral(self.actor[0], lang="Phrases_Cz") + " je prázdný"
            else:
                self.action_en = "Number of objects in " + self.actor_name + " is " + str(self.data[2])
                self.action_cz = "Počet objektů ve " + self.MatchGeneral(self.actor[0], lang="Phrases_Cz", key=2) + " " + ''.join(self.actor[1:]) + " " + " je " + str(self.data[2])

        elif "Locked" in self.data[3]:
            self.actor = re.findall('[a-zA-Z][^A-Z]*', self.data[0][0])
            self.actor_name = self.actor[0] + " " + ''.join(self.actor[1:])
            self.matched_en = self.MatchGeneral("Locked", lang="Phrases_En", key=int(self.data[2]))
            self.matched_cz = self.MatchGeneral("Locked", lang="Phrases_Cz", key=int(self.data[2]))
            self.declen_en = self.finetune.conjugate_en(self.matched_en.split()[0], 3)
            self.action_en = self.actor_name + " " + self.matched_en.replace(self.matched_en.split()[0]+" ", self.declen_en + " ")
            self.action_cz = self.MatchGeneral(self.actor[0], lang="Phrases_Cz") + " " + ''.join(self.actor[1:]) + " " + self.matched_cz

        elif "Replenish" in self.data[3]:
            self.actor = re.findall('[a-zA-Z][^A-Z]*', self.data[0][0])
            self.actor_name = self.actor[0] + " " + ''.join(self.actor[1:])
            self.matched_en = self.MatchGeneral("Replenish", lang="Phrases_En", key=int(self.data[2]))
            self.matched_cz = self.MatchGeneral("Replenish", lang="Phrases_Cz", key=int(self.data[2]))
            self.declen_en = self.finetune.conjugate_en(self.matched_en.split()[0], 3)
            self.action_en = self.actor_name + " " + self.matched_en.replace(self.matched_en.split()[0], self.declen_en)
            self.action_cz = self.MatchGeneral(self.actor[0], lang="Phrases_Cz") + " " + ''.join(self.actor[1:]) + " " + self.matched_cz

        elif "to" in self.data[3]:
            # TODO: Raise a warning?
            pass

        return [self.action_en, self.action_cz]

    def ParseBool_Robot(self, data, phrases=None):
        if phrases:
            self.eng_phrase = phrases[0]
            self.czech_phrase = phrases[1]
            self.data = data
        else:
            self.eng_phrase = ""
            self.czech_phrase = ""
            self.data = data

        if "Started" in self.data[3]:
            if self.data[2] == "1":
                self.czech_phrase_spec = ' '.join(["začne program", self.czech_phrase])
                self.eng_phrase_spec = ' '.join(["starts the program", self.eng_phrase])
            elif self.data[2] == "0":
                self.czech_phrase_spec = ' '.join(["nezačne program", self.czech_phrase])
                self.eng_phrase_spec = ' '.join(["does not start the program", self.eng_phrase])

        elif "Ended" in self.data[3]:
            if self.data[2] == "1":
                self.czech_phrase_spec = ' '.join(["skončí program", self.czech_phrase])
                self.eng_phrase_spec = ' '.join(["finishes program", self.eng_phrase])
            elif self.data[2] == "0":
                self.czech_phrase_spec = ' '.join(["neskončí program", self.czech_phrase])
                self.eng_phrase_spec = ' '.join(["does not finish the program", self.eng_phrase])

        return self.eng_phrase_spec, self.czech_phrase_spec

    def ParseNegative(self, phrase):
        self.eng_phrase = phrase[0]
        self.czech_phrase = phrase[1]

        self.czech_phrase.replace("skončí", "neskončí")
        self.czech_phrase.replace("začne", "nezačne")
        self.eng_phrase.replace("finishes", "does not finish")
        self.eng_phrase.replace("starts", "does not start")

        return self.eng_phrase, self. czech_phrase

    def MatchActionEN(self, actor, prog):
        with open(EN_PROGRAM_YAML_DIR, 'r', encoding="utf-8") as stream:
            self.action_list = yaml.load(stream)
            self.action_en = self.action_list[SCENARIO][actor][int(prog)]

        return self.action_en

    def MatchActionCZ(self, actor, prog):
        with open(CZ_PROGRAM_YAML_DIR, 'r', encoding="utf-8") as stream:
            self.action_list = yaml.load(stream)
            self.action_cz = self.action_list[SCENARIO][actor][int(prog)]

        return self.action_cz

    def MatchGeneral(self, data, lang, key=1):
        with open(GENERAL_YAML_DIR, 'r', encoding="utf-8") as stream:
            self.phrase_list = yaml.load(stream)
            self.phrase = self.phrase_list[lang][data][key]

        return self.phrase


if __name__ == "__main__":
    fill_action = FillActions()
    VarsVals = ['robotR1', '4']
    Type = "equality"
    Values = "4"
    PhraseStr = "ProgramNumber"
    TempData = [VarsVals, Type, Values, PhraseStr]
    print(TempData)
    sentence_core_part = fill_action.ParseMainAction(TempData)
    # sentence_core_spec = fill_action.ParseBool(sentence_core_part, SourcePhrase["TypeArr"][0])
    print(sentence_core_part)