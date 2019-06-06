from numpy import linalg as LA
def optimalPstructure(A,nm,sp):
	n = nm[0]
	m = nm[1]
	G = -LA.pinv(A)
	UA,SA1,VA = np.linalg.svd(np.asarray(M.A))
	VA = VA.transpose()
	SA = np.zeros((SA1.shape[0],SA1.shape[0]))
	for i in range(len(SA)):
		SA[i][i]=SA1[i]
	G = -LA.pinv(A)
	
'''def candidateP
n = nm(1)
m = nm(2)
R = GramSchmidtOrth(-1+2*rand(max([n m]))); % Random R as a start
R = R(:,1:n)';
P = UA*SA*R; % P based on economy size svd
P = round(1000.*P)./1000;

'''
'''candidateP = np.array([])
for i in range(0,m-1):
'''
'''
    fit = glmnet(G,Y(:,i));
    beta = fit.beta;    
    nPert = sum(logical(beta));

    j = max(find(nPert == sp));
    if isempty(j)
        j = max(find(nPert == sp-1));
    end
    if isempty(j)
        j = max(find(nPert == sp+2));
    end
    
    jPert = find(beta(:,j));
    
    candidateP(:,i) = beta(:,j);
    % candidateP(jPert,i) = beta(jPert,end);
    
end

import numpy as np
def P(candidateP,Y):
    def optimalPstructure(A,nm,np):
        n=nm(1)
        m=nm(2)        
        G = -np.linalg.pinv(A)
        UA,SA,VA = np.linalg.svd(A)
        G = -np.linalg.pinv(A)
        
        
        
        
        limitSVY = 0.33
        level1 = np.logspace(-1,-3,base=10,num=3)
        level = np.append(level1,level1[2])
        tol = 10**-4
        keepOneElementOnEachColumn = True

        Y=G*P
        
candidateP = np.array([])
for i in range(0,m-1):
'''
