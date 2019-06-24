from rpcUtils import toFMDateTime

ALLERGYRPCS = [

    ["selectPatient", "ORWPT SELECT", ["25"]],

    ["lookupAllergyDefinitionList", "ORWDAL32 DEF", []],

    ["listSymptoms", "ORWDAL32 SYMPTOMS", ["", "1"]],

    ["listAllergies", "ORQQAL LIST", ["25"], "Expect ^No Allergy Assessment"],

    ["getDate", "ORWU DT", ["NOW"]],

    ["lookupAllergins", "ORWDAL32 ALLERGY MATCH", ["CHOCOLATE"]],

    ["createAllergy", "ORWDAL32 SAVE ALLERGY", [
        "0",
        "25",
        {
            "GMRAGNT": "CHOCOLATE^3;GMRD(120.82,",
            "GMRATYPE": "DF^Drug,Food",
            "GMRAORIG": "63",
            "GMRANATR": "A^Allergy",
            "GMRAORDT": toFMDateTime(),
            "GMRASYMP": [
                "66^DROWSINESS^^^"
            ],
            "GMRACHT": [
                toFMDateTime()
            ],
            "GMRAOBHX": "h^HISTORICAL"
        }
    ]],

    ["listAllergies", "ORQQAL LIST", ["25"], "Expect ONE allergy"],

    ["describeAllergy", "ORQQAL DETAIL", [ "25", "1", "1" ]],

    ["createAllergy", "ORWDAL32 SAVE ALLERGY", [
        "0",
        "25",
        {
            "GMRAGNT": 'ACETAMINOPHEN/CODEINE^203;PSNDF(50.6,',
            "GMRATYPE": 'D',
            "GMRANATR": 'P',
            "GMRAORIG": "63",
            "GMRAORDT": toFMDateTime(),
            "GMRACHT": [
                toFMDateTime()
            ],
            "GMRAOBHX": 'o',
            "GMRASYMP": [
                '51^CHEST PAIN',
                '1^HIVES',
            ],
            "GMRACMTS": [
                "don't give the guy this med! ",
            ],
            "GMRARDT": toFMDateTime()
        }
    ]],

    ["listAllergies", "ORQQAL LIST", ["25"], "Expect TWO allergies"],

    ["describeAllergy", "ORQQAL DETAIL", [ "25", "1", "2" ]], 

    ["describeAllergy (Other)", "ORWDAL32 LOAD FOR EDIT", [ "2" ]],

    ["setNKA", "ORWDAL32 SAVE ALLERGY", [
        "0",
        "25",
        {
            "GMRANKA": "YES"
        }
    ], "Expect -1^Patient has active allergies - can't mark as NKA"],

    ["removeAllergy", "ORWDAL32 SAVE ALLERGY", [
        "1",
        "25",
        {
            "GMRAERR": "YES",
            "GMRAERRBY": "63",
            "GMRAERRDT": toFMDateTime(),
            "GMRAERRCMTS": [
                "I made a mistake!"
            ]
        }
    ]],

    ["listAllergies", "ORQQAL LIST", ["25"], "Expect ONE allergy"],

    ["describeAllergy", "ORQQAL DETAIL", [ "25", "1", "1" ], "Can still describe the removed allergy"],

    ["removeAllergy", "ORWDAL32 SAVE ALLERGY", [
        "2",
        "25",
        {
            "GMRAERR": "YES",
            "GMRAERRBY": "63",
            "GMRAERRDT": toFMDateTime(),
            "GMRAERRCMTS": [
                "I made YET ANOTHER mistake!"
            ]
        }
    ]],

    ["listAllergies", "ORQQAL LIST", ["25"], "Expect ^No Allergy Assessment"],

    ["setNKA", "ORWDAL32 SAVE ALLERGY", [
        "0",
        "25",
        {
            "GMRANKA": "YES"
        }
    ]],

    ["listAllergies", "ORQQAL LIST", ["25"], "Expect ^No Known Allergies"]
]
