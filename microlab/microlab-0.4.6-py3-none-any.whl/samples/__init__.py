import numpy



# Time
a = [0.0, 1.0, 2.0, 3.0, 1.0, -1.0, -2.0, -3.0, -2.0, -1.0, 1.0]
# Value
b = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

# Points
x1 = [1.,  2.75, 4.5, 6.25, 8.]
# x1 = numpy.linspace(1, 8, num=5000)

y1 = [-5., -1.75, 1.5,  4.75, 8.]
# y1 = numpy.linspace(-5, 8, num=5000)

x2 = [0., 1, 3, 4.8, 6.5 ]
y2 = [-5., -2.5, 0., 2.5,  5.]


# 1 List
List_a = list(a)
List_b = list(b)

# Tuple
Tuple_a = tuple(a)
Tuple_b = tuple(b)

# Numpy Array
npArray_a = numpy.array(a)
npArray_b = numpy.array(b)


# Datasets
dataset_list = list([List_a, List_b])
dataset_tuple = tuple([Tuple_a, Tuple_b])
dataset_npArray = numpy.array([npArray_a, npArray_b])
dataset_1 = [x1, y1]
dataset_2 = [x2, y2]


def show():
    print('~ SAMPLE DATA')
    print('\na      :{}'.format(a))
    print('b      :{}'.format(b))
    print('\nx1     :{}'.format(x1))
    print('y1     :{}'.format(y1))
    print('\nx2     :{}'.format(x2))
    print('y2     :{}'.format(y2))
