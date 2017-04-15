import random
import numpy as np

#for testing
import os
import sys
import copy
import cv2 as cv

class N21Unit(object):
	
	"""
	An n input 1 output (real or discrete) unit
	"""
	def __init__(self,ref):
		assert isinstance(ref,str)
		self.ref = ref
		self.upstream = []
		self.downstream = []
		self.o = None

	# methods to be overriden #
	def verify(self):
		pass

	def addUpstream(self,unit):
		assert isinstance(unit,N21Unit)
		self.upstream.append(unit)

	def addDownstream(self,unit):
		assert isinstance(unit,N21Unit)
		self.downstream.append(unit)

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
		assert isinstance(src, N21Unit)
		assert isinstance(dst, N21Unit)
		dst.addUpstream(src)
		src.addDownstream(dst)

	def __repr__(self):
		return 'N21Unit("%s")' % self.ref

	def __str__(self):
		return self.__repr__()

def randomReal(x):
	return random.random() * x

class LinearUnit(N21Unit):
	
	"""
	An n input 1 output (real valued) unit
	"""
	def __init__(self,ref,factor=1):
		super(LinearUnit,self).__init__(ref)
		self.factor = 0.05*factor
		self.weight = [randomReal(self.factor)]
	
	def verify(self):
		if __debug__:
			if not len(self.upstream) > 0:
				raise AssertionError("%s: A linear unit must have at least one upstream unit." % self.ref)

	def addUpstream(self,unit):
		assert isinstance(unit,N21Unit)
		self.upstream.append(unit)
		self.weight.append(randomReal(self.factor))

	def addDownstream(self,unit):
		assert isinstance(unit,N21Unit)
		self.downstream.append(unit)

	def update(self):
		x = [1]
		x.extend([upstreamUnit.o for upstreamUnit in self.upstream])
		self.o = np.inner(self.weight,x)

	def __repr__(self):
		return 'LinearUnit("%s")' % self.ref

	def __str__(self):
		return self.__repr__()

class ThresholdUnit(LinearUnit):

	"""
	An n input 1 (boolean) output unit
	"""

	def update(self):
		super(ThresholdUnit,self).update()
		self.o = 1 if self.o > 0 else -1

	def __repr__(self):
		return 'ThresholdUnit("%s")' % self.ref

	def __str__(self):
		return self.__repr__()

class SigmoidUnit(LinearUnit):

	"""
	An n input 1 (non-linear) output unit
	"""
	
	def update(self):
		super(SigmoidUnit,self).update()
		self.o = 1 / (1 + np.exp(-1*self.o))

	def __repr__(self):
		return 'SigmoidUnit("%s")' % self.ref

	def __str__(self):
		return self.__repr__()

class InputUnit(N21Unit):

	"""
	An input unit with no fan-in only fan-out
	"""
	def __init__(self,ref,factor=1):
		super(InputUnit,self).__init__(ref)
		self.factor = 1

	def update(self,v):
		self.o = self.factor * v

	def __repr__(self):
		return 'InputUnit("%s")' % self.ref

	def __str__(self):
		return self.__repr__()

class Layer(object):

	"""
	A layer of computational units
	"""
	def __init__(self,ref,size,unitClass="SigmoidUnit"):
		self.unitClassName = unitClass
		unitClass = parseClass(unitClass)
		self.ref = ref
		self.units = [unitClass(ref+"U%d"%(i),factor=1/size) for i in range(size)]
		for unit in self.units:
			unit.delta = 0
			unit.moment = 0

	def update(self):
		for unit in self.units:
			unit.update()

	@staticmethod
	def addLink(src,dst):
		assert isinstance(src, Layer)
		assert isinstance(dst, Layer)
		for upstreamUnit in src.units:
			upstreamUnit.addAllDownstream(dst.units)
		for downstreamUnit in dst.units:
			downstreamUnit.addAllUpstream(src.units)

	def __repr__(self):
		return 'Layer("%s",%d,unitClass="%s")' % self.unitClassName

	def __str__(self):
		return self.__repr__()

class InputLayer(Layer):

	def __init__(self,ref,size):
		super(InputLayer,self).__init__(ref,size,unitClass="InputUnit")

	def update(self,v):
		assert len(v) == len(self.units)
		for i, unit in enumerate(self.units):
			unit.update(v[i])


