import random
import numpy as np

class N21Unit(object):
	
	"""
	An n input 1 output (real or discrete) unit
	"""
	def __init__(self,name):
		self.name = name
		self.upstream = []
		self.downstream = []
		self.o = None
		self.sig = None

	# methods to be overriden #
	def verify(self):
		pass

	def addUpstream(self,unit):
		pass

	def addDownstream(self,unit):
		pass

	def update(self):
		pass

	# template methods
	def addAllUpstream(self,upstream):
		for unit in upstream:
			assert isinstance(unit,N21Unit) 
			self.addUpstream(unit)

	def addAllDownstream(self,downstream):
		for unit in downstream:
			assert isinstance(unit,N21Unit) 
			self.addDownstream(unit)

	@staticmethod
	def addLink(src,dst):
		dst.addUpstream(src)
		src.addDownstream(dst)

	def __repr__(self):
		return 'N21Unit("%s")' % self.name


class LinearUnit(N21Unit):
	
	"""
	An n input 1 output (real valued) unit
	"""
	def __init__(self,name):
		super(LinearUnit,self).__init__(name)
		self.weight = [random.random()]
	
	def verify(self):
		if __debug__:
			if not len(self.upstream) > 0:
				raise AssertionError("%s: A linear unit must have at least one upstream unit." % self.name)

	def addUpstream(self,unit):
		assert isinstance(unit,N21Unit)
		self.upstream.append(unit)
		self.weight.append(random.random())

	def addDownstream(self,unit):
		assert isinstance(unit,N21Unit)
		self.downstream.append(unit)

	def update(self):
		self.o = np.inner(self.weight,[1] + [upstreamUnit.o for upstreamUnit in self.upstream])

	def __repr__(self):
		return 'LinearUnit("%s")' % self.name

class ThresholdUnit(LinearUnit):

	"""
	An n input 1 (boolean) output unit
	"""

	def update(self):
		super(ThresholdUnit,self).update()
		self.o = 1 if self.o > 0 else -1

	def __repr__(self):
		return 'ThresholdUnit("%s")' % self.name

class SigmoidUnit(LinearUnit):

	"""
	An n input 1 (non-linear) output unit
	"""
	
	def update(self):
		super(SigmoidUnit,self).update()
		self.o = 1 / (1 + np.exp(-1*self.o))

	def __repr__(self):
		return 'SigmoidUnit("%s")' % self.name

class InputUnit(N21Unit):

	"""
	An input unit with no fan-in only fan-out
	"""
	def __repr__(self):
		return 'InputUnit("%s")' % self.name


def testUnits():
	A = LinearUnit("A")
	B = LinearUnit("B")
	try:
		A.verify()
	except AssertionError:
		pass
	N21Unit.addLink(A,B)
	N21Unit.addLink(B,A)
	# test linking
	A.verify()
	B.verify()
	# test update function
	A.weight[1] = 2
	B.weight[1] = 1
	A.weight[0] = 0
	B.weight[0] = 0
	A.o = 1
	B.update()
	assert B.o == 1
	A.update()
	assert A.o == 2
	B.update()
	assert B.o == 2
	A.update()
	assert A.o == 4
	# test addUpstream/Downstream
	n = 10
	l1 = [LinearUnit(i) for i in range(n)]
	l2 = [LinearUnit(i) for i in range(2*n)]
	for inputUnit in l1:
		inputUnit.addAllDownstream(l2)
	for outputUnit in l2:
		outputUnit.addAllUpstream(l1)
	for i1, inputUnit in enumerate(l1):
		for i2, outputUnit in enumerate(l2):
			assert inputUnit.downstream.index(outputUnit) == i2
			assert outputUnit.upstream.index(inputUnit) == i1

	# test representation of random functions
	O = LinearUnit("O")
	T = ThresholdUnit("T")
	S = SigmoidUnit("S")
	n = 1000
	weight = [random.random() for i in range(n)]
	inputs = [InputUnit("In[%d]" %i) for i in range(len(weight)-1)]
	O.addAllUpstream(inputs)
	T.addAllUpstream(inputs)
	S.addAllUpstream(inputs)
	assert len(O.weight) == len(weight)
	assert len(T.weight) == len(weight)
	assert len(S.weight) == len(weight)
	O.weight = T.weight = S.weight = weight
	for i in range(n):
		inputVector = [random.random() for i in range(len(weight)-1)]
		for j in range(len(weight)-1):
			inputs[j].o = inputVector[j]
		O.update()
		T.update()
		S.update()
		assert O.o == np.inner(weight,[1] + inputVector)
		assert (T.o == 1) if O.o > 0 else (T.o == -1)
		assert S.o == 1/(1+np.exp(-1*O.o))


	print("Test on Linear/Threashold/SigmoidUnits passed.")

if __name__ == "__main__":
	testUnits()

