# Generate mondrian schema from python objects
# using elementtree

# Don't forget: attribute and property should be in base class. (traits).

import xml.etree.ElementTree as ET
from xml.dom import minidom

# Base class


class MondrianElement(object):

    def __init__(self):
        self.annotations = []
        self.properties = []

    def add_annotation(self, annotation):
        self.annotations.append(annotation)

    def add_property(self, property):
        self.properties.append(property)

    def build_xml(self, parent):
        if len(self.annotations) > 0:
            annotations_xml = ET.SubElement(parent, "Annotations")
            for annotation in self.annotations:
                annotation.build_xml(annotations_xml)

        for property in self.properties:
            property.build_xml(parent)


class Annotation(object):

    def __init__(self, name, text):
        self.name = name
        self.text = text

    def build_xml(self, parent):
        annotation = ET.SubElement(parent, "Annotation")
        annotation.attrib = {
            "name": self.name,
        }
        annotation.text = self.text


class Property(object):

    def __init__(self, name, column):
        self.name = name
        self.column = column

    def build_xml(self, parent):
        property = ET.SubElement(parent, "Property")
        property.attrib = {
            "name": self.name,
            "column": self.column,
        }


# Main data classes

class Schema(MondrianElement):

    def __init__(self, name):
        self.name = name
        self.cubes = []
        self.dimensions = []
        super(Schema, self).__init__()

    def add_cube(self, cube):
        self.cubes.append(cube)

    def add_dimension(self, dimension):
        self.dimensions.append(dimension)

    def xml_render(self, pretty_print=False):
        schema = ET.Element("Schema")
        schema.attrib = {"name": self.name}

        super(Schema, self).build_xml(schema)

        for dimension in self.dimensions:
            dimension.build_xml(schema)

        for cube in self.cubes:
            cube.build_xml(schema)


        res = ET.tostring(schema, encoding='unicode', method='xml')
        if pretty_print:
            return minidom.parseString(res).toprettyxml(indent="  ")
        return res


class Cube(MondrianElement):

    def __init__(self, name, table, schema):
        self.name = name
        self.table = table
        self.schema = schema
        self.dimensions = []
        self.dimension_usages = []
        self.measures = []
        self.calculated_members = []
        self.named_sets = []
        super(Cube, self).__init__()

    # TODO change api to only use add_element?
    # Deprecate other add_<x> methods, use them
    # to just call add_element
    def add_dimension(self, dimension):
        self.dimensions.append(dimension)

    def add_dimension_usage(self, dimension_usage):
        self.dimension_usages.append(dimension_usage)

    def add_measure(self, measure):
        self.measures.append(measure)

    def add_calculated_member(self, calculated_member):
        self.calculated_members.append(calculated_member)

    def add_named_set(self, named_set):
        self.named_sets.append(named_set)

    def build_xml(self, parent):
        cube = ET.SubElement(parent, "Cube")

        cube.attrib = {
            "name": self.name,
        }

        table = ET.Element("Table")
        table.attrib = {
            "name": self.table,
            "schema": self.schema,
        }

        super(Cube, self).build_xml(cube)
        # -- Ensure table element is added after annotations
        cube.append(table)

        for dimension in self.dimensions:
            dimension.build_xml(cube)

        for dimension_usage in self.dimension_usages:
            dimension_usage.build_xml(cube)

        for measure in self.measures:
            measure.build_xml(cube)

        for calculated_member in self.calculated_members:
            calculated_member.build_xml(cube)

        for named_set in self.named_sets:
            named_set.build_xml(cube)


class View(MondrianElement):
    def __init__(self, alias=None, formula=None):
        self.alias = alias
        self.formula = formula
        super(View, self).__init__()

    def build_xml(self, parent):
        view = ET.SubElement(parent, "View")

        view.attrib = {
            "alias": self.alias,
        }

        sql = ET.SubElement(view, "SQL")
        sql.text = self.formula

        super(View, self).build_xml(view)


