import numpy as np
import cv2
import util
import model as ARModel
import HSIC

model_p_file = '/Users/jordancampbell/Desktop/Helix/code/pyNeptune/dev/model_positive.npy'
model_n_file = '/Users/jordancampbell/Desktop/Helix/code/pyNeptune/dev/model_negative.npy'

model_p_file_training = '/Users/jordancampbell/Desktop/Helix/code/pyNeptune/dev/model_positive_train.npy'
model_n_file_training = '/Users/jordancampbell/Desktop/Helix/code/pyNeptune/dev/model_negative_train.npy'

# model_p_file = model_p_file_training

class joint(object):
	pt 		= np.zeros(4)
	pt_H 	= np.zeros(3)
	pt_2D 	= np.zeros(2)
	R 		= np.eye(4)
	T 		= np.eye(4)

	radius = [40,60,90]
	points = []

	def __init__(self, _N=20):

		self.N = _N

		self.pt[3] = 1.

		self.points = [np.eye(4) for i in range(self.N)]

		rings = 3

		ang = 6.28 / float(self.N/float(rings))
		idx = 0
		for i in range(self.N/rings):

			for k in range(rings):
				self.points[idx+k][0,3] = self.radius[k] * np.cos(i*(ang+(k*0.1)))
				self.points[idx+k][1,3] = self.radius[k] * np.sin(i*(ang+(k*0.1)))

			idx += rings

	def copy(self, src):
		self.N = src.get_num_points()
		self.radius = src.get_radius()
		self.pt = src.get_pt()
		self.pt_H = src.get_pt_H()
		self.pt_2D = src.get_pt_2D()
		self.R = src.get_R()
		self.T = src.get_T()
		points = src.get_points()
		for i in range(self.N):
				self.points[i] = np.copy(points[i])

	def get_radius(self):
		return self.radius
	def get_pt(self):
		return np.copy(self.pt)
	def get_pt_H(self):
		return np.copy(self.pt_H)
	def get_pt_2D(self):
		return np.copy(self.pt_2D)
	def get_R(self):
		return np.copy(self.R)
	def get_T(self):
		return np.copy(self.T)
	def get_points(self):
		return self.points
	def get_num_points(self):
		return self.N

	def set_pt(self, src):
		self.pt = np.copy(src)
	def set_pt_H(self, src):
		self.pt_H = np.copy(src)
	def set_pt_2D(self, src):
		self.pt_2D = np.copy(src)
	def set_R(self, src):
		self.R = np.copy(src)
	def set_T(self, src):
		self.T = np.copy(src)