class Network(object):

	def __init__(self,ref,learningRate,sizes,moment=0,hiddenClass="SigmoidUnit",outputClass="SigmoidUnit",outfile="nn.save"):
		assert len(sizes) >= 2
		layerCount = len(sizes)
		self.sizes = sizes
		self.hiddenClass = hiddenClass
		self.outputClass = outputClass
		self.outfile = outfile
		self.ref = ref
		self.rate = learningRate
		self.alpha = moment
		self.layers = []
		self.layers.append(InputLayer("L0",sizes[0]))
		self.layers += [Layer("L%d"%i,sizes[i],unitClass=hiddenClass) for i in range(1,layerCount-1)]
		self.layers.append(Layer("L%d"%(layerCount-1),sizes[-1],unitClass=outputClass))
		self.o = [None] * sizes[-1]
		for i in range(len(self.layers)-1):
			Layer.addLink(self.layers[i],self.layers[i+1])

	def update(self,x):
		self.layers[0].update(x)
		for i in range(1,len(self.layers)):
			self.layers[i].update()
		self.o = tuple([unit.o for unit in self.layers[-1].units])

	def backProp(self,x,t):
		# compute delta for output layer
		# print("==> BackProp in progress...\n\tBefore BackProp: %s %s" % (t,self.o))
		for i, unit in enumerate(self.layers[-1].units):
			unit.moment = unit.delta
			unit.delta = unit.o*(1-unit.o)*(t[i]-unit.o)
		# compute delta for hidden layers if any
		for i in range(1,len(self.layers)-1):
			layer = self.layers[i]
			for index,unit in enumerate(layer.units):
				unit.moment = unit.delta
				unit.delta = unit.o * (1-unit.o) * np.sum([downstreamUnit.weight[index+1] * downstreamUnit.delta for downstreamUnit in unit.downstream])
		#update weights
		for i in range(1,len(self.layers)):
			layer = self.layers[i]
			for unit in layer.units:
				unit.weight[0] += unit.delta * self.rate
				for j in range(1,len(unit.weight)):
					unit.weight[j] += unit.delta * self.rate * unit.upstream[j-1].o + self.alpha * unit.moment
		# print("\tOutput Layer Weights")
		# print("\t\t",self.layers[-1].units[0].weight[0:3])
		# print("\t\t",self.layers[-1].units[1].weight[0:3])
		# print("\t\t",self.layers[-1].units[2].weight[0:3])
		# print("\tOutput Layer Deltas", [unit.delta for unit in self.layers[-1].units])
		# print("\tHidden Layer Weights")
		# print("\t\t",self.layers[1].units[0].weight[0:3])
		# print("\t\t",self.layers[1].units[1].weight[0:3])
		# print("\t\t",self.layers[1].units[2].weight[0:3])
		# print("\tHidden Layer Delta sample", random.choice([unit.delta for unit in self.layers[1].units]))
		# self.update(x)
		# print("\tAfter BackProp: %s %s" % (t,self.o))
		# input("")

	def train(self,trainingSet,testSet):
		error = self.error(testSet)
		lasterror = error
		i = 0
		while (error > 0):
			random.shuffle(trainingSet)
			print("Iter[%d] - Error=%.10f, dE=%.10f. ErrorRate=%.10f" % (i, error, error-lasterror, self.errorRate(testSet)))
			for x,t in trainingSet:
				self.update(x)
				self.backProp(x,t)
			self.save()
			lasterror = error
			error = self.error(testSet)
			i += 1

	def error(self,testSet):
		error = 0
		for instance,t in testSet:
			self.update(instance)
			error += sum(0.5 * np.square(np.subtract(t,self.o)))
		return error

	def errorRate(self,testSet):
		error = 0
		with open("out","wt") as f:
			for instance,t in testSet:
				self.update(instance)
				if self.o.index(max(self.o)) != t.index(max(t)):
					error += 1
				f.write(str(t)+"|"+str(self.o)+"\n")
		return error/len(testSet)


	def __str__(self):
		s =  ("[----Out] <L%d> | " % (len(self.layers)-1)) + str(self.layers[-1].units[0]) + " ... " + str(self.layers[-1].units[-1]) + "\n"
		for i in range(1,len(self.layers)-1):
			s += ("[-Hidden] <L%d> | "  % i)+ str(self.layers[i].units[0]) + " ... " + str(self.layers[i].units[-1]) + "\n"
		s += "[--Input] <L0> | " + str(self.layers[0].units[0]) + " ... " + str(self.layers[0].units[-1])
		return s

	def toString(self):
		d = {}
		d["sizes"] = self.sizes
		d["hiddenClass"] = self.hiddenClass
		d["outputClass"] = self.outputClass
		d["ref"] = self.ref
		d["learningRate"] = self.rate
		d["moment"] = self.alpha
		d["outfile"] = self.outfile
		d["layers"] = []
		for layer in self.layers[1:]:
			d["layers"].append([unit.weight for unit in layer.units])
		return repr(d)

	@staticmethod
	def fromString(s):
		d = eval(s)
		net = Network(d["ref"],d["learningRate"],d["sizes"],moment=d["moment"],hiddenClass=d["hiddenClass"],outputClass=d["outputClass"])
		for n,layer in enumerate(net.layers):
			if n == 0: continue # input unit does not need to be loaded
			for index,unit in enumerate(layer.units):
				unit.weight = d["layers"][n-1][index]
		return net

	def save(self):
		with open(self.outfile,"wt") as f:
			f.write(self.toString())

