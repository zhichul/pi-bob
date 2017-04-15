import sys
import os
import cv2
def main():
	indir = sys.argv[1]
	outdir = sys.argv[2]
	assert(os.path.isdir(indir))
	assert(os.path.isdir(outdir))
	l = list()
	r = list()
	w = list()
	u = list()
	for file in os.listdir(indir):
		img = cv2.imread(os.path.join(indir,file),0)
		cv2.imshow('classify',img)
		key = cv2.waitKey(0)
		if key == ord('w'):
			w.append(img)
		elif key == ord('a'):
			l.append(img)
		elif key == ord('d'):
			r.append(img)
		elif key == ord('s'):
			u.append(img)
		else:
			if input("Exit?") == "Y":
				break
		
	for index, item in enumerate(l):
		cv2.imwrite(os.path.join(outdir,"left-%d.jpg" % index),item)
	for index, item in enumerate(r):
		cv2.imwrite(os.path.join(outdir,"right-%d.jpg" % index),item)
	for index, item in enumerate(w):
		cv2.imwrite(os.path.join(outdir,"straight-%d.jpg" % index),item)
	for index, item in enumerate(u):
		cv2.imwrite(os.path.join(outdir,"undefined-%d.jpg" % index),item)
	return 0

main()