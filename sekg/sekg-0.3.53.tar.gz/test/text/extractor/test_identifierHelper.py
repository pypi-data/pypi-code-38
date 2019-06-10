from unittest import TestCase

from sekg.text.extractor.domain_entity.identifier_util import IdentifierInfoExtractor


class TestIdentifierHelper(TestCase):
    def test_extract_from_variable(self):
        extractor = IdentifierInfoExtractor()

        test_cases = [
            ("String filePath", {"file", "path"}),
            ("String srcFile", {"src File"}),
            ("String srcFile1", {"src File"}),
        ]
        for name, answer in test_cases:
            print("extract for method name", name)
            print(extractor.extract_from_variable(name))
            # self.assertEqual(answer, extractor.extract_from_variable(name))

    def test_extract_from_class_name(self):
        extractor = IdentifierInfoExtractor()
        # todo: fix the case problem
        test_cases = [
            ("String", {"string"}),
            ("StringSrcFile", {"string Src File"}),
            ("String3D", {"string 3d"}),
            ("UserID", {"user ID"}),
        ]
        for name, answer in test_cases:
            print("extract for method name", name)
            print(extractor.extract_from_class_name(name))
            # self.assertEqual(answer, extractor.extract_from_class_name(name))

    def test_extract_from_method_for_operate_relation(self):
        self.fail()

    def test_pos_tag_for_method(self):
        extractor = IdentifierInfoExtractor()
        # todo: fix the case problem
        test_cases = [
            ("StringBuilder.build(int)", [('build', 'VERB')]),
            ("StringBuilder.toString()", [('to', 'PART'), ('string', 'VERB')]),
            ("StringBuilder.getConn()", [('to', 'PART'), ('string', 'VERB')]),
            ("List.getUserId", ({"Container"}, set(["delete"]))),
            ("List.id", ({"Container"}, set(["delete"]))),

            ("List.findOrCreateCon", ({"Container"}, set(["delete"]))),
            ("List.buttonContainer", ({"Container"}, set(["delete"]))),

            ("List.deleteFromContainer", ({"Container"}, set(["delete"]))),
            ("List.deleteAndRemoveFromContainer", ({"Container"}, set(["delete"]))),

            ("String3D.convertStrToInt(sting,int)", ({"string"}, set())),
            ("String3D.convertStrToLargeImg(sting,int)", ({"string"}, set())),

            ("Integer.parseToInt", ({"int"}, set(["parse"]))),
            ("Integer.parseToLongInt", ({"int"}, set(["parse"]))),
            ("Integer.parseToLong", ({"int"}, set(["parse"]))),
            ("Integer.parseLong", ({"int"}, set(["parse"]))),
            ("Integer.parseInt", ({"int"}, set(["parse"]))),
            ("Integer.parseInteger", ({"int"}, set(["parse"]))),

            ("StringBuilder.id2score()", [('to', 'PART'), ('string', 'VERB')]),
            ("StringBuilder.name2score()", [('to', 'PART'), ('string', 'VERB')]),
            ("List.deleteIntFromContainer", ({"Container"}, set(["delete"]))),
            ("List.deleteIntFromContainerByID", ({"Container"}, set(["delete"]))),
            ("List.isExist", ({"Container"}, set(["delete"]))),
            ("List.isRed", ({"Container"}, set(["delete"]))),

            ("List.html", ({"Container"}, set(["delete"]))),
            ("List.list", ({"Container"}, set(["delete"]))),
            ("List.listName", ({"Container"}, set(["delete"]))),
            ("List.setButtonEnable", ({"Container"}, set(["delete"]))),
            ("List.setButtonEnabled", ({"Container"}, set(["delete"]))),
            ("List.makeButtonEnabled", ({"Container"}, set(["delete"]))),
            ("List.makeButtonEnable", ({"Container"}, set(["delete"]))),

            ("List.makeButtonUnclickable", ({"Container"}, set(["delete"]))),
            ("List.quickSort", ({"Container"}, set(["delete"]))),
            ("List.quicksort", ({"Container"}, set(["delete"]))),
            ("List.mergeSort", ({"Container"}, set(["delete"]))),
            ("List.mergesort", ({"Container"}, set(["delete"]))),
            ("List.BM25", ({"Container"}, set(["delete"]))),
            ("List.createContainer", ({"Container"}, set(["delete"]))),
            ("List.len", ({"Container"}, set(["delete"]))),
            ("List.size", ({"Container"}, set(["delete"]))),

            ("List.invokeOtherMethods", ({"Container"}, set(["delete"]))),

        ]
        for name, answer in test_cases:
            print("extract for method name", name)
            extractor.pos_tag_for_method_name(name)

            # self.assertEqual(answer, extractor.pos_tag_for_method_name(name))

    def test_extract_for_method(self):
        extractor = IdentifierInfoExtractor()
        # todo: fix the case problem
        test_cases = [
            ("StringBuilder.build(int)", [('build', 'VERB')]),
            ("StringBuilder.toString()", [('to', 'PART'), ('string', 'VERB')]),
            ("StringBuilder.getConn()", [('to', 'PART'), ('string', 'VERB')]),
            ("List.getUserId", ({"Container"}, set(["delete"]))),
            ("List.id", ({"Container"}, set(["delete"]))),

            ("List.findOrCreateCon", ({"Container"}, set(["delete"]))),
            ("List.buttonContainer", ({"Container"}, set(["delete"]))),

            ("List.deleteFromContainer", ({"Container"}, set(["delete"]))),
            ("List.deleteAndRemoveFromContainer", ({"Container"}, set(["delete"]))),

            ("String3D.convertStrToInt(sting,int)", ({"string"}, set())),
            ("String3D.convertStrToLargeImg(sting,int)", ({"string"}, set())),

            ("Integer.parseToInt", ({"int"}, set(["parse"]))),
            ("Integer.parseToLongInt", ({"int"}, set(["parse"]))),
            ("Integer.parseToLong", ({"int"}, set(["parse"]))),
            ("Integer.parseLong", ({"int"}, set(["parse"]))),
            ("Integer.parseInt", ({"int"}, set(["parse"]))),
            ("Integer.parseInteger", ({"int"}, set(["parse"]))),

            ("StringBuilder.id2score()", [('to', 'PART'), ('string', 'VERB')]),
            ("StringBuilder.name2score()", [('to', 'PART'), ('string', 'VERB')]),
            ("List.deleteIntFromContainer", ({"Container"}, set(["delete"]))),
            ("List.deleteIntFromContainerByID", ({"Container"}, set(["delete"]))),
            ("List.isExist", ({"Container"}, set(["delete"]))),
            ("List.isRed", ({"Container"}, set(["delete"]))),

            ("List.html", ({"Container"}, set(["delete"]))),
            ("List.list", ({"Container"}, set(["delete"]))),
            ("List.listName", ({"Container"}, set(["delete"]))),
            ("List.setButtonEnable", ({"Container"}, set(["delete"]))),
            ("List.setButtonEnabled", ({"Container"}, set(["delete"]))),
            ("List.makeButtonEnabled", ({"Container"}, set(["delete"]))),
            ("List.makeButtonEnable", ({"Container"}, set(["delete"]))),

            ("List.makeButtonUnclickable", ({"Container"}, set(["delete"]))),
            ("List.quickSort", ({"Container"}, set(["delete"]))),
            ("List.quicksort", ({"Container"}, set(["delete"]))),
            ("List.mergeSort", ({"Container"}, set(["delete"]))),
            ("List.mergesort", ({"Container"}, set(["delete"]))),
            ("List.BM25", ({"Container"}, set(["delete"]))),
            ("List.createContainer", ({"Container"}, set(["delete"]))),
            ("List.len", ({"Container"}, set(["delete"]))),
            ("List.size", ({"Container"}, set(["delete"]))),

            ("List.invokeOtherMethods", ({"Container"}, set(["delete"]))),

        ]
        for name, answer in test_cases:
            print("extract for method name", name)
            print(extractor.extract_from_method_name(name))

            # self.assertEqual(answer, extractor.pos_tag_for_method_name(name))
