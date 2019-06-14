import os
import sys

paths = [
    "/Users/ran/Develop/lm-billing/billing-example-1/productionBilling-1 (5).csv",
    "/Users/ran/Develop/lm-billing/billing-example-1/productionBilling-1 (6).csv",
    "/Users/ran/Develop/lm-billing/billing-example-1/productionBilling-1 (7).csv",
    "/Users/ran/Develop/lm-billing/billing-example-1/productionBilling-1 (8).csv",
    "/Users/ran/Develop/lm-billing/billing-example-1/productionBilling-1 (9).csv",
    "/Users/ran/Develop/lm-billing/billing-example-1/productionBilling-1 (10).csv",
    "/Users/ran/Develop/lm-billing/billing-example-1/productionBilling-1 (11).csv"
    ]

copy = open("/Users/ran/Develop/lm-billing/merge.csv", "w")

first_file = True
for path in paths:
    f = open(path, "r")
    first_line = True
    for line in f:
        if not first_file and first_line:
            first_line = False
            continue
        copy.write(line)

    first_file = False
    f.close()
copy.close()
