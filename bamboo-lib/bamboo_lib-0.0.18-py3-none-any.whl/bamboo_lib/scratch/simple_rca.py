'''
RCA is just
(a / b)
   /
(c / d)

'''


def gen_members(prefix, title, fn, members, allowed_cuts=None, metric="Total Population"):
    allowed_cuts = [] if not allowed_cuts else allowed_cuts
    my_list = []
    for m in members:
        if fn(m) or m in allowed_cuts:
            my_list.append("[{0}].[{0}].CurrentMember".format(m))
        else:
            my_list.append("[{0}].[{0}].[All {0}s]".format(m))
    my_member_str = ",\n\t\t".join(my_list)
    return """
    <CalculatedMember dimension="Measures" name="{prefix}_rca_{title}_pop" visible="false">
      <Formula>
        <![CDATA[
            (Measures.[{metric}], {my_member_str})
        ]]>
      </Formula>
    </CalculatedMember>
    """.format(prefix=prefix, my_member_str=my_member_str, title=title, metric=metric)

'''
me_mode is the target member
index_modes are the index columns for the RCA calculations
for example to compute the RCA of occupations by year and geography
me_mode = "PUMS Occupation"
and index_modes=["Year", "Geography"]

this function will create variables b,c,d from the RCA formula according the
me/index modes
'''
def simple_rca(prefix, me_mode, index_modes, allowed_cuts=None, metric="Total Population"):
    members = [
        "Year",
        "Geography",
        "Employment Status",
        "Workforce Status",
        "PUMS Occupation",
        "Gender",
        "Age",
        "Race",
        "Nativity",
        "Veteran Status",
        "Wage Bin",
        "Weeks Worked",
        "PUMS Degree",
        "PUMS Degree Field",
        "PUMS Industry"
    ]
    members_b = gen_members(prefix, "b", lambda m: m in index_modes, members, allowed_cuts, metric)
    members_c = gen_members(prefix, "c", lambda m: m in me_mode or m in index_modes[:-1], members, allowed_cuts, metric)
    members_d = gen_members(prefix, "d", lambda m: m in index_modes[:-1], members, allowed_cuts, metric)

    return """
    {members_b}
    {members_c}
    {members_d}

    <CalculatedMember dimension="Measures" name="{prefix} RCA" visible="true">
      <Annotations>
        <Annotation name="aggregation_method">RCA</Annotation>
      </Annotations>
      <Formula>
        <![CDATA[
        IIF([Measures].[{prefix}_rca_c_pop] > 0 and [Measures].[{prefix}_rca_d_pop] > 0,
         ([Measures].[{metric}] / [Measures].[{prefix}_rca_b_pop]) /
         ([Measures].[{prefix}_rca_c_pop] / [Measures].[{prefix}_rca_d_pop])
         , NULL)
        ]]>
      </Formula>
    </CalculatedMember>
    """.format(prefix=prefix, members_b=members_b,
               members_c=members_c, members_d=members_d,
               metric=metric)


if __name__ == "__main__":
    print(gen_rca("ygo", "PUMS Occupation", ["Year", "Geography"], "Employment Status"))
