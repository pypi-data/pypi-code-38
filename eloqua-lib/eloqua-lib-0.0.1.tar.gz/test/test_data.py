from eloqua.eloqua import CustomObjectModel

TESTING_CUSTOM_OBJECT_DOG_OWNER = {
    "name":        "TEST_Dog_Owner",
    "description": "Testing Custom Object for dog owners",
    "permissions": ["Retrieve", "Update", "SetSecurity", "Delete"],
    "fields":      [
        {
            "name":        "DogBreed",
            "displayType": "text",
            "dataType":    "text"
        },
        {
            "name":        "StartOfOwnership",
            "displayType": "text",
            "dataType":    "date"
        },
        {
            "name":        "AgeAtStartOfOwnership",
            "displayType": "text",
            "dataType":    "number"
        },
        {
            "name":        "DogColor",
            "displayType": "text",
            "dataType":    "text"
        },
        {
            "name":        "DogName",
            "displayType": "text",
            "dataType":    "text"
        }
    ]
}

TESTING_CUSTOM_OBJECT_ASSET = {
    "name":        "xxx_QuickTest_xxx123345",
    "description": "Testing Custom Object",
    "permissions": ["Retrieve", "Update", "SetSecurity", "Delete", "Create"],
    "fields":      [
        {
            "name":        "Test",
            "displayType": "text",
            "dataType":    "text"
        }
    ]
}


class DogOwner(CustomObjectModel):
    CDO_NAME = "TEST_Dog_Owner"
    PARENT_ID = "497"
    FIELDS = ["DogBreed1", "StartOfOwnership1", "AgeAtStartOfOwnership1", "DogColor1", "DogName1"]
    ID_FIELD_MAP = {
        "6041": "DogBreed1",
        "6042": "StartOfOwnership1",
        "6043": "AgeAtStartOfOwnership1",
        "6044": "DogColor1",
        "6045": "DogName1"
    }
    META_FIELDS = ["type", "id", "createdAt", "createdBy", "depth", "description", "folderId", "name", "updatedAt",
                   "updatedBy"]
    DogBreed1 = None
    StartOfOwnership1 = None
    AgeAtStartOfOwnership1 = None
    DogColor1 = None
    DogName1 = None
