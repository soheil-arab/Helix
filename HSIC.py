# HSIC

import numpy as np
import matplotlib.pyplot as plt

# N = 40
# K = 7

# H = np.zeros((N,N))
# for i in range(N):
# 	for k in range(N):
# 		H[i,k] = 0. - (1./N)
# 	H[i,i] = 1. - (1./N)
# S = np.eye(K) * (1./((K*10000)))
# S[6,6] = (1./((K*20)))

# def rbf(x, y, S):
# 	z = x-y
# 	q = np.dot(z.T, np.dot(S,z))
# 	return np.exp(-q)

# def HSIC(X, Y, H, S):
	
# 	K,L, KH, LH = np.zeros((N,N)), np.zeros((N,N)), np.zeros((N,N)), np.zeros((N,N))

# 	for i in range(N):
# 		for k in range(N):
# 			K[i,k] = rbf(X[:,i], X[:,k], S)
# 			L[i,k] = rbf(Y[:,i], Y[:,k], S)

# 	KH = np.dot(K,H)
# 	LH = np.dot(L,H)

# 	return ((1. / (N*N)) * np.trace(np.dot(KH,LH))) / (np.sqrt((1. / (N*N)) * np.trace(np.dot(LH,LH))))

# def __HSIC__(KH, Y):
	
# 	N_ = KH.shape[0]

# 	K,L, LH = np.zeros((N,N)), np.zeros((N,N)), np.zeros((N,N))

# 	for i in range(N):
# 		for k in range(N):
# 			L[i,k] = rbf(Y[:,i], Y[:,k], S)

# 	LH = np.dot(L,H)

# 	return ((1. / (N*N)) * np.trace(np.dot(KH,LH))) / (np.sqrt((1. / (N*N)) * np.trace(np.dot(LH,LH))))


