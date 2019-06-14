from decimal import Decimal


def numeric2str_convertor(arg):
    v = str(arg)
    if v.find('E'):
        v = '{:.8f}'.format(Decimal(v))
    nums = v.split('.')
    if int(nums[1]) == 0:
        result = nums[0]
    else:
        num = str(int(nums[1][::-1]))
        result = '{}.{}'.format(nums[0], num[::-1])
    return result
