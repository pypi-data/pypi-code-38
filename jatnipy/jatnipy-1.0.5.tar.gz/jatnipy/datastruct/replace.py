def replace(A,B):
	for i in range(A.shape[0]):
		for j in range(A.shape[1]):
			if B[j][i] == 1:
				return A[j][i]
