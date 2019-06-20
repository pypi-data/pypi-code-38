from data_catapult.mondrian.schema import Cube, Schema, Dimension, Measure, Level
from data_catapult.mondrian.schema import CalculatedMember  # DimensionUsage
from io import StringIO


def gen_schema(table_name, output_as_fo=False):
    schema = Schema("datausa")

    cube = Cube(
        name=table_name,
        table=table_name,
        schema="pums",
    )

    cube.add_measure(Measure(
        name="Population Total",
        column="pwgtp",
        aggregator="sum",
        database="postgres",
    ))

    cube.add_measure(Measure(
        name="Age",
        column="agep",
        aggregator="median",
        database="postgres",
    ))

    cube.add_measure(CalculatedMember(
        name="Weighted Wage",
        dimension="Measures",
        formula="[Measures].[Wage]",
        visible=True,
    ))

    dimension = Dimension("Geography")
    dimension.add_level(Level(
        name="State",
        column="st",
        unique_members=True,
    ))
    dimension.add_level(Level(
        name="PUMA",
        column="puma",
        unique_members=True,
    ))
    cube.add_dimension(dimension)

    dimension = Dimension("Year")
    dimension.add_level(Level(
        name="Year",
        column="year",
        unique_members=True,
    ))
    cube.add_dimension(dimension)

    dimension = Dimension("Occupation")
    dimension.add_level(Level(
        name="Occupation",
        column="socp",
        unique_members=True,
    ))
    cube.add_dimension(dimension)

    dimension = Dimension("Workforce Status")
    dimension.add_level(Level(
        name="Workforce Status",
        column="esr",
        unique_members=True,
    ))
    cube.add_dimension(dimension)

    dimension = Dimension("Industry")
    dimension.add_level(Level(
        name="Industry",
        column="naicsp",
        unique_members=True,
    ))
    cube.add_dimension(dimension)

    dimension = Dimension("Race")
    dimension.add_level(Level(
        name="Race",
        column="rac1p",
        unique_members=True,
    ))
    cube.add_dimension(dimension)

    dimension = Dimension("Field of Degree")
    dimension.add_level(Level(
        name="Field of Degree",
        column="fod1p",
        unique_members=True,
    ))
    cube.add_dimension(dimension)

    dimension = Dimension("Place of Birth")
    dimension.add_level(Level(
        name="Place of Birth",
        column="pobp",
        unique_members=True,
    ))
    cube.add_dimension(dimension)

    dimension = Dimension("Sex")
    dimension.add_level(Level(
        name="Sex",
        column="sex",
        unique_members=True,
    ))

    dimension = Dimension("Education")
    dimension.add_level(Level(
        name="Education Level",
        column="schl",
        unique_members=True,
    ))

    cube.add_dimension(dimension)
    schema.add_cube(cube)

    xml_output = schema.xml_render(pretty_print=True)
    if output_as_fo:
        return StringIO(xml_output)
    return xml_output


if __name__ == '__main__':
    print(gen_schema(1))
