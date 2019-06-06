import re


class CodeElementNameUtil:
    PATTERN_2_4 = re.compile(r'([A-Za-z])([24])([A-CE-Za-ce-z])')
    PATTERN_split = re.compile(r'([A-Z]+)([A-Z][a-z0-9]+)')
    PATTERN_split_num = re.compile(r'([0-9]?[A-Z]+)')

    def get_simple_name_with_parent(self, name):
        if not name:
            return None
        team_name = name.split("(")[0]
        split_names = team_name.split(".")
        if len(split_names) <= 1:
            return split_names[-1]

        child = split_names[-1].strip()
        parent = split_names[-2].strip()

        return parent + "." + child

    def simplify(self, name):
        """
        get the simple name for class, method, field, eg. java.util.ArrayList->ArrayList
        :param name:
        :return:
        """
        if not name:
            return None
        team_name = name.split("(")[0]
        simple_name = team_name.split(".")[-1].strip()

        return simple_name

    def uncamelize_from_simple_name(self, name):
        """
        uncamel from simple name of one name, rg. java.util.ArrayList->Array List
        :param name:
        :return:
        """
        if not name:
            return None
        simple_name = self.simplify(name)

        return self.uncamelize(simple_name)

    def uncamelize(self, name):
        """
        uncamel one name
        :param name: the camel styple name(include underline)
        :return:
        """
        if not name:
            return None
        # sub = re.sub(r'([A-Za-z])([24])([A-CE-Za-ce-z])', r'\1 \2 \3', name).strip()
        sub = re.sub(self.PATTERN_2_4, r'\1 \2 \3', name).strip()
        sub = re.sub(r'_', " ", sub)
        # sub = re.sub(r'([A-Z]+)([A-Z][a-z0-9]+)', r'\1 \2', sub)
        sub = re.sub(self.PATTERN_split, r'\1 \2', sub)
        # sub = re.sub(r'([0-9]?[A-Z]+)', r' \1', sub)
        sub = re.sub(self.PATTERN_split_num, r' \1', sub)
        sub = re.sub(r'\s+', " ", sub).strip()
        return sub

    def uncamelize_by_stemming(self, name):
        """
        uncamelzie the name and remove last num, eg. Student1->Student, JavaParser3->Java Parser
        :param name:
        :return:
        """
        # todo: improve this method to fix more situation, has some error for Path1->Path
        name = self.uncamelize(name)
        if not name:
            return None
        sub = re.sub(r'([0-9]+)$', '', name)
        return sub

    def generate_aliases(self, qualified_name, include_simple_parent_name=False):
        if not qualified_name:
            return []

        simple_name = self.simplify(qualified_name)
        separate_name = self.uncamelize_from_simple_name(simple_name)

        name_list = [qualified_name, simple_name, separate_name, ]

        if include_simple_parent_name:
            name_list.append(self.get_simple_name_with_parent(qualified_name))

        name_list = [name for name in name_list if name]

        return list(set(name_list))
