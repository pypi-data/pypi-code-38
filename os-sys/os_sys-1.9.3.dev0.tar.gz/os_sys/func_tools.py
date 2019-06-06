name = __name__ == '__main__'
if name:
    number = int(input())
    arr = []

    for num in range(0, number):
        num = int(input())
        arr.append(num)


def average(_list):
    return round(sum(_list)/len(_list))


def mid(_list):
    _list.sort()

    mid = (len(_list)//2)

    return _list[mid]


def frequency(_list):
    freq = {}

    for num in _list:
        if num not in freq:
            freq[num] = 1
        else:
            freq[num] += 1

    max_value = max(freq.values())
    max_value_array = []

    for key, value in freq.items():
        if value == max_value:
            max_value_array.append(key)

    max_value_array.sort()

    min_key = min(max_value_array)
    max_key = max(max_value_array)

    for num in max_value_array:
        if num > min_key or max_key == min_key:
            return num

def scope(_list):
    return max(_list) - min(_list)
if name:
    print(average(arr))
    print(mid(arr))
    print(frequency(arr))
    print(scope(arr))