class articulated_model(object):

	# general parameters
	num_legs = 4
	num_joints = 5

	legs = [[]]

	# can be changed to an array for variable lengths later
	segment_length = 120.#68.

	M = np.eye(3)

	def copy(self, src):
		for l in range(self.num_legs):
			for j in range(self.num_joints):
				self.legs[l][j].copy(src.get_legs()[l][j])
	
	def __init__(self, shape, _N=40, _write=False):

		self.N = _N

		# initialise camera matrix
		self.M[0,2] = shape[1]/2.
		self.M[1,2] = shape[0]/2.
		self.M[0,0] = 200.
		self.M[1,1] = 200.

		# initialise the legs
		# self.legs = [[] for i in range(self.num_legs)]
		self.legs = [[joint(_N) for i in range(self.num_joints)] for i in range(self.num_legs)]

		data = 3

		if data == 1:
			for i in range(self.num_legs):
				self.tz(i,1, 1000.)
				self.tx(i,1,-250.)
				self.ty(i,1,250.)
			
				for k in range(2, self.num_joints):
					self.tx(i, k, self.segment_length)	
					self.tx(i, k, self.segment_length)

			# self.rz(0,1, - 0.8)
			self.rz(0,1, - 0.9)
			self.rz(0,2, - 0.4)
			self.rz(0,3, - 0.2)
		
			self.rz(1,1, - 2.06)
			self.rz(1,2, 0.2)
			self.rz(1,3, 0.05)

		elif data == 2:
			for i in range(self.num_legs):
				self.tz(i,1, 1000.)
				self.tx(i,1,-60.)
				self.ty(i,1,380.)
			
				for k in range(2, self.num_joints):
					self.tx(i, k, self.segment_length)	
					self.tx(i, k, self.segment_length)

			self.rz(-1,1,0.14)

			# self.rz(0,1, - 0.8)
			self.rz(0,1, - 0.9)
			self.rz(0,2, - 0.4)
			self.rz(0,3, - 0.2)
		
			self.rz(1,1, - 2.06)
			self.rz(1,2, 0.2)
			self.rz(1,3, 0.1)

		elif data == 3:
			for i in range(self.num_legs):
				self.tz(i,1, 1000.)
				self.tx(i,1,-400.)
				self.ty(i,1,300.)
			
				for k in range(2, self.num_joints):
					self.tx(i, k, self.segment_length)	
					self.tx(i, k, self.segment_length)

			# self.rz(-1,1,0.14)

			self.rz(0,1, - 0.6)
			self.rz(0,2, - 0.4)
			self.rz(0,3, - 0.3)
		
			# 3rd finger
			self.rz(2,1,-1.2)
			self.rz(2,2,-.3)

			# 4th finger
			self.rz(3,1,-2.)
			self.rz(3,1,0.2)

			# 5th finger
			self.rz(1,1, - 2.7)
			self.rz(1,2, 0.8)
			self.rz(1,3, -0.06)

		else:
			print 'error'
			while(True):
				pass

		if _write:

			output_file = '/Users/jordancampbell/Desktop/Helix/code/pyNeptune/dev/model.txt'
			for i in range(self.num_legs):
				for k in range(self.num_joints):
					for j in range(self.N):
						print self.legs[i][k].get_points()[j]

	def get_legs(self):
		return self.legs

	def get_partial_points(self, _set):
		input = []

		for p in range(self.num_joints-1, -1, -1):
				
			tr = np.eye(4)										
				
			for k in range(1, p+1):
				tr = np.dot(tr, np.dot(self.legs[_set][k].get_T(), self.legs[_set][k].get_R())) 
				
			self.legs[_set][p].set_pt(np.dot(tr, self.legs[_set][0].get_pt()))
				
			if p <= self.num_joints-1:
				points = self.legs[_set][p].get_points()
				for n in range(self.legs[0][1].get_num_points()):
					pt = np.dot(tr, np.dot( points[n] ,self.legs[_set][0].get_pt()))
					if p > 0:
						input.append(pt)
				
			else:
				if p > 0:
					input.append(self.legs[_set][p].get_pt())

		proj = np.eye(3,4)
		R = np.eye(4)
		T = np.eye(4)
		T[2,3] = 50

		output = []

		for i in range(len(input)):
			H = np.dot(self.M, np.dot(np.eye(3,4), np.dot(T, np.dot(R, input[i]))))
			output.append(H[:2] / H[2])

		return output

	def get_points(self, all_points=False):
		input = []

		for l in range(self.num_legs):
			for p in range(self.num_joints-1, -1, -1):
				
				tr = np.eye(4)										
				
				for k in range(1, p+1):
					tr = np.dot(tr, np.dot(self.legs[l][k].get_T(), self.legs[l][k].get_R())) 
				
				self.legs[l][p].set_pt(np.dot(tr, self.legs[l][0].get_pt()))
				
				if all_points:
					if p <= self.num_joints-1:
						points = self.legs[l][p].get_points()
						for n in range(self.legs[0][1].get_num_points()):
							pt = np.dot(tr, np.dot( points[n] ,self.legs[l][0].get_pt()))
							if p > 0:
								input.append(pt)
				
				else:
					if p > 0:
						input.append(self.legs[l][p].get_pt())

		proj = np.eye(3,4)
		R = np.eye(4)
		T = np.eye(4)
		T[2,3] = 50

		output = []

		for i in range(len(input)):
			H = np.dot(self.M, np.dot(np.eye(3,4), np.dot(T, np.dot(R, input[i]))))
			output.append(H[:2] / H[2])

		return output

	def tx(self, _L, _J, _t):
		T_ = np.eye(4)
		T_[0,3] = _t
		if _L == -1:
			for l in range(self.num_legs):
				self.legs[l][_J].set_T(np.dot(T_, self.legs[l][_J].get_T()))
		else:
			self.legs[_L][_J].set_T(np.dot(T_, self.legs[_L][_J].get_T()))

	def ty(self, _L, _J, _t):
		T_ = np.eye(4)
		T_[1,3] = _t
		if _L == -1:
			for l in range(self.num_legs):
				self.legs[l][_J].set_T(np.dot(T_, self.legs[l][_J].get_T()))
		else:
			self.legs[_L][_J].set_T(np.dot(T_, self.legs[_L][_J].get_T()))

	def tz(self, _L, _J, _t):
		T_ = np.eye(4)
		T_[2,3] = _t
		if _L == -1:
			for l in range(self.num_legs):
				self.legs[l][_J].set_T(np.dot(T_, self.legs[l][_J].get_T()))
		else:
			self.legs[_L][_J].set_T(np.dot(T_, self.legs[_L][_J].get_T()))

	def rx(self, _L, _J, _r):
		R_ = np.eye(4)
		R_[1,1] = np.cos(_r)
		R_[2,2] = np.cos(_r)
		R_[1,2] = - np.sin(_r)
		R_[2,1] = np.sin(_r)
		if _L == -1:
			for l in range(self.num_legs):
				self.legs[l][_J].set_R(np.dot(R_, self.legs[l][_J].get_R()))
		else:
			self.legs[_L][_J].set_R(np.dot(R_, self.legs[_L][_J].get_R()))

	def ry(self, _L, _J, _r):
		R_ = np.eye(4)
		R_[0,0] = np.cos(_r)
		R_[2,2] = np.cos(_r)
		R_[0,2] = np.sin(_r)
		R_[2,0] = - np.sin(_r)
		if _L == -1:
			for l in range(self.num_legs):
				self.legs[l][_J].set_R(np.dot(R_, self.legs[l][_J].get_R()))
		else:
			self.legs[_L][_J].set_R(np.dot(R_, self.legs[_L][_J].get_R()))

	def rz(self, _L, _J, _r):
		R_ = np.eye(4)
		R_[0,0] = np.cos(_r)
		R_[1,1] = np.cos(_r)
		R_[0,1] = - np.sin(_r)
		R_[1,0] = np.sin(_r)
		if _L == -1:
			for l in range(self.num_legs):
				self.legs[l][_J].set_R(np.dot(R_, self.legs[l][_J].get_R()))
		else:
			self.legs[_L][_J].set_R(np.dot(R_, self.legs[_L][_J].get_R()))


