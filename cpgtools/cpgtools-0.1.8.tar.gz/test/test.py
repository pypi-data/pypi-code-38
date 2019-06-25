import sys,os
import numpy as np
from scipy import stats

def dt(x, mu, sig):
	'''
	The probability density of t distribution.
	'''
	return np.log(stats.t.pdf(x, loc = mu, scale = sig, df = len(x)))

#def dnorm(x, mu, sig):
#    return np.log(1/(sig * np.sqrt(2 * np.pi)) * np.exp(-(x - mu)**2 / (2 * sig**2)))

def dnorm(x, mu, sig):
	'''
	The probability density of normal distribution.
	'''
	return np.log(stats.norm.pdf(x, mu, sig))

def dexp(x, l):
	'''
	The probability density of exponential distribution.
	'''
	
	if x > 0:
		return np.log(stats.expon.pdf(x, scale = 1/l))
	else:
		return 0

def like(s1, s2, para):
	'''
	Estimate the likelihood of observing data (s1 and s2) given parameters `para`
	'''
	[mu1, sig1, mu2, sig2] = para
	return np.sum(dt(s1, mu1, sig1)) + np.sum(dt(s2, mu2, sig2))

def prior(s1, s2, para):
	'''
	Probability of mean and std.
	'''
	[mu1, sig1, mu2, sig2] = para
	pooled = np.append(s1, s2)
	prior_mean = pooled.mean()
	prior_std = 1000.0*pooled.std()
	
	return np.sum([dnorm(mu1, prior_mean, prior_std), dnorm(mu2, prior_mean, prior_std), dexp(sig1, 0.1), dexp(sig2, 0.1)])

def posterior(s1, s2, para):
	'''
	The log likelihood of posterior distribution
	Parameters
	'''
	[mu1, sig1, mu2, sig2] = para
	return like(s1, s2, [mu1, sig1, mu2, sig2]) + prior(s1, s2, [mu1, sig1, mu2, sig2])

def computeHDI(chain, interval = .95):
	'''
	Compute 95% highest density interval (HDI)
	'''
	# sort chain using the first axis which is the chain
	chain.sort()
	# how many samples did you generate?
	nSample = chain.size    
	# how many samples must go in the HDI?
	nSampleCred = int(np.ceil(nSample * interval))
	# number of intervals to be compared
	nCI = nSample - nSampleCred
	# width of every proposed interval
	width = np.array([chain[i+nSampleCred] - chain[i] for  i in range(nCI)])
	# index of lower bound of shortest interval (which is the HDI) 
	best  = width.argmin()
	# put it in a dictionary
	#HDI   = {'Lower': chain[best], 'Upper': chain[best + nSampleCred], 'Width': width.min()}
	HDI = [chain[best], chain[best + nSampleCred]]
	return HDI
    

def beta_bayes(results, id, s1, s2, seed, niter = 10000, nburn_in = 500):
	'''
	https://stats.stackexchange.com/questions/130389/bayesian-equivalent-of-two-sample-t-test
	'''
	np.random.seed(seed)
	
	mu1_samples = []	#means sampled by MCMC for s1
	mu2_samples = []	#means sampled by MCMC for s2
	
	# run MCMC (Metropolis-Hastings's sampling algorithm)
	# Initialization: mu1, sig1, mu2, sig2
	parameters = np.array([np.mean(s1), np.std(s1), np.mean(s2), np.std(s2)])	
	increment = (s1.std() + s2.std())/10	#5 times smaller than the average std
	for iteration in np.arange(1,niter):
		candidate = parameters + np.random.normal(0, increment, 4)
		if candidate[1] < 0 or candidate[3] < 0:
			continue
		ratio = np.exp(posterior(s1, s2, candidate) - posterior(s1, s2, parameters))
		if np.random.uniform() < ratio:
			parameters = candidate
		if iteration < nburn_in:
			continue
		mu1_samples.append(parameters[0])
		mu2_samples.append(parameters[2])
	
	# calculate estimated means			
	mu1_samples = np.array(mu1_samples)
	mu2_samples = np.array(mu2_samples)
	est_mu1 = mu1_samples.mean()	#estimated mu1
	est_mu2 = mu2_samples.mean()	#estimated mu2
	
	# calculate probability
	diff = (mu1_samples - mu2_samples)
	diff_median = np.median(diff)
	if diff_median < 0:
		prob = np.mean(diff < 0)
	elif diff_median > 0:
		prob = np.mean(diff > 0)
	
	# calculate HDI
	diff_HDI_h, diff_HDI_l = computeHDI(diff)
	
	# CpG_ID, mean of group1, mean of group2, diff of mean, 95%HDI_low, HDI_high, probability
	results.append( [id, est_mu1, est_mu2, est_mu1 - est_mu2, diff_HDI_h, diff_HDI_l,  prob])


def test():
	import time
	
	#group1
	g1=np.array([0.495232015,0.406789869,0.503893614,0.671983048,0.599390012,0.654400847,0.700565874,0.686020981,0.631342432,0.626395993])
	#group2
	g2=np.array([0.39637373,0.4941857,0.36698042,0.539142526,0.686674187,0.434451101,0.437110496,0.521170221,0.480415832,0.412073927])

	overall_time = 0.0
	results = []
	iter = 3
	for i in range(0,3):
		print ("running iteration %d" % (i+1), file=sys.stderr)
		start = time.time()
		beta_bayes(results,'test',g1, g2, 123, 5000, 500)
		#print (results)
		end = time.time()
		overall_time += (end - start)
	
	print("Average running time " + str(overall_time/iter), file=sys.stderr)
	print (results)
if __name__ == '__main__':
	test()