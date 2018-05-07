import numpy as np
import cv2
import sys, os, math
import pytesseract
from PIL import Image

MAX_KERNEL = 5

def get_image():
	file_name = sys.argv[1]
	img = cv2.imread(file_name)
	return img

def get_bg():
	bg = sys.argv[2]
	if bg == 'flash':
		img = cv2.imread('bg-flash.jpg')
	else:
		img = cv2.imread('bg-noflash.jpg')
	return img


def subtract_background(img, ref):
	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
	fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
	fgmask = fgbg.apply(ref)
	fgmask = fgbg.apply(img)

	return fgmask

def blacken_bg(img, fg):
	for i in range(0, len(img)):
		for j in range(0, len(img[i])):
			if fg[i][j] == 0:
				img[i][j][2] = 0
				img[i][j][1] = 0
				img[i][j][0] = 0
	

	return img

def preprocess(img):
	preprocessed = img.copy()
	# if bgr:
	# 	preprocessed = cv2.cvtColor(preprocessed, cv2.COLOR_BGR2HSV)
	height = img.shape[0]
	width = img.shape[1]
	while width > 1024 or height > 1024:
		img = cv2.resize(img, (round(height * .6), round(width * .6)))
		height = img.shape[0]
		width = img.shape[1]
	img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
	for i in range(1, MAX_KERNEL, 2):
		preprocessed = cv2.GaussianBlur(img, (i, i), 0, 0)
	return preprocessed

def get_roi(img, contour):
	x, y, w, h = cv2.boundingRect(contour)
	
	roi = img[(y-5):(y + h + 5), (x - 5):(x + w + 5)]
	return roi