def wiggle(model, w, inverse=False):

	# move the model into the given pose
	
	if inverse:
		w = [w[i] * -1 for i in range(len(w))]

	# global translation
	model.tx(-1,1,w[0])
	model.ty(-1,1,w[1])

	# global rotation
	model.rz(-1,1,w[2])

	# leg rotation
	model.rz(0,1,w[3])
	model.rz(1,1,w[4])
	model.rz(2,1,w[5])
	model.rz(3,1,w[6])

	# leg / j1 rotation
	model.rz(0,2,w[7])
	model.rz(1,2,w[8])
	model.rz(2,2,w[9])
	model.rz(3,2,w[10])

	# leg / j2 rotation
	model.rz(0,3,w[11])
	model.rz(1,3,w[12])
	model.rz(2,3,w[13])
	model.rz(3,3,w[14])

	return model

def get_KH(model, state, params, HS, _motion=False):
	model = wiggle(model, state)
	points = model.get_points(all_points=True)
	
	if _motion:
		KH = util.descriptors(params, points, points, HS, _train=True, _motion=True)
	else:
		KH = util.descriptors(params, points, points, HS)		
	
	model = wiggle(model, state, inverse=True)
	return KH

def load_model():
	return np.load(model_p_file), np.load(model_n_file)

def train_scratch(_dims, model, state, motion=False, update=False):

	params = util.parameters()
	image, hsv, dt, flow = params.get_frames()

	model = wiggle(model, state)
	
	points = model.get_points(all_points=True)

	if motion:
		HS = HSIC.HilbertSchmidt(len(points), 9)
	else:
		HS = HSIC.HilbertSchmidt(len(points), 7)

	pos = [0. for i in range(_dims)]

	P_KH = np.zeros((HS.get_N(), HS.get_N()))
	N_KH = np.zeros((HS.get_N(), HS.get_N()))

	if update:
		negative_bound = 12
		positive_bound = 6
	else:
		negative_bound = 100
		positive_bound = 20

	# --------- train --------- #
	k = 2
	for i in range(-negative_bound, negative_bound):

		if i % 10 == 0:
			print i, '% complete (training phase 1)'

		if i < -positive_bound or i > positive_bound:
			pos = [0. for idx in range(_dims)]
			pos[2] = i * 0.005
			N_KH += get_KH(model, pos, params, HS, _motion=motion)
		else:
			for k in range(_dims):
				pos = [0. for idx in range(_dims)]
				if k == 0 or k == 1:
					pos[k] = i * 2.
				else:
					pos[k] = i * 0.005
				P_KH += get_KH(model, pos, params, HS, _motion=motion)

	for i in range(100):

		if i % 10 == 0:
			print i, '% complete (training phase 2)'

		pos = ((np.random.rand(_dims) * 0.125) - 0.0625)
		P_KH += get_KH(model, pos, params, HS, _motion=motion)

		pos = 2. + ((np.random.rand(_dims) * 2.0) - 1.)
		N_KH += get_KH(model, pos, params, HS, _motion=motion)
	# ------------------------------------- #

	if not update:
		np.save(model_p_file, P_KH)
		np.save(model_n_file, N_KH)
		return 

	model = wiggle(model, state, inverse=True)

	return P_KH, N_KH

