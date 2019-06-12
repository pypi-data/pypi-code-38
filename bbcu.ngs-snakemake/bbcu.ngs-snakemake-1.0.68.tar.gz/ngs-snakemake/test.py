GROUPS = {
    "group1":["sample1","sample2"],
    "group2":["sample3","sample4"]
}

rule1:
    input:
        expand("previous_rule/{group}", group=list(GROUPS.keys()))
    run:
        sample1 = GROUPS[{group}][0]
        sample2 = GROUPS[{group}][1]
        shell("echo bla")