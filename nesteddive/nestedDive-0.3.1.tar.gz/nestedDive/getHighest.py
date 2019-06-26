
# def sum(orignalData, layers):
#     allData = {}
#     for x in range(layers):
#         for name, data in orignalData.items():
#             if x == layers - 1:
#                 allData[name] = data

#             orignalData = data
    
#     print(allData)
#     for name, data in allData.items():
#         print(name)
#         print(data)     
                
                
#     return "werkt de return zoals gemoeten"
from collections import OrderedDict

def sumData(data, layers):
    allData = {}

    # Get the latest item
    for name, value in data.items():
        for name, value in value.items():
            for name, value in value.items():
                # I have the data here`
                wijkData = []

                for nameData, data in value.items():
                    wijkData.append(data)
                calculatedData = sum(wijkData)
                allData.update({name : calculatedData})
            pass
        pass

    print(allData)    
    # Sort the array/dict
    sorted_x = sorted(allData.items(), key=lambda x: x[1], reverse = True)
    # Change
    sorted_dict = dict(OrderedDict(sorted_x)) #Force to dictionary for mongodb

    print(sorted_dict)

testData = {
    "Charlois": {
            "Tarwewijk" : {
                "test": {
                    "Veiligheidsindex" : 73,
                    "Veiligheidsindex -subjectief" : 100
                }
            },
            "Carnisse" : {
                "32": {
                    "Veiligheidsindex" : 50,
                    "Veiligheidsindex -subjectief" : 102
                }
            },
            "ss" : {
                "32": {
                    "Veiligheidsindex" : 60,
                    "Veiligheidsindex -subjectief" : 60
                }
            }
    },
    "testing": {
            "wijk1" : {
                "123123": {
                    "Veiligheidsindex" : 73,
                    "Veiligheidsindex -subjectief" : 50
                }
            },
            "wijk2" : {
                "123123123": {
                    "Veiligheidsindex" : 50,
                    "Veiligheidsindex -subjectief" : 100
                }
           },
            "ss" : {
                "1212": {
                    "Veiligheidsindex" : 60,
                    "Veiligheidsindex -subjectief" : 100
                }
            }
    }
}

