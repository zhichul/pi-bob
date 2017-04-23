import sys
import os
import numpy as np
import cv2

def parseData(path):

	res = {"l":[],"r":[],"s":[]}
	for file in os.listdir(path):
		img = cv2.imread(os.path.join(path,file),0)
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

def main():
	indir = sys.argv[1]
	outdir = sys.argv[2]
	assert(os.path.isdir(indir))
	assert(os.path.isdir(outdir))
	for file in os.listdir(indir):
		img = cv2.imread(os.path.join(indir,file),0)
		img = cv2.GaussianBlur(img,(5,5),0)
		img = cv2.resize(img,(16,12))
		cv2.imwrite(os.path.join(outdir,file),img)
	with open(sys.argv[3],"wt") as f:
		f.write(str(parseData(sys.argv[2])))
	return 0

main()