def identify_color(img):
	img2 = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
	gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
	cv2.erode(gray, None, iterations=2)
	cv2.dilate(gray, None, iterations=2)
	__, contours, __ = cv2.findContours(gray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	if len(contours) > 0:
		cnt = max(contours, key=cv2.contourArea)

		# cv2.drawContours(img, cnt, -1, (0, 255, 0), 3)
		# cv2.imshow('contour', img)
		# cv2.waitKey(0)

		x, y, w, h = cv2.boundingRect(cnt)

		avg_hue = 0
		avg_sat = 0
		avg_val = 0
		count = 0

		for i in range(x, x + w, 3):
			for j in range(y, y + h, 3):
				hsv = img2[j][i]
				if hsv[2] != 0: #not black
					avg_hue += hsv[0]
					count += 1
					avg_sat += hsv[1]
					avg_val += hsv[2]
		
		avg_hue = avg_hue / count
		avg_sat = avg_sat / count
		avg_val = avg_val / count

		# print('hue: ' + str(avg_hue))
		# print('sat: ' + str(avg_sat))
		# print('val: ' + str(avg_val))

		if avg_sat < 50:
			return 'white'
		elif avg_sat < 50 and avg_val > 50:
			return 'gray'
		else:
			#http://i.stack.imgur.com/gCNJp.jpg
			if avg_hue <= 10 or avg_hue >= 160:
				if avg_val > 160 and avg_sat < 240: 
					return 'pink'
				return 'red'
			elif avg_hue > 10 and avg_hue < 20:
				return 'orange'
			elif avg_hue >= 20 and avg_hue <= 40:
				return 'yellow'
			elif avg_hue >= 50 and avg_hue < 80:
				return 'green'
			elif avg_hue >= 80 and avg_hue <= 135:
				return 'blue'
			elif avg_hue > 135 and avg_hue < 160:
				return 'purple'
			else: 
				return ''
	else:
		return 'unknown'

# Round / Oval / Capsule
# Takes BW image
def identify_shape(img): 
	gray = img
	# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
	
	__, contours, __ = cv2.findContours(gray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	if len(contours) > 0:
		cnt = max(contours, key=cv2.contourArea)
		x, y, w, h = cv2.boundingRect(cnt)

		if w == h:
			return 'round'
		else:
			roi = get_roi(gray, cnt)

			dst = cv2.Canny(roi, 30, 255, None, 3)

			lines = cv2.HoughLines(dst, 1, np.pi / 180, 45)

			if lines is not None:
				cdst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
				for i in range(0, len(lines)):
					rho = lines[i][0][0]
					theta = lines[i][0][1]
					a = math.cos(theta)
					b = math.sin(theta)
					x0 = a * rho
					y0 = b * rho
					pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
					pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
					cv2.line(cdst, pt1, pt2, (0,0,255), 3, cv2.LINE_AA)
				# cv2.imshow("Detected Lines (in red) - Standard Hough Line Transform", cdst)
				# cv2.waitKey(0)
				# cv2.destroyAllWindows()
				if len(lines) > 2:
					return 'capsule'
				else:
					return 'oval'
	return ''

# Takes BW image
def read_imprint(img):
	# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	gray = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
	gray = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
	gray = cv2.Laplacian(img, cv2.CV_64F, ksize=3)
	# dst = cv2.Canny(img, 30, 255, None, 3)

	gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)[1]

	cv2.imwrite('gray.png', gray)
	imprint = pytesseract.image_to_string(Image.open('gray.png'))
	return imprint

# mark is 1.5 cm - should get pixel width
# 1103.3333 pixels -> 3310/3 - option to get rid of gold line
def get_measure_mark(img):
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

	__, contours, __ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	if len(contours) > 0:
		contours = np.extract(condition(contours), contours)
		cnt = min(contours, key=cv2.contourArea)

		# cv2.drawContours(img, cnt, -1, (0,255,0), 3)
		# cv2.imshow('contour', img)
		# cv2.waitKey(0)

		x, y, w, h = cv2.boundingRect(cnt)
		return h

# Isolate biggest contours
def condition(contours):
	mat = []
	for c in contours:
		if cv2.contourArea(c) > 1500:
			mat.append(True)
		else:
			mat.append(False)
	return mat

def get_roi_from_edges(edges, img):
	count = 0
	x = 0
	y = 0
	for row in edges:
		if len(np.unique(row)) == 1:
			x = count
			break
		count += 1

	count = 0
	tmp = edges.T
	for row in edges:
		if len(np.unique(row)) == 1:
			y = count
			break
		count += 1

	roi = img[y:, x:]
	return roi

# in mm 
def determine_size(img, fg_only):
	measure_mark = get_measure_mark(img)

	gray = cv2.threshold(fg_only, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
	dst = cv2.Canny(gray, 30, 255, None, 7)
	# roi = get_roi_from_edges(dst, img)

	# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	# gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
	# cv2.erode(gray, None, iterations=2)
	# cv2.dilate(gray, None, iterations=2)
	__, contours, __ = cv2.findContours(dst, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	if len(contours) > 0:
		cnt = max(contours, key=cv2.contourArea)
		# cv2.drawContours(img, cnt, -1, (0,255,0), 3)
		# cv2.imshow('contour', img)
		# cv2.waitKey(0)
		x, y, w, h = cv2.boundingRect(cnt)
		length = max([w, h])
		ratio = length / measure_mark * 1.
		size = ratio * 1.5 * 10 #convert to mm
		size = str(round(size))# + ' mm'
		return size

# Return number of scoremarks - short hough lines?? Not quite working oh well
# Takes BW img
def count_scoremarks(img):
	gray = img
	# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
	
	__, contours, __ = cv2.findContours(gray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	if len(contours) > 0:
		cnt = max(contours, key=cv2.contourArea)
		x, y, w, h = cv2.boundingRect(cnt)

		roi = get_roi(gray, cnt)
		dst = cv2.Canny(roi, 30, 255, None, 3)


		# lines = cv2.HoughLines(dst, 1, np.pi / 180, 45)
		#how to count imprint lines???
		lines = cv2.HoughLinesP(dst, 1, np.pi / 180, 55, 20, 10)
		if lines is not None:
			cdst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
			for i in range(0, len(lines)):
				rho = lines[i][0][0]
				theta = lines[i][0][1]
				a = math.cos(theta)
				b = math.sin(theta)
				x0 = a * rho
				y0 = b * rho
				pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
				pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
				cv2.line(cdst, pt1, pt2, (0,0,255), 3, cv2.LINE_AA)
			cv2.imshow("Detected Lines (in red) - Standard Hough Line Transform", cdst)
			cv2.waitKey(0)
			cv2.destroyAllWindows()
			if len(lines) <= 4:
				return len(lines)
	return 'unknown'

def get_pill_description(img, bg):
	fg = subtract_background(img, bg)
	img = preprocess(img)
	fg = preprocess(fg)
	black_bg = blacken_bg(img, fg)

	desc = {}
	desc['color'] = identify_color(img)
	desc['shape'] = identify_shape(fg)
	desc['imprint'] = read_imprint(fg)
	desc['size'] = determine_size(img, fg)
	# desc['scoremarks'] = count_scoremarks(fg)
	return desc


# img = get_image()
# bg = get_bg()
# fg_only = subtract_background(img, bg)
# img = preprocess(img)
# fg_only = preprocess(fg_only)
# black_bg = blacken_bg(img, fg_only)

# cv2.imshow('black bg', black_bg)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

img = get_image()
bg = get_bg()

desc = get_pill_description(img, bg)
print(desc)


# print(identify_shape(fg_only))
# print(identify_color(img))
# print(count_scoremarks(fg_only))
# print(determine_size(img))
# print(read_imprint(img))