class Dimension(MondrianElement):

    def __init__(self, name, table=None, schema=None, hierarchy_has_all=True, foreign_key=None):
        self.name = name

        self.default_hierarchy = Hierarchy(
            table=table,
            schema=schema,
            has_all=True,
        )

        self.foreign_key = foreign_key
        self.hierarchies = []
        super(Dimension, self).__init__()

    # add level directly to default hierarhcy
    def add_level(self, level):
        self.default_hierarchy.add_level(level)

    def add_hierarchy(self, hierarchy):
        self.hierarchies.append(hierarchy)

    def add_view(self, view):
        self.view = view

    def add_inline_table(self, alias=None, levels=None, inline_table_dict=None, dim_encodings=None):
        """
        levels is a list of level names
        inline_table_dict is a dict where keys are level name and value is list of values
        dim_encodings is the map of values to a number
        """
        self.default_hierarchy.add_inline_table(
            alias=alias,
            levels=levels,
            inline_table_dict=inline_table_dict,
            dim_encodings=dim_encodings
        )

    def build_xml(self, parent):
        dimension = ET.SubElement(parent, "Dimension")
        dimension.attrib = {
            "name": self.name,
        }

        if self.foreign_key:
            dimension.attrib["foreignKey"] = self.foreign_key

        super(Dimension, self).build_xml(dimension)

        if len(self.default_hierarchy.levels) > 0:
            self.default_hierarchy.build_xml(dimension)

        for hierarchy in self.hierarchies:
            hierarchy.build_xml(dimension)


class Hierarchy(MondrianElement):

    def __init__(self, name=None, table=None, schema=None, levels=None, view=None, has_all=True, primary_key=None):
        self.name = name
        self.levels = levels if levels else []
        self.table = table
        self.schema = schema
        self.view = view
        self.has_all = has_all
        self.inline_table = None
        self.primary_key = primary_key
        super(Hierarchy, self).__init__()

    def add_inline_table(self, alias=None, levels=None, inline_table_dict=None, dim_encodings=None):
        """
        levels is a list of level names
        inline_table_dict is a dict where keys are level name and value is list of values
        dim_encodings is the map of values to a number

        It's rendered in build_xml
        """
        self.inline_table = InlineTable(
            alias=alias,
            levels=levels,
            inline_table_dict=inline_table_dict,
            dim_encodings=dim_encodings
        )

    # add level directly to default hierarhcy
    def add_level(self, level):
        self.levels.append(level)

    def build_xml(self, parent):
        hierarchy = ET.SubElement(parent, "Hierarchy")

        if self.name:
            hierarchy.attrib["name"] = self.name

        if self.primary_key:
            hierarchy.attrib["primaryKey"] = self.primary_key

        if self.table and self.schema:
            table_el = ET.SubElement(hierarchy, "Table")
            table_el.attrib = {
                "name": self.table,
                "schema": self.schema,
            }

        super(Hierarchy, self).build_xml(hierarchy)

        hierarchy.attrib["hasAll"] = str(self.has_all).lower()

        if self.view:
            self.view.build_xml(hierarchy)

        if self.inline_table:
            self.inline_table.build_xml(hierarchy)

        for level in self.levels:
            level.build_xml(hierarchy)


class InlineTable(MondrianElement):

    def __init__(self, alias=None, levels=None, inline_table_dict=None, dim_encodings=None):
        self.alias = alias
        self.levels = levels
        self.inline_table_dict = inline_table_dict
        self.dim_encodings = dim_encodings
        super(InlineTable, self).__init__()

    def build_xml(self, parent):
        inline_table = ET.SubElement(parent, "InlineTable")
        inline_table.attrib["alias"] = self.alias

        super(InlineTable, self).build_xml(inline_table)

        # Coldefs (headers and metadata)
        column_defs = ET.SubElement(inline_table, "ColumnDefs")
        for level in self.levels:
            # label
            column_def_label = ET.SubElement(column_defs, "ColumnDef")
            column_def_label.attrib["name"] = level
            column_def_label.attrib["type"] = "String"

            # code
            column_def_code = ET.SubElement(column_defs, "ColumnDef")
            column_def_code.attrib["name"] = level + "_code"
            column_def_code.attrib["type"] = "Numeric"

        # Now rows
        # This assumes that the selected columns have the same length
        rows = ET.SubElement(inline_table, "Rows")
        col_len = len(self.inline_table_dict[self.levels[0]])
        for i in range(0, col_len):
            row = ET.SubElement(rows, "Row")
            for level in self.levels:
                # label
                value_label = ET.SubElement(row, "Value")
                value_label.attrib["column"] = level
                text = self.inline_table_dict[level][i]
                value_label.text = text

                # label
                value_code = ET.SubElement(row, "Value")
                value_code.attrib["column"] = level + "_code"

                value_code.text = str(self.dim_encodings[level][text])