class HilbertSchmidt(object):

	N = 10
	K = 7
	H = np.zeros((N,N))
	S = np.eye(K) * (1./((K*10000)))
	S[6,6] = (1./((K*20)))

	cov = np.zeros((K,K))
	cov1 = np.zeros((K,K))
	cov2 = np.zeros((K,K))

	def __init__(self, N, _K=7, _Q=200):
		self.N = N
		self.H = np.zeros((self.N,self.N))
		for i in range(self.N):
			for k in range(self.N):
				self.H[i,k] = 0. - (1./self.N)
			self.H[i,i] = 1. - (1./self.N)
		if _Q != 200:
			self.S = np.eye(_K) * (1./((_K*_Q)))
		elif _K != 7:
			self.S = np.eye(_K) * (1./((_K*200.)))
		else:
			self.S = np.eye(_K) * (1./((_K*10000)))
			self.S[6,6] = (1./((_K*20)))

	def AR_get_KH(self, X):
		if np.sum(X) == 0:
			return 0.

		K = np.zeros((self.N,self.N))

		for i in range(self.N):
			for k in range(self.N):
				K[i,k] = self.rbf(X[:,i], X[:,k])

		return np.dot(K,self.H)

	def HSIC_AR(self, X, Y):
	
		# if np.sum(Y) == 0:
		# 	return 0.

		K, L, KH, LH = np.zeros((self.N,self.N)), np.zeros((self.N,self.N)), np.zeros((self.N,self.N)), np.zeros((self.N,self.N))

		for i in range(self.N):
			for k in range(self.N):
				K[i,k] = self.rbf(X[i], X[k], 0)
				L[i,k] = self.rbf(Y[i], Y[k], 0)

		# print K[:5,:5]
		# print L[:5,:5]

		KH = np.dot(K,self.H)		
		LH = np.dot(L,self.H)

		return ((1. / (self.N*self.N)) * np.trace(np.dot(KH,LH))) / np.sqrt(((1. / (self.N*self.N)) * np.trace(np.dot(KH,KH)))*((1. / (self.N*self.N)) * np.trace(np.dot(LH,LH))))

	def HSIC(self, X, Y, _K, _Q1, _Q2):
	
		print X.shape, Y.shape

		if np.sum(Y) == 0:
			return 0.

		K, L, KH, LH = np.zeros((self.N,self.N)), np.zeros((self.N,self.N)), np.zeros((self.N,self.N)), np.zeros((self.N,self.N))

		S1 = np.eye(_K) * (1./((_K*_Q1)))
		S2 = np.eye(_K) * (1./((_K*_Q2)))

		for i in range(self.N):
			for k in range(self.N):
				K[i,k] = self.rbf2(X[:,i], X[:,k], S1)
				L[i,k] = self.rbf2(Y[:,i], Y[:,k], S2)

		# print K[:5,:5]
		# print L[:5,:5]

		KH = np.dot(K,self.H)		
		LH = np.dot(L,self.H)

		# print KH[:5,:5]
		# print LH[:5,:5]

		# print self.H[:5,:5]
		# print S1[:5,:5]
		# print S2[:5,:5]

		# print np.trace(K), np.trace(L), self.N

		# print '--------------------------------------'

		a = ((1. / (self.N*self.N)) * np.trace(np.dot(KH,LH)))
		b = ((1. / (self.N*self.N)) * np.trace(np.dot(KH,LH))) / np.sqrt(((1. / (self.N*self.N)) * np.trace(np.dot(KH,KH))))
		c = ((1. / (self.N*self.N)) * np.trace(np.dot(KH,LH))) / np.sqrt(((1. / (self.N*self.N)) * np.trace(np.dot(LH,LH))))
		d = ((1. / (self.N*self.N)) * np.trace(np.dot(KH,LH))) / np.sqrt(((1. / (self.N*self.N)) * np.trace(np.dot(KH,KH)))*((1. / (self.N*self.N)) * np.trace(np.dot(LH,LH))))

		return a, b, c, d#((1. / (self.N*self.N)) * np.trace(np.dot(KH,LH))) / np.sqrt(((1. / (self.N*self.N)) * np.trace(np.dot(KH,KH)))*((1. / (self.N*self.N)) * np.trace(np.dot(LH,LH))))

	def __HSIC__(self, KH, Y):
	
		# if np.sum(Y) == 0:
		# 	return 0.

		L, LH = np.zeros((self.N,self.N)), np.zeros((self.N,self.N))

		for i in range(self.N):
			for k in range(self.N):
				L[i,k] = self.rbf(Y[:,i], Y[:,k])

		LH = np.dot(L,self.H)

		return ((1. / (self.N*self.N)) * np.trace(np.dot(KH,LH))) / np.sqrt(((1. / (self.N*self.N)) * np.trace(np.dot(KH,KH)))*((1. / (self.N*self.N)) * np.trace(np.dot(LH,LH))))

	def rbf(self, x, y, type=0):
		z = x-y
		# if type == 1:
		# 	q = np.dot(z.T, np.dot(self.cov1,z))
		# elif type == 2:
		# 	q = np.dot(z.T, np.dot(self.cov2,z))
		# else:
		q = np.dot(z.T, np.dot(self.cov,z))
		return np.exp(-q)

	def rbf2(self, x, y, _S):
		z = x-y
		q = np.dot(z.T, np.dot(_S,z))
		return np.exp(-q)

	def get_H(self):
		return np.copy(self.H)

	def get_N(self):
		return self.N

	def get_K(self):
		return self.K


	def set_covariance(self,data, type=0):

		# self.cov = np.cov(data)

		# if data.rows > 1:
		# 	mean = np.mean(data, 1)
	
		# 	for i in range(data.shape[1]):
		# 		data[:,i] -= mean

		# 	cov = np.dot(data, data.T) / (data.shape[1] - 1)
		# 	self.cov = np.linalg.inv(cov)

		# 	for i in range(data.shape[1]):
		# 		data[:,i] += mean
		# else:
		self.cov = np.cov(data)
		print self.cov


