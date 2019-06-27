import numpy as np
import scipy.special
import scipy.linalg
from matplotlib import pyplot

from swutil.plots import plot_convergence
from swutil.np_tools import integral, toeplitz_multiplication, MCSlicer
from swutil.time import Timer

def black_scholes(times,r,sigma,S0,d,M,dW=None, random=np.random):
    '''
    Return M Euler-Maruyama sample paths with N time steps of S_t, where 
        dS_t = S_t*r*dt+S_t*sigma*dW_t
        S(0)=S0
    
    :rtype: M x N x d array
    '''
    N=len(times)
    times = times.flatten()
    p0 = np.log(S0)
    if dW is None:
        dW=np.sqrt(times[1:]-times[:-1])[None,:,None]*random.normal(size=(M,N-1,d))
    if np.squeeze(sigma).ndim<=1:
        dF = sigma*dW
        ito_correction = np.squeeze(sigma**2/2)
    else:
        dF = np.einsum('ij,...j',sigma,dW)
        ito_correction = np.sum(sigma**2,1)/2
    drift  = (r-ito_correction)*times[None,:,None]
    diffusion = integral(dF=dF,axis=1,cumulative = True)
    return np.exp(p0 + drift + diffusion)

def heston(times,mu,rho,kappa,theta,xi,S0,nu0,d,M,nu_1d=True, random=np.random):
    '''
    Return M Euler-Maruyama sample paths with N time steps of (S_t,v_t), where
        (S_t,v_t) follows the Heston model of mathematical finance. 
    Currently requires times to be uniform

    :rtype: M x N x d array
    '''
    d_nu = 1 if nu_1d else d
    N = len(times)
    nu = np.zeros((M,N,d_nu))
    S = np.zeros((M,N,d))
    nu[:,0,:] = nu0
    S[:,0,:] = S0
    if 2*kappa*theta<=xi**2:
        raise ValueError('Feller condition not satisfied')
    test = np.std(np.diff(times.flatten())) 
    if test>1e-12:
        raise ValueError
    dt = times[1]-times[0]
    if d == 1:
        if np.array(rho).size ==1:
            rho = np.array([[1,rho],[rho,1]])
    chol = np.linalg.cholesky(rho)
    dW = np.sqrt(dt)*np.einsum('ij,...j',chol,random.normal(size=(M,N-1,d+d_nu)))
    for i in range(1,N):
        nu[:,i,:] = np.abs(nu[:,i-1,:] + kappa*(theta-nu[:,i-1,:])*dt+xi*np.sqrt(nu[:,i-1,:])*dW[:,i-1,d:])
    S = S0*np.exp(integral(np.sqrt(nu),dF = dW[:,:,:d],axis=1,cumulative = True)+integral(mu - 0.5*nu,F = times,axis=1,trapez=False,cumulative = True))
    return np.concatenate((S,nu),axis=-1)


def fBrown(H,T,N,M,dW = None,cholesky = False, random=np.random):
    '''
    Sample fractional Brownian motion with differentiability index H 
    on interval [0,T] (H=1/2 yields standard Brownian motion)
    
    :param H: Differentiability, larger than 0
    :param T: Final time
    :param N: Number of time steps
    :param M: Number of samples
    :param dW: Driving noise, optional
    '''
    alpha = 0.5-H
    times = np.linspace(0, T, N)
    dt = T/(N-1)
    if cholesky:
        if dW is not None:
            raise ValueError('Cannot use provided dW if Cholesky method is used')
        times = times[1:]
        tdt = times/np.reshape(times,(-1,1))
        tdt[np.tril_indices(N-1,-1)]=0
        cov = np.reshape(times,(-1,1))**(1-2*alpha)*(1/(1-alpha))*(tdt-1)**(-alpha)*scipy.special.hyp2f1(alpha,1-alpha,2-alpha,1/(1-tdt))
        cov[0,:] = 0
        np.fill_diagonal(cov,times**(1-2*alpha)/(1-2*alpha))
        cov[np.tril_indices(N-1,-1)] = cov.T[np.tril_indices(N-1,-1)]
        L = scipy.linalg.cholesky(cov)
        return np.concatenate((np.zeros((1,M)),L.T@random.normal(size=(N-1,M))))
    if dW is None:
        dW = np.sqrt(dt)*random.normal(size=(N-1,M))
    if H == 0.5:
        return integral(dF = dW,cumulative = True)  
    a = 1/dt/(1-alpha)*((T-times[N-2::-1])**(1-alpha)-(T-times[:0:-1])**(1-alpha))#a is array that is convolved with dW. Values arise from conditioning integral pieces on dW 
    out = toeplitz_multiplication(a,np.zeros_like(a),dW[::-1])[::-1]
    out -=a[0]*dW#Redo last bit of defining integral with exact simulation below
    cov = np.array([[ dt**(1-2*alpha)/(1-2*alpha),dt**(1-alpha)/(1-alpha)],[dt**(1-alpha)/(1-alpha),dt]])
    var = cov[0,0]-cov[0,1]**2/cov[1,1]
    out += cov[0,1]/cov[1,1]*dW #Conditional mean
    out += np.sqrt(var)*random.normal(size = (N-1,M))#Conditional variance
    out = np.concatenate((np.zeros((1,M)),out))
    return out

