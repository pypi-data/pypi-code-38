

def total_pop():
    return "\n".join(['''<Measure name="Total Population{0}" column="pwgtp{0}" aggregator="sum" />'''.format(i if i != 0 else "") for i in range(0, 81)])


def measurer(mcolumn, mname):
    template1 = '''
    <Measure aggregator="None" dataType="Numeric" name="Weighted {2}{0}" visible="true">
      <MeasureExpression>
          <SQL dialect="generic">SUM(pwgtp{0} * {1})</SQL>
      </MeasureExpression>
    </Measure>
    <CalculatedMember name="Average {2}{0}" dimension="Measures">
      <Formula>[Measures].[Weighted {2}{0}] / [Measures].[Total Population{0}]</Formula>
    </CalculatedMember>
    '''

    output_xml = ""
    for i in range(0, 81):
        val = "" if i == 0 else i
        output_xml += template1.format(val, mcolumn, mname)

    deltas = []
    for i in range(1, 81):
        f = 'Power([Measures].[Average {1}] - [Measures].[Average {1}{0}], 2)'.format(i, mname)
        deltas.append(f)

    summation = "+".join(deltas)
    formula = "Power(.05 * ({}), 0.5)".format(summation)
    moe = '''<CalculatedMember name="Average {} MOE" dimension="Measures">
      <Formula><![CDATA[
        {}
      ]]></Formula>
    </CalculatedMember>
    '''.format(mname, formula)
    return output_xml  # moe


print(total_pop())
print(measurer("wagp", "Wage"))
