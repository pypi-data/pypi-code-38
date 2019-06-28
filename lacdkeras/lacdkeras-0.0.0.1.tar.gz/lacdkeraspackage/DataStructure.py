class DataStructure():

    def __init__(self,csv_name):
        self.csv_name = csv_name

    def Data_organization(self):
        fp = open(self.csv_name,'r',encoding="utf-8")
        All_Lines = fp.readlines()
        Data_Input = []
        Data_Level = []
        for Line in All_Lines:
            Data_Split = Line.replace('\n','').split(',')
            Data_Level.append(Data_Split[0]) 
            Data_Input_stack = []
            for everyInput in range(1,len(Data_Split),1):
                Data_Input_stack.append(everyInput)
            Data_Input.append(Data_Input_stack)

        self.Data_Input = Data_Input
        self.Data_Level = Data_Level

    def show(self):
        print('-顯示數據集-')
        print('以下顯示的為我們所輸入的數據集')
        print('類別:拿來預測後最後的結果為何(EX:是否會下雨)')
        print('(1):要拿來預測的變項之一(EX:溫度)')
        print('(2):要拿來預測的變項之一(EX:濕度)')
        print('(3):要拿來預測的變項之一(EX:雲量)')
        print('PS.僅會顯示前10項資訊')
        print('\n\n============================================')
        print('類別\t',end = '')
        for index in range(0,len(self.Data_Input[0]),1):
            print('('+str(index+1)+')\t',end = '')
        print()

        if(len(self.Data_Level)>10):
            for Level_Index in range(0,10,1):
                print(self.Data_Level[Level_Index]+'\t',end = '')
                for Input_Index in range(0,len(self.Data_Input[Level_Index]),1):
                    print(str(self.Data_Input[Level_Index][Input_Index])+'\t',end = '')
                print()
        else:
            for Level_Index in range(0,len(self.Data_Input[Level_Index]),1):
                print(self.Data_Level[Level_Index]+'\t',end = '')
                for Input_Index in range(0,len(self.Data_Input[Level_Index]),1):
                    print(self.Data_Input[Level_Index][Input_Index]+'\t',end = '')
                print()
