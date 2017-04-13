import sys
import os
import cv2

def main():
	indir = sys.argv[1]
	outdir = sys.argv[2]
	assert(os.path.isdir(indir))
	assert(os.path.isdir(outdir))
	for file in os.listdir(indir):
		img = cv2.imread(os.path.join(indir,file),0)
		img = cv2.resize(img,(64,48))
		img = cv2.GaussianBlur(img,(5,5),0)
		print(img.shape)
		cv2.imwrite(os.path.join(outdir,file),img)
	return 0

main()