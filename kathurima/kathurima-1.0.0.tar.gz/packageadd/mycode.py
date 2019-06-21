def fibonacci(n):
	if n <=1:
		return 1
	else:
		return fibonacci(n -2) + fibonacci(n-1)

#With pytest, the below block of code shows to have passed the test which is not true since its not tested in test_app.py.
#With coverage, you are able to detect that the function has not been covered yet
def factorial(n):
	if n == 0:
		return 1
	else:
		return n * factorial(n - 1)

# #Below commented code is used to emphasize on code coverage
# # fibonacci(1)
# # fibonacci(10)

# # factorial(0)
# # factorial(29)