def train(_dims, model, state, motion=False, update=False):

	params = util.parameters()
	image, hsv, dt, flow = params.get_frames()
	model = wiggle(model, state)
	points = model.get_points(all_points=True)
	if motion:
		HS = HSIC.HilbertSchmidt(len(points), 9)
	else:
		HS = HSIC.HilbertSchmidt(len(points), 7)
	pos = [0. for i in range(_dims)]
	P_KH = np.zeros((HS.get_N(), HS.get_N()))

	if update:
		bound = 4
	else:
		bound = 40

	for i in range(bound):

		if i % 2 == 0:
			print i, 'of', bound

		__pos = ((np.random.rand(_dims) * 0.125) - 0.0625)

		for k in range(2, 7):
			for j in range(-6,6):
				pos = np.copy(__pos)
				pos[k] += j * 0.005
				P_KH += get_KH(model, pos, params, HS, _motion=motion)
	# ------------------------------------- #

	if not update:
		np.save(model_p_file, P_KH)
		return 

	model = wiggle(model, state, inverse=True)

	np.save(model_p_file_training, P_KH)

	return P_KH

def compute_energy(state, model, params, P_KH, N_KH, HS, display=False):
	image, hsv, dt, flow = params.get_frames()

	model = wiggle(model, state)
	
	if display:
		## draw the model for testing
		points = model.get_points()
		for i in range(len(points)):
			cv2.circle(image,(int(points[i][0]),int(points[i][1])),2,(0,0,255))
		for i in range(len(points)-1):
			if i != 3 and i != 7 and i != 11:
				cv2.line(image,(int(points[i][0]),int(points[i][1])),(int(points[i+1][0]),int(points[i+1][1])),(255,0,0))

		__dir, __counter, __current_frame, __suffix = params.get_filename() 
		cv2.imwrite(__dir + str(__counter) + '__' + str(__current_frame) + __suffix, image)

		cv2.imshow("Neptune - Image", image)
		cv2.waitKey(1)

	## get the points and HS matrix
	points = model.get_points(all_points=True)
	LH = util.descriptors(params, points, points, HS)

	result = HS.HSIC(P_KH, LH)# - HS.HSIC(N_KH, LH)

	model = wiggle(model, state, inverse=True)

	return result


def PSO(state, initial_model, params, P_KH, N_KH, HS):

	M = 100        # number of particles
	K = len(state) 	      # num parameters to define functions

	c1, c2, omega       = 1.49618, 1.49618, 0.7298
	p, v = np.zeros((M, K+1)), np.zeros((M, K))
	b, g = np.zeros((M, K+1)), np.zeros(K+1)

	MAX_ITER = 20

	results = []

	p[0,:K] = state
	p[0,K] = compute_energy(p[0,:K], initial_model, params, P_KH, N_KH, HS)

	for i in range(1, M):	
		
		p[i,:K] = state + ((np.random.rand(K) * 0.2) - 0.1)

		p[i,0] *= 100.
		p[i,1] *= 100.

		v[i,:]  = ((np.random.rand(K) * 0.1) - 0.05)

		p[i,K]   = compute_energy(p[i,:K], initial_model, params, P_KH, N_KH, HS)
		b[i] = np.copy(p[i])

 #    # find the global opt
 	max, idx, = np.copy(p[0,K]), 0
 	for i in range(1, M):
 		if p[i,K] > max:
 			max, idx = np.copy(p[i,K]), i
 	g = np.copy(p[idx,:])

	# ## ==== RUN PSO ==== ##
	for iter in range(MAX_ITER):

		print '-->', iter, g[K]

		for i in range(M):
			p[i,K]      = compute_energy(p[i,:K], initial_model, params, P_KH, N_KH, HS, display=False)
			if p[i,K] > b[i,K]:
				b[i,:] = np.copy(p[i,:])

		max, idx = np.copy(g[K]), -1
		for i in range(0, M):
			if p[i,K] > max:
				max, idx = np.copy(p[i,K]), i

		if idx > -1:
			g = np.copy(p[idx,:])

		compute_energy(g[:K], initial_model, params, P_KH, N_KH, HS, display=True)

		for i in range(M):
			r1, r2 = np.random.rand(1)[0], np.random.rand(1)[0]
			v[i] = (omega * np.copy(v[i])) + (c1 * r1 * (np.copy(b[i,:K]) - np.copy(p[i,:K]))) + (c2 * r2 * (np.copy(g[:K]) - np.copy(p[i,:K])))
			p[i,:K] += np.copy(v[i])

	compute_energy(g[:K], initial_model, params, P_KH, N_KH, HS, display=True)

	state = np.copy(g[:K])

	return state