class Level(MondrianElement):

    def __init__(
        self,
        name,
        column,
        name_column=None,
        level_type=None,
        type=None,
        unique_members=None,
        hierarchy="default",
        table=None,
        schema=None,
        hide_member_if=None
    ):
        self.name = name
        self.column = column
        self.name_column = name_column
        self.level_type = level_type
        self.type = type
        self.unique_members = unique_members
        self.hierarchy = hierarchy
        self.table = table
        self.hide_member_if = hide_member_if
        super(Level, self).__init__()

    def build_xml(self, parent):
        level = ET.SubElement(parent, "Level")
        level.attrib = {
            "name": self.name,
            "column": self.column,
        }

        if self.name_column:
            level.attrib["nameColumn"] = self.name_column

        if self.level_type:
            level.attrib["levelType"] = self.level_type

        if self.type:
            level.attrib["type"] = self.type

        if self.unique_members:
            level.attrib["uniqueMembers"] = str(self.unique_members).lower()

        if self.table:
            level.attrib['table'] = self.table

        if self.hide_member_if:
            level.attrib["hideMemberIf"] = self.hide_member_if

        super(Level, self).build_xml(level)


class DimensionUsage(MondrianElement):
    def __init__(self, name, source, foreign_key):
        self.name = name
        self.source = source
        self.foreign_key = foreign_key
        super(DimensionUsage, self).__init__()

    def build_xml(self, parent):
        dimension = ET.SubElement(parent, "DimensionUsage")
        dimension.attrib = {
            "name": self.name,
            "source": self.source,
            "foreignKey": self.foreign_key,
        }

        super(DimensionUsage, self).build_xml(dimension)


class Measure(MondrianElement):
    aggregator_whitelist = [
        "sum",
        "count",
        "min",
        "max",
        "avg",
        "distinct-count",
        "median",
        "none",
    ]

    database_whitelist = [
        "postgres",
        "monetdb",
    ]

    MONET_MEDIAN = "sys.median({})"
    # xml lib automatically escapes >
    POSTGRES_MEDIAN = "PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY {} ASC) FILTER (WHERE {} > 0)"

    def __init__(self, name, column, aggregator, database=None, visible=True, sql_expr=""):
        # TODO check whitelist
        # TODO check that if aggregator == mediean, database != None
        # TODO make separate class for median aggregator? or hard code?
        self.name = name
        self.column = column
        self.aggregator = aggregator
        self.database = database
        self.visible = visible
        self.sql_expr = sql_expr
        super(Measure, self).__init__()

    def build_xml(self, parent):
        measure = ET.SubElement(parent, "Measure")

        super(Measure, self).build_xml(measure)

        measure.attrib = {
            "name": self.name,
            "aggregator": self.aggregator,
            "visible": str(self.visible).lower(),
        }

        if self.aggregator == 'median':
            measure.attrib["aggregator"] = "None"
            measure.attrib["dataType"] = "Numeric"

            expression = ET.SubElement(measure, "MeasureExpression")
            sql = ET.SubElement(expression, "SQL")
            sql.attrib = {"dialect": self.database}
            if self.database == "monetdb":
                sql.text = self.MONET_MEDIAN.format(self.column)
            elif self.database == "postgres":
                sql.text = self.POSTGRES_MEDIAN.format(self.column, self.column)
        elif self.aggregator == "none":
            measure.attrib["aggregator"] = "None"
            measure.attrib["dataType"] = "Numeric"

            expression = ET.SubElement(measure, "MeasureExpression")
            sql = ET.SubElement(expression, "SQL")
            if self.database is None:
                sql.attrib = {"dialect": "monetdb"}
            else:
                sql.attrib = {"dialect": self.database}
            sql.text = self.sql_expr

        else:
            measure.attrib["column"] = self.column



class CalculatedMember(MondrianElement):

    def __init__(self, name, dimension, formula, visible=True):
        self.name = name
        self.dimension = dimension
        self.formula = formula
        self.visible = visible
        super(CalculatedMember, self).__init__()

    def build_xml(self, parent):
        calculated_member = ET.SubElement(parent, "CalculatedMember")

        super(CalculatedMember, self).build_xml(calculated_member)

        calculated_member.attrib = {
            "name": self.name,
            "dimension": self.dimension,
            "visible": str(self.visible).lower(),
        }
        formula = ET.SubElement(calculated_member, "Formula")
        formula.text = self.formula



