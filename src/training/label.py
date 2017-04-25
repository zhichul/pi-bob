import sys
import os
import cv2
import copy

def main():
	indir = sys.argv[1]
	outdir = sys.argv[2]
	assert(os.path.isdir(indir))
	assert(os.path.isdir(outdir))
	l = list()
	r = list()
	w = list()
	u = list()
	lc = 0
	rc = 0
	sc = 0
	processed = os.listdir(outdir)
	processed = set(["-".join(s.split("-")[1:]) for s in processed])
	for file in os.listdir(indir):
		if file in processed:
			print("processed")
			continue
		img0 = cv2.imread(os.path.join(indir,file),0)
		if img0 is None:
			continue
		img = copy.copy(img0)
		y,x = img.shape
		# cv2.line(img,(x//3,0),(x//3,y),(255,255,255),2)
		cv2.line(img,(x//3,0),(x*2//3,y),(255,255,255),2)
		cv2.line(img,(x*2//3,0),(x//3,y),(255,255,255),2)
		# cv2.line(img,(x*2//3,0),(x*2//3,y),(255,255,255),2)
		while True:
			cv2.imshow('classify',img)
			key = cv2.waitKey(0)
			if key == ord('w'):
				sc += 1
				cv2.imwrite(os.path.join(outdir,"straight-%s" % file),img0)
			elif key == ord('a'):
				lc += 1
				cv2.imwrite(os.path.join(outdir,"left-%s" % file),img0)
			elif key == ord('d'):
				rc += 1
				cv2.imwrite(os.path.join(outdir,"right-%s" % file),img0)
			elif key == ord('s'):
				cv2.imwrite(os.path.join(outdir,"undefined-%s" % file),img0)
			else:
				continue
			break
		print(lc,sc,rc)
	# for index, item in enumerate(l):
	# 	cv2.imwrite(os.path.join(outdir,"left-%d.jpg" % index),item)
	# for index, item in enumerate(r):
	# 	cv2.imwrite(os.path.join(outdir,"right-%d.jpg" % index),item)
	# for index, item in enumerate(w):
	# 	cv2.imwrite(os.path.join(outdir,"straight-%d.jpg" % index),item)
	# for index, item in enumerate(u):
	# 	cv2.imwrite(os.path.join(outdir,"undefined-%d.jpg" % index),item)
	return 0

main()