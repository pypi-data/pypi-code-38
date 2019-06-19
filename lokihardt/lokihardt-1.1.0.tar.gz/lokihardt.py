"""这是wester.py模块，提供了一个print_lol函数，这个函数的作用是打印列表，其中有可能包含也可以不包含嵌套列表"""

"""print_lol是我创建的一个函数，这个函数去一个位置参数名为“the_list“,这可以是python中任意列表，也可以是嵌套列表的列表
，所制定列表中的每个数据项会递归地输出到屏幕上，每个数据各占一行"""
def print_lol(the_list):
	for num in the_list:
		if isinstance(num,list):
			print_lol(num)
		else:
			print(num)





