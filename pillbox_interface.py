import sys, os
import cv2
import urllib.request
import image_processing
from bs4 import BeautifulSoup, SoupStrainer
import easygui

color_codes = {'blue': 'C48333' , 'white': 'C48325', 'black':'C48323', 
	'brown': 'C48332', 'gray': 'C48324', 'green': 'C48329', 
	'orange': 'C48331', 'pink': 'C48328', 'purple': 'C48327', 'red': 'C48326',
	'turquoise': 'C48334', 'yellow': 'C48330', '': ''}
shape_codes = {'capsule': 'C48336', 'round': 'C48348' , 'oval': 'C48345', '': ''}
size_code = '.00'

desc = image_processing


def get_image(filename):
	# file_name = sys.argv[1]
	# img = cv2.imread(file_name)
	img = cv2.imread(filename)
	return img

def get_bg(filename):
	# bg = sys.argv[2]
	# if bg == 'flash':
	# 	img = cv2.imread('bg-flash.jpg')
	# else:
	# 	img = cv2.imread('bg-noflash.jpg')
	img = cv2.imread(filename)
	return img

def create_url(desc):
	url = 'https://pillbox.nlm.nih.gov/pillimage/search_results.php?'
	search_params = 'getimprint=&getingredient=&getshape='
	shape = desc['shape']
	shape = shape_codes[shape]
	search_params += shape + '&getinactiveingredients=&getfirstcolor='
	color = desc['color']
	color = color_codes[color]
	search_params += color  + '&getauthor=&getsize='
	size = desc['size']
	if int(size) > 20:
		size = '21'
	size += size_code
	search_params += size + '&getDEAschedule=&getscore=0&getlabelCode=&getprodCode=&getnorelabel=NULL&hide=1&submit=Search'
	url += search_params
	return url


def parse_response(response):
	candidates = []
	result = response.read().decode('utf-8')

	soup = BeautifulSoup(result, 'html.parser', parse_only=SoupStrainer(id='data'))

	soup = soup.find_all('tr')
	for tr in soup:
		row = tr.find_all('b')
		for b in row:
			if b.string == 'Name: ':
				td = b.parent
				name = td.text

				beg = name.find('Name: ') + len('Name: ') 
				name = name[beg:]
				if name not in candidates:
					candidates.append(name)	
	return candidates


def on_open():
	easygui.msgbox('Welcome to the Python Visual Pill Identifier. Please select your image background')
	bg = easygui.fileopenbox()
	easygui.msgbox('Please select the image of the pill you wish to identify')
	img = easygui.fileopenbox()
	return bg, img

def display_results(results):
	easygui.choicebox('Here are the results of your search', 'Search Results', results )


# bg_fn, img_fn = None, None
# while bg_fn == None or img_fn == None:
# 	bg_fn, img_fn = on_open()

# bg = get_bg(bg_fn)
# img = get_image(img_fn)
# desc = image_processing.get_pill_description(img, bg)
# print(desc)
# query_url = create_url(desc)
# # print(query_url)

# response = urllib.request.urlopen(query_url)
# results = parse_response(response)
# # print(results)
# display_results(results)
# eval_feature_results(desc, img_fn)
# eval_search_results(results, img_fn)
#getimprint=&getingredient=&getshape=&getinactiveingredients=&getfirstcolor=&getauthor=&getsize=&getDEAschedule=&getscore=0&getlabelCode=&getprodCode=&getnorelabel=NULL&hide=1&submit=Search

# Evaluation is a bit rigid: you might want to rank each feature separately (color, size, etc.) before going for the final full match performance.