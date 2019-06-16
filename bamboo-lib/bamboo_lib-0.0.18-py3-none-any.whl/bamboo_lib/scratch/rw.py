

def population_measures():
    pop_template = '''
        <Measure name="Total Population{0}" column="pwgtp{0}" aggregator="sum" visible="{1}"/>
    \n'''
    calc_tmp = ""
    for i in range(0, 81):
        val = "" if i == 0 else i
        calc_tmp += pop_template.format(val, "true" if i == 0 else "false")
    return calc_tmp


def population_moe():
    deltas = []
    for i in range(1, 81):
        f = 'Power([Measures].[Total Population] - [Measures].[Total Population{i}], 2)'.format(i=i)
        deltas.append(f)

    summation = "+".join(deltas)
    final_form = "1.645 * Power(.05 * ({}), 0.5)".format(summation)
    return """
    <CalculatedMember name="Total Population MOE" dimension="Measures">
    <Formula>
      <![CDATA[
        {formula}
      ]]>
    </Formula>
    </CalculatedMember>
    """.format(formula=final_form)


def gen_meas(pretty_name, col_name):
    template1 = '''
    <Measure aggregator="None" dataType="Numeric" name="Weighted {2}{0}" visible="{1}">
      <MeasureExpression>
          <SQL dialect="generic">SUM(pwgtp{0} * {3})</SQL>
      </MeasureExpression>
    </Measure>\n
    '''
    mea_tmp = ""
    for i in range(0, 81):
        val = "" if i == 0 else i
        mea_tmp += template1.format(val, "true" if i == 0 else "false", pretty_name, col_name)
    return mea_tmp


def gen_calcs(pretty_name, col_name):
    template2 = '''
    <CalculatedMember name="Average {2}{0}" dimension="Measures" visible="{1}">
      <Formula>[Measures].[Weighted {2}{0}] / [Measures].[Total Population{0}]</Formula>
    </CalculatedMember>\n
    '''

    calc_tmp = ""

    for i in range(0, 81):
        val = "" if i == 0 else i
        calc_tmp += template2.format(val, "true" if i == 0 else "false", pretty_name, col_name)

    deltas = []
    for i in range(1, 81):
        f = 'Power([Measures].[Average {pretty_name}] - [Measures].[Average {pretty_name}{i}], 2)'.format(i=i, pretty_name=pretty_name)
        deltas.append(f)

    summation = "+".join(deltas)
    final_form = "1.645 * Power(.05 * ({}), 0.5)".format(summation)
    wagp_moe = """
    <CalculatedMember name="Average {pretty_name} MOE" dimension="Measures">
    <Formula>
      <![CDATA[
        {formula}
      ]]>
    </Formula>
    </CalculatedMember>
    """.format(formula=final_form, pretty_name=pretty_name)
    return calc_tmp + "\n" + wagp_moe
# # deltas = [' for i in range(0,)


def gen_all():
    tmp = population_measures()
    metrics = [("Wage", "wagp")]
    metrics += [("Age", "agep")]
    metrics += [("Income", "pincp")]
    metrics += [("Usual Worked Per Week", "wkhp")]
    metrics += [("Weeks Worked Past Year", "wkw")]

    for metric, col in metrics:
        tmp += gen_meas(metric, col)

    for metric, col in metrics:
        tmp += gen_calcs(metric, col)
    tmp += population_moe()
    return tmp