class NamedSet(MondrianElement):

    def __init__(self, name, formula, visible=True):
        self.name = name
        self.formula = formula
        self.visible = visible
        super(NamedSet, self).__init__()

    def build_xml(self, parent):
        named_set = ET.SubElement(parent, "NamedSet")
        named_set.attrib = {
            "name": self.name,
            "visible": str(self.visible).lower(),
        }
        formula = ET.SubElement(named_set, "Formula")
        formula.text = self.formula

        super(NamedSet, self).build_xml(named_set)


if __name__ == "__main__":
    schema = Schema("cny-vitals")

    cube = Cube(
        name="acs_5yr_ygsa_poverty_status",
        table="acs_5yr_ygsa_poverty_status",
        schema="cny",
    )
    schema.add_cube(cube)

    cube.add_annotation(Annotation("test", "annotation"))

    cube.add_calculated_member(CalculatedMember(
        name="test",
        dimension="test",
        formula="test",
        visible=True,
    ))

    cube.add_measure(Measure(
        name="test",
        column="testcolumn",
        aggregator="median",
        database="monetdb",
    ))

    cube.add_measure(Measure(
        name="test",
        column="testcolumn",
        aggregator="median",
        database="postgres",
    ))

    test_mea_ann = Measure(
        name="test_annotations",
        column="testcolumn",
        aggregator="median",
        database="postgres",
    )
    test_mea_ann.add_annotation(Annotation("test", "test"))
    cube.add_measure(test_mea_ann)

    dimension = Dimension("Industry", table="industry", schema="public")
    dimension.add_level(Level(
        name="Industry Group",
        column="industry_group",
        name_column="industry_group_description",
        unique_members=True,
    ))
    test_level = Level(
        name="Industry Activity",
        column="industry_activity",
        name_column="industry_activity_description",
        unique_members=True,
    )
    dimension.add_level(test_level)
    test_level.add_annotation(Annotation("test", "test"))
    test_level.add_property(Property("testname", "testcolumn"))

    test_level_2 = Level(
        name="Group",
        column="group",
        name_column="group_description",
        unique_members=True,
        hierarchy="Nation"
    )
    test_level_3 = Level(
        name="User",
        column="user",
        name_column="user_description",
        unique_members=True,
        hierarchy="Nation"
    )
    test_level_4 = Level(
        name="Biker",
        column="biker",
        name_column="biker_description",
        unique_members=True,
        hierarchy="Nation"
    )
    dimension.add_level(test_level_2)
    dimension.add_level(test_level_3)
    dimension.add_level(test_level_4)

    schema.add_dimension(dimension)

    cube.add_dimension_usage(DimensionUsage("test dimension usage", "Industry", "geoid"))

    dimension = Dimension("Vitals", table="vitals", schema="public")
    dimension.add_level(Level(
        name="Vitals Group",
        column="Vitals",
        name_column="vitals_group_description",
        unique_members=True,
    ))
    test_level = Level(
        name="Vitals Activity",
        column="Vitals",
        name_column="vitals_activity_description",
        unique_members=True,
        table="schema.vitals2",
    )
    dimension.add_level(test_level)

    cube.add_dimension(dimension)

    dimension = Dimension("Nationality")
    hierarchy = Hierarchy("Nat", table='nat', schema="shapes")
    hierarchy.add_level(Level(
        name="Nationality Group",
        column="nationality",
        name_column="nationality_group_description",
        unique_members=True,
    ))
    dimension.add_hierarchy(hierarchy)

    hierarchy = Hierarchy("Other", table='other', schema="shapes")
    hierarchy.add_level(Level(
        name="Other Group",
        column="other",
        name_column="other_group_description",
        unique_members=True,
    ))
    hierarchy.add_level(Level(
        name="Other GroupB",
        column="otherb",
        name_column="other_group_b_description",
        unique_members=True,
    ))
    dimension.add_hierarchy(hierarchy)

    dimension.add_view(View(alias="nationality_view", formula="Union All"))
    schema.add_dimension(dimension)

    print(schema.xml_render())
