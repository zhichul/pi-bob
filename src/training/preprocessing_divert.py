import sys
import os
import numpy as np
import cv2

def parseData(path):
	# res = {"l":[],"r":[],"s":[]}
	res = {"l":[],"r":[],"s":[],"n":[],"d":[]}
	for file in os.listdir(path):
		img = cv2.imread(os.path.join(path,file),0)
		decision = file.split("-")[0]
		t = [0]
		# t = [0] * 4
		if decision == "left":
			pass
		elif decision == "right":
			pass
		elif decision == "straight":
			pass
		elif decision == "none":
			pass
		elif decision == "divert":
			t[0] = 1
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
	full = np.float32(np.full((480,640),255))
	zero = np.float32(np.full((480,640),0))
	for file in os.listdir(indir):
		sfile = file.strip(".jpg")
		for i in range(255//4,255*3//4,10):
			img = np.float32(cv2.imread(os.path.join(indir,file),0))
			img = np.minimum(img+i,full)
			img = cv2.resize(img,(16,12))
			img = cv2.GaussianBlur(img,(3,3),0)
			cv2.imwrite(os.path.join(outdir,sfile+("(+%.2f)"%(i/255))+".jpg"),img)
			# img = np.float32(cv2.imread(os.path.join(indir,file),0))
			# img = np.maximum(img-i,zero)
			# img = cv2.GaussianBlur(img,(5,5),0)
			# img = cv2.resize(img,(16,12))
			# cv2.imwrite(os.path.join(outdir,sfile+("(-%.2f)"%(i/255))+".jpg"),img)


	with open(sys.argv[3],"wt") as f:
		f.write(str(parseData(sys.argv[2])))
	return 0

main()