
'''
    @author: Yusril Rapsanjani
    @version: 1.0.0
'''
class Slicer(object):

    @staticmethod
    def cut(list_data, amount):
        slices_list, temp_slices = [], []
        for x in range(1, len(list_data)+1):
            temp_slices.append(list_data[x-1])
            if x % amount == 0 or x == len(list_data):
                slices_list.append(temp_slices)
                temp_slices = []
        return slices_list