def r_bergomi(H, T, eta, xi, rho, S0, r, N, M, dW=None, dW_orth=None, cholesky=False, return_v=False, random=np.random):
    '''
    Return M Euler-Maruyama sample paths with N time steps of (S_t,v_t), where
        (S_t,v_t) follows the rBergomi model of mathematical finance

    :rtype: M x N x d array
    '''
    times = np.linspace(0, T, N)
    dt = T/(N-1)
    times = np.reshape(times,(-1,1))
    if dW is None:
        dW = np.sqrt(dt)*random.normal(size=(N-1,M))
    if dW_orth is None:
        dW_orth = np.sqrt(dt)*random.normal(size=(N-1,M))
    dZ = rho*dW+np.sqrt(1-rho**2)*dW_orth
    Y = eta*np.sqrt(2*H)*fBrown(H,T,N,M,dW =dW,cholesky = cholesky)
    v = xi*np.exp(Y-0.5*(eta**2)*times**(2*H))
    S = S0*np.exp(integral(np.sqrt(v),dF = dZ,axis=0,cumulative = True)+integral(r - 0.5*v,F = times,axis=0,trapez=False,cumulative = True))
    if return_v:
        return np.array([S,v]).T
    else:
        return np.array([S]).T
    
def rThreeHalves(H,T,eta,xi,rho,alpha,S0,r,N,M,dW=None,dW_orth=None,cholesky = False,return_v=False, random=np.random):
    times = np.linspace(0, T, N)
    dt = T/(N-1)
    times = np.reshape(times,(-1,1))
    if dW is None:
        dW = np.sqrt(dt)*random.normal(size=(N-1,M))
    if dW_orth is None:
        dW_orth = np.sqrt(dt)*random.normal(size=(N-1,M))
    dZ = rho*dW+np.sqrt(1-rho**2)*dW_orth
    Y = eta*np.sqrt(2*H)*fBrown(H,T,N,M,dW =dW,cholesky = cholesky)
    v = _v_rThreeHalves_direct(Y,times,alpha,xi,xi,eta,H)
    S = S0*np.exp(integral(np.sqrt(v),dF = dZ,axis=0,cumulative = True)+integral(r - 0.5*v,F = times,axis=0,trapez=False,cumulative = True))
    print(np.mean(S[-1]),np.std(S[-1]))
    if return_v:
        return np.array([S,v])
    else:
        return np.array([S])
    
def _v_rThreeHalves(Y,times,alpha,vstar,xi,eta,H):
    v = 1/xi*np.ones_like(Y)
    for i in range(1,len(times)):
        dt = times[i]-times[i-1]
        dY=Y[i]-Y[i-1]
        b_geom = 1/np.sqrt(v[i-1])
        #vtilde = v[i-1]*np.exp(b_geom*dY-0.5*(eta**2*b_geom**2)*dt**(2*H))
        vtilde = v[i-1]+np.sqrt(v[i-1])*dY
        v[i] = 1/vstar+(vtilde-1/vstar)*np.exp(-alpha*dt)
        v[i] = np.abs(v[i])
    pyplot.plot(1/v[:,0])
    pyplot.show()
    print(np.mean(1/v))
    return 1/v

def _v_rThreeHalves_direct(Y,times,alpha,vstar,xi,eta,H):
    v = xi*np.ones_like(Y)
    for i in range(1,len(times)):
        dt = times[i]-times[i-1]
        dY=Y[i]-Y[i-1]
        a_geom = -alpha*(v[i-1]-vstar)
        b_geom = np.sqrt(v[i-1])
        #vtilde = v[i-1]*np.exp(a_geom*dt)*np.exp(b_geom*dY-0.5*(eta**2*b_geom**2)*dt**(2*H))
        vtilde = v[i-1]+a_geom*v[i-1]+b_geom*v[i-1]*dY
        v[i] = np.abs(vtilde)
    pyplot.plot(v[:,0])
    pyplot.show()
    print(np.mean(v))
    return v
    