def parseClass(unitClass):
	if unitClass == "ThresholdUnit":
		unitClass = ThreasholdUnit
	elif unitClass == "SigmoidUnit":
		unitClass = SigmoidUnit
	elif unitClass == "InputUnit":
		unitClass = InputUnit
	else:
		raise AssertionError("Invalid unitClass")
	return unitClass

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
	l1 = [LinearUnit(str(i)) for i in range(n)]
	l2 = [LinearUnit(str(i)) for i in range(2*n)]
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
		assert S.o == 1/(1+np.exp(-1*O.o)).layer


	print("Test on Linear/Threashold/SigmoidUnits passed.")

def testNetwork():
	ANN = Network("ANN",0.05,(64*48,4,3))
	for inputUnit in ANN.layers[0].units:
		assert inputUnit.upstream == []
		assert inputUnit.downstream == ANN.layers[1].units
	for hiddenUnit in ANN.layers[1].units:
		assert hiddenUnit.upstream == ANN.layers[0].units
		assert hiddenUnit.downstream == ANN.layers[2].units
	for outputUnit in ANN.layers[2].units:
		assert outputUnit.downstream == []
		assert outputUnit.upstream == ANN.layers[1].units
	ANN.update(np.random.rand(64*48))
	ANN.update(np.ones(64*48))
	old = copy.copy(ANN.o)
	ANN = Network.fromString(ANN.toString())
	ANN.update(np.ones(64*48))
	new = copy.copy(ANN.o)
	assert old == new
	print("Test on Network passed.")

def main():

	assert len(sys.argv) > 2
	n,m = 16,12
	data = readData(sys.argv[1])
	outfile = sys.argv[2]
	ANN = Network("ANN",0.05,(m*n,60,3),outfile=outfile)
	for i in range(10):
		D = []
		for key in data:
			D.extend(random.sample(data[key],len(data[key])*4//5))
		T = ([x for x in data['r'] if x not in D] + 
			[x for x in data['l'] if x not in D] +
			[x for x in data['s'] if x not in D])
		ANN.train(D,T)
	


def parseData(path):

	res = {"l":[],"r":[],"s":[]}
	for file in os.listdir(path):
		img = cv.imread(os.path.join(path,file),0)
		decision = file.split("-")[0]
		t = [0] * 3
		if decision == "left":
			t[0] = 1
		elif decision == "right":
			t[2] = 1
		elif decision == "straight":
			t[1] = 1
		else:
			print("Unidentified training example: %s" % file)
		if decision[0] in res:
			res[decision[0]].append((tuple(np.multiply(1/255,np.ndarray.flatten(img)).tolist()),tuple(t)))
	return res

def readData(path):
	with open(path,"rt") as f:
		return eval(f.readlines()[0])

if __name__ == "__main__":
	# testUnits()
	# testNetwork()
	main()


