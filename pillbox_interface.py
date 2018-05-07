import sys, os
import cv2
import urllib.request
import image_processing
from bs4 import BeautifulSoup, SoupStrainer

color_codes = {'blue': 'C48333' , 'white': 'C48325', 'black':'C48323', 
	'brown': 'C48332', 'gray': 'C48324', 'green': 'C48329', 
	'orange': 'C48331', 'pink': 'C48328', 'purple': 'C48327', 'red': 'C48326',
	'turquoise': 'C48334', 'yellow': 'C48330', '': ''}
shape_codes = {'capsule': 'C48336', 'round': 'C48348' , 'oval': 'C48345', '': ''}
size_code = '.00'

desc = image_processing


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

def create_url(desc):
	url = 'https://pillbox.nlm.nih.gov/pillimage/search_results.php?'
	search_params = 'getimprint=&getingredient=&getshape='
	shape = desc['shape']
	shape = shape_codes[shape]
	search_params += shape + '&getinactiveingredients=&getfirstcolor='
	color = desc['color']
	color = color_codes[color]
	search_params += color  + '&getauthor=&getsize='
	size = desc['size'] + size_code
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


def eval_search_results(results):
	return

def eval_feature_results(desc):
	return

img = get_image()
bg = get_bg()
desc = image_processing.get_pill_description(img, bg)
query_url = create_url(desc)
# print(query_url)

response = urllib.request.urlopen(query_url)
results = parse_response(response)
print(results)
#getimprint=&getingredient=&getshape=&getinactiveingredients=&getfirstcolor=&getauthor=&getsize=&getDEAschedule=&getscore=0&getlabelCode=&getprodCode=&getnorelabel=NULL&hide=1&submit=Search

# Evaluation is a bit rigid: you might want to rank each feature separately (color, size, etc.) before going for the final full match performance.