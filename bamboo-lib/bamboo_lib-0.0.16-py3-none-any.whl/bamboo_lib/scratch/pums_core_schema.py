PUMS_MASTER_XML = """<?xml version="1.0" ?>
<Schema name="datausa">

<Cube name="pums_1">
    <Annotations>
      <Annotation name="source_name">Census Bureau</Annotation>
      <Annotation name="source_description">The American Community Survey (ACS) Public Use Microdata Sample (PUMS) files are a set of untabulated records about individual people or housing units. The Census Bureau produces the PUMS files so that data users can create custom tables that are not available through pretabulated (or summary) ACS data products.</Annotation>
      <Annotation name="dataset_name">ACS PUMS 1-Year Estimate</Annotation>
      <Annotation name="dataset_link">https://census.gov/programs-surveys/acs/technical-documentation/pums.html</Annotation>
      <Annotation name="subtopic">Demographics</Annotation>
      <Annotation name="table_id">PUMS</Annotation>
      <Annotation name="topic">Diversity</Annotation>
      <Annotation name="hidden_measures">{to_hide}</Annotation>
    </Annotations>
  <Table name="pums_1" schema="pums"/>
  <Dimension foreignKey="puma" name="Geography">
    <Annotations>
      <Annotation name="dim_type">GEOGRAPHY</Annotation>
    </Annotations>
    <Hierarchy hasAll="true" primaryKey="geoid" defaultMember="[Nation].[United States]">
      <Table name="pumas" schema="shapes2017"/>
      <Level column="nation_id" nameColumn="nation_name" name="Nation" uniqueMembers="true" hideMemberIf="IfBlankName"/>
      <Level column="state_id" nameColumn="state_name" name="State" uniqueMembers="true"/>
      <Level column="geoid" nameColumn="name" name="PUMA" uniqueMembers="true"/>
    </Hierarchy>
  </Dimension>
  <Dimension name="Year">
    <Annotations>
      <Annotation name="dim_type">TIME</Annotation>
    </Annotations>
    <Hierarchy hasAll="true">
      <Level column="year" levelType="TimeYears" name="Year" type="Numeric" uniqueMembers="true"/>
    </Hierarchy>
  </Dimension>
  <Dimension name="Workforce Status">
    <Hierarchy hasAll="true">
      <Level column="in_workforce" name="Workforce Status" type="Boolean" uniqueMembers="true"/>
    </Hierarchy>
  </Dimension>
  <Dimension foreignKey="time_status" name="Employment Time Status">
    <Hierarchy hasAll="true">
      <InlineTable alias="emp_time_status">
        <ColumnDefs>
          <ColumnDef name="id" type="Numeric"/>
          <ColumnDef name="description" type="String"/>
        </ColumnDefs>
        <Rows>
          <Row>
            <Value column="id">1</Value>
            <Value column="description">Full-time</Value>
          </Row>
          <Row>
            <Value column="id">2</Value>
            <Value column="description">Part-time</Value>
          </Row>
        </Rows>
      </InlineTable>
      <Level column="id" name="Employment Time Status" nameColumn="description" uniqueMembers="true">
      </Level>
    </Hierarchy>
  </Dimension>
  <Dimension name="Age">
    <Hierarchy hasAll="true">
      <Level column="agep" name="Age" type="Numeric" uniqueMembers="true"/>
    </Hierarchy>
  </Dimension>
  <Dimension foreignKey="wkw" name="Weeks Worked">
    <Hierarchy hasAll="true">
    <InlineTable alias="wks">
      <ColumnDefs>
        <ColumnDef name="id" type="Numeric"/>
        <ColumnDef name="description" type="String"/>
      </ColumnDefs>
      <Rows>
        <Row>
          <Value column="id">1</Value>
          <Value column="description">50-52 Weeks</Value>
        </Row>
        <Row>
          <Value column="id">2</Value>
          <Value column="description">48-49 Weeks</Value>
        </Row>
        <Row>
          <Value column="id">3</Value>
          <Value column="description">40-47 Weeks</Value>
        </Row>
        <Row>
          <Value column="id">4</Value>
          <Value column="description">27-39 Weeks</Value>
        </Row>
        <Row>
          <Value column="id">5</Value>
          <Value column="description">14-26 Weeks</Value>
        </Row>
        <Row>
          <Value column="id">6</Value>
          <Value column="description">Less than 14 Weeks</Value>
        </Row>
      </Rows>
    </InlineTable>
    <Level column="id" name="Weeks Worked" nameColumn="description" uniqueMembers="true">
    </Level>
  </Hierarchy>
  </Dimension>
<DimensionUsage foreignKey="socp" source="PUMS Occupation" name="PUMS Occupation" />
<DimensionUsage foreignKey="naicsp" source="PUMS Industry" name="PUMS Industry" />
<DimensionUsage foreignKey="pobp" source="Birthplace" name="Birthplace" />
<DimensionUsage foreignKey="hisp" source="PUMS Ethnicity" name="PUMS Ethnicity" />

<Dimension foreignKey="schl" name="PUMS Degree">
    <Hierarchy hasAll="true" primaryKey="schl">
        <Table name="schl" schema="pums_dims"/>
        <Level column="schl_group" nameColumn="schl_group" name="Group" uniqueMembers="true"/>
        <Level column="schl" nameColumn="schl_name" name="Degree" uniqueMembers="true"/>
    </Hierarchy>
</Dimension>
  <Dimension foreignKey="fod1p" name="PUMS Degree Field">
    <Hierarchy hasAll="true" primaryKey="fod1p">
        <Table name="fod1p" schema="pums_dims"/>
        <Level column="cip2" nameColumn="cip2_name" name="CIP2" uniqueMembers="true"/>
        <Level column="fod1p" nameColumn="fod1p_name" name="FOD1P" uniqueMembers="true"/>
    </Hierarchy>
</Dimension>
  <Dimension foreignKey="sex" name="Gender">
    <Hierarchy hasAll="true">
      <InlineTable alias="sex">
        <ColumnDefs>
          <ColumnDef name="id" type="Numeric"/>
          <ColumnDef name="description" type="String"/>
        </ColumnDefs>
        <Rows>
          <Row>
            <Value column="id">1</Value>
            <Value column="description">Male</Value>
          </Row>
          <Row>
            <Value column="id">2</Value>
            <Value column="description">Female</Value>
          </Row>
        </Rows>
      </InlineTable>
      <Level column="id" name="Gender" nameColumn="description" uniqueMembers="true">
      </Level>
    </Hierarchy>
  </Dimension>
  <Dimension foreignKey="rac1p" name="Race">
    <Hierarchy hasAll="true">
      <InlineTable alias="race">
        <ColumnDefs>
          <ColumnDef name="id" type="Numeric"/>
          <ColumnDef name="description" type="String"/>
        </ColumnDefs>
        <Rows>
          <Row>
            <Value column="id">1</Value>
            <Value column="description">White</Value>
          </Row>
          <Row>
            <Value column="id">2</Value>
            <Value column="description">Black</Value>
          </Row>
          <Row>
            <Value column="id">3</Value>
            <Value column="description">American Indian</Value>
          </Row>
          <Row>
            <Value column="id">4</Value>
            <Value column="description">Alaska Native</Value>
          </Row>
          <Row>
            <Value column="id">5</Value>
            <Value column="description">American Indian and Alaska Native tribes specified; or American Indian or Alaska Native, not specified and no other races</Value>
          </Row>
          <Row>
            <Value column="id">6</Value>
            <Value column="description">Asian</Value>
          </Row>
          <Row>
            <Value column="id">7</Value>
            <Value column="description">Native Hawaiian and Other Pacific Islander</Value>
          </Row>
          <Row>
            <Value column="id">8</Value>
            <Value column="description">Other</Value>
          </Row>
          <Row>
            <Value column="id">9</Value>
            <Value column="description">Two or More Races</Value>
          </Row>
        </Rows>
      </InlineTable>
      <Level column="id" name="Race" nameColumn="description" uniqueMembers="true">
      </Level>
    </Hierarchy>
  </Dimension>

<Dimension foreignKey="esr" name="Employment Status">
    <Hierarchy hasAll="true">
      <InlineTable alias="esr">
        <ColumnDefs>
          <ColumnDef name="id" type="Numeric"/>
          <ColumnDef name="description" type="String"/>
          <ColumnDef name="parent" type="String"/>
        </ColumnDefs>
        <Rows>
          <Row>
            <Value column="id">1</Value>
            <Value column="description">Civilian employed, at work</Value>
            <Value column="parent">Employed</Value>

          </Row>
          <Row>
            <Value column="id">2</Value>
            <Value column="description">Civilian employed, with a job but not at work</Value>
            <Value column="parent">Employed</Value>
          </Row>
          <Row>
            <Value column="id">3</Value>
            <Value column="description">Unemployed</Value>
            <Value column="parent">Not Employed</Value>
          </Row>
          <Row>
            <Value column="id">4</Value>
            <Value column="description">Armed forces, at work</Value>
            <Value column="parent">Employed</Value>
          </Row>
          <Row>
            <Value column="id">5</Value>
            <Value column="description">Armed forces, with a job but not at work</Value>
            <Value column="parent">Employed</Value>
          </Row>
          <Row>
            <Value column="id">6</Value>
            <Value column="description">Not in labor force</Value>
            <Value column="parent">Not Employed</Value>
          </Row>
        </Rows>
      </InlineTable>
      <Level column="parent" name="Employment Status Parent" uniqueMembers="true"></Level>
      <Level column="id" name="Employment Status" nameColumn="description" uniqueMembers="true">
      </Level>
    </Hierarchy>
  </Dimension>
  <Dimension foreignKey="cit" name="Citizenship Status">
    <Hierarchy hasAll="true">
      <InlineTable alias="cit">
        <ColumnDefs>
          <ColumnDef name="id" type="Numeric"/>
          <ColumnDef name="description" type="String"/>
          <ColumnDef name="parent" type="String"/>
        </ColumnDefs>
        <Rows>
          <Row>
            <Value column="id">1</Value>
            <Value column="description">Born in the U.S.</Value>
            <Value column="parent">U.S. Citizen</Value>

          </Row>
          <Row>
            <Value column="id">2</Value>
            <Value column="description">Born in Puerto Rico, Guam, the U.S. Virgin Islands, or the Northern Marianas</Value>
            <Value column="parent">U.S. Citizen</Value>
          </Row>
          <Row>
            <Value column="id">3</Value>
            <Value column="description">Born abroad of American parent(s)</Value>
            <Value column="parent">U.S. Citizen</Value>
          </Row>
          <Row>
            <Value column="id">4</Value>
            <Value column="description">U.S. citizen by naturalization</Value>
            <Value column="parent">U.S. Citizen</Value>
          </Row>
          <Row>
            <Value column="id">5</Value>
            <Value column="description">Not a citizen of the U.S.</Value>
            <Value column="parent">Not a citizen of the U.S.</Value>
          </Row>
        </Rows>
      </InlineTable>
      <Level column="parent" name="Citizenship Status Parent" uniqueMembers="true"></Level>
      <Level column="id" name="Citizenship Status" nameColumn="description" uniqueMembers="true">
      </Level>
    </Hierarchy>
  </Dimension>
  <Dimension foreignKey="nativity" name="Nativity">
    <Hierarchy hasAll="true">
      <InlineTable alias="nativity">
        <ColumnDefs>
          <ColumnDef name="id" type="Numeric"/>
          <ColumnDef name="description" type="String"/>
        </ColumnDefs>
        <Rows>
          <Row>
            <Value column="id">1</Value>
            <Value column="description">Native</Value>
          </Row>
          <Row>
            <Value column="id">2</Value>
            <Value column="description">Foreign born</Value>
          </Row>
        </Rows>
      </InlineTable>
      <Level column="id" name="Nativity" nameColumn="description" uniqueMembers="true">
      </Level>
    </Hierarchy>
  </Dimension>

  <Dimension foreignKey="vps" name="Veteran Status">
    <Hierarchy hasAll="true">
      <InlineTable alias="veteran_status">
        <ColumnDefs>
          <ColumnDef name="id" type="Numeric"/>
          <ColumnDef name="description" type="String"/>
          <ColumnDef name="parent_description" type="String"/>

        </ColumnDefs>
        <Rows>
          <Row>
            <Value column="id">1</Value>
            <Value column="description">Gulf War: 9/2001 or later</Value>
            <Value column="parent_description">Gulf War</Value>
          </Row>
          <Row>
            <Value column="id">2</Value>
            <Value column="description">Gulf War: 9/2001 or later and Gulf War: 8/1990 - 8/2001</Value>
            <Value column="parent_description">Gulf War</Value>
          </Row>
          <Row>
            <Value column="id">3</Value>
            <Value column="description">Gulf War: 9/2001 or later and Gulf War: 8/1990 - 8/2001 and Vietnam Era</Value>
            <Value column="parent_description">Gulf War</Value>
          </Row>
          <Row>
            <Value column="id">4</Value>
            <Value column="description">Gulf War: 8/1990 - 8/2001</Value>
            <Value column="parent_description">Gulf War</Value>
          </Row>
          <Row>
            <Value column="id">5</Value>
            <Value column="description">Gulf War: 8/1990 - 8/2001 and Vietnam Era</Value>
            <Value column="parent_description">Gulf War</Value>
          </Row>
          <Row>
            <Value column="id">6</Value>
            <Value column="description">Vietnam Era</Value>
            <Value column="parent_description">Vietnam Era</Value>
          </Row>
          <Row>
            <Value column="id">7</Value>
            <Value column="description">Vietnam Era and Korean War</Value>
            <Value column="parent_description">Vietnam Era</Value>
          </Row>
          <Row>
            <Value column="id">8</Value>
            <Value column="description">Vietnam Era, Korean War, and WWII</Value>
            <Value column="parent_description">Vietnam Era War</Value>
          </Row>
          <Row>
            <Value column="id">9</Value>
            <Value column="description">Korean War</Value>
            <Value column="parent_description">Korean War</Value>
          </Row>
          <Row>
            <Value column="id">10</Value>
            <Value column="description">Korean War and WWII</Value>
            <Value column="parent_description">Korean War</Value>
          </Row>
          <Row>
            <Value column="id">11</Value>
            <Value column="description">WWII</Value>
            <Value column="parent_description">WWII</Value>
          </Row>
          <Row>
            <Value column="id">12</Value>
            <Value column="description">Between Gulf War and Vietnam Era only</Value>
            <Value column="parent_description">Between Gulf War and Vietnam Era only</Value>
          </Row>
          <Row>
            <Value column="id">13</Value>
            <Value column="description">Between Vietnam Era and Korean War only</Value>
            <Value column="parent_description">Between Vietnam Era and Korean War only</Value>
          </Row>
          <Row>
            <Value column="id">14</Value>
            <Value column="description">Between Korean War and World War II only</Value>
            <Value column="parent_description">Between Korean War and World War II only</Value>
          </Row>
          <Row>
            <Value column="id">15</Value>
            <Value column="description">Pre-WWII only</Value>
            <Value column="parent_description">Pre-WWII only</Value>
          </Row>
        </Rows>
      </InlineTable>
      <Level column="id" name="Veteran Status" nameColumn="description" uniqueMembers="true">
      </Level>
    </Hierarchy>
  </Dimension>

  <Dimension foreignKey="wage_bin" name="Wage Bin">
    <Hierarchy hasAll="true">
      <Level column="wage_bin_id" nameColumn="wage_bin" name="Wage Bin" uniqueMembers="true" ordinalColumn="wage_bin_id"></Level>
    </Hierarchy>
  </Dimension>

  <Dimension name="Age Five Plus">
    <Hierarchy hasAll="true">
      <Level column="fiveplus" name="Age Five Plus" type="Boolean" uniqueMembers="true"/>
    </Hierarchy>
  </Dimension>

  <Measure aggregator="count" column="pwgtp" name="Record Count" visible="true">
    <Annotations>
        <Annotation name="units_of_measurement">Sample Records</Annotation>
    </Annotations>
  </Measure>

  {calculations}
</Cube>
</Schema>"""
