import numpy as np
import cvxpy as cvx
from datastruct.replace import replace
import scipy
from scipy.sparse import csr_matrix
def stabilize(Atilde,*args):
	iaa = 'low'
	inputopts={
			'iaa':iaa,
			'sign':0,
		}
	optionsNames = inputopts.keys()
	nArgs = len(args)
	if round(nArgs/2) !=nArgs/2:
		print('stabilize needs Name/Value pairs')
	pair=[]
	for i in range(len(args)):
		pair.append(args[i])
		inpName = pair[0].lower()
	if inpName in optionsNames:
		inputopts['%s'%inpName] = pair[1]

	if inputopts['iaa'] == 'low':
		Epsilon = -0.01
		Gamma = -10
	elif inputopts['iaa'] == 'high':
		Epsilon = -0.01
		Gamma = -100
		Atilde = 10*Atilde
	
	tol = 10**(-4)
	S = abs(Atilde)
	for i in range(S.shape[0]):
		for w in range(S.shape[1]):
			if S[w][i]<tol:
				S[w][i] = 1
			else:
				S[w][i] = 0

	n = Atilde.shape[0]
	I = np.eye(n)
	Psi = Gamma*0.9
	Shi = Epsilon*1.1
	
	if not inputopts['sign']:
		g = cvx.Variable()
		e = cvx.Variable()
		D = cvx.Variable((n,n))
		obj = cvx.Minimize(cvx.norm(D,'fro'))
		constraints = [ g*I <= ((Atilde+D)+(Atilde + D).T),
				((Atilde+D)+(Atilde + D).T) <= e*I,
				Gamma <= g,
				g <= Psi,
				Shi <= e,
				e <= Epsilon,
				replace(D,S) == 0,
				]
		ME = cvx.Problem(obj,constraints)
		ME.solve()
		
	elif inputopts['sign']:
		Neg = Atilde
		for i in range(Neg.shape[0]):
			for w in range(Neg.shape[1]):
				if Neg[w][i]<-tol:
					Neg[w][i] = 1
				else:
					Neg[w][i] = 0
		Pos = Atilde
		for i in range(Pos.shape[0]):
			for w in range(Pos.shape[1]):
				if Pos[w][i]>tol:
					Pos[w][i] = 1
				else:
					Pos[w][i] = 0
		g = cvx.Variable()
		e = cvx.Variable()
		D = cvx.Variable((n,n))
		obj = cvx.Minimize(cvx.norm(D,'fro'))
		Atmp = Atilde+D
		constraints = [ g*I <= ((Atilde+D)+(Atilde + D).T),
				((Atilde+D)+(Atilde + D).T) <= e*I,
				Gamma <= g,
				g <= Psi,
				Shi <= e,
				e <= Epsilon,
				replace(D,S) == 1,
				replace(Atmp,Pos) >= 0,
				replace(Atmp,Neg) <= 0,
				]
		ME = cvx.Problem(obj,constraints)
		ME.solve()
	C=D.value
	D=csr_matrix(C).todense()
	A = Atilde + D
	return A
