import numpy as np
def smallworld(N,k,p,undirected,*args):
	if len(args) == 0:
		d = 0.5
	else:
		d = args[0]
	A = np.zeros((N,N))
	#s=??
	for i in range(N):
		for j in range(i+1,i+k/2):
			t = j
			if t > N:
				t = t-N
			A[i][t] = 1
			A[t][i] = 1
			r = np.random.uniform(0,1)
			if p > r:
				notselection = mod([i-k/2-1:i+k/2],N)+1
				selection = [:N]
				selection = selection !=notselection
				#selection = find??
				l = np.random.randint(len(selection),size=1)
				sel = selection[l]
				while sel == t:
					l = np.random.randint(len(selection),size=1)
					sel = selection[l]
				A[i][t] = 0
				A[t][i] = 0
				if undirected:
					A[i][l] = 1
					A[l][i] = 1
				else:
					r = np.random.uniform(0,1)
					if d > r:
						A[i][l] = 1
						A[l][i] = 1
					else:
						A[i][l] = 1
						notselection = mod([i-k/2-1:i+k/2],N)+1
						selection = [:N]
						selection = selection !=notselection
						#selection = find??
						h = np.random.randint(len(selection),size=1)
						sel = selection[h]
						A[sel][i] =1
